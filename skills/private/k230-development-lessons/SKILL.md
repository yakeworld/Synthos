---
name: k230-development-lessons
category: embedded
description: K230 (Sipeed Maix series) 嵌入式开发技能。核心原则：每一次成功都应该记录，每一次失败应该分析原因，不断进步，避免错误。覆盖串口部署、设备通信、拍照/录像功能调试、硬件故障排查、NPU算力验证。
signature: "k230-development-lessons -> processed_result"
---
version: 2.0.0

# K230 嵌入式开发技能

## 核心原则

每一次成功必须记录，每一次失败应该分析原因，不断进步，避免重复错误。

## 快速导航

| 参考文件 | 内容 |
|---------|------|
| references/deployment-notes.md | 安静模式部署完整流程、ampy 协议差异、设备通信协议 |
| references/debugging-playbook.md | 故障诊断树：从症状到根因到修复 |
| references/ampy-rawrepl-failure.md | ampy run (raw REPL) 始终失败的根因分析和替代方案 |
| references/video-test-report.md | 录像功能测试报告，含硬件管线和帧率分析 |
| references/hardware-specs.md | K230 硬件规格参考，含 NPU 算力说明和固件信息 |
| references/button-failure-diagnosis.md | K230 按键无效根因：TOUCH vs Pin 混用 |

## K230 自动化管理

### 设备管理器 — k230_manager.py

**核心发现**：K230 的 `ampy run`（raw REPL）不可用，但可以直接通过 Python 调用 `ampy.pyboard.Pyboard` 实现所有功能。

**端口**: `/dev/openmvcam` (115200 baud)

**核心 API**：
```python
from ampy.pyboard import Pyboard

board = Pyboard('/dev/openmvcam', baudrate=115200)
board.enter_raw_repl()       # 进入 raw REPL（含软重启）
result = board.exec_(code)   # 执行代码并获取输出
board.exit_raw_repl()        # 退出 raw REPL
board.close()
```

**功能封装**（在 k230_manager.py 中）：
- `k230_exec(code)` — 执行代码返回输出
- `k230_execfile(local, remote)` — 上传并执行脚本
- `k230_reboot()` — 通过 machine.reset() 软重启
- `k230_listdir(path)` — 列出目录内容
- `k230_get(remote, local)` — 下载文件
- `k230_put(local, remote)` — 上传文件

### 自动化操作管线

1. **软重启**: 通过串口发送 `import machine; machine.reset()` 实现设备重启，**不依赖物理操作**
2. **文件上传**: 通过 `Pyboard.exec_()` 发送文件内容，设备端用 `open().write()` 写入
3. **代码执行**: 通过 `Pyboard.exec_()` 发送代码并获取输出
4. **目录列举**: 通过 `Pyboard.exec_()` 执行 `os.listdir()`
5. **文件下载**: 通过 `Pyboard.exec_()` 执行 `open().read()` + hexlify

### 已验证操作

1. ✅ **清理空目录**: 删除 `/data/320p_photos/` 下所有空子目录（025-034）
2. ✅ **拍照测试**: 左摄 320x240 拍照正常，~20 FPS，文件正常写入
3. ✅ **录像测试**: H264 硬件编码 + MP4 Muxer，5秒录制99帧，18.8MB
4. ✅ **状态检查**: `state.current_mode`, `state.is_running`
5. ✅ **目录枚举**: `os.listdir('/data/')`
6. ✅ **配置读取**: `get_video_config()` 获取完整配置
7. ✅ **设备重启**: `machine.reset()` 实现完全软重启

### 录像功能管线

**硬件管线**: VI(传感器) → VENC(H264编码器) → MP4 Muxer

- `video_mode_start()`: 初始化传感器、MP4 Muxer、H264 编码器，启动管线
- `video_mode_record()`: 消费编码器输出并写入 MP4（需在主循环中周期性调用）
- `video_mode_stop()`: 停止管线，关闭文件

**录像测试结果**:
- 分辨率: 1280x720 @ 90fps
- 编码: H264, 200 Mbps (配置) / ~240 Mbps (实际)
- 帧数: 99帧 / 5秒 ≈ 20 FPS
- 文件大小: 18.8 MB / 5秒

### 已知陷阱

