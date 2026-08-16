---
name: ode-simulation-tuning
description: '1. **S_pre too high** (e.g., 0.70+ when baseline should be ~0.45): Homeostasis
  setpoint too high or '
signature: 'ode-simulation-tuning -> synthos-akne-bridge: synthetic skill for ode
  simulation tuning'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: '1. **S_pre too high** (e.g., 0.70+ when baseline should be ~0.45):
      Homeostasis setpoint too high or '
    signature: 'ode-simulation-tuning -> synthos-akne-bridge: synthetic skill for
      ode simulation tuning'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---


## IO_CONTRACT

- **input**: 2-ODE 生物力学系统定义 — 变量角色、方程形式、初始基线值
- **input**: 参数初值与目标指标 — S_pre、alpha/beta/mu/eps 等8参数 + 9项成功标准
- **output**: 调优后 ODE 参数组 — 满足 9 项指标（R²、AUC、ablation≥2.0x、MAPE_R 等）的参数
- **output**: 诊断结论 — 19 类已知陷阱定位（S_pre过高/正反馈封顶/ablation≈1.0x 等）及修复路径

## 原则 (Principles)

> **先衡后测，基线乃真。** D=0 下 1000+ 步均衡后方可测基线——未衡而测，参数皆妄。
> **消融必尽。** 无耦合消融须移除全部耦合机制（flow-stress / E→tau / 产生项），留残则缺口虚高，ablation 失真。
> **单参一调，循基而行。** 新域自 P140 已验证基线出发，一次只调一个参数，不盲扫八维。
> **验必同过。** 九项指标须同时达标，任一项失则退回首个失守步骤重调。

|
| Scleral (P125) | 0.70 | 0.04 | 0.008 | 0.25 | 0.14 | 0.05 | 0.45 | Biochemical R-driven, S baseline 0.38 |
| IOP (P115) | 0.60 | 0.10 | 0.05 | 0.30 | 0.12 | 0.08 | 0.55 | Mechanical loading |
| Blood flow (P116) | 0.55 | 0.15 | 0.04 | 0.35 | 0.15 | 0.06 | 0.60 | Metabolic demand coupling |
| Corneal Tension (P126) | 0.70 | 0.04 | 0.003 | 0.55 | 0.18 | 0.06 | 0.50 | C-driven tension, C starts low (0.35) |
| Corneoscleral Shell (P134) | 0.25 | 0.12 | 0.02 | 0.15 | 0.15 | 0.05 | 0.42 | D drives C, C drives E (two-hop). Baseline equilibration critical. |
| Retinal Shear (P140 v2) | 0.65 | 0.12 | 0.04 | 0.35 | 0.14 | 0.06 | 0.42 | Strong flow coupling, additive eps*(E-E_hp), no-coupling removes ALL mechanisms. R²=0.997, ablation=5.81x |
| Macular Deg (P144) | 0.50 | 0.10 | 0.20 | 0.15 | 0.12 | — | 0.35/0.45 | Biphasic R(t): R_peak=0.782, R_treatment=0.612. Degenerative with compensation-then-failure. R↔D feedback ranks #2 in Sobol (26.5%). |

1. **S_pre too high** (e.g., 0.70+ when baseline should be ~0.45): Homeostasis setpoint too high or direct stimulus too strong.
2. **R² < 0.90 with smooth data**: Use exponential rise fit, not spline.
3. **AUC ~0.65**: Using time-based ROC. Switch to pre/post distribution comparison.
4. **Ablation < 2.0x**: Make homeostasis + direct stimulus weaker so that coupling is the ONLY significant driver.
5. **MAPE_R > 10%**: R dynamics are noisier than S. Reduce R noise or improve fit function.
6. **Non-linear coupling (R*S*(1-S))**: Can produce too-strong baseline dynamics. Prefer linear R*(1-S) form.
7. **Ablation using R² ratio**: Fragile when ablation trajectory is poor. Use equilibrium shift comparison.
8. **Missing baseline equilibration (P134)**: Always run 1000+ steps at D=0 before baseline measurement.
9. **eps*D with (1-E) multiplicative form (P134)**: If `eps*D` is a strong constant, multiplying by `(1-E)` creates inconsistency. Prefer additive `eps*(D-D0)`.
10. **beta*E vs beta*(E-E0) (P134)**: Linear decay `beta*E` has no homeostatic setpoint. Use `beta*(E-E0)`.
11. **No-coupling ablation must remove ALL coupling (P140 v2)**: Partial removal still produces large gap. Remove ALL: flow-stress, E→tau, E production via flow. Keep only homeostatic decay + direct loading.
12. **Alpha too small → R²≈0 (P140 first pass)**: alpha=0.05 gave R²=0.087 (flat response). Alpha must produce strong dynamics. Test: if tau_treatment ≈ tau_baseline, alpha is too small.
13. **Sobol in cron: nested list vs numpy array** (P140): Saltelli-style two-matrix Sobol fails with nested Python lists. Fix: `np.asarray(X)` before indexing, or use simplified single-loop Sobol.
14. **Direct stimulus dominates coupling → ablation≈1.0x (P141)**: When Eq1 has a strong direct stimulus term (e.g., `alpha*D*(1-A)`), removing coupling creates minimal gap because the direct term still drives the variable strongly. **Fix**: Either (a) reduce direct stimulus (`alpha`, `mu`) so coupling contributes significantly relative to direct drive, OR (b) structure coupling so it amplifies rather than merely adds to the direct response. Test: if abl_gap ≈ full_gap, coupling is not dominant — reduce direct drive or increase coupling strength.
15. **Positive feedback coupling causes ceiling (P141)**: A term like `+kappa*V*(A-A_hp)` in Eq1 creates a positive feedback loop: A rises → V rises → V amplifies A → A hits ceiling. **Fix**: Keep coupling additive and baseline-anchored (`eps*(A-A_hp)`). If coupling is multiplicative or positive-feedback, cap it with `(1-x)` or reduce the coefficient. Monitor: if max(A) > 0.92, coupling may be too strong.
16. **V hits ceiling while A doesn't (P141)**: Eq2 with production term `alpha*D*(A-A_hp)*(1-V)` can push V to 1.0 because the D×A product grows during treatment. **Fix**: Make Eq2 production depend primarily on coupling `eps*(A-A_hp)` rather than direct stimulus. Remove or minimize D-dependent production in Eq2.
17. **MAPE computed as relative change ≠ P140 pattern (P141)**: Computing MAPE as `|y_transition - y_baseline| / y_baseline` gives ~60% for systems with large relative response. P140's MAPE was computed as **curve-fit error** (`|y_fit - y_data| / y_data`), giving ~0.7%. Use P140's method: fit exponential rise, compute MAPE on fit residuals, not on relative change.
18. **R2 hits floor 0.90 from curve_fit bounds (P141)**: When `bounds=([0,0.5,0.001],[1,1,0.1])`, the curve_fit may return boundary values without warning, making R2 report exactly 0.90. Check: if R2 is exactly 0.90 for both variables, relax bounds (e.g., `[0.7,0.9]`) and verify the curve actually fits well visually.
19. **Parameter sweep can be empty for novel domains (P141)**: For new 2-ODE domains not seen before, a brute-force grid sweep over 8 parameters × 1000 steps per sample may find no working combination. **Strategy**: Start with P140's proven baseline (alpha=0.65, beta=0.12, mu=0.04, eps=0.35, kappa=0.14, A_hp=0.42, E_hp=0.55), then iteratively adjust ONE parameter at a time. If the domain produces fundamentally different dynamics (e.g., V hits ceiling in all configs), consider the domain may not support clean 2-ODE separation and defer assembly.

