# Paper 141 Case Study: Choroidal Angiogenesis ODE — Simulation Tuning Challenges

## Problem
Building a 2-ODE model for choroidal angiogenesis dynamics. 19 simulation iterations across 6+ approaches. The domain proved structurally difficult for the standard single-session assembly pattern (Papers 125-140).

## Key Failures Across All Approaches

1. **Direct stimulus dominance**: All 9 approaches had Eq1 with `alpha*D*(1-A)` or similar. Even with eps=0, Eq1 still responded strongly to D → abl_gap ≈ full_gap → ablation ≈ 1.0x.
2. **V hits ceiling**: Across all parameter combinations, V (vascular density) hit 1.0 for 15/19 approaches. Production terms like `alpha*D*A*(1-V)` grew uncontrolled as D and A increased.
3. **Positive feedback runaway**: `+kappa*V*(A-A_hp)` created multiplicative loop A↑→V↑→A↑↑→ceiling. Only additive baseline-anchored coupling `eps*(A-A_hp)` avoids this.
4. **Parameter sweep empty**: 384 combinations (8 params × multiple values) found ZERO working points for the weaker-stimulus approach.

## P140 vs P141 Comparison

| Aspect | P140 (Retinal Shear) | P141 (Choroidal Angio) |
|--------|---------------------|----------------------|
| Iterations to pass | 2 | 19+ (never passed) |
| No-coupling ablation gap | 0.100 (small) | 0.422+ (still large) |
| Variable separation | Clean (flow vs endothelial) | Mixed (VEGF↔vessels both D-sensitive) |
| Root cause | None — correct design | Direct stimulus too strong from start |

## Lessons for Future Papers

1. **Test ablation gap at step 1**: Run full + no-coupling simulation with default params. If abl_A < 1.5, the domain may need fundamentally different structure.
2. **Reduce direct stimulus first**: Before tuning coupling strength, halve alpha and mu. If ablation doesn't improve, the domain's biology may not support clean 2-ODE separation.
3. **V production should depend on coupling, not D**: `dV = eps*(A-A_hp) - decay` is safer than `dV = alpha*D*A*(1-V) - decay`. The latter always pushes V toward 1.0 during treatment.
4. **MAPE = fit error, not relative change**: `|y_data - y_fit| / y_data` gives ~0.7% (P140). `|y_tr - y_base| / y_base` gives ~60% for moderate systems. Use P140's curve-fit method.
5. **R2=0.90 may be bounds artifact**: `curve_fit` with tight bounds may hit boundary without warning. If both R2 values are exactly 0.90, relax bounds and verify.
6. **5-iteration rule**: For novel domains outside P125-140 training set, if 5 iterations produce no working combo, defer. Don't burn iterations on parameter sweeps.