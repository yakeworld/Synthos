# 串口部署到 K230/CanMV 板

将通过 `embedded-python-modularization` 分解后的代码部署到 K230 开发板的方法。

## 适用场景

- CanMV IDE 未安装、不可用或连不上
- 需要通过 CI/脚本批量部署
- 需要快速迭代测试（改代码→上传→验证）
- 板子在远程服务器上（只暴露串口）

## 硬件连接

K230 通过 USB 虚拟串口暴露 REPL。宿主机的连接路径：

```
/dev/ttyACM0    # 典型路径（CanMV/OpenMV设备）
```

检查连接：
```bash
ls -la /dev/ttyACM*   # 看设备是否存在
lsusb | grep "OpenMV\|Canaan\|1209"  # 看USB是否识别
```

## 连接参数

| 参数 | 值 |
|:-----|:----|
| 波特率 | 115200（K230 默认） |
| 超时 | 3-5 秒（处理大文件需要更长） |
| 数据位 | 8 |
| 停止位 | 1 |
| 奇偶校验 | 无 |

## 基础交互（pyserial）

```python
import serial, time

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=3)
time.sleep(0.5)            # 等待设备就绪
ser.reset_input_buffer()   # 清空缓存
ser.write(b'\x03')         # Ctrl+C 中断可能的运行程序
time.sleep(0.3)
ser.read_all()             # 丢弃中断后的输出

# 执行单行命令
def run_simple(cmd, wait=2):
    ser.write(cmd.encode() + b'\r\n')
    time.sleep(wait)
    return ser.read_all().decode(errors='replace')

r = run_simple("print('hello')")
print(r)  # 应看到 "hello"
```

## Paste 模式（多行代码）

MicroPython 不支持直接发送多行。使用 Ctrl+E/Ctrl+D paste 模式：

```python
def paste_run(code, wait=3):
    """Ctrl+E 进入粘贴模式 → 发送代码 → Ctrl+D 执行"""
    ser.write(b'\x05')       # Ctrl+E
    time.sleep(0.2)
    ser.read_all()
    ser.write(code.encode())
    time.sleep(0.1)
    ser.write(b'\x04')       # Ctrl+D
    time.sleep(wait)
    return ser.read_all().decode(errors='replace')

# 执行多行代码
paste_run("""
for i in range(3):
    print('line', i)
print('done')
""")
```

## 文件上传（base64 分块法）

在 REPL 中没有文件传输通道，用 base64 编码 + 字符串拼接绕过行长度限制：

```python
import base64

def upload_file(local_path, remote_path, ser):
    """通过base64上传文件到K230"""
    with open(local_path, 'rb') as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode()
    
    # 1. 初始化空字符串
    run_simple("import ubinascii; b=''", 0.3, ser)
    
    # 2. 分块拼接（每块200字符避免REPL缓冲区溢出）
    chunk_size = 200
    for i in range(0, len(b64), chunk_size):
        chunk = b64[i:i+chunk_size]
        run_simple(f"b+='{chunk}'", 0.15, ser)
    
    # 3. 解码并写入文件
    paste_run(f"""
raw=ubinascii.a2b_base64(b)
f=open('{remote_path}','wb')
f.write(raw)
f.close()
print('ok', len(raw))
""", 3, ser)
```

**为什么分块？** MicroPython REPL 的单行输入有缓冲区限制（通常 256-512 字节）。base64 编码后的文件约膨胀 33%，分块 200 字符每行安全。

## 文件上传（ampy 工具 — 推荐）

`ampy`（Adafruit MicroPython Tool）提供可靠的文件传输，比手工 base64 上传稳定得多。

```bash
# 安装
pip3 install --break-system-packages adafruit-ampy

# 上传文件
ampy -p /dev/ttyACM0 -b 115200 put local_file.py /sdcard/remote_file.py

# 列出目录
ampy -p /dev/ttyACM0 -b 115200 ls /sdcard/

# 下载文件
ampy -p /dev/ttyACM0 -b 115200 get /sdcard/file.py

# 运行文件
ampy -p /dev/ttyACM0 -b 115200 run /sdcard/test.py
```

**注意：** `ampy run` 在涉及传感器/编码器操作时可能超时，因为硬件操作时间不确定。替代方案：用 `put` 上传后通过 boot.py 自动执行。

### CanMV IDE 自动连接冲突

CanMV IDE 在检测到 K230 设备时会**自动连接**串口，阻塞其他工具访问：

```
$ lsof /dev/ttyACM0
COMMAND    PID     USER   ... NAME
canmvide 12345 yakeworld  ... /dev/ttyACM0

$ ampy -p /dev/ttyACM0 put file.py
# → PyboardError: could not enter raw repl
```

**解决方案（按优先级）：**
1. **在 CanMV IDE 中点「断开连接」**（插头图标）— IDE 保持打开
2. **关闭 CanMV IDE** — 100% 可靠
3. **`kill <PID>`** — 仅当前两种不可行时

等待 1-2 秒让端口释放后再用 ampy。有时端口需要几秒注销（Linux 上常见）。

## boot.py 自动化测试模式

对于涉及硬件的长时间测试（摄像头、编码器），直接在 REPL 中交互容易因硬件 printk 输出导致 REPL 状态异常。更可靠的方式：

**流程：**
1. 上传测试脚本到 `/sdcard/`
2. 修改 `/sdcard/boot.py` 使其开机自动运行测试脚本
3. 发送 Ctrl+D 软重启
4. 等待测试完成（输出通过串口回流）
5. 恢复 boot.py

