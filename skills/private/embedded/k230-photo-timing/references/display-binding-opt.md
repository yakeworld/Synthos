# Display Binding Optimization — Official Pipeline vs photo.py

## Performance Comparison

| Metric | Official (Display-bound) | photo.py (no Display) |
|--------|-------------------------|-----------------------|
| snapshot() time | **21ms** | 26-33ms |
| Performance gain | **+22% faster** | Baseline |
| Pipeline type | Hardware (GDMA/DSP) | Pure software |
| Format (chn0) | YUV420SP | RGB565 |
| Display binding | Yes, LAYER_VIDEO1 | No |

## Key Finding: Display Binding Reduces snapshot() by 5-12ms

The official example (`examples/17-Sensor/camera_snapshot_and_save.py`) binds chn0 to Display layer with YUV420SP format. This enables the hardware pipeline (GDMA/DSP) for frame capture.

Our photo.py doesn't bind Display — it uses a pure software path. The difference is 21ms vs 26-33ms per snapshot — a 22% improvement.

## Official Pipeline Template

```python
from media.sensor import Sensor
from media.media import MediaManager
from media.display import Display

# Step 1: Default constructor (no params)
sensor = Sensor()
sensor.reset()

# Step 2: chn0 = YUV420SP for Display
sensor.set_framesize(width=320, height=240)
sensor.set_pixformat(Sensor.YUV420SP)

# Step 3: Bind to display (hardware pipeline)
bind_info = sensor.bind_info()
Display.bind_layer(**bind_info, layer=Display.LAYER_VIDEO1)
Display.init(Display.ST7701, to_ide=True, osd_num=2)

# Step 4: chn2 = RGB565 for saveable snapshots
sensor.set_framesize(width=320, height=240, chn=2)
sensor.set_pixformat(Sensor.RGB565, chn=2)

# Step 5: Start once (single run for all sensors)
sensor.run()
time.sleep_ms(200)

# Step 6: Snapshot from chn2 (supports save)
img = sensor.snapshot(chn=2)
img.save("/data/img.jpg")
```

## Constraints

### YUV420SP is the ONLY Display-supported format

If you try to bind any other format:
```
AssertionError: bind video layer only support format PIXEL_FORMAT_YUV_SEMIPLANAR_420
```

### YUV420SP cannot be saved

```python
img = sensor.snapshot()  # chn0, YUV420SP
img.save("/data/img.jpg")  # OSError: current format not support save function!
```

The workaround: use chn2 (RGB565/RGB888/RGBP888) for save operations.

### chn1 and chn2 are for snapshot+save

Official example configures:
- chn0: YUV420SP → for Display binding and video layer
- chn1: RGB888 (640x480) → for snapshot+save (optional)
- chn2: RGB565 (640x480) → for snapshot+save (optional)

For 320x240 photo capture, only chn0 (YUV420SP for Display) and chn2 (RGB565 for save) are needed.

### Multi-sensor rules

From `camera_dual_bind_hdmi.py`:
- Multiple sensors only need ONE `sensor.run()` call
- Multiple sensors all need individual `sensor.stop()` calls (or `Sensor.deinit()`)
- Resolution 1920x1080@30fps recommended for multi-sensor setups
- Other resolutions may cause display artifacts