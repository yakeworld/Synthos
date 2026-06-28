# Per-Slide Narration Alignment Pattern

## Problem

When producing a competition demo video from PPTX slides + Edge-TTS narration, the naive approach (one big narration file + fixed slide durations) causes the visual and audio to drift out of sync. The narration describes slide N while slide N-1 is still showing.

## Solution: Generate per-slide audio, then compose per-segment videos

### Step 1: Define slide narrations

```python
slides = [
    "Narration for slide 1...",
    "Narration for slide 2...",
    # ...
]
```

**CRITICAL: Each narration must describe exactly what the slide shows.** Extract all numbers from the slide PNG BEFORE writing narration. Every number spoken must be visually verifiable on the current slide. If slide 8 shows "6X / 85%+ / -40%", the narration must say exactly those numbers — not "4-6倍" and not "检索提升10X".

### Step 2: Generate per-slide audio

```python
import asyncio
from edge_tts import Communicate
import subprocess

async def gen_all():
    for i, text in enumerate(slides):
        out = f"audio_chunks/slide_{i+1:02d}.mp3"
        communicate = Communicate(text, "zh-CN-XiaoxiaoNeural",
                                  rate="-3%", volume="+0%", pitch="+0Hz")
        await communicate.save(out)
        dur = float(subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", out
        ], capture_output=True, text=True).stdout.strip())
        print(f"Slide {i+1}: {dur:.1f}s")

asyncio.run(gen_all())
```

**Total duration target**: 6-10 minutes for competition submissions. Use rate="-3%" for Chinese narration (typically produces 6:00-6:30 for a full 10-slide script).

### Step 3: Compose per-segment videos with exact durations

```bash
for i in $(seq 1 10); do
  idx=$(printf '%02d' $i)
  DUR=$(ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 "audio_chunks/slide_${idx}.mp3")
  
  ffmpeg -y -loglevel error \
    -loop 1 -i "frames/slide-${idx}.png" \
    -i "audio_chunks/slide_${idx}.mp3" \
    -c:v libx264 -preset fast -crf 20 \
    -c:a aac -b:a 192k \
    -pix_fmt yuv420p -s 1920x1080 \
    -t "${DUR}" -shortest \
    "segment_${idx}.mp4"
done
```

### Step 4: Concatenate segments

```bash
# Write concat file
for i in $(seq 1 10); do
  echo "file 'segment_$(printf '%02d' $i).mp4'" >> concat_list.txt
done

ffmpeg -y -f concat -safe 0 -i concat_list.txt \
  -c copy -movflags +faststart final_video.mp4

# Clean up
rm segment_*.mp4 concat_list.txt
```

## Data Integrity Requirements

Every number in the narration must be visually verifiable on the corresponding slide:

1. **Before writing narration**: export each slide as PNG, open it, and write down every number visible
2. **Narration numbers must be a subset of slide numbers** — don't add numbers that aren't on the slide
3. **Don't confuse SEARCH vs REVIEW metrics**:
   - SEARCH (检索): minutes vs hours (if slide says "数分钟/数小时")
   - REVIEW (综述): days vs weeks (if slide says "6X" or "2-3周/3-5天")
4. **If the slide text changes (PPTX edit)**, re-export and re-verify before regenerating narration
5. **Never fabricate numbers** — if data isn't on the slide, don't speak it. Use descriptive language instead.

## Troubleshooting

| Symptom | Cause | Fix |
|:--------|:------|:-----|
| Video longer than audio with silence at end | Used `-shortest` with concat demuxer | Use `-t DURATION` two-pass approach |
| Narration describes slide N while slide N-1 shows | Fixed durations don't match actual TTS pace | Use per-slide audio → measure → compose |
| User says "效率对比信息不正确" | Mixed SEARCH and REVIEW metrics | Check what the slide actually shows |
| User says "数字不严谨" | Fabricated or unverified number used | Remove it, use qualitative language |

## Key Numbers from 2026-05-13 Session

| Slide | Content | Duration |
|:-----:|:--------|:--------:|
| 1 | Opening: Synthos background, problems | 39.2s |
| 2 | Architecture: 6 atoms + router | 64.4s |
| 3 | Knowledge Acquisition demo (4 DBs) | 37.6s |
| 4 | Association & Hypothesis | 31.6s |
| 5 | Teaching scenario (AIGC) | 46.4s |
| 6 | CRISP-DM mapping | 33.9s |
| 7 | Evolution engine + dashboard | 38.7s |
| 8 | Quantified results (6X/85%/-40%) | 34.8s |
| 9 | 5 innovation points | 41.9s |
| 10 | Closing + open source | 26.1s |
| **Total** | | **394.5s (6:34)** |

## Output specs

| Metric | Value |
|--------|-------|
| Resolution | 1920×1080 |
| Format | MP4 (H.264 High + AAC LC) |
| Video params | preset=fast, crf=20 |
| Audio params | aac, 192k, 24000Hz mono |
| Total size | ~8.4 MB for 6:34 video |
