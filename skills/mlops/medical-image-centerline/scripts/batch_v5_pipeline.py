#!/usr/bin/env python3
"""
Batch uCT centerline extraction using the mature v5 pipeline (nibabel-only).
位置: scripts/batch_v5_pipeline.py (medical-image-centerline skill)

用法:
    python3 scripts/batch_v5_pipeline.py

输入: Dataset/uCT/labels/{L,R}/*.nii.gz  (62耳)
输出: centerlines_v5/modeA_no_curv_trim/HBL_uCT_v5/{case_id}/{superior,posterior,lateral}.npz
"""
import sys, os, json, time
sys.stdout.reconfigure(line_buffering=True)
from pathlib import Path
import numpy as np
import nibabel as nib

sys.path.insert(0, '/mnt/nfs/UNet_Seg/Gao/step2/evaluate')
from centerline_v5_pipeline import extract_three_scc_v5

LABELS_DIRS = [
    Path('/mnt/nfs/UNet_Seg/Dataset/uCT/labels/L'),
    Path('/mnt/nfs/UNet_Seg/Dataset/uCT/labels/R'),
]
OUTPUT_DIR = Path('/mnt/nfs/UNet_Seg/Gao/step2/centerlines_v5/modeA_no_curv_trim/HBL_uCT_v5')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def process_one(fpath, case_id, side):
    img = nib.load(str(fpath))
    arr = (img.get_fdata() > 0).astype(np.uint8)
    spacing = tuple(np.array(img.header.get_zooms()))
    if arr.sum() < 100: return None
    result = extract_three_scc_v5(arr, spacing_zyx=spacing)
    out_dir = OUTPUT_DIR / case_id
    out_dir.mkdir(exist_ok=True)
    for name, attr, pref in [('AC','superior_smooth','superior'),('PC','posterior_smooth','posterior'),('LC','lateral_smooth','lateral')]:
        pts = getattr(result, attr)
        if len(pts) >= 3:
            np.savez_compressed(str(out_dir/f'{pref}.npz'),
                smooth_mm=pts, spacing_zyx=np.array(spacing),
                name=np.array(name,dtype='<U8'), side=np.array(side,dtype='<U1'),
                case_id=np.array(case_id,dtype='<U10'))
    meta = {'n_cycles':result.n_cycles_found,'cycle_lengths':result.cycle_lengths[:10],'warnings':result.warnings[:5]}
    (out_dir/'meta.json').write_text(json.dumps(meta,indent=2))
    return meta

if __name__ == '__main__':
    files = []
    for d in LABELS_DIRS:
        s = d.name
        for f in sorted(d.glob('*.nii.gz')):
            p = f.name.replace('.nii.gz','').split('_')
            spec = '_'.join(p[1:-2]) if len(p) >= 4 else f.stem
            files.append((f, f'{spec}_{s}', s))
    print(f"Processing {len(files)} uCT files...")
    ok=0
    for fi,(fp,cid,sd) in enumerate(files):
        if (OUTPUT_DIR/cid/'meta.json').exists(): ok+=1; continue
        print(f"  [{fi+1}/{len(files)}] {cid}:", end=' ', flush=True)
        t0=time.time()
        try:
            r=process_one(fp,cid,sd)
            print(f"{'✓' if r else '✗'} ({time.time()-t0:.1f}s)")
            if r: ok+=1
        except Exception as e:
            print(f'✗ {e}')
    print(f"\nDone: {ok}/{len(files)}")
