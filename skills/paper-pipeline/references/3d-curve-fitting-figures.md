# 3D Curve Fitting Figure Generation

> 适用于半规管(SCC)中心线、血管骨架、气道中心线、神经束等 3D 解剖曲线拟合的论文图表生成。

由 scc-mathematical-morphology (2026-05-28) 实战提炼。

## Iron Rules

1. **Fitted curve only over data's angular range** — 不要画完整 2π。数据通常只覆盖 ~160–200° 弧段。
2. **Residual lines** — 每个数据点到拟合曲线最近点的连线（灰色半透明，α=0.25）。
3. **Full 3D RMSE** — 用最近点欧氏距离，非 Z 分量或代数距离。
4. **view_init(elev=25, azim=-60)** — 解剖 3D 图的稳健起始视点。
5. **Color scheme**: raw data = #e74c3c, fitted curve = #2980b9, residuals = #95a5a6.

## 3D Reconstruction from Local Frame

```python
Rmat = np.column_stack([u, v, normal])  # 3×3 rotation matrix
fitted_3d = centroid + local_pts @ Rmat.T  # ✅ 矩阵乘法
```

## Curve Range Constraint

```python
thetas = np.arctan2(y_local/b, x_local/a)  # eccentric anomaly
theta_min, theta_max = thetas.min(), thetas.max()
pad = (theta_max - theta_min) * 0.05
t_fit = np.linspace(theta_min - pad, theta_max + pad, 300)
```

## Full 3D RMSE (Nearest-Point)

```python
true_rmse = 0
for pt in pts:
    dists = np.sqrt(np.sum((fitted_3d - pt)**2, axis=1))
    true_rmse += dists.min()**2
true_rmse = np.sqrt(true_rmse / len(pts))
```

## Multi-Panel Composite Figures (6×3, 3×6 Layout)

适用于多标本×多半规管的综合对比图（如 SCC 论文 Figure 2）。

### Layout Convention

```
用户偏好：6行（半规管）× 3列（标本）
  Row 0: AC bony       Col 0: micro-CT
  Row 1: AC membranous Col 1: 7T MRI
  Row 2: PC bony       Col 2: ICT
  Row 3: PC membranous
  Row 4: LC bony
  Row 5: LC membranous
```

### Top-Row Title Spacing

Top-row subplot titles (`set_title`) must use `pad=15` to avoid collision with the plot frame. Suptitle needs `y=0.96` and `tight_layout(rect=[0,0,1,0.97])` to create visual breathing room.

```python
fig = plt.figure(figsize=(16, 20))
for canal_idx in range(6):
    for sp_idx in range(3):
        ax = fig.add_subplot(6, 3, canal_idx*3 + sp_idx + 1, projection='3d')
        ...
        if canal_idx == 0:  # top row
            ax.set_title(sp_name, fontsize=11, fontweight='bold', pad=15)
        if sp_idx == 0:     # left column
            ax.text2D(-0.4, 0.5, label, transform=ax.transAxes,
                      fontsize=10, fontweight='bold', rotation=90, va='center')

plt.suptitle('Title', fontsize=16, fontweight='bold', y=0.96)
plt.tight_layout(rect=[0, 0, 1, 0.97])
```

### Caption Must Match Layout

When switching layout (3×6 → 6×3), update the caption text. Old caption describing "rows: specimens, columns: canals" will mislead readers in the new layout.

### Color Conventions

- Bony data points: `'#2c3e50'` (dark slate)
- Membranous data points: `'#e67e22'` (orange)
- Per-specimen curve colors: `['#3498db', '#e74c3c', '#27ae60']` (blue, red, green)

## Key Pitfalls

| Pitfall | Symptom | Fix |
|:--------|:--------|:----|
| Full 2π curve drawn | Curve extends far beyond data | Constrain to data theta range |
| RMSE = Z-component only | Value ~0.15mm but visual mismatch | Compute full 3D nearest-point RMSE |
| Algebraic vs geometric distance | `((x/a)²+(y/b)²-1)²` ≠ true error | Use Euclidean nearest-point |
| Sequential fit bias | Plane error bleeds into Z sinusoid | Try Levenberg-Marquardt joint optimization |
| matplotlib 3D perspective | Poor depth perception | view_init(elev=25, azim=-60), enlarge markers |
| **Missing cx/cy offsets in 3D reconstruction** | Fitted curve visibly shifts from data in composite figures | Reconstruction must include `cx*u + cy*v` (see below) |

## 🔴 Critical: 3D Reconstruction Must Include cx/cy Offsets

When reconstructing a 3D curve from fitted 2D parameters, the spiral center `(cx, cy)` in the local plane must be explicitly added back. **Omitting them anchors the curve at the data centroid instead of the spiral center, causing a systematic visual shift.**

### Correct Reconstruction

```python
cr_fit = cx + r_fit * np.cos(t_fit + rot)   # MUST include cx
cy_fit = cy + r_fit * np.sin(t_fit + rot)   # MUST include cy
curve_3d = centroid + cr_fit[:, None] * u[None, :] + \
                    cy_fit[:, None] * v[None, :] + \
                    z_fit[:, None] * normal[None, :]
```

### Wrong (curve anchors at centroid, not spiral center)

```python
# Missing cx, cy — curve is not correctly centered
curve_3d = centroid + r_fit*np.cos(t_fit+rot)[:, None]*u[None, :] + \
                      r_fit*np.sin(t_fit+rot)[:, None]*v[None, :] + ...
```

### Detection

Compare composite figure curves vs single-specimen figures. If curves in the composite are systematically offset while single-specimen figures look correct, the reconstruction is missing cx/cy. **实战**: 2026-05-28 SCC composite figure fix.
