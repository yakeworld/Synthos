---
name: competition-video-production
description: "Produce professional demo videos for academic competitions, grants, and pitch events. Covers: PPTX→PNG→MP4 pipeline, narration sync, quality benchmarks (30fps 1080P, ~125kbps), visual design with dark themes and data visualization, and compliance with competition rules (no personal info in videos, anonymous material requirements). User context: medical researcher at Wenzhou hospital competing in China's global digital education innovation contest (AI for Medicine track). Prefers PPTX source over Pillow for image quality, uses Chinese narration via Edge-TTS, targets 6-10 minute MP4 at 1080P for submission to platforms like MeedTAC (chaoxing.com). Key pattern: generate PPTX with python-pptx using professional color palettes (dark navy + accent cards), export PNG at 300 DPI, convert to video segments, concatenate, then merge with narration — always verify video+audio stream durations match within 0.1 seconds."
license: CC BY-NC-SA 4.0
---

# Competition Video Production

## When to use

Use this when the user needs a professional demo video for:
- Academic/competition submissions (Chinese national/international contests)
- Grant proposals (NSFC, 973, etc.)
- Product pitch or investor demo
- Any presentation requiring a polished video with narration

## Entry Gate: Determine Source Material

Before starting any pipeline step, check what source material already exists:

1. **Existing PPTX** — If the user already has a .pptx with slides, USE IT. Do NOT regenerate from scratch.
2. **Images only** — If images exist, skip to image-to-video.
3. **Nothing** — Generate PPTX from scratch (see Step 1 below).

## Pre-Production: Data Verification (⛔ CRITICAL)

**Before writing a single line of narration or generating any content, verify ALL numbers against source project files.** This is the most common failure mode detected across multiple sessions.

### The rule
Every number that appears in the video (narration, slide text, on-screen graphics) must be **traceable to a project data file** — evolution-state.json, evolution-log.md, skill_tree.json, the building manual, etc. If you cannot point to the file and line that contains the number, do NOT use it.

### What to remove
- Made-up market sizes (e.g., "我国ADHD儿童约2000万")
- Fabricated hardware specs (e.g., "60fps", "30Hz", "<0.5°精度")
- Unverified benchmarks (e.g., "IoU > 0.92", "响应时间 < 10ms")
- Invented latency/performance claims (e.g., "端到端延迟 < 10ms")
- Unconfirmed numbers like "确诊率不足30%", "年门诊量5000万"

### What to use instead
| Instead of... | Use... |
|:--------------|:-------|
| "0.1°精度" | "高精度" |
| "60fps/120fps" | "高帧率" |
| "IoU > 0.92" | "分割精度经实验验证" |
| "端到端延迟 < 10ms" | "实时处理" |
| Market size numbers | Qualitative description of the clinical need |

### Acceptable sources
✅ evolution-state.json — evolution_count, overall_score, benchmark_score, structural_avg
✅ evolution-log.md — cycle count, degradation status, API health
✅ skill_tree.json — total_skills, core_atoms, extended_skills
✅ skill_registry.json — specific skill versions and statuses
✅ 智能体建设说明书 — teaching sources (73), literature projects (24), efficiency ratios
✅ README.md — architecture description, version number
❌ Numbers you "know from general knowledge" or "commonly cited figures"
❌ Numbers that seem "reasonable" but you can't cite a project file for
❌ Numbers from external sources unless the user explicitly provided them

### Verification checklist before rendering
```markdown
□ Every number in the narration script has a file:line citation in project data
□ Every number on every slide PNG matches a project data file
□ No fabricated market sizes, hardware specs, or performance claims
□ If uncertain → use qualitative language, not invented numbers
```

When the user says "数字不严谨" or "不要虚构", you used numbers without source verification. Immediately remove all unverifiable numbers and replace with qualitative descriptions. Then re-record the affected narration segments.

When using an existing PPTX:
```bash
# Convert to PDF (headless)
libreoffice --headless --convert-to pdf --outdir <work_dir> presentation.pptx

# Extract as PNGs at 150-200 DPI (sweet spot for quality vs file size)
pdftoppm -png -r 150 slides.pdf <work_dir>/slide
```
Result: ~2000×1125 PNGs (16:9, above 720P minimum). 300 DPI yields ~4000×2250 but is overkill for video.

## Pipeline — Two Paths