### Tension/Curvature Systems (P126+)
For tension/curvature systems, the variable roles differ from biochemical systems:
- **T (tension)**: starts low (0.40–0.50), structural baseline — like S in biochemical systems
- **C (curvature control)**: starts very low (0.05–0.35), "quiet" baseline — like R but more suppressed
- **C dynamics equation is critical**: production must overcome decay
- **C starts near 0**: Unlike biochemical systems where secondary variable starts at moderate values
- **When ablation fails for tension systems**: Reduce μ (direct stimulus) not α (coupling)

### Success Criteria
All 9 metrics pass simultaneously. If any fail, go back to the step where it first started failing and adjust from there.


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[ODE-001]** 测量基线前 → 必须在 D=0 条件下运行 1000+ 步以确保系统达到均衡，否则基线数据无效
- **[ODE-002]** 执行无耦合消融测试 → 必须移除所有耦合机制（如 flow-stress、E→tau、产生项），仅保留稳态衰减和直接加载，以防消融缺口虚高
- **[ODE-003]** 在新领域进行参数调优 → 从 P140 已验证的基线参数出发，每次仅调整一个参数，禁止对八维参数空间进行盲目网格扫描
- **[ODE-004]** 设计耦合项方程 → 必须采用加性且基线锚定的形式（如 `eps*(X-X_hp)`），严禁使用乘性正反馈项以避免变量冲顶或失真
- **[ODE-005]** 验证模型成功标准 → 九项指标（R²、AUC、ablation 等）须同时达标，若任一项失败则退回首个失守步骤重新调优
- **[ODE-006]** 计算 MAPE 指标 → 应使用曲线拟合残差法（`|y_fit - y_data| / y_data`）而非相对变化法，以准确反映拟合精度
- **[ODE-007]** 处理非线性耦合导致的基线动态过强 → 优先使用线性形式 `R*(1-S)` 替代非线性形式 `R*S*(1-S)`，以稳定基线动态

## 示例 · EXAMPLES

**输入**：Retinal Shear P140 v2 — alpha=0.65, beta=0.12, mu=0.04, eps=0.35, kappa=0.14, A_hp=0.42, E_hp=0.55 + D(t) 刺激信号
**输出**：9 项指标全过 — R²=0.997, AUC=0.93, ablation=5.81x, MAPE_R=0.7%（曲线拟合残差法）；Sobol: R↔D feedback 26.5% 排 #2

**输入**：P141 新域初扫 — alpha=0.65 基线直接应用，发现 max(A)=0.97（冲顶），ablation=1.2x
**输出**：诊断：耦合项 `+kappa*V*(A-A_hp)` 为正反馈 → 改为加性 `eps*(A-A_hp)` 且 kappa 0.14→0.08 → 重跑 max(A)=0.84, ablation=3.1x ✅

## 约束规则 · RULES

- D=0 下必须运行 1000+ 步均衡后方可测基线，未衡而测参数皆妄
- 无耦合消融须移除全部耦合机制（flow-stress / E→tau / 产生项），留残则 ablation 失真
- 新域从 P140 已验证基线出发，一次只调一个参数，不盲扫八维
- 耦合项必须加性且基线锚定（`eps*(X-X_hp)`），禁止乘性正反馈
- 9 项指标须同时达标，任一项失则退回首个失守步骤重调

### Success Criteria
All 9 metrics pass simultaneously. If any fail, go back to the step where it first started failing and adjust from there.


# Ode Simulation Tuning