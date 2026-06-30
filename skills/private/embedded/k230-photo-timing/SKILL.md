---
name: k230-photo-timing
description: K230 photo capture timing control, performance profiling, and Display-binding optimization. Covers interval gating, save error checking, uos.stat() quirks, ampy rules, and snapshot/save performance optimization.
signature: "k230-photo-timing -> processed_result"
---
version: 1.2.0

# K230 Photo Capture — Timing, Performance & Architecture

Fix for photo capture modes that produce empty/corrupt files due to unthrottled main-loop calls. Covers K230 sensor architecture, snapshot/save performance profiling, and optimization via Display binding.

## Root Cause

On K230 (Kendryte K230 with MicroPython + AI2D), the main loop calls photo capture functions every iteration with **zero delay**. This creates three compounding failures:

1. **Config field ignored**: `photo_interval_ms` exists in `config.json` but is never read by any capture function.
2. **No save error checking**: `img.save(path)` return value is ignored. On SD card write failure, files are silently empty/corrupt with zero logging.
3. **Pipeline speed mismatch**: Camera produces frames at N fps (e.g., 30fps = 33ms/frame), but the main loop calls `snapshot()` thousands of times/second. Most calls return duplicate frames, and the SD card write bottleneck causes silent failures.

**Result**: Directories are created (always) but contain zero or corrupt files. Only rare runs with favorable timing (SD card idle, clean power-up) produce valid images.

## Fix: Interval Gating

Every photo capture function MUST include this pattern at the top, after the mode check:

```python
# --- Interval gating ---
interval_ms = state.config.get("photo_interval_ms", 100) if state.config else 100
if not hasattr(state, "_last_photo_<mode>_ms"):
    state._last_photo_<mode>_ms = 0
now = time.ticks_ms()
elapsed = time.ticks_diff(now, state._last_photo_<mode>_ms)
if elapsed < interval_ms:
    return  # Too soon, skip this iteration
state._last_photo_<mode>_ms = now
```

Replace `<mode>` with the actual mode name: `baseline`, `batch`, `raw`, `320p`.

## Fix: Save Error Checking

Change from:
```python
img.save(filename)
state.cam_count += 1
```

To:
```python
saved = img.save(filename)
if saved is False:
    print("[MODE] CamX: SAVE FAILED count={}".format(state.cam_count))
del img
if saved is not False:
    state.cam_count += 1
```

## When to Apply

Always when modifying or debugging any photo capture mode on K230:
- `photo_mode_capture_baseline()`
- `photo_mode_capture_batch()`
- `photo_mode_capture_raw()`
- `photo_mode_capture_320p()`

**Rule**: If the capture function is called from a tight main loop (no explicit sleep between calls), interval gating is mandatory. Never assume the main loop respects timing.

## Debugging Checklist for Empty Photo Dirs

1. Check `config.json` for `photo_interval_ms` — is it set?
2. Check if the capture function reads `photo_interval_ms` — does the gating code exist?
3. Check if `img.save()` return value is checked — are failures silently ignored?
4. Check `photo_sensor_ids` — mismatched sensors (e.g., only sensor 0 for 320p but expecting both) cause silent skip of one camera.
5. Verify `photo_mode_start()` camera init timing — 50ms after `set_framesize()` may not be enough for sensor warmup.
6. **Check `uos.stat()` usage** — if file size is read via `.st_size`, it will fail silently in MicroPython. Use `[6]` instead.
7. **Check right camera init** — if right camera hangs, the entire photo loop is blocked. Wrap in try/except.

## Config Convention

`config.json` keys for photo timing:
- `photo_interval_ms`: milliseconds between frames (default 100 if missing)
- `photo_sensor_ids`: list of sensor IDs to use (e.g., `[0, 1]` or `[0]`)
- `photo_width`, `photo_height`, `photo_fps`, `photo_pixformat`

