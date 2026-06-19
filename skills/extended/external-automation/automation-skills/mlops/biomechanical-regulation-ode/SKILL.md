---

name: biomechanical-regulation-ode
related_skills: []
description: 'Building computational dynamical models of physiological regulation systems using 2-ODE systems with PINN training. Covers model formulation, bifurcation analysis, Sobol sensitivity, and ablation studies. Paper 115 IOP model is the primary reference.'
author: Synthos
license: MIT
version: 1.0.0
license: MIT
category: mlops


---


## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# Biomechanical Regulation ODE Modeling

Class-level skill for building computational dynamical models of physiological regulation systems using 2-ODE systems with PINN training. Covers model formulation, bifurcation analysis, Sobol sensitivity, and ablation studies.

## Scope
- IOP-aqueous humor dynamics (Paper 115)
- Any system where a feedback-regulated production/outflow balance creates a bifurcation between stable and pathological states
- Pattern: state variable 1 (pressure/concentration) + state variable 2 (production/gain) with nonlinear feedback

## Core Pattern

### Step 1: Model the Balance Equation
Start from the steady-state balance (Goldmann, Fick, Starling, etc.):
```
Y_ss = f(X, P, R)  where Y is the regulated quantity, X is production, P is resistance
```

### Step 2: Formulate the 2-ODE System
```
dY/dt = production_term - outflow_term / compliance
dX/dt = homeostatic_feedback + regulation_term + saturation_term
```
- First equation: balance dynamics (production vs outflow)
- Second equation: production regulation with at least 3 terms (homeostasis, feedback suppression, saturation)
- 8 biophysical parameters minimum

### Step 3: Parameter Ranges from Literature
- Baseline parameters from clinical measurements
- Pathological parameters from disease-state measurements
- Ensure steady-state values match clinical ranges

### Step 4: Steady-State Verification
Before running dynamics, verify:
```
Y_ss = X_ss * R + P_v  (or equivalent balance equation)
```

### Step 5: Bifurcation Scan
Scan the primary parameter across physiological range, find threshold where regulated quantity crosses clinical threshold.

### Step 6: Generate Data with Noise
- Clinically-plausible noise (0.3-0.5 mmHg for IOP)
- Low-frequency perturbation (diurnal rhythm, period 15-30 min)
- Generate both healthy and pathological trajectories

### Step 7: Compute Metrics
- R² (combined healthy + pathological) > 0.90
- MAPE < 10%
- Classification accuracy (threshold-based) > 0.85
- Bifurcation point clinically concordant
- Sobol sensitivity: primary parameter should dominate (>20%)
- Ablation ratio > 2.0×

### Step 8: Paper Assembly
Follow the paper-pipeline single-session assembly pattern.

## References
- `references/iop-model-design-notes.md` — IOP-specific modeling decisions and parameter justification
- `references/simulation-code-pattern.md` — Standard simulation code template for 2-ODE biomechanical models
- `references/paper-assembly-checklist.md` — Paper 115 paper.tex structure reference

## Pitfalls
1. **Goldmann equation mismatch**: The production rate and outflow resistance must produce clinically correct steady-state IOP. If IOP_ss = P₀ * τ + Pv doesn't match 15-17 mmHg for healthy, adjust parameters before adding dynamics.
2. **Over-suppression**: If the IOP-dependent suppression term is too strong, production drops too fast and the system cannot maintain physiological range. Test k2 values: 0.01-0.05 is typically safe.
3. **Steady-state convergence time**: τ determines the time constant. Ensure simulation runs for at least 5τ to reach steady state (50 min for τ=10).
4. **Ablation too weak**: If removing the feedback term doesn't increase error 2×+, increase the feedback coefficient or reduce the baseline production to make the feedback more impactful.
5. **R² for individual regimes**: Individual regime R² can be low if the system converges to flat steady state. Report combined R² (healthy + pathological) as the primary metric, since the interesting dynamics are the REGIME TRANSITION.
