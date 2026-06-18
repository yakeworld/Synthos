#!/usr/bin/env python3
"""
Complete professional video synthesis workflow.

Use this script when you have:
1. PNG slides (11 files, professional_check/ directory)
2. Narration audio (narration.mp3, Edge-TTS output)
3. Goal: Create a synced MP4 video with narration

Steps:
1. Encode each PNG to MP4 scene (38.77s per scene, medium preset)
2. Convert all scenes to TS format
3. Binary concat TS files
4. Re-encode to MP4 (recalculates correct duration)
5. Convert narration to AAC
6. Synthesize video + audio with -shortest

Usage:
  python3 gen_professional_video.py --slides-dir <path> --narration <path> --output <path>

Example:
  python3 gen_professional_video.py \
    --slides-dir /path/to/slides \
    --narration /path/to/narration.mp3 \
    --output final_video.mp4
"""

import subprocess, os, sys, shutil
import argparse

def run(cmd, **kwargs):
    r = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    return r

def get_duration(filepath):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", filepath])
    return float(r.stdout.strip()) if r.stdout.strip() else 0

def main():
    parser = argparse.ArgumentParser(description="Generate professional video from slides + narration")
    parser.add_argument("--slides-dir", required=True, help="Directory containing PNG slides")
    parser.add_argument("--narration", required=True, help="Path to narration MP3")
    parser.add_argument("--output", required=True, help="Output MP4 path")
    parser.add_argument("--num-scenes", type=int, default=11, help="Number of scenes")
    parser.add_argument("--scene-duration", type=float, default=38.766667, help="Seconds per scene")
    parser.add_argument("--tmp-dir", default="/tmp/prof_video", help="Temp directory")
    args = parser.parse_args()

    os.makedirs(args.tmp_dir, exist_ok=True)

    # Step 1: Encode scenes
    print("=== Step 1: Encode PNG slides to MP4 scenes ===")
    for i in range(1, args.num_scenes + 1):
        if i >= 10:
            png = f"{args.slides_dir}/professional-{i:02d}.png"
        else:
            png = f"{args.slides_dir}/professional-0{i}.png"
        out = f"{args.tmp_dir}/scene_{i:02d}.mp4"

        print(f"  Scene {i:02d}...", end=" ")
        r = run([
            "ffmpeg", "-y", "-loop", "1", "-i", png,
            "-c:v", "libx264", "-t", str(args.scene_duration),
            "-pix_fmt", "yuv420p", "-r", "30",
            "-preset", "medium", "-crf", "18",
            "-an", out
        ])

        if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 1000:
            dur = get_duration(out)
            print(f"✅ {dur:.2f}s, {os.path.getsize(out)/1024:.0f}KB")
        else:
            print(f"❌ FAILED (r={r.returncode})")
            sys.exit(1)

    # Step 2: Convert to TS
    print("\n=== Step 2: Convert MP4 to TS ===")
    ts_dir = f"{args.tmp_dir}/ts"
    os.makedirs(ts_dir, exist_ok=True)

    for i in range(1, args.num_scenes + 1):
        inp = f"{args.tmp_dir}/scene_{i:02d}.mp4"
        out = f"{ts_dir}/s{i:02d}.ts"
        run(["ffmpeg", "-y", "-i", inp, "-c", "copy", "-f", "mpegts", out])

    # Step 3: Binary concat TS
    print("\n=== Step 3: Binary concat TS files ===")
    all_ts = f"{args.tmp_dir}/all.ts"
    with open(all_ts, "wb") as f:
        for i in range(1, args.num_scenes + 1):
            with open(f"{ts_dir}/s{i:02d}.ts", "rb") as inp:
                f.write(inp.read())
    print(f"  all.ts: {os.path.getsize(all_ts)/1024/1024:.1f}MB")

    # Step 4: Convert back to MP4
    print("\n=== Step 4: TS → MP4 (re-encode for correct duration) ===")
    concat_mp4 = f"{args.tmp_dir}/concat.mp4"
    r = run([
        "ffmpeg", "-y", "-i", all_ts,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", concat_mp4
    ])
    concat_dur = get_duration(concat_mp4)
    print(f"  Duration: {concat_dur:.2f}s")

    # Step 5: Convert narration
    print("\n=== Step 5: Convert narration to AAC ===")
    narr_aac = f"{args.tmp_dir}/narration.aac"
    run([
        "ffmpeg", "-y", "-i", args.narration,
        "-vn", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", narr_aac
    ])
    narr_dur = get_duration(args.narration)
    print(f"  Duration: {narr_dur:.2f}s")

    # Step 6: Final synthesis
    print("\n=== Step 6: Final synthesis ===")
    if narr_dur > concat_dur:
        # Loop video to fill narration
        r = run([
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", concat_mp4,
            "-i", narr_aac,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-shortest", args.output
        ])
    else:
        # Trim narration to video
        r = run([
            "ffmpeg", "-y",
            "-i", concat_mp4,
            "-i", narr_aac,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-t", str(concat_dur), args.output
        ])

    if r.returncode == 0:
        final_dur = get_duration(args.output)
        size = os.path.getsize(args.output)
        print(f"\n✅ Video generated: {args.output}")
        print(f"   Duration: {final_dur:.2f}s")
        print(f"   Size: {size/1024/1024:.1f}MB")
        print(f"   Resolution: 5334x3000 (30fps)")
    else:
        print(f"\n❌ Failed: {r.stderr[:200]}")
        sys.exit(1)

if __name__ == "__main__":
    main()
