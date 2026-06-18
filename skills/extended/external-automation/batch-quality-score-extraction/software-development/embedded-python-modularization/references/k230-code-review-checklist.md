# K230 CanMV 代码审查清单

针对 K230/CanMV Micropython 项目的 Review 清单，基于实际项目的全面审查总结。

## P0 — 必须修复（编译通过≠运行正确）

### [ ] KeyManager.check() 变量名遮蔽

```python
# ❌ 遮蔽了模块 state
state = key["pin"].value()

# ✅ 改明确名字
pin_state = key["pin"].value()
# 或 level
level = key["pin"].value()
```

### [ ] encoder.GetStream 必须配对 ReleaseStream

```python
# ❌ 异常路径不释放，编码器缓冲区耗尽
try:
    state.encoder.GetStream(...)
    # 处理 packets ...
    state.encoder.ReleaseStream(...)  # 异常时跳过
except:
    pass

# ✅ try/finally 确保释放
got_stream = False
try:
    state.encoder.GetStream(...)
    got_stream = True
    # 处理 packets ...
except Exception as e:
    if 'timeout' not in str(e).lower():
        print("[录像] 异常:", e)
finally:
    if got_stream:
        try:
            state.encoder.ReleaseStream(...)
        except:
            pass
```

### [ ] handle_stop_key 无条件 machine.reset()

停止模式后立即重启，用户无法连续测试不同模式。应标注 TODO 明确这是临时 workaround。

### [ ] 拍照计数不对称

`photo_count` 无条件递增 vs `photo_count_right` 仅在成功时递增 → 单摄/双摄混合时计数错乱。**重构陷阱**：旧字段 + 新字段并存时，旧的计算公式（`lfs_count = state.photo_count if ...`）仍在使用但旧字段不再递增 → OLED 永远显示 0/0。

**修复**：彻底替换为 `cam0_count`/`cam1_count` 独立计数，各自仅在实际成功保存后递增。grep 所有引用旧字段的地方一次性替换干净。

### [ ] upload_inference_results 遍历目录错误

重构后 `uos.listdir(state.INFER_DIR)` 可能指向错误路径——实际批次文件在 `state.infer_session_dir` 子目录。文件路径随变量迁移后未同步。

**修复**：改为 `uos.listdir(state.infer_session_dir)`，上传成功后删除文件避免重复上传。

### [ ] save_idr_left 缓冲区写死分辨率

缓冲区大小写死 `1280 * 720 * 3 // 4` 但实际配置可能不同。改分辨率即溢出。

**修复**：`buf_size = cfg["width"] * cfg["height"] * 3 // 2` 动态分配，加入 `_safe_copy()` 边界检查：溢出时警告并跳过，而非切片赋值崩掉。

### [ ] frame_count 双重身份

推理模式中 `frame_count` 同时是"全局帧号"和"批次内计数器"。批次满 100 重置为 0，导致：
- 日志打印、OLED 刷新、GC 的 `% N == 0` 判断每批次被打断
- 批次切换瞬间（frame_count=0），`%30` `%10` `%60` 全部为真 → 日志+OLED+GC 在 save 之后瞬间叠加

**修复**：分离 `frame_count`（批次内，满 100 重置）和 `infer_total_frames`（全局递增，永不重置）：

```python
state.frame_count += 1      # 批次内
state.infer_total_frames += 1  # 全局

if state.frame_count >= INFER_BATCH_SIZE:
    save_inference_batch()
    state.frame_count = 0

if state.infer_total_frames % 30 == 0:  # 日志
if state.infer_total_frames % 10 == 0:  # OLED
if state.infer_total_frames % 60 == 0:  # GC
```

录像模式同理：`state.frame_count` 在 video／photo／inference 之间共享，切换时可能残留。各模式的 start 函数中应清零。

### [ ] handle_stop_key 无条件 machine.reset()

停止模式后立即重启，用户无法连续测试不同模式。根因是录像 encoder/MediaManager/link 释放顺序敏感，清理不彻底。

**修复**：短期加 TODO 明确标记。长期引入资源栈模式——acquire 推栈，release 时 LIFO 弹出。

```python
# 替代方案：尝试干净停止，失败才 fallback 到 reset
try:
    stop_current_mode()
    cleanup()
    set_oled_log("Mode Stopped", False, 2000)
except Exception as e:
    print("[系统] 停止失败，执行重启:", e)
    import machine
    machine.reset()
```

### [ ] visualizer 阻塞 send 拖垮推理 FPS

`socket.send()` + `settimeout(2)` 在 90fps 推理循环中，单次阻塞 2 秒直接拖到 0.5fps。

**修复**：改用 UDP (`SOCK_DGRAM`) + `sendto()` + `settimeout(0)` 非阻塞，失败静默丢弃。

### [ ] AI2D / 软件预处理 dtype 不一致

AI2D 硬件加速路径输出 `np.uint8`，软件回退路径输出 `np.float32`（归一化后）。如果模型期望 float32，AI2D 路径给出错误输入。

**修复**：两条路径的最终输出必须对齐模型输入要求。在 `init_ai2d_for_inference` 和 `preprocess_for_inference_software` 的返回值中明确标注 dtype。

### [ ] except: pass 吞 KeyboardInterrupt

多处 `except: pass` 会吞掉 Ctrl+C，在嵌入式调试中极难中断。全部改为 `except Exception:`。

