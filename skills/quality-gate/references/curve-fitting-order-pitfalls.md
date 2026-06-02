# Curve Fitting: Point-Ordering Pitfalls

## The Trap: `np.argsort(theta)` on Non-Monotonic Data

When fitting parametric curves (log spiral, ellipse, helix) to 3D centerline data, **the order of points matters**. A common mistake is using `np.argsort(theta)` to sort points by angle, which fails when:

1. **The curve spirals** (overlapping angular ranges)
2. **Points densely sample a closed/near-closed loop**
3. **The curve is non-planar** (projection onto best-fit plane creates angle overlap)

### Symptom
```
Canal        Correct RMSE   Wrong RMSE    Correct b      Wrong b
AC bony            0.1330       2.2700       0.0958       0.0958    ← RMSE inflated 17×
PC bony            0.2714       1.1359      -0.0191      -0.0463    ← b also wrong
PC memb            0.1704       2.1731      -0.0671      -0.0671    ← RMSE inflated 13×
LC bony            0.1745       0.8548       0.0052       0.0267    ← b also wrong
```

### Root Cause

`argsort(theta)` groups points at similar angular positions together, **breaking the anatomical continuity** of the centerline. For a spiral, points at θ=170° and θ=190° are anatomically adjacent on the curve but map to -170° and 170° in `arctan2`. Sorting by angle scatters them.

### Fix: Nearest-Neighbor Path

Always use **anatomical path ordering** (nearest-neighbor traversal along the point set) for the final fit:

```python
def nearest_neighbor_path(pts):
    """Build point ordering by repeatedly finding the closest unvisited point."""
    n = len(pts)
    visited = [False] * n
    path = [0]
    visited[0] = True
    current = 0
    while len(path) < n:
        dists = [np.linalg.norm(pts[current] - pts[j]) if not visited[j] else float('inf') for j in range(n)]
        nearest = np.argmin(dists)
        path.append(nearest)
        visited[nearest] = True
        current = nearest
    return path

# Then: use path to order points before fit
theta_path_order = theta_raw[path]
theta_unwrapped = np.unwrap(theta_path_order)  # monotonic
```

`argsort` is acceptable only during **center-finding grid search** (a coarse optimization step), never for the final parameter estimation.

## L0.5 Audit Check

Add this to data quality audits for any paper using parametric curve fitting:

- [ ] Locate all `np.argsort(theta)` or equivalent angle-sorting code
- [ ] Verify it is only used in coarse/auxiliary optimization, NOT in final parameter estimation
- [ ] Confirm the final fit uses nearest-neighbor path or explicit anatomical ordering

## References

- 2026-05-31 SCC paper audit: `gen_all_figures.py` had duplicate `fit_logspiral_3d` — the second (live) version used argsort, inflating RMSE from 0.13mm to 2.27mm on AC bony.
