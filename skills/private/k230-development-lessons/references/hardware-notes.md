# K230 硬件笔记

## 关键发现

### 1. 串口洪水导致 REPL 不可用

**问题**: 设备正常运行时串口输出大量数据，使 ampy run 和 serial 交互失败。

**解决**: 通过 `ampy put` 上传文件到 SD 卡，然后修改 `boot.py` 为精简版本减少输出。

### 2. 文件部署

- 使用 `ampy put` 上传文件到 `/sdcard/` 路径
- 设备从 `/sdcard/` 加载 `main.py` 和 `boot.py`
- 文件内容需要符合 MicroPython 语法

### 3. 拍照功能

- 使用 `photo.py` 实现拍照功能
- 文件保存在 `/data/320p_photos/` 目录下
- 存在单摄/双摄模式

### 4. 录像功能

- 使用 `video.py` 实现录像功能
- 需要硬件编码器支持
- 文件输出路径需要验证

### 5. 系统限制

- 设备重启后 `/tmp` 目录可能被清除
- 需要使用 `/sdcard/` 路径保存持久文件
- MicroPython 不支持某些 Python 功能
