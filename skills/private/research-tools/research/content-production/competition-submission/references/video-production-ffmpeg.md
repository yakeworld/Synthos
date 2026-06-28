# FFmpeg Video Production — Competition Demo Video

Produce a 6-10 minute MP4 demo video for competition submissions using FFmpeg + Pillow + edge-tts. This is the **recommended approach** (Scheme A) for all competition video production in this session.

## Recommended Toolchain

1. **Pillow** (Python) — Generate 1920×1080 scene images
2. **edge-tts** — Generate Chinese narration audio (free, high quality)
3. **FFmpeg** — Compose video from scene segments + narration

## Workflow

### Step 1: Generate Scene Images

```python
from PIL import Image, ImageDraw, ImageFont
import os

def get_font(size):
    for path in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]:
        try:
            return ImageFont.truetype(path, size)
        except:
            pass
    return ImageFont.load_default()

def generate_scene(output_path, title, content, subtitle, bottom_bar):
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), (10, 22, 40))  # Dark blue gradient
    draw = ImageDraw.Draw(img)
    
    draw.text((600, 150), title, fill="#00BCD4", font=get_font(36))
    y = 280
    for line in content.split("\n"):
        if line.strip():
            draw.text((width//2 - len(line)*8, y), line, fill="white", font=get_font(20))
            y += 35
    draw.text((width//2 - len(subtitle)*7, y), subtitle, fill="#AAAAAA", font=get_font(18))
    draw.rectangle([0, h-40, w, h], fill=(0, 100, 150))
    draw.text((width//2, h-25), bottom_bar, fill="white", font=get_font(16))
    
    img.save(output_path, "PNG")
```

**Key rules**:
- Use **Noto Sans CJK** or **Noto Serif CJK** fonts for Chinese text
- Background: dark blue gradient (#0A1628 → #1A3A5C)
- Size: 1920×1080 (1080p minimum)
- Scene count: 10-12 scenes for a 6-10 minute video (each scene ~50 seconds)

### Step 2: Generate Narration Audio

```bash
# Save narration text to file first
cat > narration.txt << 'EOF'
在医学研究领域，信息爆炸与科研效率瓶颈的矛盾日益突出...
（所有旁白文字逐段拼接）
EOF

# Generate audio using edge-tts (free, high quality)
edge-tts --text "$(cat narration.txt)" \
    --voice zh-CN-XiaoxiaoNeural \
    --rate +5% \
    --write-media narration.mp3
```

**Voice options**:
- `zh-CN-XiaoxiaoNeural` — Female, professional, recommended
- `zh-CN-YunxiNeural` — Male, professional
- `zh-CN-YunjianNeural` — Male, warm

**Rate**: `+5%` to `+10%` for better pacing (standard speech is ~180 words/min for Chinese)

### Step 3: Create Video Segments

Each scene should be a separate video file (50 seconds each):

```bash
for i in $(seq 1 10); do
    ffmpeg -y \
        -loop 1 \
        -i "scene_${i:03d}.png" \
        -t 50 \
        -c:v libx264 \
        -pix_fmt yuv420p \
        -vf scale=1920:1080 \
        "segments/scene_${i:03d}.mp4"
done
```

**Important**: Use `-loop 1` to repeat the single image for the full duration. Without `-loop 1`, ffmpeg treats each image as a single frame.

### Step 4: Concatenate Segments

```bash
# Create concat list
> concat.txt
for i in $(seq 1 10); do
    echo "file 'segments/scene_${i:03d}.mp4'" >> concat.txt
done

# Concatenate
ffmpeg -y -f concat -safe 0 -i concat.txt -c:v libx264 -pix_fmt yuv420p video_combined.mp4
```

### Step 5: Add Narration Audio

```bash
# Method that works: copy video, add audio with proper stream selection
ffmpeg -y \
    -i video_combined.mp4 \
    -i narration.mp3 \
    -map 0:v:0 \
    -map 1:a:0 \
    -c:v copy \
    -c:a aac \
    -b:a 192k \
    -movflags +faststart \
    final_video.mp4
```

If this fails, try re-encoding:
```bash
ffmpeg -y \
    -i video_combined.mp4 \
    -i narration.mp3 \
    -c:v libx264 \
    -c:a aac \
    -b:a 192k \
    -shortest \
    final_video.mp4
```

## Pitfalls

- **`-loop 1` is mandatory**: Without `-loop 1`, ffmpeg treats each image as a single frame (1 frame at framerate), producing a video that plays instantly. Always verify with `ffprobe` after segment creation.
- **FFmpeg glob in `-i` doesn't work**: `ffmpeg -i "scene_*.png"` will fail. Either use a concat list or pipe via `cat scene_*.png | ffmpeg -f image2pipe`.
- **Image2pipe pipe chain**: When using `cat scene_*.png | ffmpeg -f image2pipe`, the images must be in strict numerical order and the pipe may fail silently. Prefer the concat list approach.
- **Video duration mismatch**: If the video duration doesn't match the narration length, use `-shortest` to trim to the shorter stream, or adjust `-t` per segment.
- **Audio codec**: Use AAC (`-c:a aac`) for MP4 compatibility. MP3 audio files need re-encoding when added to MP4.
- **File naming**: Competition videos must be named exactly as the 智能体名称 (e.g., `Synthos—自主进化学术科研平台.mp4`). No personal names, no school names.
- **Chinese font availability**: Not all systems have Chinese fonts. Check with `fc-list :lang=zh` before starting. The Noto Sans/ Serif CJK fonts are available on most Linux systems at `/usr/share/fonts/opentype/noto/` or `/usr/share/fonts/truetype/noto/`.

## Quick Reference

| Step | Command | Output |
|------|---------|--------|
| Scene images | Python/Pillow | scene_001.png, scene_002.png, ... |
| Narration | edge-tts | narration.mp3 |
| Segments | ffmpeg (loop + t 50) | segments/scene_001.mp4, ... |
| Concat | ffmpeg concat | video_combined.mp4 |
| Final | ffmpeg map + copy | final_video.mp4 |

## Example Duration Calculation

- 10 scenes × 50 seconds = 500 seconds (8.3 minutes)
- 12 scenes × 50 seconds = 600 seconds (10 minutes)
- Narration: ~2000 Chinese characters at ~200 chars/min = ~10 minutes
- Use `-shortest` to trim to narration length if video is longer
