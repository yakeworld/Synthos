# 软件架构总览 — 三层管线 + 模块职责

## 三层架构

```
采集层 (Sensor → CSI → Frame)
    ↓
预处理层 (AI2D硬件 / ulab软件)
    ↓
推理层 (KPU → .kmodel → 后处理 → JSON/WebSocket)
```

## 模块职责矩阵

### state.py — 全局状态与常量

定义所有全局常量和可变状态：
- 路径常量: DATA_ROOT="/data", CONFIG_FILE="/sdcard/config.json"
- 路径: PHOTO_DIR, INFER_DIR, VIDEO_DIR, 各序列文件
- 硬件常量: KEY0-KEY3 GPIO, OLED I2C, INFER配置
- 可变状态: current_mode, is_running, 各模式session计数
- 资源句柄: active_sensor, kpu_session, oled, encoder, mp4_handle
- AI2D内部: _ai2d, _ai2d_builder, _ai2d_output_tensor, _ai2d_meta
- 网络: wifi_ip, _wlan, _visualizer_sock

**关键模式**: 所有硬件资源通过 `state.xxx = None` 初始化，运行时赋值。`state.is_running` 控制所有模式循环。

### config.py — 配置管理

核心功能:
1. `load_config()` — 从config.json加载，带缓存（state.config）
2. `save_config(new_config)` — 保存配置
3. 序列号管理: `get_next_photo_sequence()`, `get_next_video_sequence()`, `get_next_infer_sequence()`
4. 格式转换: `get_pixformat_value()` — 字符串→Sensor常量
5. 各模式getter: `get_photo_config()`, `get_inference_config()`, `get_video_config()`, `get_model_config()`, `get_visualizer_config()`

**关键模式**: 加载后缓存在 `state.config`，避免重复IO。序列号独立文件存储，会话间持久化。

### hardware.py — 硬件抽象

四大模块:
1. **OLEDDisplay** (SSD1306 128×32 I2C)
   - `display_boot()`, `display_main()`, `display_photo_running()`, `display_inference_running()`, `display_video_running()`
   - WiFi信号图标绘制（4级）
   - 刷新率控制（100ms间隔）

2. **KeyManager** (GPIO18-21, PULL_UP, 50ms消抖)
   - `register_callback(key_name, callback)`
   - `check()` — 检测按键下降沿，触发回调

3. **摄像头初始化**
   - `init_sensor()` — 标准模式
   - `init_sensor_for_inference()` — 推理模式（GRAYSCALE）
   - `init_sensor_for_video()` — 录像模式（YUV420SP）

4. **WiFi管理**
   - `connect_wifi()` — STA模式，自动连接
   - `get_wifi_signal()` — RSSI→4级信号强度

### inference.py — 推理引擎

完整生命周期:
1. `inference_mode_start()` — 初始化Sensor+KPU+AI2D+可视化
2. `inference_mode_process()` — 主循环：capture→preprocess→infer→postprocess→save/push
3. `save_inference_batch()` — 每100帧保存JSON
4. `upload_inference_results()` — 上传批次到服务器
5. `inference_mode_stop()` — 清理资源

**AI2D开关**: `state._ai2d_builder is not None` → AI2D模式，否则软件回退。

### ai2d.py — AI2D预处理

核心函数:
- `init_ai2d_for_inference(src_w, src_h, src_ch, dst_w, dst_h, dst_ch)` — 初始化AI2D，配置pad+resize
- `ai2d_preprocess_for_inference(img)` — 执行AI2D预处理，返回tensor+meta+耗时
- `preprocess_for_inference_software(img)` — 软件回退方案

**内部实现**: NCHW格式，uint8，bilinear resize，half_pixel模式。

### eye_gaze.py — 完整演示管线

双模型级联: FaceDetApp → EyeGazeApp
- 人脸检测（320×320，置信度0.5，NMS 0.2）
- 对每个检测人脸做注视估计（448×448，crop+resize）
- 输出: 人脸bbox + [(pitch, yaw), ...]
- 绘制: 在人脸中心画箭头指向注视方向

## 数据流

```
config.json (WiFi/分辨率/模型路径)
    → config.py (加载+缓存)
    → hardware.py (初始化Sensor/OLED/按键/WiFi)
    → inference.py (启动推理循环)
    → ai2d.py (预处理)
    → KPU (推理)
    → 后处理 → JSON
    → 本地保存 + WebSocket推送
```

## 会话管理

每种模式独立计数:
- photo_session_seq / video_session_seq / infer_session_seq
- 每个会话创建独立目录: /data/photos/{seq}/, /data/inference/{seq}/
- 序列号持久化在 /sdcard/{mode}_sequence.txt
