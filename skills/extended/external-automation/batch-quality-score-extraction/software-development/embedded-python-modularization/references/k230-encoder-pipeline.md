# K230 CanMV 编码器流水线（Encoder Pipeline）实践指南

## 问题背景

原来的 K230 眼动仪 `video.py` 录像模式启动后编码链路不稳定——测试时出现 `MediaManager link failed(6)`。对照 CanMV 官方示例（`video_encoder.py`, `mp4muxer.py`）发现多处关键差异。

## 官方示例 vs 原始代码

### 1. Link 顺序（最关键）

```python
# ❌ 原始代码：先 init 再 link（不稳定，可能 link failed(6)）
MediaManager.init()
link = MediaManager.link(bind_info['src'], (2, 0, ch))

# ✅ 官方示例：先 link 再 init（稳定）
link = MediaManager.link(sensor.bind_info()['src'],
                         (VIDEO_ENCODE_MOD_ID, VENC_DEV_ID, venc_chn))
MediaManager.init()
```

CanMV API 要求先建立硬件绑定关系，再初始化媒体管理器。顺序反过来时管道的内部状态机可能异常。

### 2. Width 16 字节对齐

```python
# ❌ 原始代码：直接用 config 的 width
sensor.set_framesize(width=1280, height=720, chn=0)

# ✅ 官方示例：要对齐到 16 字节
width_aligned = (width + 15) // 16 * 16  # 1280→1280, 800→800, 640→640
sensor.set_framesize(width=width_aligned, height=height, chn=0, alignment=12)

# Encoder 的输出缓冲也用对齐后的宽度
encoder.SetOutBufs(venc_chn, 8, width_aligned, height)
```

`alignment=12` 是 CanMV K230 传感器的特殊参数，12 对应 4K 对齐模式。即使 width 本身已经是 16 的倍数（如 1280），也要显式传 `alignment=12`。

### 3. `GetStream` 的 pack_cnt 遍历

```python
# ❌ 原始代码：只取第一个 packet
stream_type = streamData.stream_type[0]
data_size = streamData.data_size[0]

# ✅ 官方示例：遍历所有 packets
for pack_idx in range(streamData.pack_cnt):
    stream_type = streamData.stream_type[pack_idx]
    data_size = streamData.data_size[pack_idx]
    pts = streamData.pts[pack_idx]
    data_ptr = streamData.data[pack_idx]
```

一次 `GetStream` 调用可能返回多个数据包。特别是首帧 I 帧之前，可能有多个 SPS/PPS header 包 + 一个 I 帧包在同一个 `StreamData` 中。只取 `[0]` 会漏掉这些 header，导致 MP4 文件缺少编解码参数。

### 4. 使用常量代替魔数

```python
# ❌ 魔法数字
stream_type == 0  # 是什么？SPS？PPS？
stream_type == 1  # I 帧？
frame_data.codec_id = 3  # H265? H264?

# ✅ 使用常量
stream_type == encoder.STREAM_TYPE_HEADER  # SPS/PPS
stream_type == encoder.STREAM_TYPE_I       # I 帧
frame_data.codec_id = K_MP4_CODEC_ID_H265  # 从 mpp.mp4_format 导入
```

### 5. Link 目标使用官方常量

```python
# ❌ 魔数：
(2, 0, venc_chn)

# ✅ 官方常量：
from media.vencoder import VIDEO_ENCODE_MOD_ID, VENC_DEV_ID
(VIDEO_ENCODE_MOD_ID, VENC_DEV_ID, venc_chn)
```

### 6. Sensor 构造方式

官方示例中 `Sensor()` 不带参数，然后单独调用 `reset()`：

```python
sensor = Sensor()                                            # ✅ 无参数
sensor.reset()
sensor.set_framesize(width=w, height=h, alignment=12)
sensor.set_pixformat(Sensor.YUV420SP)
```

原始代码用带参数构造：

```python
sensor = Sensor(id=0, width=1280, height=720, fps=60)       # ❌ 带参数
sensor.reset()
sensor.set_framesize(width=w, height=h, chn=0)
sensor.set_pixformat(fmt, chn=0)
```

两种方式在 K230 上都能工作，但官方示例模式更安全——Sensor 构造时不绑定硬件，直到 `reset()` 才真正初始化。

## 完整正确流程

```python
from media.sensor import Sensor
from media.media import MediaManager
from media.vencoder import Encoder, ChnAttrStr, StreamData, \
    VIDEO_ENCODE_MOD_ID, VENC_DEV_ID

# 1. 初始化 Sensor（不传分辨率参数）
sensor = Sensor()
sensor.reset()
width_aligned = (width + 15) // 16 * 16
sensor.set_framesize(width=width_aligned, height=height, alignment=12)
sensor.set_pixformat(Sensor.YUV420SP)

# 2. 初始化 Encoder
encoder = Encoder()
venc_chn = VENC_CHN_ID_0
encoder.SetOutBufs(venc_chn, 8, width_aligned, height)

# 3. 先 link，后 init MediaManager（关键顺序）
link = MediaManager.link(
    sensor.bind_info()['src'],
    (VIDEO_ENCODE_MOD_ID, VENC_DEV_ID, venc_chn)
)
MediaManager.init()

# 4. 创建并启动编码器
chnAttr = ChnAttrStr(
    encoder.PAYLOAD_TYPE_H265,
    encoder.H265_PROFILE_MAIN,
    width_aligned, height
)
encoder.Create(venc_chn, chnAttr)
encoder.Start(venc_chn)

# 5. 启动 sensor
sensor.run()

# 6. 循环获取编码帧
streamData = StreamData()
while True:
    encoder.GetStream(venc_chn, streamData, timeout=-1)

    # 遍历所有 packets
    for pack_idx in range(streamData.pack_cnt):
        stream_type = streamData.stream_type[pack_idx]
        data_size = streamData.data_size[pack_idx]
        # ... 处理或写入文件

    encoder.ReleaseStream(venc_chn, streamData)

# 7. 清理（反向顺序）
sensor.stop()
del link                      # 解除绑定
encoder.Stop(venc_chn)
encoder.Destroy(venc_chn)
MediaManager.deinit()
```