### Path A: Full Production (no existing PPTX, need to generate everything)

When the user does NOT have pre-made slides, generate them with `python-pptx`:

**Step 1A: Generate PPTX Slides**

Use `python-pptx` to create slides. Key patterns:

1. **Dark theme** for professional look — `RGBColor(0x0F, 0x17, 0x2A)` as background
2. **Accent colors** per section — blue for tech, green for results, orange for warnings
3. **Card-based layout** — rounded rectangles with title, description, accent bar
4. **Data visualization** — stat callouts, comparison tables, progress bars
5. **DAG/flow diagrams** — for architecture overviews with arrow connectors
6. **Numbered badges** — colored circles for sequential steps

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Inches(13.333)  # 16:9
prs.slide_height = Inches(7.5)

# Dark background
background = slide.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = RGBColor(0x0F, 0x17, 0x2A)

# Card with accent bar
card = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height,
    fill_color=RGBColor(0x1E, 0x2A, 0x4A),
    line_color=RGBColor(0x2A, 0x3A, 0x5C)
)
```

**Design rules:**
- Every slide needs visual elements (cards, icons, charts) — no text-only slides
- Vary layouts across slides (don't repeat same card pattern)
- Use `line_spacing` on text frames to prevent overflow
- Add `font_name="Calibri"` consistently
- Include both Chinese and English text where relevant (bilingual competition material)

Then continue with Step 2A (export images) through Step 8A (verify).

### Path B: Fast Track — Existing PPTX to Video

When the user already has a good PPTX, use this lighter pipeline. This was the approach used in the 2026-05-13 Synthos competition session.

**Step 1B: Export slides as images**
```bash
libreoffice --headless --convert-to pdf --outdir frames_dir source.pptx
pdftoppm -png -r 150 frames_dir/slides.pdf frames_dir/slide
```

**Step 2B: Write concat file with timed durations**
Each slide gets a duration (in seconds) matching its narration segment length.

```python
# concat format: file <path>\nduration <sec>
with open('concat.txt', 'w') as f:
    for slide_idx, duration, _ in segments:
        f.write(f"file 'slide-{slide_idx+1:02d}.png'\n")
        f.write(f"duration {duration}\n")
```

**Step 3B: Generate narration with Edge-TTS**
```python
import asyncio
from edge_tts import Communicate

async def gen():
    communicate = Communicate(full_text,
        "zh-CN-XiaoxiaoNeural",
        rate="+0%", volume="+0%", pitch="+0Hz")
    await communicate.save("narration.mp3")

asyncio.run(gen())
```

⚠️ **Edge-TTS rate adjustment for duration targeting**: Edge-TTS reads Chinese at roughly 60 字/分钟 at 0% rate. When you estimate a total narration time from text length, the actual TTS duration can be significantly shorter (by 30-40%) because TTS reads faster than spoken speech. To hit a specific duration target:

   1. **Write the script** estimating ~60 字/分钟 for Chinese narration
   2. **Generate a first pass** at rate="+0%" and measure: `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 output.mp3`
   3. **If too short**, regenerate at rate="-N%" where N = (target_duration / actual_duration - 1) * 100
      - Example: target 360s (6min), got 292s at 0% → need 360/292 = 1.23x longer → rate ≈ "-5%" to "-8%"
   4. **If too long**, speed up with rate="+N%"
   5. **Adjust, regenerate, re-measure** — one iteration is usually sufficient (±2% accuracy)
   6. **Edge-TTS rate limits**: rate can go from "-50%" to "+50%". Beyond -20% the voice starts sounding unnatural.
   
   The per-slide approach automatically handles this: generate 10 short audio files, measure each exactly, and compose video segments with pinpoint-accurate durations.

**Step 4B: Compose video — use `-t` not `-shortest`**
```bash
DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 narration.mp3)

# FIRST PASS: create video from images using concat demuxer
ffmpeg -y -f concat -safe 0 -i concat.txt -c:v libx264 -preset medium \
  -crf 18 -pix_fmt yuv420p -s 1920x1080 raw_video.mp4

# SECOND PASS: trim to exact narration duration, overlay audio
ffmpeg -y -i raw_video.mp4 -i narration.mp3 \
  -c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 -t "$DUR" \
  final_video.mp4
