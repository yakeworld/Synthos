# Encoder FPS Test Results (K230 + GC2093)

## 1280×720 H264 @ 200Mbps
```
ENC 1280x720 200/3346ms FPS:59.8
```
- Encoder: H265 (official example default)
- Sensor: `Sensor()` no-args, gc2093_csi0

## 1920×1080 H264 @ default bitrate
```
1080p_H264 100/1665ms FPS:60.1
```
- Encoder: H264
- Measured via boot.py auto-run test

## 1280×720 H264 @ 200Mbps
Not directly measured but encoder pipeline throughput is independent of bitrate (hardware DMA). Expected: ~60 FPS.

## raw REPL test script (encoder FPS)

```python
from media.vencoder import *
from media.sensor import *
from media.media import *
import time, os, uctypes

def test(w,h,n):
    c=VENC_CHN_ID_0
    wa=(w+15)//16*16
    s=Sensor();s.reset()
    s.set_framesize(width=wa,height=h,alignment=12)
    s.set_pixformat(Sensor.YUV420SP)
    e=Encoder();e.SetOutBufs(c,8,wa,h)
    l=MediaManager.link(s.bind_info()['src'],(VIDEO_ENCODE_MOD_ID,VENC_DEV_ID,c))
    MediaManager.init()
    a=ChnAttrStr(e.PAYLOAD_TYPE_H265,e.H265_PROFILE_MAIN,wa,h)
    sd=StreamData()
    e.Create(c,a);e.Start(c);s.run()
    for _ in range(30):
        e.GetStream(c,sd);e.ReleaseStream(c,sd)
    t0=time.ticks_ms();fc=0
    while fc<n:
        e.GetStream(c,sd)
        for p in range(sd.pack_cnt):fc+=1
        e.ReleaseStream(c,sd)
    el=time.ticks_diff(time.ticks_ms(),t0)
    print('ENC %dx%d %d/%dms FPS:%.1f'%(w,h,fc,el,fc*1000/el))
    s.stop();del l;e.Stop(c);e.Destroy(c);MediaManager.deinit()

test(1280,720,200)
```