For 320p mode, if keys are prefixed `photo_320p_`, the defaults in `config.py` are used (320x240, 30fps, RGB565). Missing keys fall back gracefully but the interval is the one that causes silent failure.

## K230 MicroPython Platform Quirks

### `uos.stat()` returns tuple, NOT stat_result object

On K230 MicroPython, `uos.stat(path)` returns a **tuple** of 10 values:
```python
(16895, 5330480, 0, 0, 7362368, 0, 0, 5421280, 0, 7259136)
```
File size is at **index 6** (standard POSIX stat struct layout).

WRONG (CPython style): `uos.stat(path).st_size`
CORRECT: `uos.stat(path)[6]`

All K230 MicroPython code must use `[6]` for file size. Using `.st_size` causes `AttributeError: 'tuple' object has no attribute 'st_size'`.

Create a helper: `def fsize(path): return uos.stat(path)[6]`

### CSI1 (Right Camera) Initialization Can Hang

`Sensor(id=1, ...)` for the right camera (gc2093_csi1) may hang indefinitely during `reset()` or `run()`. The output shows:
```
find sensor gc2093_csi1...
```
and then nothing — the device becomes unresponsive. This may indicate:
- Right camera not physically connected
- CSI1 hardware fault
- Different initialization sequence needed

ALWAYS handle right camera init with try/except and graceful fallback to left-only.

### ampy Tool Usage Rules

**`ampy run` takes LOCAL file paths, not device paths.**

- `ampy run /tmp/script.py` — reads `/tmp/script.py` from HOST filesystem, sends content via stdin to device, executes it, captures stdout
- `ampy run /sdcard/script.py` — tries to open `/sdcard/script.py` on the HOST filesystem → **FAILS** with "Failed to find or read input file"

The `run` command works by: read local file → `exec_()` the content to the board → capture output. It does NOT read files from the device filesystem.

**`ampy ls` works on device paths:** `ampy ls /sdcard/` lists device files. `ampy ls /sdcard/file.py` (single file) fails with ENOENT because ampy calls `listdir()` on the full path.

**`ampy get` retrieves device files to local filesystem.**

**ampy run output is unreliable on K230** — `stream_output=True` mode may not return any stdout due to MicroPython implementation differences. Use direct serial communication for capturing output, or write results to a file and `ampy get` the file.

## Snapshot/Save Performance Profile

Measured on K230 with `gc2093_csi0` (left camera) at 320x240, RGB565:

| Operation | Time | Notes |
|-----------|------|-------|
| `snapshot()` only | 24-33ms | Pure camera capture, no save |
| `img.save()` | 17-27ms | JPEG write to SD card |
| **Total `snapshot + save`** | **50-60ms** | ~20 FPS theoretical limit (current photo.py) |
| `snapshot + save + sleep_ms(50)` | 100-110ms | ~10 FPS (typical photo.py with sleep) |

**Key Insight**: FPS bottleneck is `snapshot()` + `save()` combined, NOT the main loop speed. The main loop runs at ~100,000 iterations/second with no sleep. Even with `photo_interval_ms = 10`, each `snapshot + save` takes 50ms, so **20 FPS is the hard limit** at current config.

## Optimized Pipeline: Bind Display for Faster Snapshot

Official example (`examples/17-Sensor/camera_snapshot_and_save.py`) achieves **21ms snapshot** by binding chn0 to Display layer. Our photo.py (no Display binding) takes 26-33ms — 22% slower.

### Official Pipeline (Fast — Hardware Pipeline)

```python
sensor = Sensor()                          # Default constructor
sensor.reset()
sensor.set_framesize(width=320, height=240) # chn0: resolution
sensor.set_pixformat(Sensor.YUV420SP)       # chn0: Display format

# Bind to display layer (hardware pipeline)
bind_info = sensor.bind_info()
Display.bind_layer(**bind_info, layer=Display.LAYER_VIDEO1)
Display.init(...)

# Set chn2 for saveable snapshots
sensor.set_framesize(width=320, height=240, chn=2)
sensor.set_pixformat(Sensor.RGB565, chn=2)

sensor.run()                               # Start once
time.sleep_ms(200)

# Snapshot from chn2 (RGB565, supports save)
img = sensor.snapshot(chn=2)
img.save("/data/img.jpg")
```

