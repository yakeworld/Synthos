# 推理管线详解 — AI2D预处理 → KPU推理 → 后处理

## 核心文件: inference.py

完整的单帧推理流程 `run_inference_optimized(img, kpu, use_ai2d=True)`：

### 阶段1: 图像采集
```python
img = state.active_sensor.snapshot()  # 从Sensor获取当前帧
cap_time = time.ticks_diff(...)       # 采集耗时
```

### 阶段2: AI2D预处理（或软件回退）

**AI2D路径** (当 `state._ai2d_builder is not None`):
```python
input_tensor, meta, preprocess_time = ai2d_preprocess_for_inference(img)
# AI2D内部操作:
#   - 如果GRAYSCALE→保持，否则转灰度
#   - 计算scale = min(dst_w/src_w, dst_h/src_h)
#   - letterbox padding (pad_left, pad_top, pad_right, pad_bottom)
#   - bilinear resize
#   - 输出NCHW格式tensor
```

**软件回退路径**:
```python
input_tensor, meta, preprocess_time = preprocess_for_inference_software(img)
# 内部使用ulab.numpy:
#   - resize → padding → (pixels/127.5)-1.0归一化
```

### 阶段3: KPU推理
```python
kpu.set_input_tensor(0, input_tensor)
kpu.run()
static_params = kpu.get_output_tensor(0).to_numpy().flatten()  # 静态参数
dynamic_params = kpu.get_output_tensor(1).to_numpy().flatten()  # 动态参数
```

### 阶段4: 后处理算法

**置信度计算**:
```python
ecx, ecy, r_eye, r_iris = static_params[0:4]
icx, icy = dynamic_params[6:8]
A = icx - ecx
B = icy - ecy
dist_sq = A*A + B*B
depth_sq = r_eye*r_eye - r_iris*r_iris - dist_sq

if depth_sq < 0:
    confidence = 0.0  # 瞳孔投影超出眼球半径
    C = 0.0
else:
    confidence = 1.0
    C = math.sqrt(depth_sq)
```

**角度计算**:
```python
norm = math.sqrt(dist_sq + C*C + 1e-8)
nz = C / norm
axis_a = 2 * r_iris
axis_b = axis_a * nz
angle_deg = math.atan2(B, A) * 180.0 / math.pi
```

**坐标映射回原始图像**:
```python
scale = meta['scale']
pad_left = meta.get('pad_left', 0)
pad_top = meta.get('pad_top', 0)

pupil_x = (dynamic_params[0] - pad_left) / scale
pupil_y = (dynamic_params[1] - pad_top) / scale
pupil_w = dynamic_params[2] / scale
pupil_h = dynamic_params[3] / scale

iris_x = (icx - pad_left) / scale
iris_y = (icy - pad_top) / scale
iris_a = axis_a / scale
iris_b = axis_b / scale
```

### 阶段5: 输出与推送

```python
# 保存到本地批次
state.inference_results.append({
    "frame": state.infer_total_frames,
    "timestamp": current_time,
    "result": result
})
# 每INFER_BATCH_SIZE=100帧保存为JSON
if state.frame_count >= INFER_BATCH_SIZE:
    save_inference_batch()

# 实时推送到可视化服务器
push_to_visualizer({
    "frame": state.infer_total_frames,
    "timestamp": current_time,
    "result": result,
    "timing": timing
})
```

## 生命周期管理

### 启动流程 (inference_mode_start)
1. 清理传感器
2. 加载config.json获取kmodel_path和sensor_id
3. 初始化Sensor
4. 创建KPU session + load_kmodel
5. 尝试初始化AI2D（获取测试帧→初始化→失败则回退软件）
6. 启动可视化推送
7. OLED显示"INF{}"（A=AI2D启用，S=软件模式）

### 运行循环 (inference_mode_process)
1. 捕获帧
2. 执行run_inference_optimized
3. 更新FPS统计
4. 批量保存（每100帧）
5. 每30帧打印耗时日志
6. 每10帧更新OLED
7. 每60帧GC收集

### 停止流程 (inference_mode_stop)
1. 保存剩余批次
2. 上传所有批次JSON到upload_url
3. 清理KPU+Sensor资源
4. 重置状态

## 性能监控

**耗时分布**（典型值）:
- preprocess: AI2D ~2-5ms，软件 ~20-50ms
- kpu: ~5-15ms（取决于模型大小）
- 后处理+映射: <2ms
- 总耗时: AI2D模式 ~10-20ms → 50-100fps，软件模式 ~30-60ms → 15-30fps

**性能日志**（每30帧输出）:
```
[推理] cap:2ms AI2D pre:5ms kpu:10ms total:17ms fps:58.8
```
