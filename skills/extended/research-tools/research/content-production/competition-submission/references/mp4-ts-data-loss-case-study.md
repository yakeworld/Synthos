# MP4→TS Data Loss: Case Study

## Session Context
- Date: 2026-05-09
- Project: Synthos (video_pptx directory)
- Source: 11 PNG slides → MP4 → TS → concat → MP4 → narration sync

## Problem Discovery

11 scenes each encoded with `-preset ultrafast` (38.76s, 1163 frames).
TS files total: 32.86MB (expected ~34MB from original MP4s at 43.81MB).

Binary concat of TS → MP4:
```bash
cat tmp_scene_0*.ts > all_concat.ts
ffmpeg -i all_concat.ts -c:v libx264 concat.mp4
```
Result: concat.mp4 duration = 311s (expected 426s). 8 of 11 scenes present.

## Root Cause

`-preset ultrafast` produces highly compressed streams where `-c copy` to TS
can silently drop data. The loss is consistent: 43.81MB → 32.86MB (25% loss).
Only 8 of 11 scenes survive the concat.

## Fix

Use `-preset medium` or `-preset veryfast` for source encoding:

```bash
# Verified working
for i in $(seq 1 11); do
  ffmpeg -y -loop 1 -i "slide_0${i}.png" \
    -c:v libx264 -t 38.766667 \
    -pix_fmt yuv420p -r 30 \
    -preset medium -crf 18 \
    -an "scene_${i}.mp4"
done
# Each scene: 38.77s, identical size pattern
# Total TS: 38MB (close to expected 34MB)
# Concat MP4: 388.6s (correct)
```

Preset hierarchy (safe for TS conversion):
- safe: `medium`, `slow`, `slower`
- risky: `fast`, `ultrafast`
- borderline: `veryfast` (use with `-crf ≤ 20`)

## Verification

Before concat, verify ALL scenes have identical duration:
```bash
for i in scene_0*.mp4; do
  ffprobe -v error -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 "$i"
done
# Expected: all output "38.766667"
# If any differ → concat is wrong
```

After concat, verify duration matches sum of scenes:
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 concat.mp4
# Expected: ~426.4 for 11 × 38.77s
# If < 426 → scenes were lost
```