### Our Current Pipeline (Slower — Software Path)

```python
sensor = Sensor(id=0, width=320, height=240, fps=30)
sensor.reset()
sensor.set_framesize(width=320, height=240, chn=0)
sensor.set_pixformat(Sensor.RGB565, chn=0)
sensor.run()
img = sensor.snapshot()                    # chn0, no Display binding
img.save("/data/img.jpg")
```

### Differences

| Aspect | Official | photo.py |
|--------|----------|----------|
| Constructor | `Sensor()` default | `Sensor(id=0, w, h, fps)` |
| chn0 format | YUV420SP (Display) | RGB565 (save) |
| Display binding | bind chn0 to LAYER_VIDEO1 | No Display binding |
| chn1/chn2 | Set to RGB888/RGB565 | Not configured |
| snapshot() target | chn0 (YUV420SP) or chn2 (RGB565) | Default chn0 (RGB565) |
| Pipeline | Hardware (GDMA/DSP) | Pure software |
| snapshot time | **21ms** | **26-33ms** |

**Result**: With Display binding, total `snapshot + save` should be ~35-40ms → **25-28 FPS** vs current 20 FPS.

### YUV420SP Constraint

**YUV420SP is the ONLY format supported by Display.bind_layer.** Assert error:
```
AssertionError: bind video layer only support format PIXEL_FORMAT_YUV_SEMIPLANAR_420
```

YUV420SP cannot be saved via `img.save()` — `OSError: current format not support save function!`

The workaround is using chn1 (RGB888) or chn2 (RGB565/RGBP888) for snapshot+save operations.

## Multi-Sensor Rules

From `examples/17-Sensor/camera_dual_bind_hdmi.py`:

- Multiple sensors only need ONE `sensor.run()` call (any sensor's run() starts all)
- Multiple sensors all need `sensor.stop()` calls (each sensor must be stopped individually)
- Or call `Sensor.deinit()` once to stop all
- Comment warns: "当使用多个 Sensor 时，分辨率建议均设置为 1920 × 1080, 且 fps 设置为 30" — using other resolutions may cause display artifacts

## Throttle Timing Verification

Test with `photo_interval_ms = 10`:
- 209,595 main loop iterations → only 21 actual snapshot calls
- 21/21 save successful → throttle works correctly
- Effective FPS = 20.1 (limited by snapshot+save time, not by 1/0.01 = 100)

Test with `photo_interval_ms = 100`:
- 209,595 main loop iterations → 20 actual snapshot calls
- 20/20 save successful
- Effective FPS = 10.0 (exactly 1/0.1)

**Conclusion**: The throttle gate correctly limits to `1000/millis` calls regardless of main loop speed. Main loop runs at ~100,000 iterations/second, but only the gated calls execute snapshot.

## Empty Photo Directory Diagnosis

When `/data/320p_photos/` has multiple numbered directories but only one has files (e.g., 024 has 542 files, 025-034 are empty):

1. Check `/sdcard/photo_sequence.txt` — if it shows 34, then 34 sessions were initiated
2. Check if `photo_mode_start()` creates directory before sensor init — yes it does
3. Failed sessions still create directories but produce no files
4. Only sessions where ALL sensors initialize AND `current_mode == "photo"` AND `is_running == True` produce files

## New Pitfall: Directory Lifecycle After Serial Flood

**Root cause discovered 2026-06-18**: When main loop floods the serial port, `photo_mode_start()` may succeed in creating the directory (`ensure_dir()`) but the subsequent sensor init or camera run() call gets lost in the serial flood. The directory remains on SD card as an empty stub. This produces a cascade of empty directories (e.g., 025-034) with only the final successful run (024) containing actual photo files.

**Diagnosis pattern**:
- Directories exist but are empty → `ensure_dir()` ran, but sensor init failed (silently) or was interrupted
- Only one directory has files → all intermediate sessions failed to complete photo_mode_start()
- Directory with few files only on one camera → the other camera's init hung and triggered early stop

**Prevention**: Add a post-stop cleanup in `photo_mode_stop()` or a startup check that removes empty photo session directories older than N minutes. Consider:
```python
# In photo_mode_start(), before ensure_dir():
existing = [d for d in os.listdir(photo_dir) if os.path.isdir(os.path.join(photo_dir, d))]
for d in existing:
    full = os.path.join(photo_dir, d)
    try:
        files = os.listdir(full)
        if len(files) == 0:
            os.rmdir(full)  # Remove empty dir
    except:
        pass
```

## New Pitfall: REPL Window After rmmod Recovery

After `rmmod ftdi_sio; modprobe ftdi_sio`, the K230 serial port recovers BUT `main.py` continues flooding the UART with print statements. The first 2-3 seconds of REPL commands are often lost or garbled because:
- `main.py`'s `while True` loop has already been running since boot
- Thousands of print statements per second flood the 115200 baud serial buffer
- The device is NOT in a clean REPL state after driver reload — it's still executing `main.py`

**Recovery protocol**:
1. `sudo rmmod ftdi_sio; sleep 1; sudo modprobe ftdi_sio; sleep 1` — reload driver
2. Send 5-10x `Ctrl+C` to interrupt main loop
3. Send `Ctrl+D` to enter clean REPL
4. Send 1-2 `Ctrl+C` again to ensure clean `>>>` prompt
5. **Wait 0.5s** before sending the first useful command
6. If first command shows `...` continuation prompt, send Ctrl+C again

**Ampy is unreliable after recovery**: Use direct serial (`python3 -c "import serial..."`) for initial connectivity test, then switch to ampy for file operations once you have confirmed `>>>` prompt.

## K230 Device Recovery — Auto Serial Reset

When the K230 serial port becomes completely dead (all reads return empty, `ampy` hangs at rc=124), the serial driver (`ftdi_sio`) must be reloaded:

```bash
sudo rmmod ftdi_sio 2>/dev/null
sudo rmmod usb_serial 2>/dev/null
sleep 1
sudo modprobe ftdi_sio
sleep 1
```

After rmmod, the device may show `OSError: [Errno 5] Input/output error` on `in_waiting`. After modprobe, a simple `print("HI")` test confirms recovery.

This is NOT the same as a soft reset (Ctrl+D). The K230 can enter a state where the UART hardware is completely locked up — only the kernel driver reload restores it.

## K230 Sensor Multi-Channel Bug

**Critical limitation**: `Sensor(id=N, width, height, fps)` constructor + setting chn2 via `set_framesize(..., chn=2)` + `run()` **causes device hang**. Only single-channel init (chn0) works reliably with this constructor.

Both `Sensor()` default constructor + `set_framesize` + `set_framesize(..., chn=2)` + `run()` also hang.

**Workaround**: Only initialize and run chn0. Do NOT set chn1/chn2 when using `Sensor(id=N, ...)`. If multi-channel output is needed, use the official `Sensor()` default constructor without chn2, then use chn0 for everything.

**Evidence**: Both `Sensor(id=0, 320, 240, fps=30)` + chn2 set → hang AND `Sensor()` default + chn2 set → hang. The hang is immediate and unrecoverable without `rmmod ftdi_sio` + `modprobe ftdi_sio`.

## Related: Serial Flood → Silent Write Failure

When the K230 main loop floods the serial port (print statements, no throttling), ampy operations hang or timeout. **This compounds the silent-write problem:** you cannot verify the fix via ampy because the serial port is blocked. Debugging chain:

**Full session transcript with directory-lifecycle diagnosis**: references/serial-flood-empty-dir.md

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。



# K230 Photo Timing

