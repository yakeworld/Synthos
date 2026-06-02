---
name: embedded-python-modularization
description: "Decompose monolithic embedded-Python/Micropython files into maintainable modules — the state.py pattern, deferred-import cycle breaking, lightweight-state discipline, and post-surgery verification. Works on K230, ESP32, RP2040, STM32, and similar platforms where RAM is tight and `global` doesn't scale."
version: 1.1.0
author: Synthos
metadata:
  hermes:
    tags: [software-engineering, refactoring, micropython, embedded, modularization]
    related_skills: [writing-plans, hermes-agent-skill-authoring]
---

# Embedded Python Modularization

## 核心原则（文言）

| 白话 | 文言 | 义 |
|:-----|:-----|:----|
| 大型单体文件 → 低耦合模块 | **大行必裂，裂则易守** | >500行单体必拆分 |
| 全局状态集中管理，不散落各模块 | **状态归一，不散于野** | state.py 统管所有可变状态 |
| 延迟导入打破循环依赖 | **导入从缓，环以代入** | 函数体内 import，不模块顶 |
| state.py 不放硬件导入 | **状态体轻，不携重器** | 硬件类型在各模块内导 |
| 先备份再改，不改原文件 | **改前备份，以全退路** | cp file.py file_original.py |

## 工作流（做什么）

| 阶段 | 方法 | 加载子skill | 产出 |
|:-----|:-----|:-----------|:-----|
| 0 分析 | 逐段扫描，标记面积和依赖 | - | 各区域行数+依赖图 |
| 1 计划 | 按功能域划分模块，建立依赖序 | writing-plans | 模块清单+依赖方向 |
| 2 提取 | state.py → 辅助模块 → 业务模块 ← 按序写 | hermes-agent-skill-authoring | N个新.py文件 |
| 3 重写入口 | 精简 main.py 为初始化+分发的协调器 | - | 新 main.py |
| 4 验证 | 函数存在性、导入完整性、global残留 | - | ✅/❌ 检查清单 |
| 5 部署 | 通过串口上传到K230（ampy优先，base64备选） | references/k230-serial-deployment.md | 板子上 `import` 通过 |

## 五种核心模式

### 1. state.py 模式（嵌入式最重要）

嵌入式 Micropython 没有 `global` 跨模块方案。将所有可变状态集中到一个 `state.py`：

```python
# state.py — 轻量，只有常量和变量，不放 import
INFER_BATCH_SIZE = 100
current_mode = None
is_running = False
sensor_left = None
kpu_session = None
_ai2d_builder = None
```

```python
# photo.py — 通过 state.xxx 读写
import state
def photo_mode_start():
    state.current_mode = "photo"
    state.is_running = True
```

**禁止** `from state import current_mode` — 那会创建局部别名，赋值改不了外部状态。

**触发条件**：当 3+ 模块需要共享同一个可变状态时。

### 2. 轻量化 state（防 RAM 膨胀）

`state.py` 只放常量+变量声明。不放：
- `import machine, ssd1306, nncase_runtime` 等硬件库（每个模块自导）
- 函数定义和类定义（在各自的模块里）
- 一次性计算值（在 config.py 或各模块里）

RAM 有限的设备上，多一次的 import 就有风险。state.py 体积目标：<200行。

### 3. 延迟导入断环

当 A.py 调 B.py，B.py 调 A.py 时，在函数体内 import 而非模块顶：

```python
# utils.py — 循环依赖场景
def handle_stop_key():
    from photo import photo_mode_stop  # 函数体内延迟导入
    ...
```

**适用场景**：
- 停止按钮处理函数调多个模式模块
- 主循环的回调注册
- 任何涉及 A↔B 双向调用的关系

**不适用**：性能热路径（每帧都调用的循环），但嵌入式通常可以接受。

### 4. 功能域模块提取

按注释的分割标记提取。典型嵌入式单体模式：

