#!/usr/bin/env python3
"""
High-resolution centerline extraction for uCT data.
Scales greedy walk parameters (max_count, jump_threshold) by voxel spacing.
CT(0.3-0.5mm) → max_count=40 OK.
uCT(0.06mm) → max_count≈200 needed for 10mm arc.

Usage:
    from extract_hr_centerline import extract_hr
    import nibabel as nib, numpy as np

    img = nib.load('F01_uCT_LABELS.nii')
    data = (img.get_fdata() > 0).astype(np.uint8)
    spacing = np.array(img.header.get_zooms())

    result = extract_hr(data, spacing, axis_upper=2, keep_side='min')
    print(f"AC: {len(result.superior)} pts, {arc_length(result.superior, spacing):.1f}mm")
    print(f"PC: {len(result.posterior)} pts, {arc_length(result.posterior, spacing):.1f}mm")
    print(f"LC: {len(result.lateral)} pts, {arc_length(result.lateral, spacing):.1f}mm")
"""
import sys
import numpy as np
from skimage.morphology import skeletonize

sys.path.insert(0, '/mnt/nfs/UNet_Seg/Gao/step2/evaluate')
from centerline_extraction import _walk_both_directions, ThreeSCCCenterlines


def extract_hr(full_mask, spacing, axis_upper=0, keep_side='max',
               min_walk_count_default=10, min_walk_count_lateral=8):
    """
    High-res centerline extraction with resolution-scaled max_count.
    
    Parameters
    ----------
    full_mask : (D, H, W) uint8/bool
        Binary mask of the full bony labyrinth.
    spacing : (3,) array-like
        Voxel spacing (zyx order), e.g. [0.06, 0.06, 0.06] for uCT.
    axis_upper : int (0, 1, or 2)
        Axis for median cut separation.
    keep_side : 'max' or 'min'
        Which side of the median to keep.
    
    Returns
    -------
    ThreeSCCCenterlines
    """
    mean_sp = np.mean(spacing)
    scale = max(1.0, 0.3 / mean_sp)  # CT ref spacing = 0.3mm
    max_count = int(40 * scale)
    jump_th = max(5.0, 3.0 * scale)
    
    warnings = []
    full_bin = (full_mask > 0).astype(np.uint8)
    
    skel = skeletonize(full_bin).astype(np.uint8)
    all_skel_coords = np.argwhere(skel > 0).astype(np.float64)
    
    if len(all_skel_coords) == 0:
        empty = np.empty((0, 3))
        return ThreeSCCCenterlines(empty, empty, empty, empty, empty,
                                    np.empty(0, dtype=bool), {}, ['empty skeleton'])
    
    axes = [axis_upper] + [a for a in [0, 1, 2] if a != axis_upper]
    median_val = np.median(all_skel_coords[:, axis_upper])
    
    upper_mask = (all_skel_coords[:, axis_upper] > median_val) if keep_side == 'max' \
                 else (all_skel_coords[:, axis_upper] < median_val)
    upper_points = all_skel_coords[upper_mask]
    
    N = len(upper_points)
    if N < 10:
        empty = np.empty((0, 3))
        return ThreeSCCCenterlines(empty, empty, empty, all_skel_coords, upper_points,
                                    np.empty(0, dtype=bool), {}, ['too few upper points'])
    
    dist_matrix = np.linalg.norm(upper_points[:, np.newaxis, :] -
                                 upper_points[np.newaxis, :, :], axis=-1)
    neighbor_counts = np.sum(dist_matrix < 1.8, axis=1) - 1
    branch_mask = neighbor_counts > 2
    endpoint_mask = neighbor_counts <= 1
    
    x_axis_idx, y_axis_idx, z_axis_idx = axes
    claimed = set()
    
    # Superior (AC)
    start = int(np.argmax(upper_points[:, x_axis_idx]))
    try:
        idx = _walk_both_directions(start, dist_matrix, branch_mask, endpoint_mask,
                                     min_walk_count_default, max_count, jump_th, claimed)
        claimed.update(idx)
        sup = upper_points[idx]
    except Exception as e:
        sup = np.empty((0, 3))
        warnings.append(f'AC walk failed: {e}')
    
    # Posterior (PC)
    rem = [i for i in range(N) if i not in claimed]
    if len(rem) >= 5:
        start = rem[int(np.argmax(upper_points[rem, y_axis_idx]))]
        try:
            idx = _walk_both_directions(start, dist_matrix, branch_mask, endpoint_mask,
                                         min_walk_count_default, max_count, jump_th, claimed)
            claimed.update(idx)
            post = upper_points[idx]
        except Exception as e:
            post = np.empty((0, 3))
            warnings.append(f'PC walk failed: {e}')
    else:
        post = np.empty((0, 3))
    
    # Lateral (LC)
    rem = [i for i in range(N) if i not in claimed]
    if len(rem) >= 5:
        start = rem[int(np.argmin(upper_points[rem, z_axis_idx]))]
        try:
            idx = _walk_both_directions(start, dist_matrix, branch_mask, endpoint_mask,
                                         min_walk_count_lateral, max_count, jump_th, claimed)
            lat = upper_points[idx]
        except Exception as e:
            lat = np.empty((0, 3))
            warnings.append(f'LC walk failed: {e}')
    else:
        lat = np.empty((0, 3))
    
    return ThreeSCCCenterlines(
        sup, post, lat,
        all_skel_coords, upper_points, branch_mask,
        {'max_count': max_count, 'jump_threshold': jump_th,
         f'axis{axis_upper}_median': float(median_val)},
        warnings,
    )


