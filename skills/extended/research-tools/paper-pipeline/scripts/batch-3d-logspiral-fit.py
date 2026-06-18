#!/usr/bin/env python3
"""
Batch 3D Logarithmic Spiral Fitting for Anatomical Centerlines.
Takes .npz files with smooth_mm (N, 3) coordinates, fits the model:
  r(θ) = O + R · (a·e^(bθ)·cosθ, a·e^(bθ)·sinθ, A·sin(ωθ+φ))ᵀ

Two-stage strategy:
1. SVD plane fit → 2D projection → log-linear spiral fit → nonlinear refinement
2. Out-of-plane sinusoidal residual fit with multi-initialization

Output: JSON with per-canal parameters (a, b, A, ω, φ, RMSE, arc_length, etc.)

Adapt for other anatomical structures by changing:
- INPUT glob pattern and .npz key
- Point count filter (min_points)
- Fitting parameter bounds
"""

import json, os, glob, time
import numpy as np
from scipy.optimize import minimize

# ---- CONFIGURATION ----
INPUT_GLOB = "/mnt/nfs/UNet_Seg/Gao/step2/centerlines_v5/modeA_no_curv_trim/A_manual/CT*/superior.npz"
COORD_KEY = "smooth_mm"        # key in .npz for 3D coordinates (mm)
MIN_POINTS = 20                # skip canals with fewer points
MAX_B_ABS = 0.5                # sanity filter for spiral growth rate
OUTPUT = "/tmp/batch_logspiral_results.json"

def best_fit_plane(points):
    centroid = np.mean(points, axis=0)
    centered = points - centroid
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    normal = Vt[2, :] / np.linalg.norm(Vt[2, :])
    return normal, centroid

def fit_logspiral(points):
    """Two-stage: planar spiral → out-of-plane sinusoidal."""
    n = len(points)
    normal, centroid = best_fit_plane(points)
    centered = points - centroid
    ref = np.array([1, 0, 0])
    if abs(np.dot(normal, ref)) > 0.9:
        ref = np.array([0, 1, 0])
    u = np.cross(normal, ref); u /= np.linalg.norm(u)
    v = np.cross(normal, u); v /= np.linalg.norm(v)
    pts_2d = np.column_stack([np.dot(centered, u), np.dot(centered, v)])
    cx, cy = np.mean(pts_2d, axis=0)
    thetas = np.arctan2(pts_2d[:, 1] - cy, pts_2d[:, 0] - cx)
    radii = np.sqrt((pts_2d[:, 0] - cx)**2 + (pts_2d[:, 1] - cy)**2)
    valid = radii > 0.01
    if np.sum(valid) < 10: return None
    A_log = np.column_stack([thetas[valid], np.ones(np.sum(valid))])
    coeffs, *_ = np.linalg.lstsq(A_log, np.log(radii[valid]), rcond=None)
    b, ln_a = coeffs; a = np.exp(ln_a)
    def planar_err(p):
        a_nl, b_nl, cxn, cyn = p
        r_pred = a_nl * np.exp(b_nl * (thetas - np.arctan2(-cyn, -cxn)))
        dist = np.sqrt((pts_2d[:,0]-cxn)**2 + (pts_2d[:,1]-cyn)**2)
        return np.sum((dist - r_pred)**2)
    res = minimize(planar_err, [a, b, cx, cy], method='Nelder-Mead')
    a_opt, b_opt, cx_opt, cy_opt = res.x
    z_dev = np.dot(centered, normal)
    def sin_err(p):
        A_s, w, ph = p
        return np.sum((A_s * np.sin(w * thetas + ph) - z_dev)**2)
    best_sin = float('inf'); best_p = [0, 1, 0]
    for w0 in [0.5, 1.0, 2.0, 3.0]:
        for p0 in [0, np.pi/4, np.pi/2]:
            try:
                r = minimize(sin_err, [0.2, w0, p0], method='Nelder-Mead')
                if r.fun < best_sin: best_sin, best_p = r.fun, r.x
            except: pass
    A_opt, omega_opt, phi_opt = best_p
    t_sorted = np.sort(thetas)
    r_sorted = a_opt * np.exp(b_opt * (t_sorted - np.arctan2(-cy_opt, -cx_opt)))
    x3 = centroid[0] + r_sorted*np.cos(t_sorted)*u[0] + r_sorted*np.sin(t_sorted)*v[0] + (A_opt*np.sin(omega_opt*t_sorted+phi_opt))*normal[0]
    y3 = centroid[1] + r_sorted*np.cos(t_sorted)*u[1] + r_sorted*np.sin(t_sorted)*v[1] + (A_opt*np.sin(omega_opt*t_sorted+phi_opt))*normal[1]
    z3 = centroid[2] + r_sorted*np.cos(t_sorted)*u[2] + r_sorted*np.sin(t_sorted)*v[2] + (A_opt*np.sin(omega_opt*t_sorted+phi_opt))*normal[2]
    model_pts = np.column_stack([x3, y3, z3])
    inv = np.argsort(np.argsort(thetas))
    model_pts = model_pts[inv]
    arc = float(np.sum(np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1))))
    rms_plane = float(np.sqrt(np.mean(z_dev**2)))
    return {
        'a': float(a_opt), 'b': float(b_opt),
        'A': float(A_opt), 'omega': float(omega_opt), 'phi': float(phi_opt),
        'rmse_3d': float(np.sqrt(np.mean(np.sum((points - model_pts)**2, axis=1)))),
        'arc_mm': arc, 'n_points': int(n),
        'rms_plane_mm': rms_plane,
        'non_planarity_pct': rms_plane/arc*100 if arc > 0 else 0,
        'normal': normal.tolist(), 'centroid': centroid.tolist(),
    }

def convert(o):
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return float(o)
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, dict): return {k: convert(v) for k, v in o.items()}
    if isinstance(o, list): return [convert(v) for v in o]
    return o

if __name__ == '__main__':
    files = sorted(glob.glob(INPUT_GLOB))
    print(f"Found {len(files)} files")
    results, total, success, failed = {}, 0, 0, 0; t0 = time.time()
    for fpath in files:
        case_dir = os.path.dirname(fpath)
        case_id = os.path.basename(case_dir)
        canal_name = os.path.basename(fpath).replace('.npz', '')
        results.setdefault(case_id, {'canals': {}})
        total += 1
        try:
            data = np.load(fpath); pts = data[COORD_KEY]
            if len(pts) < MIN_POINTS: failed += 1; continue
            fit = fit_logspiral(pts)
            if fit is None: failed += 1; continue
            fit.update(canal=canal_name, case_id=case_id, side=str(data.get('side','?')), name=str(data.get('name',canal_name)))
            results[case_id]['canals'][canal_name] = fit; success += 1
        except: failed += 1
    meta = {'total': total, 'success': success, 'failed': failed, 'elapsed_seconds': time.time()-t0, 'model': '3D Logarithmic Spiral'}
    with open(OUTPUT, 'w') as f:
        json.dump({'metadata': meta, 'cases': convert(results)}, f, indent=1)
    print(f"\n{total} total | {success} success | {failed} failed | {meta['elapsed_seconds']:.1f}s\nOutput: {OUTPUT}")