| 原文件章节 | → 模块 |
|:-----------|:-------|
| 配置/路径/序列号 | `config.py` |
| 硬件抽象(OLED/按键/传感器init/WiFi) | `hardware.py` |
| 加速器/协处理器 | `ai2d.py` 或 `accelerator.py` |
| 业务模式A层 | `photo.py`, `inference.py`, `video.py` |
| 网络/推送 | `visualizer.py`, `uploader.py` |
| 辅助函数/清理 | `utils.py` |
| 全局状态 | `state.py` |
| 主循环入口 | `main.py`（精简） |

### 5. 分解后验证

写完所有模块后，逐项检查：

- [ ] 无残留 `global` 声明（除 state.py）
- [ ] 所有模块正确 `import state`
- [ ] 所有函数引用存在（`grep -c 'def func_name' module.py`）
- [ ] 类定义存在（`grep -c 'class ClassName' module.py`）
- [ ] 无循环导入（运行时 import 链可达）
- [ ] 主循环调用的函数在各模块中存在
- [ ] 备份文件保留在目录

## 陷阱

- ❌ `from state import sensor_left` → 赋值不生效。必须 `state.sensor_left = xxx`
- ❌ 模块顶导入导致循环依赖崩溃 → 热点路径用函数体内 import，冷路径不优化
- ❌ state.py 导入硬件库 → 所有模块都被迫加载，RAM 爆炸
- ❌ 提取时遗漏某个状态 → `global` 在模块外不生效，运行时报 NameError
- ❌ 恢复成原来的文件名 → 嵌入式固件总指向 `main.py`，不破坏启动入口
- ❌ 过分追求单文件大小一致 → 核心模块 300-400 行正常，不必均匀
- ❌ **`ensure_dir` 放错模块** → `config.py` 和 `photo.py`/`video.py`/`inference.py` 都需要它。放 `config.py` 里则其他模块必须从 config import（反直觉，且 config 本来可以轻量）。**正确做法**：`file_exists`、`ensure_dir` 这种零依赖纯工具函数放在 `utils.py`，`config.py` 自己 `from utils import ensure_dir`。这样所有业务模块都能统一 `from utils import ensure_dir`。
- ❌ **Micropython `uos` 代替 `os`** → CanMV/rt-smart 上 `import os` 不存在，必须 `import uos`。`uos.listdir()`、`uos.stat()`、`uos.mkdir()`。所有涉及文件系统的模块都要注意这一点，不要把 `import os` 带到提取后的模块里。
- ❌ **`MediaManager.init()` 每 boot 只能一次** → 跨分辨率测试时必须在一个 sensor 对象上 `<sensor>.stop()` → `<sensor>.reset()` → `<sensor>.set_framesize/set_pixformat` → `<sensor>.run()`，不能 `del sensor; sensor = Sensor(...)`（同一个 sensor id 不能创建两次）。测试脚本设计中要预见到这个限制，否则测试多个分辨率时会报 `The VideoBuffer has been initialized!!!`。
- ❌ **`MediaManager.link()` 必须在 `init()` 之前** → CanMV K230 API 约束：硬件事先绑定，然后初始化媒体管理器。反过来（先 init 再 link）会导致 `MediaManager link failed(6)`。正确顺序见 `references/k230-encoder-pipeline.md`。
- ❌ **编码器 Width 未 16 字节对齐** → `sensor.set_framesize()` 和 `encoder.SetOutBufs()` 的 width 必须对齐到 16 字节：`width_aligned = (width + 15) // 16 * 16`，同时传 `alignment=12`。不对齐会导致编码器输出异常或崩溃。
- ❌ **`encoder.GetStream()` 只取 `[0]` 漏掉 `pack_cnt`** → `GetStream` 单次调用可能返回多个数据包（SPS/PPS header + I 帧在同一次调用中）。必须遍历 `range(streamData.pack_cnt)`，取 `stream_data[pack_idx]`。原始代码只取 `[0]` 导致 IDR 帧收集不完整。
- ❌ **使用魔数 0/1 代替 `STREAM_TYPE_HEADER`/`STREAM_TYPE_I`** → 可读性差且容易出错。用 `encoder.STREAM_TYPE_HEADER` / `encoder.STREAM_TYPE_I` 常量。
- ❌ **`(2, 0, ch)` 代替 `(VIDEO_ENCODE_MOD_ID, VENC_DEV_ID, ch)`** → 可读性差。用 `from media.vencoder import VIDEO_ENCODE_MOD_ID, VENC_DEV_ID`。
- ❌ **`snapshot()` 测试不能反映真实编码帧率** → `snapshot()` 走 Python 内存拷贝（瓶颈 ~30MB/s），实际录像走硬件编码 DMA 链路。1280×720 YUV `snapshot()` 测出来只有 ~31fps，但编码链路可以达到传感器原生 60fps。测试录像性能应该用编码链路测，不是 `snapshot()`。
- ❌ **H265 在 1080p 可能达不到 60fps** → H265 编码计算量约 H264 的 2x。1280×720 两者都能到 60fps，但 1920×1080 下 H265 估计只能 ~30fps，而 H264 实测可达 60.1fps。眼动仪场景（高对比度黑白目标）对码率节省不敏感，推荐用 H264。
- ❌ **`k_u64_ptr` 导入路径错误** → 在 K230 CanMV 上，`k_u64_ptr` 类型位于 `media.mp4format` 模块中，不在 `mpp.mp4_format` 也不在 `mpp.mp4_format_struct`。正确导入：`from media.mp4format import k_u64_ptr`。从 `mpp.mp4_format import k_u64_ptr` 会报 `ImportError: can't import name k_u64_ptr`。
- ❌ **计数器重构不对称** → 重构拍照计数时将旧字段 `photo_count`/`photo_count_right` 改为独立 `cam0_count`/`cam1_count`，但容易遗留旧的 `state.photo_count = 0` 初始化和复杂的 `lfs_count = state.photo_count if ...` 显示计算公式。检查和替换步骤：① 在所有文件中 grep 旧字段名 ② 删除旧字段的初始化 ③ 删除旧字段的所有引用（包括主循环中 OLED 显示的复杂计算）④ 确保 `state.py` 中旧字段声明已删除。遗留一根旧字段引用就会导致 OLED 显示永远为 0 或乱码。
- ❌ **`uos.statvfs` 在热路径中高频调用** → `get_storage_info()` 每帧调用 `uos.statvfs`（昂贵的系统调用）。应在循环启动时缓存一次结果，或加 5 秒 TTL 缓存：用 `_last_check` / `_cache` 全局变量，`if _last_check and time.ticks_diff(now, _last_check) < 5000: return _cache`。
- ❌ **主循环每帧 `gc.collect()`** → 非录像模式下每次迭代都 `gc.collect()` 会显著影响帧率，尤其在 90fps 推理模式下。改为计数触发：每 100 次循环 GC 一次（`gc_counter += 1; if gc_counter >= 100: gc_counter = 0; gc.collect()`）。
- ❌ **`load_config()` 默认配置未写回文件** → 首次启动时 `/sdcard/config.json` 不存在，代码生成默认配置字典但不保存。下次启动还是找不到文件，继续走默认。应在创建默认配置后调用 `save_config(state.config)` 持久化。
- ❌ **上传文件列表遍历错路径** → 重构后 `upload_inference_results()` 用 `uos.listdir(state.INFER_DIR)` 但实际批次文件在 `state.infer_session_dir` 子目录里。正确的路径是 `uos.listdir(state.infer_session_dir)`。类似的上传/搜索操作在重构后要检查文件路径是否随变量迁移了。
- ❌ **`frame_count` 双重身份** → 重构推理模式时容易让一个变量同时充当"批次内计数器"和"全局帧号"。批次满 100 时计数器重置为 0，导致 `frame_count % 30 == 0` 这类日志/OLED/GC 触发节奏每批次被打断一次，且在批次切换瞬间（0%30/10/60 全为 true）叠加额外开销。**正确做法**：分离 `frame_count`（批次内，满 100 重置）和 `infer_total_frames`（全局递增，永不重置，用于日志/OLED/GC 判断）。
- ❌ **`save_idr_left` 缓冲区写死 720p** → 重构录像模块后缓冲区大小容易写死为测试时的分辨率。改分辨率后缓冲区溢出导致切片赋值失败或内存损坏。**正确做法**：`buf_size = cfg["width"] * cfg["height"] * 3 // 2` 动态计算，或按最大分辨率（1920×1080）分配。
- ❌ **`except: pass` 吞掉 `KeyboardInterrupt`** → 裸 `except:` 在嵌入式调试中让 Ctrl+C 失效。所有 `except:` 应改为 `except Exception:`。
- ❌ **重命名变量时遮蔽模块名** → 如 `state = key["pin"].value()` 遮蔽了 `state` 模块。即使当前函数内不用模块 `state`，后续修改者会困惑且容易引入 bug。检查所有变量名是否与模块名/内建名冲突。
- ❌ **重构后遗漏旧字段清理** → 如 `photo_count` → `cam0_count/cam1_count` 后，旧字段声明删除但初始化赋值、OLED 显示计算、主循环中的引用可能残留。**修复步骤**：① `grep -rn 'old_field_name' .` 全部找到 ② 逐处评估替换或删除 ③ 不遗留一条引用。
- ❌ **`is_timeout` 用字符串匹配异常类型** → `if 'timeout' in str(e).lower()` 脆弱（SDK 改异常文案即失效）。应捕获具体异常类型，或至少用白名单关键词列表：`_TIMEOUT_MSGS = ('timeout','timed out')`。
- ❌ **`gc.collect()` 每帧调用拖慢推理** → 推理模式 90fps 下每帧 GC 会显著拉低帧率。**正确做法**：主循环中用计数器（每 100 轮一次），推理模块内部用 `infer_total_frames % 60 == 0`。
- ❌ **`visualizer` 的 TCP 阻塞 send 拖垮推理 FPS** → 推理循环中 `socket.send()` 可能阻塞 2 秒（`settimeout(2)`），把 90fps 直接拖到 0.5fps。**正确做法**：可视化推送用 UDP（`SOCK_DGRAM`）+ `settimeout(0)` 非阻塞发送，失败静默丢弃。json 中无需 `\n` 分隔符（UDP 消息自带边界）。
- ❌ **AI2D 和软件预处理输出 dtype 不一致** → AI2D 路径输出 `np.uint8`，软件路径输出 `np.float32`（归一化后）。如果模型期望 float32，AI2D 路径会给出错误输入。**重构时要检查两条路径的输出 dtype 是否对齐模型输入要求**。
- ❌ **`handle_stop_key` 用 `machine.reset()` 收尾** → 暴露了资源释放路径不可靠的根本问题。硬件编码器/MediaManager/link 的释放顺序敏感。**根治**：用 try/finally 严格守护释放顺序，引入资源栈模式（acquire 推栈，释放时 LIFO 弹出）。短期用 TODO 标记。
- ❌ **变量影子导入** → `from config import load_config` 后又调用 `load_config()` 但全局 `config` 变量（dict）被 import 名遮蔽。用 `import config as cfg` 或 `from config import load_config, CONFIG_FILE as CFG` 避免混淆。

