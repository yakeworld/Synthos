#!/usr/bin/env python3
"""
Batch centerline extraction for uCT labels from Dataset/uCT/labels/{L,R}/.
处理62耳（31 L + 31 R）裁剪版uCT二值标签 → 三根半规管中心线 NPZ

策略：每例扫描6种(axis_upper × keep_side)配置，选总点数最多的通过配置。
输出格式兼容现有A_manual的NPZ格式。
"""
import sys, json, warnings, csv
from pathlib import Path

import numpy as np
import nibabel as nib
from scipy.ndimage import gaussian_filter1d

sys.path.insert(0, '/mnt/nfs/UNet_Seg/Gao/step2/evaluate')
from centerline_extraction import extract_three_scc_centerlines

LABELS_DIRS = [
    Path('/mnt/nfs/UNet_Seg/Dataset/uCT/labels/L'),
    Path('/mnt/nfs/UNet_Seg/Dataset/uCT/labels/R'),
]
OUTPUT_DIR = Path('/mnt/nfs/UNet_Seg/Gao/step2/centerlines_v5/modeA_no_curv_trim/HBL_uCT')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CONFIGS = [(a, s) for a in [0, 1, 2] for s in ['max', 'min']]
MIN_POINTS = 20


def smooth_and_resample(pts_voxel, n_target=100, sigma=1.0):
    if len(pts_voxel) < 3:
        return pts_voxel.copy()
    diffs = np.diff(pts_voxel, axis=0)
    seg_lens = np.linalg.norm(diffs, axis=1)
    cum_len = np.concatenate([[0], np.cumsum(seg_lens)])
    total_len = cum_len[-1]
    if total_len < 1e-8:
        return pts_voxel.copy()
    smoothed = np.zeros_like(pts_voxel)
    for dim in range(3):
        smoothed[:, dim] = gaussian_filter1d(pts_voxel[:, dim], sigma=sigma, mode='nearest')
    query = np.linspace(0, total_len, n_target)
    resampled = np.zeros((n_target, 3))
    for dim in range(3):
        resampled[:, dim] = np.interp(query, cum_len, smoothed[:, dim])
    return resampled


def resample_to_arc(pts, n_arc=20):
    if len(pts) < 3:
        return pts.copy()
    diffs = np.diff(pts, axis=0)
    seg_lens = np.linalg.norm(diffs, axis=1)
    cum_len = np.concatenate([[0], np.cumsum(seg_lens)])
    total_len = cum_len[-1]
    if total_len < 1e-8:
        return pts.copy()
    query = np.linspace(0, total_len, n_arc)
    resampled = np.zeros((n_arc, 3))
    for dim in range(3):
        resampled[:, dim] = np.interp(query, cum_len, pts[:, dim])
    return resampled


def estimate_radii(pts_voxel, full_mask, search_radius=5):
    radii = []
    coords = np.round(pts_voxel).astype(int)
    shape = full_mask.shape
    for c in coords:
        if not (0 <= c[0] < shape[0] and 0 <= c[1] < shape[1] and 0 <= c[2] < shape[2]):
            radii.append(0); continue
        z0, y0, x0 = c
        z_min, z_max = max(0, z0-search_radius), min(shape[0], z0+search_radius+1)
        y_min, y_max = max(0, y0-search_radius), min(shape[1], y0+search_radius+1)
        x_min, x_max = max(0, x0-search_radius), min(shape[2], x0+search_radius+1)
        patch = full_mask[z_min:z_max, y_min:y_max, x_min:x_max]
        if patch.sum() == 0:
            radii.append(0); continue
        center = np.array([z0-z_min, y0-y_min, x0-x_min])
        bg_coords = np.argwhere(patch == 0)
        if len(bg_coords) == 0:
            radii.append(float(search_radius+1)); continue
        dists = np.linalg.norm(bg_coords - center, axis=1)
        radii.append(float(dists.min()))
    return np.array(radii)


def compute_pca_normal(pts_voxel):
    if len(pts_voxel) < 4:
        return np.array([0, 0, 1.0])
    centroid = pts_voxel.mean(axis=0)
    centered = pts_voxel - centroid
    cov = centered.T @ centered / len(pts_voxel)
    evals, evecs = np.linalg.eigh(cov)
    return evecs[:, 0]


def parse_filename(fname):
    stem = fname.replace('.nii.gz', '').replace('.nii', '')
    parts = stem.split('_')
    if len(parts) >= 4 and parts[0] == 'uCT' and parts[-2] == 'labels':
        side = parts[-1]
        name = '_'.join(parts[1:-2])
        return name, side
    return stem, '?'


