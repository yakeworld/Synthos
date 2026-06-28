# K230 调试手册

## 故障诊断树

```
设备无响应？
  ↓
串口完全无输出？
  → 是 → 物理重启（断电5秒或拔USB重插）
  → 否 ↓
串口有输出但全是 >>> 或 echo？
  → 是 → 串口洪水，main.py 的 while True 循环在 print
         解决：安静模式部署（替换 boot.py）
  → 否 ↓
ampy run/put/get 失败？
  → 是 → 先 ampy ls 确认文件存在
         然后软重启 Ctrl+D
         再重试
  → 否 ↓
ampy run 无输出但有错误？
  → 检查：raw REPL 吞了 print 输出，脚本可能已执行
         通过 ampy ls 检查文件是否创建
```

## 串口洪水诊断

### 症状
- 所有 ampy 命令返回 "Failed to find or read input file"
- 串口输出为空 `b''` 或只有 echo
- `SyntaxError: invalid syntax` 在 REPL 中
- raw REPL 模式无法退出（Ctrl+B 无效）

### 根因
main.py 的 `while True` 循环在 photo/video/inference 模式下持续 print。

### 验证方法
```bash
# 检查设备是否还在打印
timeout 3 ampy -p /dev/openmvcam ls /sdcard/ 2>&1
# 如果输出中有多行 >>> 或乱码，说明洪水存在
```

### 修复步骤
1. 用 ampy get 下载当前 boot.py 备份
2. 创建 noop 版本（无 print）
3. ampy put 上传 noop boot.py
4. Ctrl+D 软重启
5. 执行操作
6. 恢复原 boot.py

## ampy 故障排除

### ampy run 报 "not found" 但 ampy ls 能看到
- **原因**: K230 raw REPL 与 ampy 不兼容——**始终失败**，不是路径问题
- **解决**: 不要用 ampy run。改用设备自动加载/串口指令/GPIO触发

### ampy run 无输出
- **原因**: raw REPL 吞了 print 输出，脚本可能已执行
- **解决**: 通过 ampy ls 检查文件是否创建，或通过串口直接 exec 代码
- **注意**: 在 K230 上，am py run 根本不执行，所以无输出

### ampy 超时
- **原因**: K230 raw REPL 握手持续等待（300s+），设备在正常运行时破坏握手
- **解决**: 不要用 ampy run。改用其他执行方案。

## 设备通信协议细节

### Serial
- **设备路径**: `/dev/openmvcam` → `/dev/ttyACM0`
- **USB VID/PID**: `1209:abd1` (Generic OpenMV Cam)
- **波特率**: 115200

### 串口控制字符
```python
b'\x03'  # Ctrl+C — 中断当前执行
b'\x04'  # Ctrl+D — 软重启 (MPY: soft reboot)
b'\x02'  # Ctrl+B — 退出 raw REPL 模式
```

### GVFS PTP 挂载
```
/run/user/1000/gvfs/gphoto2:host=Kendryte_CanMV_001000000
```
- **限制**: 仅支持目录枚举，不支持文件读写
- **用途**: 确认设备在线

## Micropython 兼容性

### 不支持的语法
- 列表推导式: `[x for x in range(10)]`
- 三元表达式: `a if condition else b`
- f-string: `f"value: {x}"`
- triple-quoted 字符串: `"""..."""`

### 支持的语法
- 基本 if/else
- for 循环
- import os
- 基本函数定义

### os 模块差异
```python
# 标准 Python
import os
stat_result = os.stat('file')
size = stat_result.st_size  # 对象属性

# Micropython (K230)
import os
stat_tuple = os.stat('file')
size = stat_tuple[6]  # 元组索引
```

### 文件操作
```python
# 空目录检查
files = os.listdir('/path')
if len(files) == 0:
    os.rmdir('/path')  # 删除空目录

# 非空目录删除需要先删除所有文件
for f in os.listdir('/path'):
    os.remove('/path/' + f)
os.rmdir('/path')
```