1. **串口洪水**: main.py 的 print 淹没 REPL → 已通过移除 main.py 的 print 解决
2. **ampy run 失败**: K230 raw REPL 协议不兼容 → 使用 Python Pyboard 直接调用
3. **右摄 CSI1 故障**: 初始化导致设备挂死
4. **空目录积累**: `ensure_dir()` 无条件创建 → 需定期清理
5. **Micropython 限制**: 不支持 f-string、列表推导式、f-string、triple-quoted
6. **设备死锁**: 串口完全无输出时 sendBreak/Ctrl+C/Ctrl+D 均无效 → 物理断开 USB 重插
7. **lsusb 假阳性**: lsusb 成功 ≠ 串口可用，设备可能处于哑状态
8. **gvfs PTP 只读**: PTP 挂载仅支持枚举，不支持读写
9. **GPIO 按键 FPIOA 映射 — 分固件版本**:
    - **标准 CanMV 固件**: `machine.Pin()` 内部自动处理 FPIOA 映射，不需要显式调用 FPIOA。直接用 `machine.Pin(pin, Pin.IN, Pin.PULL_UP)` 即可，额外 FPIOA 调用会覆盖正确映射。
    - **RT-Smart 固件**（从 revision.txt 的 `rtsmart` 字符串确认）: `machine.Pin()` 不自动配置 FPIOA，**必须**先显式调用 `fpioa.set_function(pin, FPIOA.GPIO0 + pin)` 再 `machine.Pin(pin, Pin.IN, Pin.PULL_UP)`。官方示例 `examples/16-AI-Cube/DataCollectionCamera.py` 验证了此模式。
    - **判断方法**: 检查 `/revision.txt` 中是否包含 `rtsmart`。如果板子上运行的是 RT-Smart 固件，FPIOA 是必需的。
    - **注意**: `FPIOA.GPIO0 + pin` 中 `pin` 是 GPIO 逻辑编号（如 18, 19），K230 的 FPIOA.GPIO0 到 GPIO63 是连续整数 0-63，所以 `GPIO0 + 18 = GPIO18` 是正确的 GPIO 函数值。

10. **不同 K230 板型的按键 GPIO 号不同**: 通过 `os.uname()[-1]` 检测板型：
    - `k230_canmv_01studio`: 按键在 GPIO21，按键值 0（按下=低电平）
    - `k230_canmv_lckfb`: 按键在 GPIO53，按键值 1（按下=高电平）
    - 其他板型：默认 GPIO21，按键值 0
    - 开发者应当在代码中检测板型并分配不同的 GPIO 号，见 `examples/16-AI-Cube/DataCollectionCamera.py`

11. **`inference_mode_start()` 缺少 `state.current_mode` 设置**: 初始化推理模式时必须同时设置 `state.current_mode = "inference"` 和 `state.is_running = True`，否则主循环不会进入推理模式分支。这是除硬件之外的常见逻辑错误。

12. **主循环 idle `time.sleep()` 扼杀按键轮询**: `key_manager.check()` 必须高频调用才能可靠检测按键按下。如果空闲态添加 `time.sleep(0.1)`，每次循环间隔 100ms，短按（<100ms）的按键事件会被完全错过。正确的 idle 处理是 `pass` 或者 `time.sleep_us(1000)`（1ms 级别的微小延迟），保持微秒级轮询频率。

13. **重复 `main()` 调用导致 Pin 对象冲突**: `main.py` 末尾如果有两个 `if __name__ == "__main__": main()` 块，第一个 `main()` 意外退出后会再运行第二个。第二个 KeyManager 会尝试在已被第一个 KeyManager 占用的引脚上创建 Pin 对象，导致 GPIO 引脚处于不一致状态。必须使用 `while True: main(); time.sleep(1)` 无限重启循环（如同 `main_origin.py`），确保一次只有一个 `main()` 在运行。

14. **主循环结构必须与 `main_origin.py` 一致**: 分模块重构时容易破坏主循环的语义等价性。关键点：
    - 必须使用 `while True: main(); time.sleep(1)` 无限重启循环
    - idle 态不得有超过 1ms 的 sleep
    - 避免任何 `if __name__ == "__main__": main()` 的重复写法
    - 所有 GPIO 相关的异常必须被捕获并打印到串口，不能静默吞掉

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
