# K230 / CanMV GC2093 摄像头 FPS 实测基准

源自 K230 眼动仪（2× GC2093 传感器）的实测算例。数据收集方法：每个分辨率/格式在 sensor 上 capture 20-30 帧取平均。

## 传感器参数

| 项目 | 值 |
|:-----|:----|
| 型号 | GC2093（格科微） |
| 数量 | 2（csi0=左眼, csi1=右眼） |
| 原生输出上限 | 1920×1080@60fps |
| CanMV 驱动版本 | v1.4-41 (rt-smart) |

## 实测 FPS

| 分辨率 | 格式 | 实测 FPS | 每帧耗时 | 用途 | 稳定性 |
|:-------|:-----|:--------:|:--------:|:-----|:------|
| **640×480** | GRAYSCALE | **59.5** | 16.8ms | 推理（最快） | ✅ |
| **640×480** | RGB565 | **30.3** | 33.0ms | 拍照 | ✅ |
| **800×480** | GRAYSCALE | **30.9** | 32.4ms | 推理（原配置） | ✅ |
| **1280×720** | YUV420SP | **~31.4** | ~32ms | 录像 H265 | ✅ |
| **1920×1080** | YUV420SP (snapshot) | — | — | 最大分辨率 | ❌ 崩溃 |
| **1920×1080** | H264 **编码链路** | **60.1** | 16.65ms | 1080p 录像 | ✅ 编码链路可用 |

## 关键发现

### 1. 640×480 GRAYSCALE 是最快模式

达到传感器硬件帧率上限（60fps）。适合实时推理场景。

### 2. 编码链路 vs snapshot() — 天壤之别

| 测量方式 | 1280×720 H265 FPS | 1920×1080 H264 FPS | 瓶颈 |
|:---------|:-----------------:|:------------------:|:-----|
| `sensor.snapshot()` | **~31** | ❌ 崩溃 | Python 内存拷贝 ~30MB/s |
| 编码链路 `MediaManager.link()` + `GetStream` | **59.8** | **60.1** | 传感器硬件上限 |

**重要：** `snapshot()` 测的不是真正的录像帧率。录像时走硬件编码 DMA 链路，帧率 = 传感器输出帧率。

### 3. 1080p 录像需要 H264 编码

| 编码器 | 1280×720 FPS | 1920×1080 FPS |
|:-------|:-----------:|:-------------:|
| H265 (HEVC) | **59.8** | ❓ 未测（可能 ~30） |
| H264 (AVC) | 未测 | **60.1** |

H264 在 K230 上编码计算量更低，1080p 可以达到 ~60fps。H265 计算量约 2x，在 1080p 下可能只能到 30fps 左右。

### 4. H264 vs H265 对眼动仪场景的影响

- **瞳孔追踪**对编码格式**不敏感**（高对比度黑白目标）
- **60fps 帧率**比 H265 的 30% 码率节省**重要得多**
- 建议：录像用 H264@60fps，码率 25-50Mbps 足够
- 推理用 GRAYSCALE（与录像编码格**式无关**）

**测试编码性能的正确方法（详见 `references/k230-encoder-pipeline.md`）：**
```python
from media.vencoder import *
from media.sensor import Sensor
from media.media import MediaManager

s = Sensor(); s.reset()
s.set_framesize(width=1280, height=720, alignment=12)
s.set_pixformat(Sensor.YUV420SP)
e = Encoder(); e.SetOutBufs(0, 8, 1280, 720)
l = MediaManager.link(s.bind_info()['src'],
    (VIDEO_ENCODE_MOD_ID, VENC_DEV_ID, 0))
MediaManager.init()
a = ChnAttrStr(e.PAYLOAD_TYPE_H265, e.H265_PROFILE_MAIN, 1280, 720)
e.Create(0, a); e.Start(0); s.run()
sd = StreamData()

for _ in range(20):
    e.GetStream(0, sd); e.ReleaseStream(0, sd)

t0 = time.ticks_ms(); fc = 0
while fc < 200:
    e.GetStream(0, sd)
    fc += sd.pack_cnt
    e.ReleaseStream(0, sd)
el = time.ticks_diff(time.ticks_ms(), t0)
print('Encoder FPS:', fc * 1000 / el)
```

### 5. GC2093 的不同分辨率对应不同的传感器输出模式

硬件会自动切换输出模式（从日志可看出 `type 22` / `type 24` 等变化），这与 `sensor.reset()` 的分辨率参数有关。

## 测试方法示例

```python
from media.sensor import Sensor
from media.media import MediaManager
import time

s = Sensor(id=0, width=640, height=480, fps=60)
s.reset()
s.set_framesize(width=640, height=480, chn=0)
s.set_pixformat(Sensor.GRAYSCALE, chn=0)
MediaManager.init()
s.run()
time.sleep_ms(200)

# warmup
for i in range(5): s.snapshot()

# measure
count = 30
t0 = time.ticks_ms()
for i in range(count):
    s.snapshot()
t1 = time.ticks_ms()
fps = count * 1000 / (t1 - t0)
print(f'{fps:.1f} FPS')
```

## 跨分辨率测试注意事项

`MediaManager.init()` 每 boot 只能调用一次。切换分辨率需要：

```python
s.stop()                        # 停止当前流
s.reset()                       # 重置传感器
s.set_framesize(w, h, chn=0)    # 设新尺寸
s.set_pixformat(fmt, chn=0)     # 设新格式
s.run()                         # 重新启动
```

不可以 `del s; s = Sensor(id=0, ...)` — 同一个 sensor id 不能创建两次。

## 代码配置建议

你的 config/video 部分应该反映实际能力：

```python
# 录像模式（编码链路，已达传感器上限）
RECORD_WIDTH = 1280
RECORD_HEIGHT = 720       # 与 config 一致
RECORD_FPS = 60           # ✅ 编码链路实测 59.8 FPS
# 或 1920×1080 H264 @60.1fps
# bit_rate=200000 可获得接近无损画质

# 拍照模式（snapshot + save，SD卡写入瓶颈）
# 640×480 GRAYSCALE → ~37张/秒
# 640×480 RGB565 → ~20张/秒
```
