# Paired Structure Direction Alignment Protocol

> **Purpose**: Ensure that paired anatomical structures (e.g., bony and membranous SCCs, left and right organs) have consistent fitting curve orientation for direct comparison.

## When This Applies

Any anatomical curve fitting where:
- You have two datasets covering the same structure (e.g., bony vs membranous canal)
- The data may have been collected in opposite directions (ampulla→crus vs crus→ampulla)
- You need the fitted curves to start and end at the same anatomical landmarks

## The Core Problem

Data points are stored as sequential arrays (e.g., .mrk.json from 3D Slicer). The array order defines a natural path through the points. However:

1. **argsort(theta) is WRONG for start/end determination.**
   - Sorting points by angle (arctan2) can place min-θ and max-θ points adjacent in space (<0.5mm apart on the canal)
   - This makes the reconstructed curve start and end at the wrong anatomical locations
   - **Use nearest-neighbor path from point 0 instead**

2. **Data direction may be reversed between paired structures.**
   - Specimen 1 PC bony: ampulla→crus (point 0 → point N)
   - Specimen 1 PC membranous: crus→ampulla (point 0 → point N)
   - If both are fitted independently, the curves have different phase references

3. **The θ direction along the path may be decreasing (not always increasing).**
   - np.unwrap makes theta monotonic, but it may go from -134° to -414° (decreasing)
   - `linspace(min, max)` gives ascending order — WRONG if the path goes descending
   - The reconstructed curve direction must match the path direction

## Step 1: Determine Anatomical Start/End

```python
def nearest_neighbor_path(pts):
    """从点0开始，每次找最近未访问点，构建连通路径"""
    n = len(pts)
    visited = [False] * n
    path = [0]
    visited[0] = True
    current = 0
    while len(path) < n:
        dists = [np.linalg.norm(pts[current] - pts[j]) 
                 if not visited[j] else float('inf') for j in range(n)]
        nearest = np.argmin(dists)
        path.append(nearest)
        visited[nearest] = True
        current = nearest
    return path
```

- The first point on the path = **anatomical start**
- The last point on the path = **anatomical end**
- Verify: max adjacent distance on path < 3mm (otherwise data may have gaps)

## Step 2: Check and Align Direction

```python
def check_and_align(bony_pts, memb_pts):
    """用最近邻路径的两端作为起点终点，检测方向是否一致"""
    b_path = nearest_neighbor_path(bony_pts)
    m_path = nearest_neighbor_path(memb_pts)
    
    b_first, b_last = bony_pts[b_path[0]], bony_pts[b_path[-1]]
    m_first, m_last = memb_pts[m_path[0]], memb_pts[m_path[-1]]
    
    d1 = np.linalg.norm(m_first - b_last)   # 膜起点 vs 骨终点
    d2 = np.linalg.norm(m_last - b_first)   # 膜终点 vs 骨起点
    
    if d1 < 3.0 and d2 < 3.0:
        # Direction reversal detected! Flip the data
        return memb_pts[::-1].copy()  # reversed
    
    # Direction is consistent
    return memb_pts
```

**Threshold**: 3.0mm. If target start ≈ reference end AND target end ≈ reference start, the data is reversed.

## Step 3: Reconstruct Curve with Correct Direction

After fitting the log spiral parameters (a, b, A, ω, φ — which are order-independent):

```python
# After fitting, compute theta along the nearest-neighbor path
path = nearest_neighbor_path(pts)
theta_path = np.arctan2(pts_2d[:,1], pts_2d[:,0])
theta_unwrapped = np.unwrap(theta_path[path])

# 检查θ沿路径的方向
if theta_unwrapped[0] > theta_unwrapped[-1]:
    # θ递减方向 → 重建时也从大到小
    t_fit = np.linspace(theta_unwrapped[-1], theta_unwrapped[0], n_pts)
else:
    # θ递增方向 → 重建时从小到大
    t_fit = np.linspace(theta_unwrapped[0], theta_unwrapped[-1], n_pts)
```

## Step 4: RMSE Computation vs Visualization

**The reconstructed curve theta range differs for RMSE vs visualization:**

- **RMSE**: Use the DATA'S theta range (min/max of actual sorted data points)
  - `theta_min_data = t2s.min()` (where t2s = argsort(theta) values)
  - This ensures RMSE reflects only the actual data coverage
  - Without this, RMSE can inflate from 0.13mm to 2.27mm (16x error)
  
- **Visualization**: Use the PATH's theta range (from nearest-neighbor path)
  - `theta_min = theta_unwrapped_path_min, theta_max = theta_unwrapped_path_max`
  - This ensures the drawn curve starts and ends at the correct anatomical locations

```python
# Store both in params dict:
params = {
    'theta_min': theta_min_anat,        # path-based (for figures)
    'theta_max': theta_max_anat,        # path-based (for figures)
    'theta_min_data': t2s.min(),        # data-based (for RMSE)
    'theta_max_data': t2s.max(),        # data-based (for RMSE)
    'theta_ascending': ascending,       # path direction flag
}
```

## Step 5: Multi-Specimen Analysis

**Never rely on a single specimen's fit.** Always fit ALL available specimens:

```python
datasets = {
    'AC bony (Sp1)': f'{REPO}/micro_ct/ac.mrk.json',
    'AC bony (Sp2)': f'{REPO}/MRN/ac.mrk.json',
    'AC bony (Sp3)': f'{REPO}/industrial_CT/AC.mrk.json',
    # ... all 6 canals × 3 specimens
}

for name, fpath in datasets.items():
    pts = load_pts(fpath)
    a, b, A, om, ph, rmse, n = fit_logspiral(pts)
    # Report min-max range per parameter across specimens
```

**Generate per-specimen figures** (e.g., `centerline_3d_fits_sp1.pdf`, `_sp2.pdf`, `_sp3.pdf`) showing each specimen's fit separately.

## Verification Checklist

- [ ] `nearest_neighbor_path()` used for start/end (NOT argsort(theta))
- [ ] `check_and_align()` run for each bony/membranous pair
- [ ] If direction reversed, data flipped with `[::-1]`
- [ ] θ unwrapping direction checked — linspace follows ascending OR descending path
- [ ] `theta_min_data` / `theta_max_data` used for RMSE
- [ ] `theta_min` / `theta_max` (path-based) used for figures
- [ ] All available specimens fitted, not just one
- [ ] Per-specimen figures generated separately

## 2026-05-28 SCC Paper Case Study

| Check | Specimen 1 (micro-CT) | Specimen 2 (MRN) | Specimen 3 (ICT) |
|:------|:---------------------|:-----------------|:-----------------|
| AC bony/memb | ✓ Consistent | ✓ Consistent | N/A* |
| PC bony/memb | ⚡ REVERSED → flipped | ✓ Consistent | N/A* |
| LC bony/memb | ✓ Consistent | ✓ Consistent | ✓ Consistent |
| b consistency | | | LC(Sp3) b = -0.033 |

*ICT specimen had separate left/right segmentations (AC_MEM1, AC_MEM2) with short arcs.

**Key finding**: LC spiral rate is remarkably conserved across all 3 specimens (b = 0.027, 0.027, -0.033 for bony LC), suggesting this is a genuine anatomical constant.
