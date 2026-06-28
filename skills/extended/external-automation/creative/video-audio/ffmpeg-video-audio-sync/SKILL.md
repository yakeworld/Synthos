---

name: ffmpeg-video-audio-sync
description: Debug and fix FFmpeg video-audio synchronization issues including duration
author: Synthos
license: MIT
version: 1.2
license: MIT
  mismatches, sample rate problems, and MP4 concatenation pitfalls. Covers ffprobe
  diagnostics, stream trimming, audio conversion, and verification of synced output.
allowed-tools:
- terminal
- read_file
- write_file
- search_files
metadata:
  synthos:
    signature: 'video_path: str -> synced_path: str'
    related_skills:
    - academic-diagram
    - architecture-diagram
    - comfyui
    - excalidraw
    - figure-generation


---


## IO_CONTRACT

- **input**: `video_file: str, audio_file: str` — 用户请求描述、上下文信息
- **output**: `synced_output: str — 音视频同步文件`

> 对应原则：P2（机械原子暴露输入输出规范）




# FFmpeg Video-Audio Sync Troubleshooting

## Quick Reference

When video and audio don't sync in FFmpeg composites, check these three things first:

### 1. Duration Mismatch (Most Common)

**Symptom:** `-shortest` cuts video but leaves audio, or vice versa.

```
# WRONG — -shortest only preserves the SHORTER stream
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a copy -shortest out.mp4
# If video=500s, audio=426s → output is 426s of video (trailing frames dropped)

# RIGHT — explicitly trim the longer one BEFORE combining
ffmpeg -i video.mp4 -t 426.4 -c:v libx264 trimmed.mp4
ffmpeg -i trimmed.mp4 -i audio.mp3 -c:v copy -c:a copy -shortest out.mp4
```

**Verify before and after:**
```bash
ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 out.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 out.mp4
```

### 2. Audio Sample Rate Mismatch

**Symptom:** FFmpeg complains about sample rate, or audio/video drift over time.

```
# Check source audio
ffprobe -v error -show_entries stream=sample_rate,channel_layout,channels -of default=noprint_wrappers=1:nokey=1 audio.mp3

# Convert to standard before combining
ffmpeg -i audio.mp3 -vn -c:a aac -b:a 192k -ar 44100 -ac 2 clean.aac
```

Standard output: AAC, 44100Hz, stereo, 192kbps.

### 3. MP4 Concatenation Pitfall

`cat` does NOT work on MP4 files (moov box issue). Use:

```bash
# Method 1: ffmpeg concat protocol (requires ts intermediate)
for i in scene_0*.mp4; do
  ffmpeg -y -i "$i" -c copy -f mpegts "tmp_$(basename "$i" .mp4).ts" -nostdin
done

# Create concat list
for i in tmp_*.ts; do echo "file '$i'" >> concat_input.txt; done

ffmpeg -y -f concat -safe 0 -i concat_input.txt -c:v libx264 -preset fast -pix_fmt yuv420p -an concat.mp4
```

**⚠️ Critical: MP4 concat with `-c copy` silently drops frames (v1.2)**

When MP4 scenes all have `start_time=0.000000` and `duration=X`, FFmpeg's
`-f concat -c copy` may only output the **first N segments** (not all), producing
a video whose `ffprobe` duration is shorter than expected. This is because all
segments share the same PTS origin (0), causing frame collision in the muxer.

**Symptom:**
- Each scene reports 38.77s individually → total should be N × 38.77s
- After concat with `-c copy`, ffprobe reports ~311s for 11 scenes (only 8 segments)
- `-t <duration>` then trims audio/video to the **wrong** shorter duration
- No FFmpeg error is emitted — it appears to succeed silently

**Debug:**
```bash
# Check each scene's start_time and duration
for i in scene_0*.mp4; do
  ffprobe -v error -show_entries stream=start_time,duration,nb_frames -of json "$i" | grep -E '"start_time"|"duration"|"nb_frames"'
done
# If all have "start_time": "0.000000" → concat with copy is UNSAFE

# Check concat output
ffprobe -v error -show_entries stream=nb_frames -of json concat.mp4
# Compare total scene frames vs concat frames
# If concat has fewer frames, the concat silently dropped segments
```

