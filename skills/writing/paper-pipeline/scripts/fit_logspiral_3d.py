#!/usr/bin/env python3
"""
Fit 3D Logarithmic Spiral to SCC centerline data (path-ordered method).

USAGE:
    python3 fit_logspiral_3d.py <path_to.mrk.json> [--specimen-id ID]

OUTPUT:
    Prints parameters: a, b, A, omega, phi
    Saves plot to <input_stem>_fitted.pdf

REQUIRES: numpy, scipy, matplotlib
"""
import json, math, sys, os
import numpy as np
from scipy.optimize import minimize

def load_centerline(path):
    with open(path) as f:
        data = json.load(f)
    pts = data['markups'][0]['controlPoints']
    return np.array([p['position'] for p in pts])

def nearest_neighbor_path(pts):
    """Path-ordering: start at point 0, greedily visit nearest unvisited"""
    n = len(pts)
    visited = [False] * n
    path = [0]; visited[0] = True
    current = 0
    while len(path) < n:
        dists = [np.linalg.norm(pts[current] - pts[j]) if not visited[j] else float('inf')
                 for j in range(n)]
        nearest = np.argmin(dists)
        path.append(nearest); visited[nearest] = True
        current = nearest
    return path

def fit_logspiral(pts):
    """3-stage 3D log spiral fitting"""
    # Stage 1: SVD best-fit plane
    centroid = np.mean(pts, axis=0)
    U, S, Vt = np.linalg.svd(pts - centroid, full_matrices=False)
    normal = Vt[2, :] / np.linalg.norm(Vt[2, :])
    ref = np.array([1, 0, 0]) if abs(normal @ [1,0,0]) < 0.9 else np.array([0, 1, 0])
    u = np.cross(normal, ref); u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    pts_2d = np.column_stack([(pts - centroid) @ u, (pts - centroid) @ v])
    z_dev = (pts - centroid) @ normal
    
    # Stage 2: Path-ordered theta → unwrap
    path = nearest_neighbor_path(pts)
    dx, dy = pts_2d[:,0] - np.mean(pts_2d[:,0]), pts_2d[:,1] - np.mean(pts_2d[:,1])
    theta_raw = np.arctan2(dy, dx)
    r2 = np.sqrt(dx**2 + dy**2)
    
    theta_path = theta_raw[path]
    theta_unwrapped = np.unwrap(theta_path)
    r_path = r2[path]
    z_path = z_dev[path]
    
    # Fit log(r) = log(a) + b*θ
    A = np.column_stack([np.ones_like(theta_unwrapped), theta_unwrapped])
    coeffs = np.linalg.lstsq(A, np.log(r_path), rcond=None)[0]
    a, b = np.exp(coeffs[0]), coeffs[1]
    
    # Fit z = A*sin(ω*θ + φ) — grid search
    def sin_err(p):
        Am, om, ph = p
        return np.sum((Am*np.sin(om*theta_unwrapped+ph) - z_path)**2)
    best_s = float('inf'); best_p = [0.2, 2.0, 0]
    for A0 in [0.05, 0.1, 0.2, 0.3, 0.4]:
        for om0 in [0.5, 1, 1.5, 2, 2.5, 3]:
            for ph0 in [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi]:
                r = minimize(sin_err, [A0, om0, ph0], method='Nelder-Mead')
                if r.fun < best_s: best_s, best_p = r.fun, r.x
    A_s, om_s, ph_s = best_p
    
    # RMSE (evaluate only where data exists)
    t_min, t_max = theta_unwrapped[0], theta_unwrapped[-1]
    t_eval = np.linspace(t_min, t_max, 500)
    r_eval = a * np.exp(b * t_eval)
    z_eval = A_s * np.sin(om_s * t_eval + ph_s)
    x = centroid[0] + (np.mean(pts_2d[:,0]) + r_eval*np.cos(t_eval)) * u[0] \
        + (np.mean(pts_2d[:,1]) + r_eval*np.sin(t_eval)) * v[0] + z_eval * normal[0]
    y = centroid[1] + (np.mean(pts_2d[:,0]) + r_eval*np.cos(t_eval)) * u[1] \
        + (np.mean(pts_2d[:,1]) + r_eval*np.sin(t_eval)) * v[1] + z_eval * normal[1]
    z = centroid[2] + (np.mean(pts_2d[:,0]) + r_eval*np.cos(t_eval)) * u[2] \
        + (np.mean(pts_2d[:,1]) + r_eval*np.sin(t_eval)) * v[2] + z_eval * normal[2]
    curve = np.column_stack([x, y, z])
    
    # Nearest-point RMSE
    from scipy.spatial import KDTree
    tree = KDTree(curve)
    dists, _ = tree.query(pts)
    rmse = np.sqrt(np.mean(dists**2))
    
    arc = np.sum(np.sqrt(np.sum(np.diff(pts, axis=0)**2, axis=1)))
    
    return {'a': a, 'b': b, 'A': A_s, 'omega': om_s, 'phi': ph_s,
            'rmse': rmse, 'arc': arc, 'normal': normal, 'centroid': centroid}

if __name__ == '__main__':
    path = sys.argv[1]
    pts = load_centerline(path)
    r = fit_logspiral(pts)
    name = os.path.splitext(os.path.basename(path))[0]
    print(f"{name}: a={r['a']:.3f}, b={r['b']:.4f}, A={r['A']:.3f}, "
          f"ω={r['omega']:.1f}, φ={r['phi']:.1f}°, RMSE={r['rmse']:.3f}mm, arc={r['arc']:.1f}mm")