```

⚠️ **CRITICAL: Do NOT use `-shortest` in the first-pass composition**. The concat demuxer declares `Duration: N/A` for its output stream. When combined with `-shortest`, FFmpeg cannot determine which stream is actually shorter — it defaults to the video's unlimited duration. The result is a video much longer than the audio, with silence after the narration ends. Always use `-t DURATION` to explicitly trim to the narration length in a separate second pass.

**Verification:**
```bash
# Must match within 0.1s
ffprobe -v error -select_streams v:0 -show_entries stream=duration final_video.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=duration final_video.mp4
```

### Step 5B (Optional): Apply zoom/pan effect
Add subtle Ken Burns effect to each slide to make static images feel more dynamic:
```bash
ffmpeg -y -loop 1 -i slide.png -c:v libx264 -t 45 -pix_fmt yuv420p \
  -vf "scale=2560:1440,zoompan=z='min(zoom+0.001,1.05)':d=25*45:fps=25" \
  scene.mp4
```

Then use the TS-concat approach from Path A Step 6 to join zoomed scenes.

### Path A Continuation: Steps 2A–8A

These steps apply after generating the PPTX (Step 1A). They use per-scene MP4 files and the TS-concat approach described below.

**Step 2A: Export PNG at High Resolution**

```bash
# Convert PPTX → PDF via LibreOffice
libreoffice --headless --convert-to pdf --outdir <output_dir> presentation.pptx

# Export PNG at 300 DPI for maximum quality
pdftoppm -png -r 300 presentation.pdf slide_png
```

Result: ~4000×2250 PNG files (200-400KB each, lossless).

**Step 3A: Convert PNG to Video Segments**

Each slide becomes a video segment (typically 40-50 seconds per scene):

```bash
ffmpeg -y -loop 1 -i slide_png-01.png \
  -c:v libx264 -t 42.64 \
  -pix_fmt yuv420p -r 30 \
  -preset medium -crf 16 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" \
  -an \
  scene_01.mp4
```

- CRF 16 for good quality (CRF 14 = maximum, CRF 18 = smaller file)
- 30fps for smooth playback
- Scale to 1920×1080 with padding (center-align)
- Each segment duration matches the narration segment length

**Step 4A: Generate Narration**

```bash
# Chinese narration with Edge-TTS
edge-tts --text "你的旁白文本" \
  --voice zh-CN-XiaoxiaoNeural \
  --rate +10% \
  -f narration.mp3
```

Alternative: record voice directly or use another TTS engine.

**Step 5A: Convert Narration to AAC**

```bash
ffmpeg -y -i narration.mp3 \
  -vn -c:a aac -b:a 192k -ar 44100 -ac 2 \
  narration.aac
```

**Step 6A: Concatenate Video Segments**

**⚠️ CRITICAL: MP4 concat with `-c copy` silently drops frames (v1.2)**

When all scene MP4s share `start_time=0.000000`, FFmpeg's `-f concat -c copy`
produces output with a shorter duration than expected — it silently discards
overlapping PTS packets. Using `-t` on this broken output truncates audio/video
to the wrong shorter duration.

```bash
# CORRECT: Convert to TS, binary concat, then re-encode to MP4
for i in $(seq 1 10); do
  ffmpeg -y -i scene_$(printf '%02d' $i).mp4 -c copy -f mpegts \
    "tmp_scene_$(printf '%02d' $i).ts" -nostdin
done

# Binary concat (works correctly for TS)
cat tmp_scene_0*.ts > all_concatenated.ts

# Re-encode to MP4 (recalculates correct duration)
ffmpeg -y -i all_concatenated.ts -c:v libx264 -preset medium -crf 18 \
  -pix_fmt yuv420p full_video.mp4
```

**Verify duration after concat:**
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 full_video.mp4
# Should equal: num_scenes × duration_per_scene
```

**Step 7A: Final Synthesis**

```bash
NARR_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 narration.mp3)

ffmpeg -y -i full_video.mp4 -i narration.aac \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -c:a aac -b:a 192k -ar 44100 -ac 2 \
  -t "$NARR_DUR" \
  final_video.mp4
```

**Critical: Do NOT use `-shortest`** — it truncates to the shorter stream, causing sync issues. Use `-t` to trim video to narration duration instead.