def arc_length(pts_voxel, spacing):
    """Compute physical arc length from voxel-space centerline points."""
    if len(pts_voxel) < 2:
        return 0.0
    pts_mm = pts_voxel * np.array(spacing)
    return float(np.sum(np.sqrt(np.sum(np.diff(pts_mm, axis=0)**2, axis=1))))


def scan_configs(full_mask, spacing, min_points=20):
    """
    Try all 6 (axis_upper, keep_side) configs and return the best result.
    Uses original max_count first; if arcs < 5mm, retries with HR scaling.
    """
    from centerline_extraction import extract_three_scc_centerlines
    
    configs = [(a, s) for a in [0, 1, 2] for s in ['max', 'min']]
    
    # First try with original max_count=40
    best = None; best_total = 0
    for a, s in configs:
        r = extract_three_scc_centerlines(full_mask, axis_upper=a, keep_side=s)
        ns, npc, nl = len(r.superior), len(r.posterior), len(r.lateral)
        if ns >= min_points and npc >= min_points and nl >= min_points and (ns+npc+nl) > best_total:
            best_total = ns + npc + nl
            best = (a, s, r, False)
    
    # Check arc lengths
    if best is not None:
        r = best[2]
        arcs = [arc_length(r.superior, spacing) if len(r.superior) > 2 else 0,
                arc_length(r.posterior, spacing) if len(r.posterior) > 2 else 0,
                arc_length(r.lateral, spacing) if len(r.lateral) > 2 else 0]
        if all(a > 5.0 for a in arcs):
            return best[2], best[:2], False  # Good enough with original
    
    # If arcs are short, retry with HR scaling
    best2 = None; best_total2 = 0
    for a, s in configs:
        r = extract_hr(full_mask, spacing, axis_upper=a, keep_side=s)
        ns, npc, nl = len(r.superior), len(r.posterior), len(r.lateral)
        if ns >= min_points and npc >= min_points and nl >= min_points and (ns+npc+nl) > best_total2:
            best_total2 = ns + npc + nl
            best2 = (a, s, r, True)
    
    if best2 is not None:
        return best2[2], best2[:2], True
    
    # Fallback: best effort with HR
    for a, s in configs:
        r = extract_hr(full_mask, spacing, axis_upper=a, keep_side=s)
        total = len(r.superior) + len(r.posterior) + len(r.lateral)
        if total > best_total2:
            best_total2 = total
            best2 = (a, s, r, True)
    
    return best2[2] if best2 else None, best2[:2] if best2 else None, True
