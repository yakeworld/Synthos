---
name: biomechanical-regulation-ode
description: "Class-level skill for building computational dynamical models of physiological regulation systems using 2-ODE systems with PINN training. Covers model formulation, bifurcation analysis, Sobol sensitivity, and ablation studies."
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

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

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
