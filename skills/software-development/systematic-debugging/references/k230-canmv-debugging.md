# K230 CanMV Debugging via Serial

## Platform Overview

K230 runs rt-smart with CanMV Micropython (v1.4). Connected via USB CDC ACM (`/dev/ttyACM0`, 115200 baud).

**Device re-enumeration:** After unplug/replug, the device can show up as `/dev/ttyACM1` (or higher) if `/dev/ttyACM0` persists from a stale connection. Always check `ls /dev/ttyACM*` to find the active port.

**CanMV IDE conflict:** CanMV IDE holds the serial port exclusively. Must disconnect in CanMV IDE (click disconnect icon) OR kill the canmvide process before any other tool can access the board.

## File Transfer

### ampy (most reliable)

```bash
# Install
pip3 install --break-system-packages adafruit-ampy

# Upload file to board
ampy -p /dev/ttyACM0 -b 115200 put local_file.py /sdcard/remote.py

# List directory
ampy -p /dev/ttyACM0 -b 115200 ls /sdcard

# Run a script (blocks until completion, may timeout for long tests)
ampy -p /dev/ttyACM0 -b 115200 run /tmp/test_script.py
```

**Important:** `ampy put` is the most reliable file transfer method when the board REPL is healthy. The base64 paste-mode approach is fragile with large files (>5KB).

### Base64 upload via serial (fallback when ampy unavailable)

```python
import base64
b64 = base64.b64encode(file_content).decode()
# On board REPL:
# import ubinascii; b=''
# b+='<base64_chunk>'  (200 char chunks, max 200 per paste mode)
# raw=ubinascii.a2b_base64(b)
# open('/sdcard/file.py','wb').write(raw)
```

**Pitfall:** With files >5KB, base64 data can overflow serial buffers, causing corrupt uploads. Chunk at 200 chars max per line.

### Direct line-by-line via f.write() (unreliable)

Direct `f.write('...\n')` for each line of a Python file is fragile — special characters (quotes, backslashes, Chinese chars) break the string. Avoid unless file is tiny and ASCII-only.

## Running Tests Reliably

### Method 1: Boot.py auto-run (most reliable for long tests)

1. Write test script to `/sdcard/test.py`
2. Set boot.py: `open('/sdcard/boot.py','w').write('exec(open("/sdcard/test.py","rb").read())\n')`
3. Reboot (Ctrl+D from REPL, or power cycle)
4. Test output appears in boot console — capture with `ser.read_all()` after ~15s
5. **ALWAYS restore boot.py** after test: `open('/sdcard/boot.py','w').write('import uos\nprint("boot ok")\n')`

**Best for:** Encoder tests, sensor tests, any test that takes >2s or involves hardware init.

### Method 2: Paste mode (Ctrl+E / Ctrl+D)

- Ctrl+E enters paste mode (no echo, no auto-indent)
- Paste multi-line code
- Ctrl+D executes the pasted code
- Good for scripts up to ~50 lines

### Method 3: REPL one-liners

- Single-line commands work well: `print("hello")`
- Multi-line `for` loops can be sent as semicolon-separated
- NOT reliable for complex multi-line code (Python indent sensitivity)

## REPL Echo-Only Recovery

After hardware operations (sensor init, encoder start), the REPL sometimes enters an echo-only state where commands are echoed but NOT executed.

**Recovery sequence:**
1. Send Ctrl+E to enter paste mode
2. Send `pass` or `print(1)` then Ctrl+D to execute
3. If that fails: Ctrl+D for soft reboot
4. If that fails: toggle DTR for hardware reset:
   ```python
   ser.setDTR(False); time.sleep(0.3); ser.setDTR(True)
   ```
5. If still dead: **physical reset button or USB re-plug** (hardware state corrupted)

**Prevention:** The echo-only state is triggered by hardware operations that leave the sensor/encoder initialized. Always call `s.stop()`, `MediaManager.deinit()` before disconnecting.

## Sensor Lifecycle (Critical)

The GC2093 sensor has strict lifecycle constraints:

```python
# CORRECT pattern:
s = Sensor(id=0, width=640, height=480, fps=60)
s.reset()                    # must call before changing settings
s.set_framesize(...)
s.set_pixformat(...)
s.run()                      # start streaming
img = s.snapshot()           # capture frame
s.stop()                     # stop streaming
# CANNOT create Sensor(id=0) again in same session!
```

**Rules:**
- `Sensor(id=X)` can only be created **ONCE per boot** per ID
- To change resolution: `s.stop()` → `s.reset()` → `s.set_framesize()` → `s.run()`
- `MediaManager.init()` can only be called **ONCE per boot**
- `MediaManager.deinit()` + re-init does NOT work reliably
- `Sensor()` WITHOUT arguments (official example pattern) auto-detects the first available sensor

## Video Encoder Pipeline (Official Pattern)

From `/sdcard/examples/02-Media/video_encoder.py` and `mp4muxer.py`:

### Critical: link BEFORE init

