#!/usr/bin/env python3
"""
Batch fit 3D logarithmic spiral to SCC centerlines.
Usage:  python3 scripts/batch_logspiral_fit.py <input_dir> <output_json>

Fits: r(θ) = O + R · (a·e^(bθ)·cosθ, a·e^(bθ)·sinθ, A·sin(ωθ+φ))^T

Two-stage fitting:
  1. Planar log spiral to 2D projection (linearized: ln(r)=ln(a)+bθ)
  2. Non-linear refinement + out-of-plane sinusoidal component
"""
import json, os, sys, glob, time
import numpy as np
from scipy.optimize import minimize

def best_fit_plane(points):
    centroid = np.mean(points, axis=0)
    centered = points - centroid
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    normal = Vt[2, :]
    normal = normal / np.linalg.norm(normal)
    return normal, centroid

def fit_logspiral(points):
    """Two-stage 3D logarithmic spiral fitting. Returns dict or None."""
    n = len(points)
    normal, centroid = best_fit_plane(points)
    centered = points - centroid
    
    ref = np.array([1, 0, 0])
    if abs(np.dot(normal, ref)) > 0.9:
        ref = np.array([0, 1, 0])
    u = np.cross(normal, ref)
    u = u / np.linalg.norm(u)
    v = np.cross(normal, u)
    
    pts_2d = np.column_stack([np.dot(centered, u), np.dot(centered, v)])
    cx, cy = np.mean(pts_2d, axis=0)
    thetas = np.arctan2(pts_2d[:, 1] - cy, pts_2d[:, 0] - cx)
    radii = np.sqrt((pts_2d[:, 0] - cx)**2 + (pts_2d[:, 1] - cy)**2)
    
    valid = radii > 0.01
    if np.sum(valid) < 10:
        return None
    
    A_log = np.column_stack([thetas[valid], np.ones(np.sum(valid))])
    coeffs, _, _, _ = np.linalg.lstsq(A_log, np.log(radii[valid]), rcond=None)
    b, ln_a = coeffs
    a = np.exp(ln_a)
    
    def planar_err(params):
        a_nl, b_nl, cxn, cyn = params
        r_pred = a_nl * np.exp(b_nl * (thetas - np.arctan2(-cyn, -cxn)))
        dist = np.sqrt((pts_2d[:, 0] - cxn)**2 + (pts_2d[:, 1] - cyn)**2)
        return np.sum((dist - r_pred)**2)
    
    result = minimize(planar_err, [a, b, cx, cy], method='Nelder-Mead')
    a, b, cx, cy = result.x
    
    z_dev = np.dot(centered, normal)
    best_sin, best_sp = float('inf'), [0, 1, 0]
    for w0 in [0.5, 1.0, 2.0, 3.0]:
        for p0 in [0, np.pi/4, np.pi/2]:
            r = minimize(lambda p: np.sum((p[0]*np.sin(p[1]*thetas+p[2])-z_dev)**2),
                        [0.2, w0, p0], method='Nelder-Mead')
            if r.fun < best_sin:
                best_sin, best_sp = r.fun, r.x
    
    A_opt, omega_opt, phi_opt = best_sp
    arc = np.sum(np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1)))
    rms_plane = np.sqrt(np.mean(z_dev**2))
    
    return {
        'a': float(a), 'b': float(b),
        'A': float(A_opt), 'omega': float(omega_opt), 'phi': float(phi_opt),
        'rmse_3d': float(np.sqrt(best_sin/n)),
        'arc_mm': float(arc), 'n_points': int(n),
        'rms_plane_mm': float(rms_plane),
        'non_planarity_pct': float(rms_plane/arc*100) if arc>0 else 0,
    }

def load_npz_centerline(path, key='smooth_mm'):
    """Load NPZ centerline file. Returns (N,3) array or None."""
    import numpy as np
    try:
        d = np.load(path)
        if key not in d:
            return None
        pts = d[key]
        return pts if len(pts) >= 20 else None
    except:
        return None

if __name__ == '__main__':
    in_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    out_file = sys.argv[2] if len(sys.argv) > 2 else '/tmp/logspiral_results.json'
    
    cases = sorted(glob.glob(os.path.join(in_dir, "CT*")))
    results = {}
    success = 0
    
    for case_dir in cases:
        cid = os.path.basename(case_dir)
        results[cid] = {'canals': {}}
        for canal in ['superior', 'posterior', 'lateral']:
            npz = os.path.join(case_dir, f"{canal}.npz")
            if not os.path.exists(npz):
                continue
            pts = load_npz_centerline(npz)
            if pts is None:
                continue
            fit = fit_logspiral(pts)
            if fit is None:
                continue
            fit['canal'] = canal
            results[cid]['canals'][canal] = fit
            success += 1
    
    print(f"Cases: {len(cases)}, Successful fits: {success}")
    json.dump(results, open(out_file, 'w'), indent=1)
    print(f"Saved to {out_file}")
