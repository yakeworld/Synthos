# MP4→TS Conversion Data Loss

## Problem

When converting MP4 files to TS format with `ffmpeg -c copy`, the output TS file
can be significantly smaller than the input MP4 and contain less data:

```
MP4 total: 43.81MB → TS total: 32.86MB  (25% data loss!)
Individual scene: 38.77s each → TS concat: 388.6s (missing 1 scene worth)
```

## Root Cause

This is NOT a universal issue. It occurs when:

1. **MP4 files are QuickTime/mov format** (container: `mov,mp4,m4a,3gp,3g2,mj2`)
   - ffmpeg reports format as QuickTime, not plain MP4
   - Contains extra metadata tracks or atoms that `-c copy` may skip

2. **Encoding used aggressive presets** (`-preset ultrafast/fast`)
   - May produce B-frames or frame structures that TS container can't copy faithfully

3. **Scene files use `-loop 1` with PNG input**
   - Creates a still-image video with specific timing characteristics
   - TS container may truncate the single still-image loop incorrectly

## Symptoms

- Each source MP4 is correctly 38.77s (verified with ffprobe)
- After TS conversion + binary concat, MP4 output is ~388.6s instead of 426.4s
- Missing ~38s (exactly one scene duration)
- TS files are 25% smaller than MP4 files
- No FFmpeg error or warning during TS conversion

## Fix

**Option A: Re-encode with medium preset (recommended, most reliable)**
```bash
# Re-encode all scenes with medium preset (not ultrafast/fast)
for i in scene_*.mp4; do
  ffmpeg -y -i "$i" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -an \
    "reencoded_$i"
done
# Then convert to TS and concat as normal
```
Trade-off: takes ~30s per scene, but guarantees data integrity.

**Option B: Use `-f mp4` flag for TS conversion**
```bash
# Explicitly specify MP4 container during conversion
for i in scene_*.mp4; do
  ffmpeg -y -i "$i" -f mp4 -c copy -f mpegts "tmp_$(basename $i .mp4).ts"
done
```
Trade-off: may still lose data for QuickTime-format files.

**Option C: Skip TS entirely, use filter_complex concat**
```bash
# Direct MP4 concat with filter (no format conversion needed)
ffmpeg -y \
  -i scene_01.mp4 -i scene_02.mp4 -i scene_03.mp4 \
  -filter_complex "[0:v][1:v][2:v]concat=n=3:v=1:a=0[outv]" \
  -map "[outv]" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p concat.mp4
```
Trade-off: only works for small N (11 inputs = long command). Not scalable.

## Prevention

When encoding scene files, use:
- `-preset medium` or `-preset fast` (not ultrafast)
- `-crf 18-20` for good quality
- Always verify scene duration after encoding: `ffprobe -show_entries stream=duration scene.mp4`
- After TS conversion, verify TS file size is comparable to MP4 (>90% of original)
- Before binary concat, verify each TS has correct duration: `ffprobe -show_entries format=duration file.ts`

## Reference: Session Data

From 2026-05-09 session (Synthos video):
- 11 scenes, each 38.766667s, total MP4: 43.81MB
- After TS conversion: total 32.86MB (25% loss)
- After binary concat → MP4: 388.6s (missing ~38s, one scene)
- After re-encode with medium preset: all scenes intact, correct duration achieved
- Root cause: scenes encoded with `-preset fast` or `-preset ultrafast` + PNG input via `-loop 1`