def main():
    file_pairs = []
    for d in LABELS_DIRS:
        side_dir = d.name
        for f in sorted(d.glob('*.nii.gz')):
            spec_name, _ = parse_filename(f.name)
            case_id = f"{spec_name}_{side_dir}"
            file_pairs.append((f, case_id, side_dir))

    print(f"Found {len(file_pairs)} uCT label files")
    print(f"Output: {OUTPUT_DIR}")

    summaries = []
    success = fail = 0

    for fpath, case_id, side in file_pairs:
        fname = fpath.name
        print(f"\n>>> {fname}  →  {case_id}", end=' ', flush=True)

        try:
            img = nib.load(str(fpath))
            data = img.get_fdata()
            spacing = np.array(img.header.get_zooms())
            arr_bin = (data > 0).astype(np.uint8)

            if arr_bin.sum() < 100:
                print(f"✗ TOO FEW VOXELS ({arr_bin.sum()})")
                fail += 1
                continue

            # Try all 6 configs, pick best
            best_config = best_result = None
            best_total = 0

            for axis_upper, keep_side in CONFIGS:
                result = extract_three_scc_centerlines(
                    arr_bin, spacing_zyx=tuple(spacing),
                    axis_upper=axis_upper, keep_side=keep_side,
                )
                n = (len(result.superior), len(result.posterior), len(result.lateral))
                n_total = sum(n)
                if all(nn >= MIN_POINTS for nn in n) and n_total > best_total:
                    best_total = n_total
                    best_config = (axis_upper, keep_side)
                    best_result = result

            if best_result is None:
                # Fallback: best total even if weak canals
                for ax, ks in CONFIGS:
                    r = extract_three_scc_centerlines(arr_bin, axis_upper=ax, keep_side=ks)
                    nt = len(r.superior) + len(r.posterior) + len(r.lateral)
                    if nt > best_total:
                        best_total, best_config, best_result = nt, (ax, ks), r
                print(f"⚠ best-effort", end=' ')

            # Save
            out_dir = OUTPUT_DIR / case_id
            out_dir.mkdir(exist_ok=True)

            canal_map = [
                ('superior', 'AC', best_result.superior),
                ('posterior', 'PC', best_result.posterior),
                ('lateral', 'LC', best_result.lateral),
            ]
            canals_ok = 0
            for fp, cn, pts in canal_map:
                if len(pts) < 3:
                    continue
                sv = smooth_and_resample(pts)
                sm = sv * spacing
                av = resample_to_arc(pts)
                rv = estimate_radii(pts, arr_bin)
                pn = compute_pca_normal(pts)
                np.savez_compressed(str(out_dir / f'{fp}.npz'),
                    smooth_voxel=sv, smooth_mm=sm, arc_voxel=av,
                    spacing_zyx=spacing,
                    name=np.array(cn, dtype='<U8'),
                    side=np.array(side, dtype='<U1'),
                    case_id=np.array(case_id, dtype='<U10'),
                    radii_voxel=rv, pca_normal=pn)
                canals_ok += 1

            (out_dir / 'config.json').write_text(json.dumps({
                'specimen': case_id, 'side': side,
                'shape': list(data.shape), 'spacing': spacing.tolist(),
                'voxels': int(arr_bin.sum()),
                'axis_upper': best_config[0], 'keep_side': best_config[1],
                'canals': {'AC': len(best_result.superior),
                          'PC': len(best_result.posterior),
                          'LC': len(best_result.lateral)},
            }, indent=2))

            print(f"✓ {side} ax={best_config[0]}/ks={best_config[1]}  "
                  f"AC={len(best_result.superior)} PC={len(best_result.posterior)} LC={len(best_result.lateral)}")
            summaries.append({'specimen': case_id, 'side': side, 'status': 'OK',
                              'axis_upper': best_config[0], 'keep_side': best_config[1],
                              'n_AC': len(best_result.superior),
                              'n_PC': len(best_result.posterior),
                              'n_LC': len(best_result.lateral)})
            success += 1

        except Exception as e:
            print(f"✗ ERROR: {e}")
            fail += 1

    print(f"\n{'='*50}")
    print(f"Complete: {success}/{len(file_pairs)} OK, {fail} failed")

    csv_path = OUTPUT_DIR / 'summary.csv'
    with open(csv_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['specimen', 'side', 'status',
                                           'axis_upper', 'keep_side',
                                           'n_AC', 'n_PC', 'n_LC'])
        w.writeheader()
        for s in summaries:
            w.writerow(s)
    print(f"Summary: {csv_path}")


if __name__ == '__main__':
    main()
