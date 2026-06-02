# PPTX Slide-to-Video Workflow for Professional Demos

## Use Case

When creating demo videos for academic competitions, hackathons, or presentations
where the slides need to look genuinely professional (not basic bullets on white
background), and you want to convert them to video with narration.

## Why PPTX > Pillow for Slide Images

Using Pillow to draw slide backgrounds creates visibly amateur results:
- Flat solid color backgrounds
- No gradients, shadows, or depth
- Inconsistent typography rendering
- Font substitution issues in video players

PPTX (python-pptx) produces professional slides that convert cleanly to video:
- Real font rendering with proper CJK support (Noto Sans CJK SC)
- Consistent spacing and typography
- Proper text wrapping and sizing
- Clean PDF export (no font issues)
- Can be converted to high-res PNGs (4000x2250 at 300dpi)

## Complete Workflow

### 1. Create PPTX with python-pptx

Use the powerpoint skill for design guidance. Key decisions:

- **Font**: `Noto Sans CJK SC` for Chinese text (check with `fc-list :lang=zh`)
  Common paths: `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`
- **Background**: Dark navy `#0F172A` for professional look
- **Accent colors**: Blue `#3B82F6`, teal `#06B6D4`, purple `#8B5CF6`
- **Slide size**: Default (10" x 5.625") = 960 x 540 points at 96dpi
- **Layout**: Avoid center-aligned body text, left-align paragraphs
- **Padding**: 0.5" minimum margins, 0.3-0.5" between content blocks

### 2. Export to PDF

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
```

### 3. Convert to High-Res PNGs

```bash
pdftoppm -png -r 300 output.pdf slide
# Produces: slide-01.png, slide-02.png, etc. at 4000x2250 (300dpi)
```

### 4. Generate Video Segments

Each PNG becomes a video segment:

```bash
for i in $(seq 1 N); do
  ffmpeg -y -loop 1 -i slide-0${i}.png \
    -c:v libx264 -t 38.76 \
    -pix_fmt yuv420p -r 30 \
    -preset medium -crf 18 \
    -an scene_${i}.mp4
done
```

### 5. Convert PNGs → Video with FFmpeg

Each static image becomes a video segment (~38.77 seconds at 30fps, 1163 frames).

```bash
for i in scene_0*.mp4; do
  ffmpeg -y -i "$i" -c copy -f mpegts "tmp_$(basename $i .mp4).ts"
done

# Binary concat TS files (NOT ffmpeg concat protocol for MP4!)
cat tmp_scene_0*.ts > all_concatenated.ts

# Re-encode to MP4 (recalculates correct duration)
ffmpeg -y -i all_concatenated.ts -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p full_video.mp4
```

### 6. Convert Narration

```bash
# Generate Chinese narration with edge-tts
edge-tts --voice zh-CN-XiaoxiaoNeural \
  --text "你的旁白文本" \
  --write-media narration.mp3

# Convert to AAC for video
ffmpeg -i narration.mp3 -vn -c:a aac -b:a 192k -ar 44100 -ac 2 narration.aac
```

### 7. Final Synthesis

```bash
# If narration > video: loop video
ffmpeg -y -stream_loop -1 -i full_video.mp4 -i narration.aac \
  -c:v copy -c:a aac -b:a 192k -ar 44100 -ac 2 -shortest final.mp4

# If video > narration: trim with -t
ffmpeg -y -i full_video.mp4 -i narration.aac \
  -c:v copy -c:a aac -b:a 192k -ar 44100 -ac 2 -t <duration> final.mp4
```

## Common Pitfalls

1. **MP4 concat with `-c copy` silently drops frames** — when all scenes have
   `start_time=0`, FFmpeg's concat protocol may only keep the first N segments.
   Solution: Convert to TS first, binary concat, then re-encode to MP4.

2. **MP4→TS conversion with `-c copy` can drop data** — if scenes were encoded
   with `-preset ultrafast/fast` or are in QuickTime format, TS conversion may
   silently lose ~25% of data. Always re-encode with `-preset medium -crf 18`.

3. **Chinese fonts not found** — `fc-list :lang=zh` to check installed fonts.
   Common paths: `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`

4. **Text overflow on slides** — use `txt = p.add_run().text = "text"` with
   explicit font size and avoid center alignment. Use margins of 0.5" minimum.

5. **Video duration mismatch** — `-t <duration>` with `-c copy` may not work
   correctly. Use `-shortest` or re-encode video during synthesis.

6. **Audio/video sync** — convert audio to AAC 44100Hz stereo before combining.
   Always verify both stream durations match within 0.2s.

## Session Reference (2026-05-09)

Context: Generating demo video for 全球数智教育创新大赛 AI for Medicine track.
Synthos project, 11 slides, professional PPTX design.

Issues encountered and fixed:
- Slide 2 had "7维认知原子" typo (should be "6维")
- Video was 307s instead of 426s due to MP4 concat frame drop
- Root cause: all scenes had start_time=0, FFmpeg concat dropped 3 segments
- Fix: TS binary concat + re-encode MP4

Result: Final video `Synthos—自主进化学术科研平台.mp4` at 5334x3000, 30fps, 426s.