**Alternative:** If video is shorter than narration, loop the video:
```bash
ffmpeg -y -stream_loop -1 -i full_video.mp4 -i narration.aac \
  -c:v copy -c:a aac -b:a 192k -ar 44100 -ac 2 -shortest final_video.mp4
```

**Step 8A: Verify**

```bash
# Check streams match
ffprobe -v error -select_streams v:0 -show_entries stream=duration final.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=duration final.mp4
# Should match within 0.1 seconds

# Check quality
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,bit_rate -of default=noprint_wrappers=1 final.mp4
# Target: 1920×1080, 25-30fps, 100-150kbps
```

## Quality Benchmarks

| Metric | Target |
|--------|--------|
| Resolution | 1920×1080 (minimum) |
| Frame rate | 25-30 fps |
| Video bitrate | 100-150 kbps (static content) / 2000-5000 kbps (motion) |
| Duration | 6-10 minutes for competition submissions |
| Audio | AAC 192k 44100Hz stereo |
| Audio+Video sync | Within 0.1 seconds |
| File size | 15-30 MB for 7-min video |

## Competition Compliance

- ❌ **No personal names** in video content or cover (except official forms)
- ❌ **No institution names** (school, department) in video
- ❌ **No real patient data** — use only anonymized/derived data
- ✅ Use generic titles, institution-neutral branding
- ✅ Video must be self-contained with narration

## Common Pitfalls

### Narration-Slide Alignment

1. **Don't use a single narration file with fixed slide durations** — the TTS engine reads at a variable pace, so your estimated durations will drift. The result is narration describing slide N while slide N-1 is still showing. This was the main failure mode in the 2026-05-13 Synthos session.

   **Fix: Generate per-slide audio, measure each, then compose per-segment videos.**
   ```python
   # For each slide, generate a separate audio file
   for i, text in enumerate(slide_narrations):
       communicate = Communicate(text, "zh-CN-XiaoxiaoNeural", rate="-3%")
       await communicate.save(f"slide_{i+1:02d}.mp3")
       # Measure exact duration
       dur = float(subprocess.run(["ffprobe", ...], ...))
   
   # Then compose a video segment per slide with EXACT duration matching
   for i, dur in enumerate(durations):
       ffmpeg -y -loop 1 -i slide_{i+1}.png -i audio_{i+1}.mp3 \
         -t {dur:.3f} -shortest segment_{i+1}.mp4
   
   # Finally concatenate all segments
   ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy final.mp4
   ```

2. **Narration must DESCRIBE exactly what the slide shows** — never add data, statistics, or claims in the narration that don't appear on the corresponding slide. The user will notice the mismatch and ask for a remake. Verification steps:
   - Extract all numbers from each slide's text BEFORE writing narration
   - Every number in the narration must be visually verifiable on the current slide
   - If slide 3 shows "6X文献综述效率提升" but the narration mentions "10X检索效率提升", that's a misalignment even if both numbers are factually correct
   - After composing, do a final scan: play 5 seconds from each segment to confirm the visual matches the audio

3. **Efficiency comparison data must match slide labels exactly** — common confusion point in this user's Synthos project: there are TWO different metrics that look similar:
   - **Literature SEARCH** (文献检索): manual = hours, Synthos = minutes (10x improvement)
   - **Literature REVIEW** (文献综述撰写): manual = 2-3 weeks, Synthos = 3-5 days (4-6x improvement)
   - The slide that shows "传统手动检索：数小时 / Synthos 自动化检索：数分钟" is the SEARCH metric
   - The slide that shows "6X" is the REVIEW (综述) metric
   - Never mix these up in narration. Verify by reading the exact text on each PNG image after export.
   - **User correction**: if the user says "效率对比信息不正确", you likely mixed SEARCH and REVIEW metrics. Fix the narration, not the slide data.
   
4. **All narration numbers must match slide numbers exactly** — if slide 3 shows "6X文献综述效率提升 / 85%+ / -40%" the narration must say exactly those numbers. Don't add extra data like "检索提升10X" that only exists in the construction manual but not on the slide. Every number spoken must be visually verifiable on the current slide.

