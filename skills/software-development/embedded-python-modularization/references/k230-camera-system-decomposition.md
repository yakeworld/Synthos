# K230 多摄像头系统分解案例

源自 `/media/yakeworld/sda2/canmv/k230/main.py` 的 2071 行单体 → 10 模块重构。

## 原始结构（2071 行）

| 区域 | 行数 | 内容 |
|:-----|:----:|:-----|
| 导入 | 17-40 | 标准库 + 硬件库 (Sensor, nncase, image, ssd1306...) |
| 工具函数 | 44-63 | file_exists, ensure_dir, ALIGN_UP |
| 全局常量 | 65-113 | 路径、GPIO引脚、摄像头尺寸、推理参数、AI2D参数 |
| 全局状态 | 119-189 | 所有 global 变量声明 |
| 配置管理 | 192-356 | load/save 配置、序列号、get_*_config |
| WiFi | 359-420 | connect_wifi, get_wifi_signal |
| OLED | 423-631 | OLEDDisplay 类 |
| 按键 | 633-676 | KeyManager 类 |
| 摄像头init | 678-736 | init_sensor / init_sensor_for_inference / init_sensor_for_video |
| AI2D加速 | 739-886 | AI2D init/preprocess + 软件回退 |
| 推理函数 | 889-979 | KPU init, run_inference_optimized |
| 拍照模式 | 981-1171 | start/capture/stop |
| 推理模式 | 1174-1441 | start/process/save/stop/upload |
| 可视化推送 | 1444-1513 | UDP socket 推推理结果 |
| 录像模式 | 1516-1875 | start/record/stop + mp4 muxer |
| OLED日志/清理 | 1878-1958 | set_oled_log, cleanup, 辅助函数 |
| 主循环 | 1961-2072 | main() + 入口 |

## 分解方案

```
main.py         155行    轻量入口：OLED→WiFi→按键→主循环分发
├── state.py    162行    所有常量+可变状态（不放硬件import）
├── config.py   208行    配置加载/保存、序列号管理、getter函数
├── utils.py    211行    清理函数(sensor/video/global)、OLED日志、温度/存储
├── hardware.py 398行    OLEDDisplay类、KeyManager、三种sensor init、WiFi
├── ai2d.py     156行    AI2D硬件加速init/preprocess + 软件回退
├── visualizer.py 62行   UDP可视化推送
├── inference.py 374行   KPU init、推理执行、模式生命周期、结果上传
├── photo.py    199行    拍照模式 start/capture/stop
└── video.py    255行    录像模式 start/record/stop + mp4 muxer
```

## 依赖关系

```
state.py ──→ config.py ──→ utils.py ──→ hardware.py
   │                                  └─→ ai2d.py
   │                                       │
   │                                       ├── inference.py
   │                                       ├── photo.py
   │                                       └── video.py
   │                                            │
   └──────────────── main.py (调度+主循环) ──────┘
```

无循环依赖。`utils.py` 中 `handle_stop_key()` 使用函数体内延迟导入避免间接循环。

## 关键技术决议

### 1. state.py 轻量化

**不导入** `machine`, `nncase_runtime`, `image`, `media.*`, `ssd1306`, `uctypes`, `ulab.numpy`。这些留各模块自导。只有 `uos`（用于路径常量）。

### 2. 延迟导入

```python
# utils.py — 避免循环
def handle_stop_key():
    from photo import photo_mode_stop   # 函数体内
    from inference import inference_mode_stop
    from video import video_mode_stop
```

### 3. 模块内 import 硬件库

```python
# photo.py — 函数体内导入避免启动时加载
def photo_mode_start():
    from media.sensor import Sensor
    from media.media import MediaManager
```

这确保只有在进入拍照模式时才加载 Sensor 库，而不是启动时就加载。

### 4. 备份策略

```bash
cp main.py main_original.py   # 改前先备份
```

### 5. 验证命令

```bash
# 检查残留 global 声明
grep -rn '^[[:space:]]*global ' *.py | grep -v state.py

# 检查函数存在
grep -c 'def func_name' module.py
grep -c 'class ClassName' module.py

# 检查 state import
grep -l 'import state' *.py

# 统计行数
wc -l *.py | sort -rn
```

## 结果

- 原: 1 文件, 2071 行, 67 KB
- 新: 10 文件, 2180 行, ~70 KB
- 差异: +109 行（≈ 各模块头部的 docstring + import 开销）
- main.py 精简: 2071 → 155 行 (-92%)