### [ ] is_timeout 用字符串匹配异常

`if 'timeout' not in str(e).lower()` — SDK 改异常文案即失效。用关键词集合：

```python
_TIMEOUT_MSGS = ('timeout', 'timed out')
def _is_timeout(e):
    s = str(e).lower()
    return any(k in s for k in _TIMEOUT_MSGS)
```

### [ ] 变量遮蔽模块名

```python
# ❌ state = key["pin"].value()  → 遮蔽 state 模块
# ✅ pin_state = key["pin"].value()
```

## P1 — 必须修复（性能/稳定性）

`/sdcard/config.json` 不存在时创建默认配置字典但不保存。下次重启仍走默认。

**修复**：创建默认配置后调用 `save_config(state.config)` 持久化。

### [ ] 死代码残留

- `init_kpu()` 定义了但从未被调用
- `from hardware import init_sensor_for_video` 在 photo.py 中从未使用
- `v_payload_type = 3` 赋值后从未被读取
- 注释里的双摄录像（`dual_camera_mode` 始终 False）

## P1 — 必须修复（性能/稳定性）

### [ ] 主循环每帧 gc.collect()

`inference` 模式 90fps 下每帧都 GC → 帧率抖动。改为每 N 帧一次：

```python
gc_counter = 0
while True:
    ...
    gc_counter += 1
    if gc_counter >= 100:
        gc_counter = 0
        gc.collect()
```

### [ ] load_config() 默认配置未写回文件

首次启动 `/sdcard/config.json` 不存在时用默认值，但不持久化。下次启动依然走默认路径。

**修复**：`save_config(state.config)` 后返回。

### [ ] get_storage_info() 每帧调用开销大

`uos.statvfs` 是昂贵系统调用。加 5 秒缓存：

```python
_last_check = 0
_cache = "N/A"
def get_storage_info():
    global _last_check, _cache
    now = time.ticks_ms()
    if _last_check and time.ticks_diff(now, _last_check) < 5000:
        return _cache
    # ... 实际查询 ...
    _last_check = now
    return _cache
```

### [ ] video_mode_record 宽 except:pass 吞错误

GetStream 超时是预期行为，但其他异常应记录。区分：

```python
except Exception as e:
    if 'timeout' not in str(e).lower():
        print("[录像] 异常:", e)
```

### [ ] 高频推送场景 TCP→UDP

visualizer.py 注释写 UDP 但实际用 TCP socket。90fps 高频推送建议用 UDP `SOCK_DGRAM` + `sendto`。

### [ ] inference_count 在禁用本地保存时不递增

`save_inference_batch()` 中 `if not save_local: return` — 跳过了递增。虽然影响有限（upload 语义一致），但应明确。

## P2 — 应修复（可维护性）

### [ ] state.py 拆分

60+ 全局变量过于集中。建议按领域拆为 `state/photo_state.py`、`state/video_state.py`，或用 dataclass 封装。

### [ ] 魔法数字

- `6` / `8` / `10` / `12` / `20` / `24` / `128` / `32` 等 OLED 坐标散落各处
- 提取为 `OLED_WIDTH=128`, `OLED_HEIGHT=32`, `ICON_X_OFFSET=20`
- `format_duration(start_ms)` 在多个 `display_*` 函数中重复，抽成工具函数

### [ ] 死代码

- `init_kpu()` 定义了但从未被调用（`inference.py`）
- `dual_camera_mode` 始终 False 但保留大量双摄逻辑
- 注释与实现不一致（visualizer UDP/TCP）

### [ ] 配置无 schema 验证

`load_config()` 直接接受 JSON 字段，类型错误直到使用时才暴露。加字段/类型检查。

## 测试策略

K230 串口 REPL 不稳定，按优先级使用：

1. **ampy CLI** — 最可靠的文件上传/运行方式
   ```bash
   ampy -p /dev/ttyACM0 -b 115200 put local.py /sdcard/remote.py
   ampy -p /dev/ttyACM0 -b 115200 run test.py
   ```
2. **boot.py 自动化** — 将测试脚本设为 boot.py，重启自动跑，结果写文件
3. **paste mode** — Ctrl+E 进入，Ctrl+D 执行（REPL 稳定的情况下）
4. **独立单行命令** — 最基础的调试方式，一行一个命令

**常见问题：**
- CanMV IDE 占用串口 → 先断开
- USB 重枚举 → ttyACM0→ttyACM1 可能变，检查 `ls /dev/ttyACM*`
- 传感器操作后 REPL 不稳定 → 按复位键
- `MediaManager.init()` 每 boot 只能一次 → 跨测试需要 `sensor.stop()→reset()→set_framesize()→run()`

## 性能基准（GC2093 传感器）

| 分辨率 | 格式 | snapshot FPS | 编码链路FPS |
|--------|------|-------------|-------------|
| 640×480 | GRAYSCALE | 59.5 | - |
| 640×480 | RGB565 | 30.3 | - |
| 1280×720 | YUV420SP | 31.4 | **59.8** (H264) |
| 1920×1080 | YUV420SP | 崩溃(OOM) | **60.1** (H264) |

**snapshot 瓶颈**：Python 内存拷贝（~30MB/s），不是传感器上限。
**编码链路**：硬件 DMA，不经过 Python，达到传感器原生 60fps。
