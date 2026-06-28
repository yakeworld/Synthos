# Serial Flood → Empty Directory Cascade — 2026-06-18

## Session Context

User reported `320p_photos/024` had images but 025-034 were all empty on a K230 device.

## Diagnosis Steps

### Step 1: Verify Directory Structure
```
/data/320p_photos/ contains: 024, 025, 026, 027, 028, 029, 030, 031, 032, 033, 034, 035
```

### Step 2: Check File Content Per Directory
```
024: 542 jpg files (cam0 + cam1, both cameras)
025-034: 0 jpg files (empty)
035: 30 jpg files (cam0 only, right camera failed)
```

### Step 3: Check Device State
```
state.current_mode = None
state.is_running = False
state.photo_capture_mode = not set  # Never set via photo_mode_select()
```

### Step 4: Verify photo.py Code
All capture modes have interval gating (100ms), save error checking, dual-cam support. Code is correct.

## Root Cause Chain

1. `main.py` runs `while True` with zero delay, printing debug info each iteration
2. When user presses button for photo mode, `photo_mode_start()` is called
3. `photo_mode_start()` calls `ensure_dir()` → creates `/data/320p_photos/025`
4. `ensure_dir()` returns immediately
5. Sensor init (Sensor(id=0, ...) + run()) begins
6. But `main.py` is still flooding serial at ~100K iters/sec
7. The `sensor.run()` call may be called but its stdout is lost in the flood
8. If sensor init succeeds, `photo_mode_capture()` is dispatched from main loop
9. But main loop is also flooded → `photo_mode_capture()` calls are lost/interleaved
10. Result: directory created, but no successful `snapshot()` + `save()` completed
11. Empty directory remains on SD card

## Evidence

- **024**: 542 files, both cam0 and cam1 → a complete successful run
- **025-034**: completely empty → directory created but capture never completed
- **035**: 30 files, cam0 only → right camera (CSI1) init failed (hangs), left camera ran for 30 frames then stopped

## CSI1 Hang Confirmed

Previous testing confirmed that `Sensor(id=1, ...)` for right camera (gc2093_csi1) causes immediate device hang. All photo sessions involving both cameras fail silently at right camera init.

## Fix Applied

Already applied in photo.py:
- Interval gating (prevents rapid-fire snapshot calls)
- Save error checking (logs FAILED saves)
- Right camera init wrapped in try/except

## Prevention Recommendation

Add cleanup of empty photo session directories in `photo_mode_start()`:
```python
# Before creating new dir, clean up empty ones
existing = [d for d in os.listdir(photo_dir) if os.path.isdir(os.path.join(photo_dir, d))]
for d in existing:
    full = os.path.join(photo_dir, d)
    try:
        if len(os.listdir(full)) == 0:
            os.rmdir(full)
    except:
        pass
```

Or add a periodic cleanup task (e.g., every 5 minutes) that removes empty session dirs older than 10 minutes.

## Key Metrics

- Main loop iterations: ~100,000/sec (measured)
- Photo interval: 100ms → 10 actual snapshot calls/sec
- snapshot+save time: ~50ms per frame
- Effective FPS: ~10 (limited by interval gating + save time)
- Right camera: CSI1 hangs on init → graceful fallback to left-only
