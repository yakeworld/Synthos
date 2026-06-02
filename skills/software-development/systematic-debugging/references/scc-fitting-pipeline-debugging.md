# SCC Fitting Pipeline Debugging (2026-05-31)

## Session Summary

Found a bug in `gen_all_figures.py` where two duplicate `fit_logspiral_3d()` functions existed. The second (last-defined, which Python uses) used `np.argsort(theta)` instead of nearest-neighbor path ordering for the log-spiral fitting, producing wrong RMSE values (2.27mm vs correct 0.13mm for AC bony).

## Detection Method

1. **Function duplication check**: `grep -n "^def fit_logspiral\|^def nearest_neighbor" gen_all_figures.py` showed two definitions of both `fit_logspiral_3d` and `nearest_neighbor_path`.

2. **Side-by-side comparison**: Wrote `compare_fitting.py` that runs both implementations on identical data and outputs a comparison table.

3. **Key diagnostic metric**: RMSE difference > 2x between implementations is a red flag for algorithm divergence, not numerical noise.

## Root Cause

The second `fit_logspiral_3d` (line 176, the active one) used:
```python
it2 = np.argsort(t2); t2s, r2s = t2[it2], r2[it2]  # WRONG - sorts by angle
```

Instead of:
```python
theta_path_order = theta_raw[path]  # CORRECT - follows anatomical path
r_path_order = r2[path]
```

For spiral data, points at similar angles but different positions on the spiral get mixed by argsort, producing wrong fits.

## Affected Figures

- `centerline_3d_fits_sp1/sp2/sp3.pdf` (supplementary) — regenerated
- `centerline_all_specimens.pdf` (Fig 3) — was correct (gen_composite_figure.py used path ordering)

## Fix Applied

- Removed duplicate function (lines 73-167, first def)
- Fixed remaining function to use `theta_raw[path]` ordering
- Updated OUT_DIR from `figures/` to `05-figures/`

## Pipeline Architecture

| Script | Fitting Method | Status |
|--------|---------------|--------|
| `gen_all_figures.py` | NN-path (after fix) | ✅ Fixed |
| `gen_composite_figure.py` | NN-path | ✅ Correct |
| `generate_figures.py` | Separate implementations | ⚠️ Not used for log spiral |
| `fit_logspiral_aligned.py` | NN-path + direction alignment | ✅ Reference |
| `fit_all_three.py` | NN-path | ✅ Reference |
