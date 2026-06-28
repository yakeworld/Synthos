# Empty Photo Directory Diagnosis — 024-Only-Files Pattern

## Symptom

`/data/320p_photos/` has multiple numbered directories (024 through 034), but only directory 024 has files (e.g., 542 files). All other directories (025-034) are empty.

## Root Cause Analysis

1. **Sequence persistence**: `/sdcard/photo_sequence.txt` shows 34 — meaning `photo_mode_start()` was called 34 times.
2. **Only first session succeeded**: 024 = 542 frames over ~5.4s at 100ms throttle.
3. **Sessions 025-034 all failed**: `photo_mode_start()` created directories, but actual photo captures failed.
4. **Only complete photo loops produce files**: ALL of the following must be true:
   - Sensors initialize successfully (both `state.sensor_left` and optionally `state.sensor_right`)
   - `state.current_mode == "photo"` (set by `photo_mode_start()`)
   - `state.is_running == True` (set by `photo_mode_start()`)
   - Main loop enters photo branch: `if state.current_mode == "photo"`

## Why Subsequent Sessions Fail

Possible reasons after initial success:

1. **Sensor resource exhaustion**: First session works fine. But if `photo_mode_stop()` doesn't fully clean up sensors, subsequent `photo_mode_start()` calls may fail during sensor init.

2. **Right camera hang**: If the code tries to init the right camera and it hangs, the entire photo loop is blocked. The directory is created (by `photo_mode_start()`), but no frames are captured because the right camera init blocks.

3. **SD card thermal protection**: After 542 frames in ~5.4s, the SD card may enter a protective state where subsequent writes fail silently.

4. **`current_mode` gets cleared prematurely**: `photo_mode_stop()` sets `state.current_mode = None` and `state.is_running = False` — but only after a 2-second sleep. If something clears `current_mode` earlier, the main loop skips the photo branch.

## Diagnostic Steps

```python
# Check sequence number
ampy -p /dev/openmvcam -b 115200 get /sdcard/photo_sequence.txt /tmp/seq.txt
cat /tmp/seq.txt  # Expected: 34

# List all directories
ampy -p /dev/openmvcam -b 115200 ls /data/320p_photos/
# Expected: 024, 025, ..., 034

# Check 024 content
ampy -p /dev/openmvcam -b 115200 ls /data/320p_photos/024/ | wc -l
# Expected: 542

# Check 025 content  
ampy -p /dev/openmvcam -b 115200 ls /data/320p_photos/025/
# Expected: empty
```

## Fix Direction

1. **Verify `photo_mode_start()` sets `current_mode` and `is_running`**: Both must be set for the main loop to enter the photo branch.
2. **Ensure sensors fully clean up between sessions**: `photo_mode_stop()` must fully release sensor resources.
3. **Handle right camera init failure gracefully**: If right camera hangs, fall back to left-only mode.
4. **Check `photo_mode_capture()` exit conditions**: The function returns early if `not state.is_running or state.current_mode != "photo"` — verify these are correct.

## Config File Impact

- `photo_interval_ms` controls frame rate but NOT directory creation
- Directory creation happens in `photo_mode_start()` regardless of whether any frames are captured
- The sequence number increments on EVERY call to `photo_mode_start()`, even failed ones