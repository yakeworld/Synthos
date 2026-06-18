# Parameter Mapping: Bony → Membranous Log-Spiral Parameters

> Generated: 2026-05-29, based on 9 paired datasets (3 specimens × 3 canals)
> Referenced by: `scc-bppv-kinematics` skill

## Data Correction Note

Three membranous annotations were split into multiple segments and required merging:

| Specimen | Canal | Segments | Gap | Merged |
|:---------|:------|:---------|:---:|:-------|
| sp3 ICT | AC | MEM1 (49pts, 7.2mm) + MEM2 (41pts, 8.3mm) | 0.00mm | AC_MEM_merged (90pts, 15.5mm) |
| sp3 ICT | PC | MEM1 (29pts, 6.1mm) + MEM2 (59pts, 9.1mm) | 0.00mm | PC_MEM_merged (88pts, 15.2mm) |
| sp1 microCT | LC | lc_mem (95pts, 12.3mm) + lc_mem2 (29pts, 4.2mm) | 0.22mm | LC_MEM_merged (124pts, 16.7mm) |

**Impact of LC fix on paper conclusions:**
- LC memb arc range: 12.3-13.6 → 12.5-16.7 (upper bound +23%)
- LC arc ratio: 0.97 (outlier) → 1.32 (consistent with sp2 1.26, sp3 1.39)
- LC memb A > bony A: previously sp1 was equal (0.166 vs 0.166), now 43% larger (0.238 vs 0.166)
- Wilcoxon test: p=0.25 → p=0.039 (now significant)
- Rank-biserial r: 0.67 → 0.78

## Method 1: Parameter Equation Transform

### Universal (cross-canal) mappings

| Parameter | Equation | r | p | Id-MAE | Lin-MAE |
|:----------|:---------|:-:|:--:|:------:|:-------:|
| a (mm) | memb = 0.93×bony + 0.70 | 0.927 | 0.0003 | 0.469 | **0.168** |
| b | memb = 0.78×bony − 0.058 | 0.814 | 0.008 | 0.068 | **0.041** |
| arc (mm) | memb = 0.91×bony + 3.76 | 0.885 | 0.002 | 2.666 | **0.759** |

### Per-canal corrections for non-significant parameters

| Parameter | AC r | PC r | LC r | Strategy |
|:----------|:----:|:----:|:----:|:---------|
| A (mm) | 0.812 | 0.975 | 0.997 | PC/LC use identity (MAE<0.04mm); AC flip sign |
| ω | 0.988 | 0.088 | 0.944 | AC/LC use identity; PC fixed ~2.5 |
| φ (°) | -0.888 | -0.992 | -0.816 | Per-canal phase offset; MAE 3-5° within canal |

### Basis vectors

The u, v, normal axes barely change from bony to membranous (<3°). They can be assumed identical.

## Method 2: Centerline Displacement Field D(s)

**Model**: `X_memb(s) = X_bony(s) + D_canal(s)`

where s ∈ [0,1] is normalized arc length, D(s) is the per-canal mean displacement field (200 samples).

### Leave-one-out cross-validation

| Canal | LOOCV RMSE | Per-specimen breakdown |
|:------|:----------:|:-----------------------|
| **PC** | **0.67mm** | sp1: 0.77, sp2: 0.51, sp3: 0.73 |
| **AC** | **0.80mm** | sp1: 0.79, sp2: 0.76, sp3: 0.85 |
| **LC** | **0.94mm** | sp1: 0.97, sp2: 0.96, sp3: 0.88 |

PC (Epley target) has the best prediction accuracy.

### Displacement field characteristics

| Canal | Mean |D| | Max |D| | Direction consistency | Max displacement location |
|:------|:----------:|:--------:|:--------------------:|:-------------------------|
| AC | 0.30mm | 0.46mm | 0.41 | s≈0.94 (near ampulla) |
| PC | 0.37mm | 0.53mm | 0.63 | s≈0.75 (mid-canal) |
| LC | 0.85mm (merged) | 1.70mm | 0.50 | s≈1.00 (end) |

## Clinical Translation

Given a new clinical CT scan:
1. Extract bony SCC centerline (manual or via UNet)
2. Fit 3D log-spiral model → get parameters (a, b, A, ω, φ, arc)
3. Apply parameter mapping to estimate membranous parameters
4. Apply D_canal(s) displacement field to refine centerline
5. Reconstruct predicted membranous SCC geometry
6. Use for patient-specific BPPV simulation/planning