## K230 CanMV 板级调试 (Absorbed)

> 吸收自: `k230-canmv-debugging` skill (archived). 板级调试是模块化开发工作流的配套技能——写模块→上传→调试→部署。

### 连接与串口 REPL

- K230 表现为 `/dev/ttyACM[0-1]` (USB CDC ACM), 波特率 115200
- CanMV IDE 占用串口 → 断开IDE或用 ampy 前必须 kill canmvide 进程
- 三种 REPL 模式: Normal (`>>>`), Raw (`>` via Ctrl+A), Paste (Ctrl+E, 多行代码首选)

### 文件传输

| 方法 | 命令 | 适用场景 |
|:-----|:-----|:---------|
| ampy | `ampy -p /dev/ttyACM0 -b 115200 put/run/get` | 首选，但 main.py 运行时阻塞 |
| Base64 paste | 分块 base64 → ubinascii.a2b_base64 → open().write() | ampy 不可用时的 fallback |
| boot.py 注入 | 覆盖 boot.py 自动执行测试脚本 | 长时间运行测试 |

### 硬件编码器管线

初始化顺序 (CanMV 官方顺序):
1. `Sensor()` — 无参构造 → `reset()` → `set_framesize()` → `set_pixformat()`
2. `Encoder()` → `SetOutBufs()`
3. **先 `MediaManager.link()` 再 `MediaManager.init()`** — 顺序颠倒会报 `MediaManager link failed(6)`
4. `Create()` → `Start()` → `sensor.run()`