## IDR 帧收集

首帧必须包含 SPS/PPS（header）后才能写入 MP4。正确做法：

```python
save_idr = bytearray(width * height * 3 // 4)  # 预分配 buffer
idr_index = 0
get_first_I_frame = False

while not get_first_I_frame:
    encoder.GetStream(venc_chn, streamData, timeout=-1)
    for pack_idx in range(streamData.pack_cnt):
        st = streamData.stream_type[pack_idx]
        sz = streamData.data_size[pack_idx]
        dp = streamData.data[pack_idx]

        if st == encoder.STREAM_TYPE_HEADER:   # SPS/PPS → 累积
            save_idr[idr_index:idr_index+sz] = uctypes.bytearray_at(dp, sz)
            idr_index += sz
        elif st == encoder.STREAM_TYPE_I:      # I 帧 → 合并 header 一起写入
            save_idr[idr_index:idr_index+sz] = uctypes.bytearray_at(dp, sz)
            idr_index += sz
            # 写入完整的 save_idr[:idr_index]
            get_first_I_frame = True
            break
    encoder.ReleaseStream(venc_chn, streamData)
```

## H264 vs H265 编码选择

| 编码器 | 1280×720 | 1920×1080 | 同码率画质 | 计算量 |
|:-------|:--------:|:---------:|:----------|:------|
| H265 (HEVC) | **59.8 FPS** | ❓ 未测（估计 ~30） | 好 30-50% | ~2x |
| H264 (AVC) | ✅ 稳定 60 | **60.1 FPS** | 基准 | 1x |

**眼动仪场景建议：** 用 **H264@1280×720，bit_rate=200000**（200Mbps 接近无损）。瞳孔追踪对 H265 的码率节省不敏感，60fps 帧率比编码效率重要得多。

## 高码率设置

200Mbps 不影响编码帧率（编码器硬件吞吐固定），只增大输出包大小：

```python
# video.py 中创建编码器时：
chnAttr = ChnAttrStr(
    state.encoder.PAYLOAD_TYPE_H264,
    state.encoder.H264_PROFILE_MAIN,
    width_aligned, v_height,
    bit_rate=200000         # 200Mbps，接近无损
)
```

对应 MP4 CODEC ID 也需改为 H264：

```python
from media.mp4format import K_MP4_CODEC_ID_H264
frame_data.codec_id = K_MP4_CODEC_ID_H264
```

## 常见失败模式

| 症状 | 原因 | 修复 |
|:-----|:-----|:-----|
| `MediaManager link failed(6)` | link 在 init 之后 | 先 link 再 init |
| `The VideoBuffer has been initialized!!!` | 一个 boot 中多次 init | 全局只 init 一次 |
| `sensor(N) is already inited` | 重复创建相同 id 的 Sensor | 用 `stop()`+`reset()` 复用 |
| 编码 FPS 只有 31（snapshot 测得） | 用了 snapshot() 而非编码链路 | 用 `GetStream` 测（snapshot 和编码是两条完全不通的路径） |
| 1920×1080 `snapshot()` 崩溃（编码链路不崩） | `snapshot()` 走 Python 内存拷贝（~3MB/帧 OOM），**编码链路走硬件 DMA 不受影响** | 用编码链路的 `GetStream` 测，1920×1080 H264 @60.1fps 已实测通过 |
| MP4 文件无法播放 | 缺少 SPS/PPS header | 检查 IDR 帧收集逻辑，遍历 `pack_cnt` 收集所有 STREAM_TYPE_HEADER |
| `ImportError: can't import name k_u64_ptr` | `k_u64_ptr` 不在 `mpp.mp4_format` 也不在 `mpp.mp4_format_struct` | 从 `media.mp4format` 导入：`from media.mp4format import k_u64_ptr`。该类型在 `/sdcard/libs/media/mp4format.py` 中定义，不在 `mpp/` 包中。 |
| `ampy` 上传报 `could not enter raw repl` | `main.py` 正在前台运行，抢占 REPL | 先用串口发送 Ctrl+C 中断 main.py 的 `while True` 主循环，`main()` 退出并清理资源后 ampy 就能连上了 |
| 串口只回显命令不输出结果 | REPL 卡在 echo-only 状态（通常由之前的 paste mode 残留或硬件操作崩溃导致） | 用 paste mode（Ctrl+E→代码→Ctrl+D）执行命令，或 Ctrl+B 退出 raw REPL 回到 normal REPL |
