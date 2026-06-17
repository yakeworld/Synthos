---
name: embedded-python-modularization
description: >-
version: 1.0.0
  嵌入式Python模块化 — state.py模式, 延迟导入, 循环依赖消除。
  以K230 CanMV项目为参照：state.py集中管理全局状态，config.py负责配置加载/保存/缓存，
  hardware.py做硬件抽象（OLED/按键/摄像头/WiFi），inference.py管理推理生命周期。
  适用于MicroPython+RTSmart嵌入式AI项目。
metadata:
  synthos:
    version: 2.0.0
    author: Synthos
    absorbed_skills:
    - embedded-python-modularization (原v1.0)

---


# Embedded Python Modularization

嵌入式Python模块化 — state.py模式, 延迟导入, 循环依赖消除。

## 核心模式：state.py集中状态管理

```python
# state.py — 全局常量 + 可变状态
# 所有模块通过 import state 访问

# 常量
DATA_ROOT = "/data"
CONFIG_FILE = "/sdcard/config.json"

# 可变状态
current_mode = None
is_running = False
active_sensor = None
kpu_session = None
oled = None
```

**规则**: 全局可变状态只通过 `state.xxx` 访问，不通过 import 传递引用。

## 配置加载与缓存

```python
def load_config():
    if state.config is not None:  # 缓存检查
        return state.config
    with open(CONFIG_FILE) as f:
        state.config = json.loads(f.read())
    return state.config
```

**规则**: 加载一次，缓存在state.config，后续直接返回缓存。

## 硬件抽象分离

hardware.py 封装所有硬件交互：
- OLEDDisplay (SSD1306 I2C)
- KeyManager (GPIO按键+消抖+回调)
- init_sensor() / init_sensor_for_inference() / init_sensor_for_video()
- connect_wifi() / get_wifi_signal()

**规则**: 其他模块不直接操作GPIO/I2C/CSI，全部通过hardware.py。

## 延迟导入

```python
def init_sensor_for_inference(sensor_id):
    from media.sensor import Sensor  # 延迟导入，避免启动时加载所有模块
    from media.media import MediaManager
    ...
```

**规则**: 在函数内部import，不放在文件顶部。减少启动时间和内存占用。

## 生命周期管理

inference.py管理完整生命周期：
- `inference_mode_start()` → 初始化
- `inference_mode_process()` → 运行循环
- `inference_mode_stop()` → 清理

**规则**: 每个模式有明确的start/process/stop三阶段，资源在stop时统一释放。

详细示例请查看 references/ 目录下的参考文件。