**关键约束:**
- Width 必须 16 字节对齐: `(w + 15) // 16 * 16`
- `k_u64_ptr` 在 `media.mp4format` 模块, 不在 `mpp.mp4_format`
- `GetStream` 可能返回多个 packet, 必须遍历 `streamData.pack_cnt`
- `ReleaseStream` 必须和 `GetStream` 配对, 否则编码器 stall

### GC2093 传感器

- CSI0 (左眼), CSI1 (右眼)
- 最大输出: 1920×1080@60
- 仅一个硬件编码器 → 双摄像头不能满速录制
- 编码链路可达 60fps (硬件 DMA), snapshot() 路径仅 ~31fps (Python 瓶颈)

### 导入路径修正表

| 符号 | 实际模块 |
|:-----|:---------|
| `k_u64_ptr` | `media.mp4format` |
| `kd_mp4_create` | `mpp.mp4_format` |
| `k_mp4_config_s` | `mpp.mp4_format_struct` |
| `StreamData`, `Encoder` | `media.vencoder` |

### 常见故障

| 症状 | 原因 | 修复 |
|:-----|:-----|:-----|
| 命令回显无输出 | REPL 卡在 paste/raw 模式 | 发送 Ctrl+B → Ctrl+C |
| 空读 | 板子挂死 | 物理复位按钮 |
| Device or resource busy | CanMV IDE 占用 | Kill canmvide |
| ttyACM* 消失 | USB 重枚举 | `ls /dev/ttyACM*; lsusb` |
| ampy: "could not enter raw repl" | main.py 前台运行 | Ctrl+C 打断 |

