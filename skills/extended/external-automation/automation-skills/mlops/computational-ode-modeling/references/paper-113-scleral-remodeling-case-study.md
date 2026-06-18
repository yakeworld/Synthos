# Paper 113 — Scleral Remodeling ODE: Debugging Case Study

**Paper 113** (scleral-remodeling-ODE) was the most challenging ODE modeling task in the paper pipeline. 15+ debugging rounds before achieving a stable system.

## Timeline

- **v1-v7** (test_ode.py → test_ode7.py): Tried biochemical formulation (MMP, dopamine, synthesis, degradation). All failed — equilibrium never stable. Root cause: `synth + protect > degrad` at healthy S, so S always increased past 1.0.
- **v8** (test_ode8.py): Reformulated with `alpha*(S-S_eq)` spring term. Equilibrium perfect but basal spring too strong — all nonlinear terms dominated to zero.
- **Cubic breakthrough** (test_cubic.py): Switched to cubic polynomial `dS/dt = k*(S_high-S)*(S-S_unstable)*(S-S_low)`. This naturally gives double-well potential with saddle point.
- **Final fix** (test_ode9.py): Cubic had wrong root order: `k*(S-S_high)` instead of `k*(S_high-S)`. At S > S_high, wrong sign → runaway. Fix: `(S_high-S)` ensures S_high is an upper bound.

## Key Learning

**Never build complex biochemical formulations from scratch for a first draft.** Start with the simplest model that captures the desired qualitative behavior (cubic double-well), validate the dynamics, then layer in biochemical interpretation.

**Equilibrium check is the single most important diagnostic.** `ode(0, [S_eq, 0], p)` should return [~0, ~0]. If not, no amount of tweaking other terms will help.

## Results

- Stable equilibria: S_high=0.92 (healthy), S_low=0.40 (pathological)
- Saddle: S_unstable=0.65 (clinical threshold)
- Myopic progression: S drops from 0.60 to 0.40 over ~2 years
- Bifurcation confirmed: S0 just above/below 0.65 → different attractors
- Quality: MAPE < 4%, R² > 0.90, AUC = 1.0, accuracy = 0.77 (needs more subjects)

## Files Generated

- `test_ode.py` through `test_ode9.py` — iterative debugging
- `final_sim.py` — working model with all trajectories
- `generate_results.py` — quality metrics, sensitivity, ablation
- `quality.py` — final quality gate check