```python
# 步骤 2：设置 boot.py
ser.write(b"open('/sdcard/boot.py','w').write("
    b"'import sys;sys.path.insert(0,\"/sdcard\");"
    b"exec(open(\"/sdcard/test_script.py\",\"rb\").read())\\\n')\\n")

# 步骤 3：重启
ser.write(b'\x04')  # Ctrl+D 软重启
time.sleep(10)      # 等待测试完成

# 步骤 4：读取输出
out = ser.read_all()

# 步骤 5：恢复 boot.py
ser.write(b"open('/sdcard/boot.py','w').write('import uos\\nprint(\"boot ok\")\\n')\\n")
```

**适用场景：** 编码器 FPS 测试、传感器多分辨率测试、长时间录制测试。任何无法在 REPL 单次交互内完成的硬件操作。

## 导入路径设置

K230 上文件放在 `/sdcard/`，但 Python 默认不搜索该路径：

```python
# 每次 REPL 会话需执行
import sys
sys.path.insert(0, '/sdcard')

# 然后才能 import
import state
from config import load_config
```

## K230 特性与陷阱

### REPL 回显模式陷阱

K230 的 REPL 在长时间运行或硬件操作后会进入"只回显不执行"状态：发送的每个命令都在终端回显，但不会实际执行。这是由硬件驱动层的 printk 消息打乱 REPL 状态机导致的。

**症状：**
```
>>> print("hello")
print("hello")    # ← 只有回显，没有 "hello" 输出
```

**原因：** 传感器 `snapshot()`、`MediaManager` 操作、编码器 `GetStream()` 等硬件操作会产生内核级 printk 输出，这些输出会穿插在 REPL 中破坏解析状态。

**解决方案：**

1. **物理复位** — 按 K230 板上的 Reset 按钮。这是最可靠的方法。
2. **DTR 复位** — 部分板子支持通过串口 DTR 线复位：
   ```python
   ser.setDTR(False); time.sleep(0.3)
   ser.setDTR(True); time.sleep(2)
   ser.read_all()  # 等待启动输出
   ```
3. **Ctrl+D 软重启** — 软重启不一定恢复，因为硬件状态可能已被污染。

**预防：**
- 每个测试用 `ser.reset_input_buffer()` 清空缓存
- 发送命令后等待 `>>>` 提示符出现再发下一条
- 在 `while` 循环中读取直到提示符出现：
  ```python
  def run_and_wait(cmd, ser, timeout=5):
      ser.write(cmd.encode() + b'\r\n')
      out = b''
      for _ in range(timeout * 2):
          d = ser.read()
          if d:
              out += d
              if b'>>>' in out:
                  break
          time.sleep(0.5)
      return out.decode(errors='replace')
  ```
- 涉及传感器的测试尽量一次完成（paste mode），不拆成多步

### 文件系统

| 路径 | 用途 | 可写 |
|:-----|:-----|:-----|
| `/sdcard/` | 用户代码 + 配置文件 | ✓ |
| `/data/` | 数据输出（照片/视频/推理结果） | ✓ |
| `/` | 系统根目录 | 只读 |
| `/bin/` | 系统二进制 | 只读 |

### 字符串比较

CanMV 基于 `rt-smart`，非标准 MicroPython。`uos` 替代 `os`：

```python
import uos  # 不要用 import os
files = uos.listdir('/sdcard')
```

### 内存

加载 10 个模块（~70KB 代码）后，可用 RAM 约 500-600KB。如果运行中内存不足：
- 减少模块数（合并小型模块）
- 检查 state.py 是否导入了不必要的内容（它只应有常量和变量）
- 在模块函数体内 import 硬件库（延迟加载）

### 重置

```python
import machine
machine.reset()   # 软重启板子
```

## 完整部署脚本模板

```python
import serial, time, base64, os

SERIAL_PORT = '/dev/ttyACM0'
BAUD = 115200
REMOTE_DIR = '/sdcard'

def connect():
    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=5)
    time.sleep(0.5)
    ser.reset_input_buffer()
    ser.write(b'\x03')
    time.sleep(0.3)
    ser.read_all()
    return ser

def run_simple(cmd, wait, ser):
    ser.write(cmd.encode() + b'\r\n')
    time.sleep(wait)
    return ser.read_all().decode(errors='replace')

def upload(local, remote, ser):
    with open(local, 'rb') as f:
        raw = f.read()
    b64 = base64.b64encode(raw).decode()
    run_simple("import ubinascii; b=''", 0.3, ser)
    for i in range(0, len(b64), 200):
        run_simple(f"b+='{b64[i:i+200]}'", 0.15, ser)
    run_simple(
        f"raw=ubinascii.a2b_base64(b);"
        f"f=open('{remote}','wb');f.write(raw);f.close()",
        2, ser
    )

def verify_imports(modules, ser):
    run_simple("import sys; sys.path.insert(0,'/sdcard')", 0.5, ser)
    for mod in modules:
        r = run_simple(f"exec('import {mod}'); print('{mod}: OK')", 1.5, ser)
        if 'OK' not in r:
            print(f"FAIL: {mod}")

# 使用
ser = connect()
files = ['state.py', 'config.py', 'main.py']
for f in files:
    upload(f, f"{REMOTE_DIR}/{f}", ser)
verify_imports(['state', 'config', 'main'], ser)
ser.close()
```

## 验证清单

部署后执行以下检查：

- [ ] `import state` — 常量读取正确
- [ ] `config.load_config()` — 返回 dict，key 齐全
- [ ] `utils.get_temp()` — 返回 float（~40-55°C 正常）
- [ ] `gc.mem_free()` — 剩余内存 > 300KB
- [ ] 模型文件存在 — `uos.stat(config['kmodel_path'])` 无异常
- [ ] 硬件模块可导入 — `from media.sensor import Sensor`
