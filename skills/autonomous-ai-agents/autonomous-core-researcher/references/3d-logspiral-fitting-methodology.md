# 3D Logarithmic Spiral Fitting Methodology

## Model

```
r(θ) = O + R · (a·e^(bθ)·cosθ, a·e^(bθ)·sinθ, A·sin(ωθ+φ))^T
```

7 parameters: a (scale), b (spiral growth rate), A (torsion amplitude), ω (torsion frequency), φ (torsion phase), R (rotation matrix, 2 DOF), O (center offset, 3 DOF).

## Two-Stage Fitting

Stage 1 — Planar log spiral (time: ~0.5s):
1. SVD best-fit plane → normal vector
2. Project points to 2D in local frame
3. Linearized least squares: ln(r) = ln(a) + bθ
4. Non-linear refinement via Nelder-Mead

Stage 2 — Out-of-plane sinusoidal (time: ~0.5s):
1. z_dev = signed distance from best-fit plane
2. Minimize ||A·sin(ωθ+φ) - z_dev||² with 12 initializations (ω∈{0.5,1,2,3} × φ∈{0,π/4,π/2})
3. Select lowest residual

## Batch Processing Performance

| Dataset | Cases | Centerlines | Success | Time |
|:--------|:-----:|:-----------:|:-------:|:----:|
| CT manual labels | 160 | 480 | 475 (99%) | 48s |

## Model Comparison (AIC/BIC)

| Model | Params | AIC range | BIC range |
|:------|:------:|:---------:|:---------:|
| Planar Circle | 6 | -2 to 18 | 3 to 34 |
| Planar Ellipse | 8 | -239 to -13 | -215 to -5 |
| **3D Log Spiral** | **7** | **-504 to -61** | **-483 to -54** |
| HSMM-2 (sine ellipse) | 10 | -595 to -65 | -565 to -56 |
| Fourier(4) | 27 | 124 to 696 | 149 to 776 |
| Helix | 7 | -35 to 27 | -14 to 45 |

## Key Pitfalls

1. **NPZ smooth_mm vs smooth_voxel**: Use `smooth_mm` (3D coordinates in mm), NOT `smooth_voxel` (voxel indices).
2. **JSON serialization of numpy types**: np.float64 → float, np.ndarray → tolist(), otherwise json.dump fails.
3. **Curvature_filter parameter**: For CT data with noisy centerlines, set `curvature_filter_mm=0.8` (default 0.5) to avoid over-detecting kinks.
4. **Memory on batch**: 160 cases × 3 canals × 100 points = ~1.2M points. Fits in <500MB RAM.
