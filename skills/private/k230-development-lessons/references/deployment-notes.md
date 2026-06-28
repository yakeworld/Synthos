# 安静模式部署完整流程

## 背景

K230 设备的 main.py 在 `while True` 循环中持续打印状态（特别是 photo/video/inference 模式），导致串口被淹没。在洪水模式下，所有 ampy 命令都会失败。

## 安静模式部署流程

### Step 1: 备份原 boot.py
```bash
ampy -p /dev/openmvcam get /sdcard/boot.py /tmp/original_boot.py
```

### Step 2: 创建 noop boot.py
```python
import time
import machine
import ssd1306
# ... 只保留 OLED 显示，无 print 输出
```
保存到 `/tmp/noop_boot.py`

### Step 3: 上传 noop boot.py
```bash
ampy -p /dev/openmvcam put /tmp/noop_boot.py /sdcard/boot.py
```

### Step 4: 软重启进入安静模式
```python
import serial
s = serial.Serial('/dev/openmvcam', 115200, timeout=5)
s.write(b'\x04')  # Ctrl+D
time.sleep(5)
s.read_all()
s.close()
```

### Step 5: 上传脚本
```bash
ampy -p /dev/openmvcam put <local_script> /sdcard/<remote_script>
```

### Step 6: 执行脚本
**注意**: `ampy run` 在 K230 上始终失败。见 `references/ampy-rawrepl-failure.md`。

替代方案：
- 将脚本上传到设备后，通过设备自动加载执行（如替换 main.py）
- 通过串口指令解析器触发（需在 main.py 中预留）
- 通过按键触发（需在 main.py 中预留）

```bash
# ampy run 不可用，不要使用！
# ampy -p /dev/openmvcam run /sdcard/<remote_script>  → 始终失败
```

### Step 7: 恢复原 boot.py
```bash
ampy -p /dev/openmvcam put /tmp/original_boot.py /sdcard/boot.py
```

## ampy 协议差异

| 子命令 | 协议 | 特点 |
|-------|------|------|
| `ampy ls` | Text REPL | 列出文件，输出稳定 |
| `ampy put` | Text REPL | 上传文件，输出稳定 |
| `ampy get` | Text REPL | 下载文件 |
| `ampy run` | Raw REPL | 执行脚本，print 输出被吞，stdout 延迟 |

**关键**: `ampy run` 使用 raw REPL，**在 K230 上始终失败**。这不是串口洪水问题，而是 K230 raw REPL 实现与 ampy 不兼容。

- `ampy put` 和 `ampy ls` 使用 text REPL——工作正常
- `ampy run` 使用 raw REPL——始终报 "not found"
- 即使设备无串口输出（boot.py noop + main.py 无 print），raw REPL 仍失败
- 详见 `references/ampy-rawrepl-failure.md`

## 设备通信协议

- **设备路径**: `/dev/openmvcam` → `/dev/ttyACM0`
- **USB VID/PID**: `1209:abd1` (Generic OpenMV Cam)
- **波特率**: 115200
- **串口控制**:
  - Ctrl+C — 中断当前执行
  - Ctrl+D — 软重启 (MPY: soft reboot)
  - Ctrl+B — 退出 raw REPL 模式
- **GVFS 限制**: PTP 挂载仅支持目录枚举 (`gphoto2://Kendryte_CanMV_001000000/`)，不支持文件读写

## 目录结构

- **SD卡挂载**: `/sdcard/` — boot.py、photo.py 等代码文件
- **数据目录**: `/data/` — 照片、视频等实际数据
- **拍照输出**: `/data/320p_photos/` (320x240) 或 `/data/photos/` (640x480)
- **录像输出**: `/data/` 下的 video 子目录

## 验证清单

- [ ] 串口是否安静（无洪水输出）
- [ ] ampy ls 能列出目标文件
- [ ] ampy run 执行后 Ctrl+B 能退出
- [ ] 执行后恢复原始 boot.py
- [ ] 记录结果到 session
- [ ] 更新此技能（如有新发现）
