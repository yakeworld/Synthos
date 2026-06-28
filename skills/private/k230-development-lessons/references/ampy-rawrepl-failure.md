# ampy run (raw REPL) 在 K230 上始终失败

## 现象

```
$ ampy -p /dev/openmvcam put /tmp/test.py /sdcard/test.py
# 返回 0 (成功)

$ ampy -p /dev/openmvcam ls /sdcard/
# 看到 test.py

$ ampy -p /dev/openmvcam run /sdcard/test.py
# "Failed to find or read input file: /sdcard/test.py"
# 或超时 300s+
```

## 验证过程

1. `ampy put` 返回 0，文件确实上传到 `/sdcard/`
2. `ampy ls` 能看到文件
3. `ampy run` 始终报 "not found"
4. 空脚本（无 print）也失败
5. 即使 boot.py 是 noop 版本（无串口输出），ampy run 仍然失败
6. ampy run 超时（raw REPL 握手持续等待，300s+）
7. `ampy get /tmp/xxx` 失败——设备 `/tmp/` 路径不存在

## 根因分析

K230 的 raw REPL 实现与 ampy 不兼容。

**关键发现**:
- `ampy put` 和 `ampy ls` 使用 text REPL 协议——工作正常
- `ampy run` 使用 raw REPL 协议——始终失败
- 即使设备没有串口输出（boot.py noop + main.py 无 print），raw REPL 握手仍然失败
- 这说明不是串口洪水导致的问题，而是 K230 raw REPL 实现本身的限制

**可能的原因**:
1. K230 的 raw REPL 入口命令（0xAB）被 FPIOA 映射的其他功能干扰
2. K230 的 Micropython 固件中 raw REPL 实现不完整或有 bug
3. CSI1 硬件故障导致 UART 引脚信号异常，影响 raw REPL 握手
4. 设备在正常运行时（main.py while True），raw REPL 进入被破坏

**结论**: 这是 K230 平台的已知限制。ampy run 不可用于 K230。

## 替代方案

### 方案 A: ampy put + 设备自动加载
将测试脚本放到设备会自动加载的路径（如 main.py 的位置）。

### 方案 B: 串口指令解析器
在 main.py 中预留串口指令解析器，通过串口发送指令触发功能执行。

示例：
```python
# 在 main.py 的 while True 中添加
if uart.any():
    cmd = uart.read().decode().strip()
    if cmd == "START_PHOTO":
        photo_mode_start()
    elif cmd == "START_VIDEO":
        video_mode_start()
```

### 方案 C: 按键触发
通过 GPIO 按键触发特定功能执行。

### 方案 D: Python serial 直接 exec
通过 Python serial 模块直接发送代码到 REPL。

```python
import serial
s = serial.Serial('/dev/openmvcam', 115200, timeout=5)
s.write(b'print("TEST")\n')
# 需要处理 timeout 和输出捕获问题
```

**当前最佳方案**: 方案 B（串口指令解析器）或方案 A（自动加载）。

## 影响

- 所有通过 ampy run 执行 K230 脚本的操作都需要改用其他方案
- 测试流程需要重新设计：先 upload 脚本，再通过设备端触发执行
- 不能依赖 ampy run 的 stdout/stderr 输出获取结果
- 需要通过 ampy get 读取结果文件，或通过设备端写入文件后读取

## 2026-06-19 新增：设备完全无响应时的诊断

当 K230 串口完全无输出（sendBreak + Ctrl+C + Ctrl+D 均无效）：

1. **lsusb 确认设备是否仍在 USB 枚举中**
   - 如果 `lsusb` 不再显示 `1209:abd1` → 物理断开重插
   - 如果 `lsusb` 仍显示 → 设备固件可能卡死但未断电

2. **检查 dmesg 是否有 USB 错误**
   - `device descriptor read/64, error -32` → USB 硬件通信层错误
   - 这通常意味着物理 USB 连接有问题

3. **gvfs PTP 可能仍可访问**
   - 即使串口死，PTP（USB bulk endpoint）可能仍然可用
   - `gvfs` 挂载路径: `/run/user/1000/gvfs/gphoto2:host=Kendryte_CanMV_001000000/`
   - 只能枚举文件，不能读写（只读挂载）

4. **ampy ls 也可能超时**
   - 串口完全死锁时，ampy 任何操作都会超时
   - 这不是 ampy 的问题，是串口物理层无响应

5. **终极修复**: 物理断开 USB，等待 5 秒，重新插入。设备软重启后串口应恢复 `>>>` 提示符。