5. **ALL numbers must be rigorous and verifiable (用户偏好: '所有数字必须严谨，不要虚构')** — never fabricate quantitative claims in narration, slide content, or written materials:
   - If you don't know the exact number, use a qualitative description instead (e.g., "高精度" instead of "0.1°精度")
   - Remove: made-up market sizes ("我国ADHD儿童约2000万"), fabricated hardware specs ("60fps", "<0.5°精度"), unverified benchmarks ("IoU > 0.92"), invented latency claims ("<10ms端到端延迟")
   - Replace with: "高空间分辨率" instead of "0.1°精度", "高" instead of "60fps/120fps", "实验验证" instead of specific metric
   - Acceptable: numbers from the project's actual data files (evolution-state.json, evolution-log.md, skill_tree.json, building manual)
   - Always check: "Have I seen this number in a project file, or did I invent it?"

### `-shortest` pitfalls

1. **`-shortest` truncation**: Always use `-t DURATION` instead of `-shortest` for final synthesis. See the "Best Practice" below for the two-pass approach.

2. **concat demuxer + `-shortest` is broken**: When using `-f concat` with image files, the demuxer declares `Duration: N/A` for the video stream. Combining this with `-shortest` means FFmpeg cannot determine which stream is actually shorter — it defaults to the video's unlimited duration. The result is a video much longer than the audio, with silence after the narration ends. **Always use a two-pass approach instead:**
   ```bash
   # Pass 1: create video with concat
   ffmpeg -y -f concat -safe 0 -i concat.txt -c:v libx264 ... raw_video.mp4
   # Pass 2: trim to exact narration duration
   DUR=$(ffprobe -v error -show_entries format=duration ... narration.mp3)
   ffmpeg -y -i raw_video.mp4 -i narration.mp3 -map 0:v:0 -map 1:a:0 -t "$DUR" final.mp4
   ```

### PPTX text editing (python-pptx)

3. **PPTX text in \u000b-separated multi-line paragraphs**: When a PPTX text box has two lines in one paragraph separated by a line break, python-pptx stores them as multiple run elements. Setting `run.text = ''` on each run leaves the paragraph empty. To fix:

   ```python
   from lxml import etree
   A_NS = 'http://schemas.openxmlformats.org/drawingml/2006/main'
   
   for run in para.runs:
       run.text = ''
   runs[0].text = '第一行'
   
   br = etree.SubElement(para._p, f'{{{A_NS}}}br')
   para._p.remove(br)
   para._p.insert(list(para._p).index(runs[0]) + 1, br)
   
   for i in range(1, len(runs)):
       txt = runs[i].find(f'{{{A_NS}}}t')
       if txt is not None:
           txt.text = '第二行'
           break
   ```

4. **Visual verification after PPTX text edits**: After modifying a PPTX, `para.text` may show correct text but visual rendering may differ. Always re-export to PDF and check: `pdftotext -f N -l N slides.pdf - | grep keyword`

### Other pitfalls

5. **`-shortest` truncation**: Always use `-t DURATION` instead of `-shortest` for final synthesis
2. **Low bitrate on static images**: Single-image video segments naturally have low bitrate. This is expected and fine — CRF controls perceived quality, not absolute bitrate
3. **MP4 concatenation**: Cannot use `cat` to join MP4 files (each has its own moov box). Use ffmpeg concat protocol with .ts or .txt file
4. **Frame rate mismatch**: Ensure all segments use the same frame rate before concatenation
5. **PNG vs JPEG**: Always use PNG for intermediate export — JPEG at 150 DPI loses too much detail for text-heavy slides
6. **Narration duration**: Get narration duration BEFORE final synthesis and use it as the trim target
7. **Font rendering**: Use `font_name="Calibri"` for broad compatibility; check Chinese fonts with `fc-list :lang=zh`

## Script Templates

See `scripts/` directory for reusable scripts:
- `generate_pptx_slides.py` — PPTX creation template
- `generate_video_pipeline.py` — Full pipeline automation
- `verify_sync.py` — Audio/video sync verification

## References

See `references/` for project-specific notes, including:
- `references/ffmpeg-video-audio-sync.md` — FFmpeg sync troubleshooting, MP4→TS concatenation, and stream trimming (absorbed from ffmpeg-video-audio-sync skill)
- `references/gen_professional_video.py` — Reusable professional video generation script (absorbed from ffmpeg-video-audio-sync skill)
- `references/mp4-ts-conversion-data-loss.md` — Data loss case study and fix for MP4→TS conversion
- `references/mp4-ts-data-loss-case-study.md` — Full case study with timeline
