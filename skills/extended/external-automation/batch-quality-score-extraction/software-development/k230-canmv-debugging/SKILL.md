---
name: k230-canmv-debugging
category: autonomous-ai-agents
description: K230 CanMV board debugging — serial REPL, ampy transfers, hardware encoder
version: 1.4
  pipeline, sensor init order, and import quirks specific to Kendryte K230 / Micropython
  / CanMV v1.4.
allowed-tools:
- terminal
- file
- read_file
triggers:
- K230 board
- CanMV
- Kendryte
- Micropython embedded debugging
- serial REPL
- ampy upload
- eye tracker hardware
- gc2093 camera sensor
metadata:
  synthos:
    signature: 'error: str -> fix: str'
    related_skills:
    - agent-orchestration-harness
    - debugging-hermes-tui-commands
    - embedded-python-modularization
    - github-agent-contributions
    - hermes-agent-skill-authoring

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

**ampy run takes LOCAL file paths** — it reads the local file and sends its content to the device via stdin. It does NOT read device files.

```bash
ampy -p /dev/ttyACM0 -b 115200 put local_file.py /sdcard/remote.py
ampy -p /dev/ttyACM0 -b 115200 get /sdcard/remote.py
ampy -p /dev/ttyACM0 -b 115200 run /tmp/test_script.py   # LOCAL path, not /sdcard/...
```

**CRITICAL: Do NOT touch the serial port before ampy.** Any serial read/write/open blocks ampy internally. If the board's main.py is flooding the serial port with print statements, ampy will hang/timeout.

**ampy workflow sequence — NEVER open serial first:**
1. Spawn ampy as a standalone subprocess — it opens its own serial connection. If you open serial first, ampy will hang.
2. If board is already alive and flooding serial: send Ctrl+C flood (200+) to kill the loop, then IMMEDIATELY spawn ampy as a subprocess — no serial reads/writes between Ctrl+C and ampy.
3. **ampy succeeds only when no other code is using the serial port.** Each Ctrl+C + serial read attempt consumes the ~5s window before main.py restarts.

**Serial flooding detection:** ampy rc=124 (timeout), 0 bytes output. Serial reads return empty `b''` even after 200+ Ctrl+C. Board may be completely dead (zero output for any input).

**CRITICAL: ampy run returns empty stdout on K230.** The `ampy run` command (which reads a local file and sends it via stdin) returns rc=0 but stdout is ALWAYS 0 bytes on K230 CanMV. This is because the K230's MicroPython `exec_with_output()` does not return captured stdout — the data is lost.

**Workaround for test scripts:**
1. Write test results to a file on the board (`open('/data/result.txt', 'w').write(...)`)
2. Use `ampy get` to retrieve the result file
3. OR use `ampy run` only once per boot cycle and read stdout immediately (not reliable)
4. For reliable output: use `ampy run` + `ampy get` in separate calls, or use `exec_` (not `run`) to send code via pyboard exec mode.

**CRITICAL: ampy run is unreliable for test scripts.** Empirically, ampy run may succeed on first call (rc=1, captures stdout) but completely hang (rc=124, 0 bytes) on subsequent calls within the same session.

**CRITICAL: Modifying boot.py to be noop breaks ampy entirely.** After replacing boot.py with a noop version (to stop main.py auto-run), ALL ampy operations hang (rc=124, 0 bytes). This is not a serial-flooding issue — it is an ampy protocol stack incompatibility with the noop boot.py state. The board enters REPL but ampy's RAW MODE handshake fails. **Rule: Never replace boot.py with noop if you need ampy afterward.** Instead, modify main.py to suppress serial output, or restore boot.py before testing.

**Solution for dead board:** Physical reset: unplug USB or press RESET button 3s. After reset: ampy immediately — do NOT open serial port first. If ampy fails: rapid Ctrl+C flood (500+) → spawn ampy subprocess immediately.

**gvfs gphoto2 mount limitation:** K230's PTP implementation via gvfs (gphoto2:// URI) can list directory NAMES but CANNOT read or write file contents. `os.listdir()` on the mount point returns directory names but all files are empty. This is a known K230 PTP limitation — the Imaging interface (Class 6) supports directory enumeration but not actual file access. File transfer MUST go through serial/ampy.

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

### K230 MicroPython Python-ism Limitations

K230 CanMV runs a constrained MicroPython — NOT all Python 3 features are available:

- **NO f-strings** — `f'hello {x}'` causes `SyntaxError: invalid syntax`. Use `'%s' % x` or `str.format()` or `+` concatenation.
- **`str.zfill()` does not exist** — `str.zfill()` is Python 3.6+ CPython only. Use `'%04d' % n` instead.
- **`sys.path[0]` may be empty or `/`** — use `__file__` or check `sys.path` explicitly.
- **`sys.setrecursionlimit()` may fail silently** — stack depth is limited by hardware.
- **`gc.collect()` is essential** before heavy sensor operations — MicroPython GC is manual/periodic, not generational.
- **`uos.stat()` returns a tuple, NOT stat_result** — `uos.stat(path)` returns a 10-element tuple (POSIX stat struct). File size is at index 6: `uos.stat(path)[6]`. Using `.st_size` (CPython style) causes `AttributeError`.

### Photo save failure diagnostic

When `img.save(path)` returns `False` (or directories created but no files):

1. **Check save path existence** — `uos.stat(path)` should succeed. If the directory doesn't exist, save silently fails.
2. **Check SD card free space** — use `uos.statvfs()` to verify available space (every 5s, cache result).
3. **Check file permissions** — `/data/` is writable, `/sdcard/` may be read-only depending on boot config.
4. **Check image validity** — if `snapshot()` returns `None`, the camera was not running or timed out.
5. **Check file suffix** — `img.save()` may expect `.bmp` vs `.jpg` — the sensor's native format may differ.
6. **Throttle is critical** — without interval gating, the main loop fires `snapshot()` thousands of times/second, overwhelming SD card write buffer and causing silent save failures.

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
