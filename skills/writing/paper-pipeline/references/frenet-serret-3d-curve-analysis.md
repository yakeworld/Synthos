# Frenet-Serret 3D Curve Analysis Figure Workflow

> For generating publication-ready figures of 3D anatomical centerline data
> with curvature κ(s) and torsion τ(s) analysis panels.

## Figure Layout
- **Fig 1**: B-spline 3D rendering (6-panel 2×3) — raw points + smooth curve + residual lines
- **Fig 2**: κ(s) & τ(s) profiles (6-panel 2×3) — curvature solid, torsion dashed, x=normalized arc
- **Fig 3**: RMSE bar chart — Circle vs Planar Ellipse vs HSMM-2 vs B-spline

## Key Code
```python
# B-spline fit
tck, u = splprep(points.T, s=0.5, k=3)
curve = np.column_stack(splev(np.linspace(0,1,500), tck))

# 3D equal aspect (critical for honest visual)
mr = max(np.ptp(pts, axis=0)) / 2
mp = np.mean(pts, axis=0)
ax.set_xlim(mp[0]-mr, mp[0]+mr)
ax.set_ylim(mp[1]-mr, mp[1]+mr)
ax.set_zlim(mp[2]-mr, mp[2]+mr)
ax.view_init(elev=25, azim=-55)

# Frenet-Serret derivatives
d1 = np.gradient(curve, s, axis=0)
d2 = np.gradient(d1, s, axis=0)
d3 = np.gradient(d2, s, axis=0)
kappa = np.linalg.norm(np.cross(d1, d2), axis=1) / np.linalg.norm(d1, axis=1)**3
torsion = np.sum(np.cross(d1, d2) * d3, axis=1) / np.linalg.norm(np.cross(d1, d2), axis=1)**2
```

## Critical Pitfalls
1. **Fit curve to data's angular range only** — not full 2π ellipse
2. **Verify RMSE is full 3D geometric** — NOT just Z-component
3. **Use Taubin geometric ellipse** — not algebraic distance
4. **Equal aspect ratio** — without it, 3D plotting distorts shape