```python
from media.sensor import Sensor
from media.media import MediaManager
from media.vencoder import Encoder, ChnAttrStr, StreamData, VIDEO_ENCODE_MOD_ID, VENC_DEV_ID

# 1. Sensor WITHOUT constructor args (official pattern)
s = Sensor()
s.reset()
wa = (w + 15) // 16 * 16  # ALIGN_UP to 16 — REQUIRED
s.set_framesize(width=wa, height=h, alignment=12)  # alignment=12 required
s.set_pixformat(Sensor.YUV420SP)

# 2. Encoder
e = Encoder()
e.SetOutBufs(ch, 8, wa, h)

# 3. CRITICAL: link BEFORE init!
l = MediaManager.link(s.bind_info()['src'], (VIDEO_ENCODE_MOD_ID, VENC_DEV_ID, ch))
MediaManager.init()

# 4. Create and start
a = ChnAttrStr(e.PAYLOAD_TYPE_H264, e.H264_PROFILE_MAIN, wa, h, bit_rate=200000)
e.Create(ch, a)
e.Start(ch)
s.run()

# 5. Get encoded frames — iterate ALL packets!
sd = StreamData()
e.GetStream(ch, sd, timeout=1)
for p in range(sd.pack_cnt):
    stream_type = sd.stream_type[p]
    data_ptr = sd.data[p]
    data_size = sd.data_size[p]
    # STREAM_TYPE_HEADER: SPS/PPS, accumulate for first I-frame
    # STREAM_TYPE_I: key frame, write accumulated header + I data
e.ReleaseStream(ch, sd)
```

### Pitfalls

| Mistake | Symptom |
|---------|---------|
| `init()` before `link()` | `MediaManager link failed(6)` |
| Width not 16-aligned | Encoder fails silently or corrupt output |
| Only reading `streamType[0]` | Miss SPS/PPS headers, first I-frame corrupt |
| `Sensor(id=X, ...)` with args + then `set_framesize()` | Conflicts, use `Sensor()` no-arg pattern |
| Creating `Sensor(id=X)` after `s.stop()` | `OSError: sensor(X) is already inited` |

### Expected performance

| Pipeline | Resolution | Format | FPS | Notes |
|---|---|---|---|---|
| **`MediaManager.link()`** | **1280×720** | **H264** | **60** | Hardware DMA, full sensor rate |
| **`MediaManager.link()`** | **1920×1080** | **H264** | **60** | Hardware DMA, 200Mbps tested |
| `MediaManager.link()` | 1280×720 | H265 | 60 | Slightly more CPU, same FPS |
| `snapshot()` | 640×480 | GRAYSCALE | 60 | Python mem copy ~30MB/s |
| `snapshot()` | 1280×720 | YUV420SP | 31 | Python mem copy bound |
| `snapshot()` | 1920×1080 | YUV420SP | CRASH | Out of memory (3MB/frame) |

**Key insight:** `snapshot()` is the bottleneck (Python memory copy ~30MB/s). The hardware encoder pipeline (`MediaManager.link()`) provides full sensor rate.

### H264 vs H265 for Video Recording

| Factor | H264 | H265 |
|--------|------|------|
| 1080p@60fps | ✅ Verified (200Mbps) | ❓ Untested, likely lower |
| Quality at 200Mbps | Near-lossless (avg ~50KB/frame) | Same |
| Encoder hardware | 1 instance | Same hardware |
| File size vs 80Mbps | ~6x larger | ~4x larger |
| Playback compat | Universal | Newer players only |

**Recommendation:** Use H264 at **200Mbps** for eye-tracking video — preserves pupil edge pixels, runs at 60fps on both 720p and 1080p.

### Dual Camera Limitation

K230 has **only one hardware encoder**. Dual-camera recording requires:
- One camera via `MediaManager.link()` (hardware, 60fps)
- Other camera via `encoder.SendFrame()` (software, ~15fps)

Not practical for synchronous eye tracking.

## 200Mbps High-Bitrate Encoder Config

For near-lossless video recording (pupil tracking quality):

```python
a = ChnAttrStr(
    e.PAYLOAD_TYPE_H264,
    e.H264_PROFILE_MAIN,
    wa, h,
    bit_rate=200000    # 200 Mbps — near-lossless at 60fps
)
```

Verified: 1280×720 H264 @200Mbps = **60 FPS**, 1920×1080 H264 @200Mbps = **60 FPS**.

The encoder pipeline is bandwidth-independent — bit_rate only affects output data size, not encoding speed.

## Photo Mode Performance (Estimated)

Photo mode uses `snapshot()` + `img.save()` (JPEG to SD card).

| Resolution | Format | Est. FPS | Bottleneck |
|---|---|---|---|
| 640×480 | RGB565 JPEG | ~20/s | snapshot + SD write |
| 640×480 | GRAYSCALE JPEG | ~37/s | Smaller file, faster snap |

SD card write speed is the secondary bottleneck after Python snapshot.

## File System

- `/sdcard/` — SD card, persists across reboots. Code lives here.
- `/data/` — Data partition (~13GB free). Photos, videos, inference results.
- `/` — Root, read-only firmware.
- **No USB mass storage or PTP/MTP.** Only serial (ttyACM0/ttyACM1) for host communication.
- CanMV IDE can also transfer files via its built-in file browser (when connected).

## main.py Auto-Start

When `/sdcard/main.py` exists, CanMV firmware auto-runs it after `boot.py` completes. To prevent this during testing:
1. Rename: `uos.rename('/sdcard/main.py','/sdcard/main.bak')`
2. Reboot to get clean REPL without camera hardware initialization
3. Restore after testing: `uos.rename('/sdcard/main.bak','/sdcard/main.py')`
