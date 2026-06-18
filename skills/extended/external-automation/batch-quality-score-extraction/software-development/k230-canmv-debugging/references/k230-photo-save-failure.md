# K230 Photo 320p Save Failure — Session Debugging

## Date
2026-06-18

## Symptoms
- `/data/320p_photos/` directory has 024 subdirectory with images
- All other numbered subdirectories (001-023, 025+) are empty (0 files)
- Main loop calls `photo_mode_capture()` at full speed without throttling

## Root Cause
The main loop in `main.py` calls `photo_mode_capture()` in its `while True` loop at the full loop speed (thousands of iterations/second). The `photo_mode_capture_320p()` function calls `state.sensor_left.snapshot()` every time, but there is NO interval gating. This overwhelms the SD card write buffer:
- `snapshot()` succeeds (returns image object)
- `img.save(filename)` returns `False` silently (SD card write fails due to congestion)
- No file is written, but the session directory was already created by the dispatcher
- Result: empty directories in `/data/320p_photos/`

## Fix Applied
Added interval gating in `photo_mode_capture_320p()`:
```python
interval_ms = state.config.get("photo_interval_ms", 100) if state.config else 100
if not hasattr(state, "_last_photo_320p_ms"):
    state._last_photo_320p_ms = 0
now = time.ticks_ms()
elapsed = time.ticks_diff(now, state._last_photo_320p_ms)
if elapsed < interval_ms:
    return  # Too soon, skip this iteration
state._last_photo_320p_ms = now
```

Also added save failure detection:
```python
saved = img0.save(filename0)
if saved is False:
    print("[320p] Cam0: SAVE FAILED count={}".format(state.cam0_count))
```

## Tooling Findings

### ampy run returns empty stdout
- `ampy run /tmp/script.py` on K230 returns rc=0 but stdout is ALWAYS 0 bytes
- The K230's MicroPython `exec_with_output()` does not return captured stdout data
- **Workaround:** Write results to a file on device, then `ampy get` to retrieve
- **Workaround:** Use `exec_` (not `run`) to send code via pyboard exec mode

### f-strings not supported
- `f'hello {x}'` causes `SyntaxError: invalid syntax` on K230 MicroPython
- `str.zfill()` does not exist — use `'%04d' % n` instead
- Always use `+` concatenation or `'%s' % x` format strings

### Direct serial REPL unreliable
- After sending code via serial port, `ser.read_all()` returns `b''` (empty)
- Board appears dead — no output for any input
- Physical reset (power cycle) required to recover

### SD card save failure detection
- `img.save()` returns `False` on failure (not exception)
- Empty directories are created before save attempts
- Must check `saved is False` AND `stat().st_size > 0` for validation

## References
- photo.py fix: adds `photo_mode_capture_320p()` with interval gating
- main.py fix: corrects display logic for 320p mode
- test_photo_capture.py: standalone test that validates camera+save pipeline
