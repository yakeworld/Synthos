# K230 按键无效 — 诊断与修复

## 症状

KEY0-KEY3 所有按键无响应，模块化代码（`hardware.py` + `main.py`）不工作，但单体文件（`main_origin.py`）正常。

## 诊断流程

### 第一步：确认固件类型

```python
import os
print(os.uname())
# 关注最后一个元素: brd = os.uname()[-1]
```

**查 `revision.txt`** 中是否包含 `rtsmart`。

**两个固件分支**：

| 固件 | `machine.Pin()` 自动配置 FPIOA? | 需要手动 FPIOA? |
|------|------|------|
| 标准 CanMV | ✅ 是 | ❌ 不要加 |
| RT-Smart | ❌ 否 | ✅ 必须加 |

### 第二步：检查 GPIO 引脚号

不同板型的按键 GPIO 不同，通过 `os.uname()[-1]` 检测：

| 板型标识 | 按键 GPIO | 按键值 |
|---------|-----------|-------|
| `k230_canmv_01studio` | GPIO21 | 0 (按下低) |
| `k230_canmv_lckfb` | GPIO53 | 1 (按下高) |
| 其他默认 | GPIO21 | 0 (按下低) |

验证代码见官方示例 `examples/16-AI-Cube/DataCollectionCamera.py`。

### 第三步：检查主循环结构

与 `main_origin.py` 对比以下关键点：

| 检查项 | 正确做法 | 错误做法 |
|-------|---------|---------|
| 重启循环 | `while True: main(); sleep(1)` | 无无限重启，或双 `main()` 调用 |
| Idle sleep | `pass` 或 `sleep_us(1)` | `time.sleep(0.1)` 扼杀按键轮询 |
| 异常捕获 | 捕获 + 打印 + 继续循环 | 异常逃逸导致主循环退出 |

## 按固件的正确配置

### 标准 CanMV 固件

不需要 FPIOA，`machine.Pin()` 内部自动完成 IO 映射：

```python
def __init__(self):
    from machine import Pin
    self.keys = {}
    self.callbacks = {}
    for name, pin in [("KEY0", 18), ("KEY1", 19), ("KEY2", 20), ("KEY3", 21)]:
        try:
            p = Pin(pin, Pin.IN, Pin.PULL_UP)
            self.keys[name] = {"pin": p, "pressed": False,
                               "last_state": True, "last_press_time": 0}
        except Exception as e:
            print("[Key] {} init failed: {}".format(name, e))
```

### RT-Smart 固件

**必须**显式 FPIOA 映射再 `machine.Pin()`：

```python
def __init__(self):
    from machine import Pin, FPIOA
    self.keys = {}
    self.callbacks = {}

    fpioa = FPIOA()
    for pin_num in (18, 19, 20, 21):
        fpioa.set_function(pin_num, FPIOA.GPIO0 + pin_num)

    for name, pin_num in [("KEY0", 18), ("KEY1", 19),
                          ("KEY2", 20), ("KEY3", 21)]:
        try:
            p = Pin(pin_num, Pin.IN, Pin.PULL_UP)
            self.keys[name] = {"pin": p, "pressed": False,
                               "last_state": True, "last_press_time": 0}
        except Exception as e:
            print("[Key] {} init failed: {}".format(name, e))
```

**为什么 `FPIOA.GPIO0 + pin` 对 RT-Smart 正确**：K230 的 `FPIOA.GPIO0` 到 `FPIOA.GPIO63` 在枚举中定义为连续整数 0-63，所以 `GPIO0 + 18 = GPIO18` 得到正确的 GPIO 函数值。官方示例已验证此模式。

## 常见逻辑错误（非硬件原因）

### 1. `inference_mode_start()` 缺 `state.current_mode`

```python
# ❌ 错误
state.is_running = True

# ✅ 正确
state.current_mode = "inference"
state.is_running = True
```

漏设 `current_mode` 后，主循环 `elif state.current_mode == "inference":` 永远为 False，按键看似有效但模式无法进入。

### 2. 主循环 idle sleep 扼杀轮询

```python
# ❌ 错误 — 100ms 间隔导致短按被错过
else:
    time.sleep(0.1)

# ✅ 正确 — 保持微秒级轮询
else:
    pass
```

`key_manager.check()` 必须在每次循环中高频执行。100ms 的延迟会使 <150ms 的短按键事件大概率被错过。

### 3. 重复 `main()` 调用

```python
# ❌ 错误 — 第二个 main() 会在第一个意外退出后覆盖 Pin 对象
if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()

# ✅ 正确 — 无限重启保证单一 main() 实例
if __name__ == "__main__":
    while True:
        main()
        time.sleep(1)
```

## 串口诊断输出

启动时应看到：

```
[Key] KEY0 init success
[Key] KEY1 init success
[Key] KEY2 init success
[Key] KEY3 init success
[DEBUG] keys = {'KEY0': {...}, 'KEY1': {...}, ...}     ← 4 个按键对象
[DEBUG] KEY0 raw = 1                                    ← 未按下读高
[DEBUG] KEY0 raw = 0                                    ← 按下时读低
[Key] Callback exception: ...                           ← 回调异常（如果有）
```

如果 `keys` 为空 → `Pin()` 初始化全部失败，检查固件类型和 FPIOA 配置。
如果 `raw` 始终为 1（按不下）→ 硬件或 FPIOA 映射问题。
如果 `raw` 变化但回调不触发 → `check()` 中的 `pin_state == 0 and last_state == 1` 条件不满足（检查 `last_state` 初始值）。