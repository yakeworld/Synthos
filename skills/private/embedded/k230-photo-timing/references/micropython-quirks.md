# MicroPython Platform Quirks — K230

## uos.stat() returns tuple, NOT stat_result object

On K230 MicroPython, `uos.stat(path)` returns a **tuple** of 10 values:
```python
(16895, 5330480, 0, 0, 7362368, 0, 0, 5421280, 0, 7259136)
```
File size is at **index 6** (standard POSIX stat struct layout).

WRONG (CPython style): `uos.stat(path).st_size`
CORRECT: `uos.stat(path)[6]`

All K230 MicroPython code must use `[6]` for file size.

## CSI1 (Right Camera) Hangs on Init

`Sensor(id=1, ...)` for the right camera (gc2093_csi1) hangs indefinitely during `reset()` or `run()`. Output shows:
```
find sensor gc2093_csi1...
```
then nothing — device becomes unresponsive.

Possible causes:
- Right camera not physically connected
- CSI1 hardware fault
- Different initialization sequence needed

ALWAYS handle right camera init with try/except and graceful fallback to left-only.

## ampy Tool Rules

| Command | Path Type | Behavior |
|---------|-----------|----------|
| `ampy run /tmp/script.py` | LOCAL | Reads `/tmp/script.py` from HOST, sends via stdin to device, executes it |
| `ampy run /sdcard/script.py` | DEVICE | **FAILS** — ampy tries to open `/sdcard/script.py` on HOST filesystem |
| `ampy ls /sdcard/` | DEVICE | Lists device directory |
| `ampy ls /sdcard/file.py` | DEVICE | **FAILS** — ampy calls `listdir()` on full path treating it as directory |
| `ampy get /sdcard/file.txt /tmp/file.txt` | DEVICE→LOCAL | Retrieves device file to local filesystem |

**ampy run output is unreliable on K230** — `stream_output=True` may return empty stdout due to MicroPython implementation differences. Use direct serial communication for capturing output, or write results to a file and `ampy get` the file.

## Serial Dead = Physical Reset Required

When serial returns `b''` consistently, the K230 device is dead. There is no software recovery. Physical reset (unplug USB, wait 5s, replug) is required.