**Fix — Binary concatenation of TS files:**
```bash
# Step 1: Convert all MP4s to TS (no re-encoding, preserves all frames)
for i in scene_0*.mp4; do
  ffmpeg -y -i "$i" -c copy -f mpegts "tmp_$(basename "$i" .mp4).ts"
done

# Step 2: Binary concatenate (cat) all TS files
cat tmp_scene_0*.ts > all_concatenated.ts

# Step 3: Convert back to MP4 with re-encoding
ffmpeg -y -i all_concatenated.ts -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p final.mp4

# Step 4: Verify the re-encoded MP4 has the correct total duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 final.mp4
# Should now equal sum of all scene durations
```

**Alternative: Use `-stream_loop -1` with `-shortest`**
If you want video to fill narration duration:
```bash
ffmpeg -y -stream_loop -1 -i concat.mp4 -i narration.aac \
  -c:v copy -c:a aac -b:a 192k -ar 44100 -ac 2 -shortest out.mp4
```
This loops the video until narration ends, avoiding duration mismatch entirely.

## Debugging Checklist

1. Check video duration: `ffprobe -v error -show_entries format=duration -of ... video.mp4`
2. Check audio duration: `ffprobe -v error -show_entries format=duration -of ... audio.mp3`
3. If durations differ → trim longer one with `-t` BEFORE combining
4. Check audio format: `ffprobe -show_entries stream=sample_rate,codec_name -of ...`
5. If non-standard → convert to AAC 44100Hz stereo before combining
6. If using MP4s as sources → convert to ts first, then concat
7. Verify final: compare v:0 and a:0 stream durations (difference <0.2s is acceptable)

## MP4→TS Conversion Data Loss

See `references/mp4-ts-data-loss-case-study.md` for the full case study with timeline and verification steps.

**Root Cause:** MP4 scenes encoded with `-preset ultrafast` or `-preset fast` produce
compressed bitstreams where the TS container conversion (`-c copy`) can silently drop
significant data. Observed loss: 43.8MB → 32.9MB (25% data loss). The concat then
produces a video with only 8 of 11 scenes, ffprobe reports ~311s instead of 426s, and
all downstream operations (trimming, audio sync) operate on wrong durations.

**Fix: Always use `-preset medium` or higher when encoding source MP4 scenes:**
```bash
# WRONG — fast/ultrafast can cause data loss during TS conversion
ffmpeg -loop 1 -i slide.png -c:v libx264 -t 38.76 -preset ultrafast -an scene.mp4

# CORRECT — medium preset preserves all data for reliable TS conversion
ffmpeg -loop 1 -i slide.png -c:v libx264 -t 38.76 -preset medium -crf 18 -an scene.mp4

# Alternative: veryfast is also acceptable
ffmpeg -loop 1 -i slide.png -c:v libx264 -t 38.76 -preset veryfast -crf 20 -an scene.mp4
```

**Pitfall chain:** If you use `-preset ultrafast/fast` for the source MP4 → TS conversion drops 25% of data → concat produces wrong duration → `-t DURATION` trims audio to wrong value → final video is shorter than narration.

**Always verify scene duration before concat:**
```bash
for i in scene_0*.mp4; do
  ffprobe -v error -show_entries stream=duration,nb_frames -of json "$i"
done
# All scenes must have identical duration (38.766667 for 30fps × 38.76s)
# If any scene has different duration, the concat will be wrong
```

## Automated Script

See `scripts/gen_professional_video.py` — a reusable script that encodes PNG slides, converts to TS, binary concatenates, re-encodes to MP4, and synthesizes with narration. Use when generating professional presentation videos from slides.

## PPTX Slide-to-Video Workflow

For creating professional demo videos from PPTX slides (competition demos, presentations), see `references/pptx-video-workflow.md`. This covers the full pipeline: PPTX creation → PDF export → high-res PNG → video segments → narration sync.

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
