"""录像功能测试 - 直接通过 raw REPL 执行"""
import time
from config import get_video_config, video_fps
import state
import video as video_module

print("=== 录像功能测试开始 ===")

# Step 1: 检查录像配置
print("1. 录像配置:")
config = get_video_config()
print(f"   resolution: {config['video_width']}x{config['video_height']}")
print(f"   fps: {config['video_fps']}")
print(f"   bit_rate: {config['bit_rate']}")
print(f"   gop_len: {config['gop_len']}")
print(f"   record_time: {config['record_time']}")

# Step 2: 启动录像模式
print("\n2. 启动录像...")
try:
    result = video_module.video_mode_start()
    print(f"   video_mode_start result: {result}")
except Exception as e:
    print(f"   ERROR: {e}")
    import sys
    sys.print_exception(e)

# Step 3: 录制 30 帧
print("\n3. 录制 30 帧...")
NUM_FRAMES = 30
start_time = time.ticks_ms()
frame_count = 0

try:
    for i in range(NUM_FRAMES):
        frame_result = video_module.video_mode_record_frame()
        if frame_result:
            frame_count += 1
        else:
            print(f"   Frame {i+1}: FAILED")
            break
        if i % 10 == 9:
            print(f"   Progress: {i+1}/{NUM_FRAMES} frames")
except Exception as e:
    print(f"   Recording ERROR: {e}")
    import sys
    sys.print_exception(e)

elapsed = time.ticks_ms() - start_time
fps = frame_count / (elapsed / 1000.0) if elapsed > 0 else 0

print(f"   Completed: {frame_count}/{NUM_FRAMES} frames")
print(f"   Time: {elapsed}ms")
print(f"   FPS: {fps:.1f}")

# Step 4: 停止录像
print("\n4. 停止录像...")
try:
    video_module.video_mode_stop()
    print("   video_mode_stop: OK")
except Exception as e:
    print(f"   ERROR: {e}")

# Step 5: 检查输出文件
print("\n5. 检查输出文件:")
import os
try:
    video_files = os.listdir('/data')
    for f in sorted(video_files):
        if 'video' in f.lower() or f.endswith('.mp4'):
            path = '/data/' + f
            try:
                size = os.stat(path)[6]
                print(f"   {f}: {size} bytes")
            except:
                print(f"   {f}: <error reading size>")
except Exception as e:
    print(f"   ERROR: {e}")

# Step 6: 检查 H264 编码器状态
print("\n6. H264 编码器状态:")
print(f"   encoder: {state.encoder}")
print(f"   venc_chn: {state.venc_chn}")
print(f"   video_track_handle: {state.video_track_handle}")
print(f"   media_link: {state.media_link}")

print("\n=== 录像功能测试完成 ===")
