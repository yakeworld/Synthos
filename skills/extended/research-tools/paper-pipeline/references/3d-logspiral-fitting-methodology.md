# 3D Logarithmic Spiral Fitting Methodology for SCC Centerlines

> Methodology developed during SCC mathematical morphology paper revision (2026-05-28).

## Core Principle: Data-Driven Adjacency Over Angular Sorting

The critical lesson: **never use `argsort(theta)` to determine curve start/end**. The anatomical start/end of a canal centerline must be determined by the nearest-neighbor path through points, not by angular sorting.

```python
# ❌ WRONG — sorts by angle, ignores anatomical connectivity
idx = np.argsort(theta)
theta_start, theta_end = theta[idx].min(), theta[idx].max()

# ✅ CORRECT — uses nearest-neighbor path to find true anatomical ends
def nearest_neighbor_path(pts):
    n = len(pts); visited = [False]*n; path = [0]; visited[0] = True; current = 0
    while len(path) < n:
        dists = [np.linalg.norm(pts[current]-pts[j]) if not visited[j] else float('inf') 
                 for j in range(n)]
        nearest = np.argmin(dists); path.append(nearest); visited[nearest] = True
        current = nearest
    return path

path = nearest_neighbor_path(pts)
theta_path = np.arctan2(pts_2d[:,1], pts_2d[:,0])
theta_unwrapped = np.unwrap(theta_path[path])  # monotonic along path
theta_start = theta_unwrapped[0]
theta_end = theta_unwrapped[-1]
# Reconstruct curve from start_theta to end_theta
t_fit = np.linspace(theta_start, theta_end, 500)
```

## Direction Alignment Between Bony and Membranous

When fitting paired data (bony + membranous of the same canal), check if data direction is consistent:

```python
def check_and_align(bony_pts, memb_pts):
    b_path = nearest_neighbor_path(bony_pts)
    m_path = nearest_neighbor_path(memb_pts)
    b_first, b_last = bony_pts[b_path[0]], bony_pts[b_path[-1]]
    m_first, m_last = memb_pts[m_path[0]], memb_pts[m_path[-1]]
    
    # If memb start ≈ bony end, direction is reversed
    if np.linalg.norm(m_first - b_last) < 3.0 and np.linalg.norm(m_last - b_first) < 3.0:
        return memb_pts[::-1].copy()  # flip
    return memb_pts
```

## Multi-Specimen Fitting

When 3 specimens exist (micro-CT, MRN, ICT), fit ALL of them, not just one. Store data in paper's `code/data/` directory organized by specimen.

## 🔴 Critical: 3D Reconstruction Must Include Spiral Center Offsets

After fitting the log spiral parameters `(a, b, A, ω, φ)` in the local 2D plane, the **reconstruction step must add back the spiral center offsets `(cx, cy)`**. This is the most common bug in 3D curve fitting scripts.

### Correct Reconstruction

```python
r_fit = a * np.exp(b * t_fit)            # log spiral radius
cr_fit = cx + r_fit * np.cos(t_fit + rot) # ← MUST include cx
cy_fit = cy + r_fit * np.sin(t_fit + rot) # ← MUST include cy
curve_3d = centroid + cr_fit[:, None] * u[None, :] + \
                    cy_fit[:, None] * v[None, :] + \
                    (A_s * np.sin(om_s * t_fit + ph_s))[:, None] * normal[None, :]
```

### Wrong (centroid-anchored)

```python
# ❌ Missing cx, cy: curve centered at data centroid, not spiral center
curve_3d = centroid + r_fit*np.cos(...)*u + r_fit*np.sin(...)*v + ...
```

### Detection

Compare composite multi-specimen figure against per-specimen figures. If curves in the composite are shifted away from data points while per-specimen figures are correct, cx/cy are missing.

## Check for Split Annotations

3D Slicer or other annotation tools may export a single centerline as multiple `.mrk.json` files (e.g., `AC_MEM1.mrk.json` + `AC_MEM2.mrk.json`). This happens when the user traced the canal from two opposite directions meeting at a midpoint.

**Detection**: Load both files and check if they share a common endpoint (distance < 0.01mm). If so, they are halves of the same centerline.

**Merge**:
```python
m1 = load_mrk('AC_MEM1.mrk.json')   # start→midpoint
m2 = load_mrk('AC_MEM2.mrk.json')   # other_end→midpoint  
merged = np.vstack([m1, m2[-2::-1]])  # MEM1 forward + MEM2 reversed, skip dup midpoint
```

**Impact**: Using only half the data produces unreliable spiral rate estimates (b=0.0026 or 0.5039 instead of 0.1929 for AC memb) and underestimates arc length (7.2mm → 15.5mm). Fitting a logarithmic spiral on a short arc segment (<8mm) produces near-circular or explosive spiral rates.

**Arc length sanity check**: Any centerline with arc length < 8mm is suspicious—check if it's a partial annotation that needs merging.

## Complete Pipeline

The full pipeline is in `code/regenerate_all.py`:
1. Load all .mrk.json files by specimen
2. For each canal: nearest-neighbor path → fit log spiral params → compute anatomical theta range → reconstruct → compute 3D RMSE
3. Direction-align bony/memb pairs
4. Report parameters

## Verification

- Each data point's 3D distance to fitted curve = true geometric RMSE
- `.mrk.json` is already nearest-neighbor ordered (verified: 0/33 points differ for PC bony)
- Run `python3 code/regenerate_all.py` to regenerate all figures
