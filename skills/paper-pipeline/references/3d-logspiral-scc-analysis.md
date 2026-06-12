# 3D Logarithmic Spiral SCC Centerline Morphology Analysis

## Pipeline Overview

```
Raw CT/Micro-CT → UNet segmentation → Centerline extraction (.npz)
    → SVD plane fit → 2D projection → Log-linear spiral fit
    → Nonlinear refinement → Sinusoidal out-of-plane fit
    → Canal-type b-value statistics → LR symmetry analysis
    → Cochlear comparison
```

## Model

**3D Logarithmic Spiral** (7 parameters):
```
r(θ) = O + R · (a·e^(bθ)·cosθ, a·e^(bθ)·sinθ, A·sin(ωθ+φ))ᵀ
```

| Param | Meaning | Anatomical interpretation |
|-------|---------|--------------------------|
| a | Spiral scale (mm) | Canal size / radius |
| b | Spiral growth rate | How tightly coiled; b=0 = circle |
| A | Torsion amplitude (mm) | Out-of-plane twist magnitude |
| ω | Torsion frequency | Twist periodicity |
| φ | Torsion phase | Twist start angle |

## Two-Stage Fitting Strategy

### Stage 1: Planar Log Spiral
1. Compute best-fit plane via SVD of centered point cloud
2. Build local orthonormal frame (u, v vectors in plane, n normal)
3. Project to 2D: convert to (u, v) coordinates
4. Compute polar angles θ = atan2(v, u) and radii r = sqrt(u² + v²)
5. Linearize: ln(r) = ln(a) + b·θ → least squares for initial (a, b)
6. Nonlinear refinement: minimize sum((r_predicted - r_actual)²) via Nelder-Mead for (a, b, cx, cy)

### Stage 2: Out-of-Plane Sinusoidal
1. Compute signed distance z = dot(centered_points, normal)
2. Fit z = A·sin(ωθ + φ) via nonlinear least squares
3. Multiple initializations: ω ∈ {0.5, 1.0, 2.0, 3.0}, φ ∈ {0, π/4, π/2}
4. Keep the solution with lowest residual

### 3D RMSE
Reconstruct full 3D curve from fitted parameters, compare to original points.

## Batch Processing

Script: `scripts/batch-3d-logspiral-fit.py`

Usage:
```bash
# Edit INPUT_GLOB and COORD_KEY at top of script
python3 scripts/batch-3d-logspiral-fit.py
```

### Expected Output Format
```json
{
  "metadata": {"total": 480, "success": 475, "failed": 5},
  "cases": {
    "CT215951_L": {
      "canals": {
        "superior": {"a": 2.33, "b": 0.096, "A": 0.21, "omega": 2.3, "phi": 0.3, "rmse_3d": 0.686, "arc_mm": 11.3, ...}
      }
    }
  }
}
```

## Analysis Statistics

### Canal-Type b Values (Human CT, 160 cases, 475 centerlines)

| Canal | N | b mean | b median | b std | Range |
|-------|---|--------|----------|-------|-------|
| Superior (AC) | 160 | 0.096 | 0.109 | 0.039 | [0.0002, 0.147] |
| Posterior (PC) | 156 | 0.032 | 0.017 | 0.039 | [0.0002, 0.158] |
| Lateral (LC) | 159 | 0.048 | 0.033 | 0.043 | [0.0003, 0.155] |
| All | 475 | 0.059 | 0.047 | 0.049 | [0.0002, 0.158] |

### Key Findings
- **Canal-type differentiation**: AC > LC > PC in spiral rate
- **LR symmetry**: Cohen's d < 0.25 for all canals
- **Cochlear overlap**: Mean b=0.059 falls within cochlear range (b≈0.02-0.08)
- **Non-planarity**: ~1.5% of arc length, conserved across tissue types
- **Micro-CT RMSE**: 0.07-0.17 mm (high-res reference)

## Common Pitfalls

1. **Posterior canal failures**: The posterior (PC) is hardest to segment (longest, curves near sigmoid sinus). Expect 2-3% failed fits.
2. **Anisotropic voxels**: MRI data requires spacing correction before centerline extraction.
3. **Combined labels**: Some segmentations don't separate the three canals. Need canal separation before fitting.
4. **b > 0.5**: Values above 0.5 indicate fitting failure (usually too few points or collinear points). Apply sanity filter.
5. **RMSE inflation in CT**: Clinical CT (0.5 mm voxels) gives RMSE ~0.6-0.7 mm vs micro-CT ~0.1-0.2 mm. This is expected.
