# K230 录像功能测试报告

## 测试环境
- 设备: K230 (Sipeed Maix series)
- 固件: CanMV IDE K230 4.0.9
- 连接: USB CDC ACM `/dev/openmvcam` @ 115200 baud
- 摄像头: gc2093 @ 1280x720 @ 90fps

## 测试方法

### 自动化协议
由于 `ampy run`（raw REPL）在 K230 上不可用，通过 Python 直接调用 `ampy.pyboard.Pyboard`：

```python
from ampy.pyboard import Pyboard

board = Pyboard('/dev/openmvcam', baudrate=115200)
board.enter_raw_repl()       # 进入 raw REPL（含软重启）
result = board.exec_(code)   # 执行代码
board.exit_raw_repl()
board.close()
```

### 录像测试流程

1. `video_mode_start()` → 启动硬件管线（VI → VENC → MP4 Muxer）
2. 模拟主循环，每 50ms 调用 `video_mode_record()`（目标 ~20 FPS）
3. 录制 5 秒
4. `video_mode_stop()` → 停止管线

## 测试结果

### 录像功能 v1（直接调用 video_mode_start 后等待，不主动调用 record）
- 录制时间: ~5秒
- 录制帧数: **0 帧**
- 文件大小: **24 bytes**（仅 MP4 header）
- 结论: 管线启动成功但帧未写入

### 录像功能 v2（模拟主循环，周期性调用 video_mode_record）
- 录制时间: 5057ms
- video_mode_record 调用: **18 次**
- 录制帧数: **99 帧**
- 文件大小: **19,725,682 bytes (18.8 MB)**
- 实际帧率: ~20 FPS
- 实际码率: ~240 Mbps（配置 200 Mbps）

## 分析

1. **录像管线设计**: VI → VENC → MP4 Muxer 是硬件流水线，帧自动从传感器流经编码器到 MP4 Muxer
2. **关键**: `video_mode_record()` 需要周期性调用以消费编码器输出并写入 MP4
3. **帧率瓶颈**: 实际帧率受限于 `video_mode_record()` 调用频率（每 50ms = 20 FPS）
4. **码率偏高**: 实际 240 Mbps > 配置 200 Mbps，可能因为 GOP 长度 gop_len=1（每帧都是 I 帧）

## 文件位置

- 测试脚本: `/media/yakeworld/sda2/canmv/k230/test_video_record.py`
- 输出文件: `/data/videos/051/video_cam0.mp4` (19,725,682 bytes)
