"""Fast batch centerline extraction + log spiral fitting for MRI (semical_lab_smooth)."""
import os, sys, glob
import numpy as np
import nibabel as nib
import pandas as pd
from scipy.optimize import minimize

# === Config (customize per dataset) ===
LABEL_DIR = '/mnt/nfs/UNet_Seg/Gao/step2/evaluate/zhoumi/semical_lab_smooth'
OUT_CSV = './batch_logspiral_params_MRI.csv'
SUFFIX = '_lab.nii.gz'
REJECTION_RATIO = 0.40

def fit_one_curve(pts):
    """Two-stage fast fit: SVD-plane LSQ + light Nelder-Mead refinement."""
    if len(pts) < 10:
        return None
    centroid = pts.mean(axis=0)
    c = pts - centroid
    
    U, S, Vt = np.linalg.svd(c, full_matrices=False)
    normal = Vt[2, :] / np.linalg.norm(Vt[2, :])
    ref = np.array([1, 0, 0]) if abs(normal @ [1, 0, 0]) < 0.9 else np.array([0, 1, 0])
    u = np.cross(normal, ref); u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    x = c @ u; y = c @ v; z = c @ normal
    
    # Stage 1: planar log spiral via linear LSQ
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    valid = r > 0
    if valid.sum() < 5:
        return None
    theta_v, r_v = theta[valid], r[valid]
    coeff = np.linalg.lstsq(np.column_stack([np.ones_like(theta_v), theta_v]),
                             np.log(r_v), rcond=None)[0]
    a0, b0 = np.exp(coeff[0]), coeff[1]
    
    # Stage 2: sine fit (light)
    def sin_obj(params):
        A, om, ph = params
        return np.mean((z - A * np.sin(om * theta + ph))**2)
    best = (1e8, None)
    for om_init in [1.0, 2.0, 3.0, 4.0]:
        for ph_init in [0, np.pi/4, np.pi/2]:
            res = minimize(sin_obj, [0.2, om_init, ph_init], method='Nelder-Mead')
            if res.fun < best[0]:
                best = (res.fun, res.x)
    A0, om0, ph0 = best[1]
    
    # Stage 3: full 3D (lightweight)
    def full3d(params):
        a, b, cx, cy, A, om, ph = params
        if a <= 0: return 1e8
        th = np.arctan2(y - cy, x - cx)
        pred_x = a * np.exp(b * th) * np.cos(th)
        pred_y = a * np.exp(b * th) * np.sin(th)
        pred_z = A * np.sin(om * th + ph)
        return np.mean((x - pred_x)**2 + (y - pred_y)**2 + (z - pred_z)**2)
    
    res = minimize(full3d, [a0, b0, 0, 0, A0, om0, ph0],
                   method='Nelder-Mead', options={'maxiter': 2000})
    a_f, b_f, cx_f, cy_f, A_f, om_f, ph_f = res.x
    
    # RMSE
    th_f = np.arctan2(y - cy_f, x - cx_f)
    pred_x = a_f * np.exp(b_f * th_f) * np.cos(th_f)
    pred_y = a_f * np.exp(b_f * th_f) * np.sin(th_f)
    pred_z = A_f * np.sin(om_f * th_f + ph_f)
    rmse = np.sqrt(np.mean((x - pred_x)**2 + (y - pred_y)**2 + (z - pred_z)**2))
    arc_len = float(np.sum(np.sqrt(np.sum(np.diff(pts, axis=0)**2, axis=1))))
    
    return {'a': a_f, 'b': b_f, 'A': A_f, 'om': om_f,
            'ph_deg': np.degrees(ph_f), 'rmse': rmse,
            'arc_mm': arc_len, 'n_pts': len(pts)}

# === Main ===
files = sorted(glob.glob(os.path.join(LABEL_DIR, f'*{SUFFIX}')))
print(f"Found {len(files)} files in {LABEL_DIR}")

results = []
for idx, f in enumerate(files):
    case = os.path.basename(f).replace(SUFFIX, '')
    try:
        nii = nib.load(f)
        data = nii.get_fdata()
        spacing = nii.header.get_zooms()[:3]
        from clean_centerline import extract_centerlines
        res = extract_centerlines(data, spacing, ampulla_rejection_ratio=REJECTION_RATIO,
                                   smooth_n_pts=100, use_curvature_trim=True)
        al = res.arc_lengths
        
        # Determine side
        side = 'R' if '_R' in case else 'L'
        
        for cname, label in [('superior', 'ac'), ('posterior', 'pc'), ('lateral', 'lc')]:
            pts = getattr(res, cname)
            params = fit_one_curve(pts)
            if params:
                results.append({'case_id': case, 'side': side, 'canal': label, **params})
        
        if (idx + 1) % 20 == 0:
            pd.DataFrame(results).to_csv(OUT_CSV, index=False)
            print(f"  [{idx+1}/{len(files)}: {len(results)} rows saved]")
    except Exception as e:
        print(f"  FAIL {case}: {e}")

if results:
    pd.DataFrame(results).to_csv(OUT_CSV, index=False)
    print(f"\nDone! {len(results)} results → {OUT_CSV}")
