# IOP Model Design Notes (Paper 115)

## Parameter Selection Rationale

### Goldmann Equation Structure
```
dIOP/dt = P(t) - (IOP - Pv) / τ
```
where Pv = 8 mmHg (episcleral venous pressure), τ = outflow time constant = R × C.

**Why this form**: The classic Goldmann equation IOP = P·R + Pv is a steady-state relation. The ODE version introduces compliance through the time constant τ, making it a proper dynamical model.

### Parameter Ranges
- τ: 3.0–25.0 min (healthy ~3-5, glaucoma ~10-20+)
- P₀: 0.5–1.5 mmHg/min (baseline production)
- k₁: 0.1–0.5 min⁻¹ (production feedback gain)
- k₂: 0.0–0.08 min⁻¹mmHg⁻¹ (IOP suppression)
- k₃: 0.2–0.8 mmHg/min (max production capacity)
- I₀: 12.0–18.0 mmHg (suppression setpoint)
- β: 0.01–0.1 mmHg⁻¹ (IOP suppression factor)

### Key Design Decisions

1. **k₂ = 0.04**: Chosen to give ~12.4× ablation ratio when removed. Small enough to be realistic (clinically, aqueous suppression at elevated IOP is modest), but large enough that removal dramatically changes dynamics.

2. **I₀ = 12 mmHg**: Set below normal IOP (15-17) so suppression is active even in the "healthy" range, making the feedback continuous rather than thresholded.

3. **P₀ = 1.3 mmHg/min**: Higher than clinical 0.3 µL/min because the ODE formulation uses pressure units (mmHg/min) rather than flow units. The steady-state relationship IOP_ss = P_ss × τ + Pv determines the effective P_ss.

4. **Exponential saturation term**: `k₃ × exp(-β × IOP)` provides smooth saturation of production at high IOP without discontinuous threshold.

## Common Design Patterns for Biomechanical Regulation

1. **Balance equation first**: Start with Y_ss = f(X, R). Work backwards to find parameter ranges.
2. **Feedback term**: At least 3 terms in the production ODE (homeostasis, feedback, saturation).
3. **Steady-state verification**: Before adding dynamics, verify steady-state values match clinical ranges.
4. **Bifurcation at clinical threshold**: The critical parameter value should correspond to a known clinical threshold.
5. **Sobol dominance**: The primary biophysical parameter (resistance, conductance) should explain >50% of variance.