详细内容见 `references/k230-canmv-debugging.md`.

## 参考文件

- `references/k230-camera-system-decomposition.md` — K230 眼动仪相机系统分解实战案例
- `references/k230-serial-deployment.md` — 通过串口将模块化代码部署到 K230 板
- `references/k230-camera-fps-benchmark.md` — K230 GC2093 摄像头各分辨率/格式的实测 FPS 基准数据
- `references/k230-encoder-pipeline.md` — CanMV K230 H265/H264 编码器流水线正确初始化顺序
- `references/k230-code-review-checklist.md` — K230 代码审查清单
- `references/k230-canmv-debugging.md` — K230 CanMV 板级调试完整参考 (serial REPL, ampy, 编码器管线, 导入修正)
- `references/encoder-fps-tests.md` — 编码器 FPS 测试数据 (absorbed from k230-canmv-debugging)

## 相关技能

- `writing-plans` — 分解前写实施计划
- `hermes-agent-skill-authoring` — skill 设计规范（层级/长度/三语）
- `systematic-debugging` — 拆完跑不起来怎么办

## 参考文件

- `references/k230-camera-system-decomposition.md` — K230 眼动仪相机系统分解实战案例
- `references/k230-serial-deployment.md` — 通过串口将模块化代码部署到 K230 板的方法（base64分块上传 + paste模式 + ampy + boot.py自动化 + REPL回显陷阱）
- `references/k230-camera-fps-benchmark.md` — K230 GC2093 摄像头各分辨率/格式的实测 FPS 基准数据 + snapshot/编码链路区分 + 1080p H264@60fps 实测
- `references/k230-encoder-pipeline.md` — CanMV K230 H265/H264 编码器流水线正确初始化顺序和常见失败模式
- `references/k230-code-review-checklist.md` — K230 代码审查清单：P0/P1/P2 问题分级、常见 Reviewer 发现的 Bug 模式、性能基准数据、测试策略（含串口不稳定时的替代方案）
