---
name: k230-canmv-debugging
category: autonomous-ai-agents
description: K230 CanMV board debugging — serial REPL, ampy transfers, hardware encoder pipeline, sensor init order, and import quirks specific to Kendryte K230 / Micropython / CanMV v1.4.
triggers:
  - K230 board
  - CanMV
  - Kendryte
  - Micropython embedded debugging
  - serial REPL
  - ampy upload
  - eye tracker hardware
  - gc2093 camera sensor
---

# K230 CanMV Board Debugging

## 原理层·文言

> 嵌入式者，裸机之舞。无系统之庇护，有串口为窗。
> 问其 REPL，答以 Python。不响应则查驱动，再无声则断电源。
> 引脚电平，时序波形，一一排查，步步为营。

##

## Connection

- The K230 appears as `/dev/ttyACM[0-1]` (USB CDC ACM)
- **CanMV IDE holds the serial port** — must disconnect IDE or kill process before using ampy
- The device can re-enumerate (ttyACM0 → ttyACM1) after USB replug
- Baud rate: **115200**

## Serial REPL Modes

- **Normal REPL** (`>>> ` prompt) — standard interaction
- **Raw REPL** (`>` prompt) — entered via Ctrl+A, used by ampy internally
- **Paste mode** — entered via Ctrl+E, exit+execute via Ctrl+D. Best for multi-line code

### Reliable Output Capture

```python
# Paste mode is most reliable for multi-line:
ser.write(b'\x05')     # Ctrl+E enter paste mode
ser.write(code.encode())
ser.write(b'\x04')     # Ctrl+D execute
time.sleep(wait)
out = ser.read_all()

# For one-liners, wait for prompt:
ser.write(cmd.encode() + b'\r\n')
time.sleep(wait)
out = b''
for _ in range(5):
    d = ser.read_all()
    out += d
    if b'>>>' in d:
        break
    time.sleep(0.3)
```

### Common States

| Symptom | Cause | Fix |
|---|---|---|
| Commands echo but no output | REPL in paste/raw mode leak | Send Ctrl+B (normal mode) then Ctrl+C |
| Empty reads | Board hung after hardware test | **Physical reset button** required |
| `Device or resource busy` | CanMV IDE holding port | Kill canmvide process |
| `/dev/ttyACM*` disappeared | USB re-enumerated | Check `ls /dev/ttyACM*; lsusb` |
| ampy: `could not enter raw repl` | main.py running foreground | Interrupt with Ctrl+C first |

## File Transfer

### ampy (preferred)

```bash
ampy -p /dev/ttyACM0 -b 115200 put local_file.py /sdcard/remote.py
ampy -p /dev/ttyACM0 -b 115200 get /sdcard/remote.py
ampy -p /dev/ttyACM0 -b 115200 run test_script.py
```

**Blocked when main.py is running.** Solution:
1. Connect serial, send Ctrl+C to stop main loop
2. Then use ampy (within the same ~5s window before board reboots)

### Base64 via paste mode (fallback)

```python
b64 = base64.b64encode(content).decode()
ser.write(b"import ubinascii;b=''\n")
for i in range(0,len(b64),200):
    ser.write(("b+='"+b64[i:i+200]+"'\n").encode())
    time.sleep(0.02)
ser.write(b"raw=ubinascii.a2b_base64(b);open('/sdcard/file.py','wb').write(raw);print('ok')\n")
ser.write(b'\x04')
```

### Boot.py auto-run (most reliable for long tests)

Write a test script to `/sdcard/test.py`, then overwrite boot.py:

```python
open('/sdcard/boot.py','w').write(
    'import sys;sys.path.insert(0,"/sdcard");'
    'exec(open("/sdcard/test.py","rb").read())\n'
)
```

Reboot (Ctrl+D or power cycle). The test auto-runs. Results can be written to a file and read back.

**Always restore boot.py after test completes!**

## K230 Hardware Encoder Pipeline

### Correct init order (official CanMV example)

```python
from media.sensor import Sensor
from media.vencoder import Encoder, ChnAttrStr, StreamData, VIDEO_ENCODE_MOD_ID, VENC_DEV_ID
from media.media import MediaManager

# 1. Sensor - NO constructor args!
sensor = Sensor()
sensor.reset()
sensor.set_framesize(width=width_aligned, height=h, alignment=12)
sensor.set_pixformat(Sensor.YUV420SP)

# 2. Encoder
encoder = Encoder()
encoder.SetOutBufs(venc_chn, 8, width_aligned, height)

# 3. LINK before MediaManager.init() — critical!
link = MediaManager.link(sensor.bind_info()['src'],
    (VIDEO_ENCODE_MOD_ID, VENC_DEV_ID, venc_chn))
MediaManager.init()    # ← init AFTER link

# 4. Create, Start, then run sensor
encoder.Create(venc_chn, chnAttr)
encoder.Start(venc_chn)
sensor.run()
```

### Key patterns

- **Width must be 16-byte aligned**: `wa = (w + 15) // 16 * 16`
- **`Sensor()` without args** — then use `set_framesize()` + `set_pixformat()`
- **`k_u64_ptr`** is in `media.mp4format`, NOT in `mpp.mp4_format` or `mpp.mp4_format_struct`
- **Encoder link target**: `(VIDEO_ENCODE_MOD_ID, VENC_DEV_ID, venc_chn)` not raw `(2, 0, ch)`
- **GetStream returns multiple packets**: iterate `streamData.pack_cnt`

### Encoder FPS limits

| Resolution | Codec | Measured FPS |
|---|---|---|
| 1280×720 | H265 | ~60 |
| 1280×720 | H264 200Mbps | ~60 |
| 1920×1080 | H264 | ~60 |
| 1920×1080 | H265 | ~30 (theoretical) |

- **`snapshot()` path is ~31 FPS at 720p** (Python memory copy bottleneck)
- **Encoder DMA path is ~60 FPS** (hardware bypasses Python)

### GC2093 Sensor

- 2 cameras: csi0 (left), csi1 (right)
- Max native output: 1920×1080@60
- Only ONE hardware encoder — dual camera recording not possible at full speed

## Import Quirks

| Symbol | Actual Module |
|---|---|
| `k_u64_ptr`, `k_u32_ptr`, etc. | `media.mp4format` |
| `kd_mp4_create`, `kd_mp4_create_track` | `mpp.mp4_format` |
| `k_mp4_config_s`, `k_mp4_track_info_s` | `mpp.mp4_format_struct` |
| `StreamData`, `ChnAttrStr`, `Encoder` | `media.vencoder` |

## Pitfalls

### ReleaseStream must be paired with GetStream

```python
got_stream = False
try:
    encoder.GetStream(venc_chn, streamData, timeout=1)
    got_stream = True
    # ... process ...
except Exception:
    pass
finally:
    if got_stream:
        try:
            encoder.ReleaseStream(venc_chn, streamData)
        except Exception:
            pass
```

Without `finally`, an exception during processing leaks the stream and stalls the encoder.

### Photo counting

Use independent `cam0_count` / `cam1_count` per camera, never a shared counter. Only increment on successful `save()`.

### handle_stop_key machine.reset()

The root cause is unreliable cleanup in video mode. Use try/finally to guard every resource release. Until fixed, the TODO should be explicit.

### `statvfs` is expensive

Cache storage info for at least 5 seconds.
