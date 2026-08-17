# GOLDEN_SET.md — ode-simulation-tuning

> 对应原则：P1（原子可复现性）/ P2（机械原子暴露输入输出规范）
> golden_set_origin: self_defined
>
> golden 三件套 = 本文件 + `cases/` + `expected/`。所有改进必须通过 golden 测试。

## 设计依据

本技能的输入是「2-ODE 生物力学系统定义 + 参数初值（8 参数）+ D(t) 刺激信号」，输出是「调优后参数组（满足 9 项指标）+ 19 类陷阱诊断结论」（见 SKILL.md IO_CONTRACT）。金标准目标：验证 9 项指标同时达标（R²、AUC、ablation≥2.0x、MAPE_R 等）、D=0 下 1000+ 步均衡后方可测基线（ODE-001）、消融移除全部耦合机制（ODE-002）、新域从 P140 基线出发单参调整（ODE-003）、耦合项加性基线锚定（ODE-004）、MAPE 用曲线拟合残差法（ODE-006）。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 参数集 | P140 v2（已验证基线） | alpha=0.65, beta=0.12, mu=0.04, eps=0.35, kappa=0.14, A_hp=0.42, E_hp=0.55 |
| 成功标准 | 9 项指标 | R²>0.90、AUC>0.85、ablation≥2.0x、MAPE<10% 等 |
| 均衡化 | D=0 下 1000+ 步 | ODE-001 |
| 错误路径 | 正反馈耦合冲顶 | 陷阱 15（P141）：max(A)>0.92、ablation<2.0x |

## 测试用例 (cases/)

### case_001: 正常路径 — P140 v2 已验证基线（Retinal Shear）
- **输入**: 8 参数（alpha=0.65, beta=0.12, mu=0.04, eps=0.35, kappa=0.14, A_hp=0.42, E_hp=0.55）+ 完整 2-ODE 方程 + D(t) 刺激信号（D=0 基线 → D=0.8 治疗）
- **期望**: 9 项指标全过 — R²=0.997、AUC=0.93、ablation=5.81x、MAPE_R=0.7%（曲线拟合残差法）；Sobol 排序输出（R↔D feedback 26.5% 排 #2）

### case_002: 错误路径 — 正反馈耦合冲顶（P141 陷阱 15）
- **输入**: 同 P140 参数但 Eq1 含乘性正反馈耦合项 `+kappa*V*(A-A_hp)`
- **期望**: 诊断 `max(A)=0.97`（>0.92 冲顶）且 `ablation=1.2x`（<2.0x 失败）；修复路径：耦合改为加性基线锚定 `eps*(A-A_hp)` 且 kappa 0.14→0.08，重跑后 max(A)=0.84、ablation=3.1x 通过

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_XXX.json`：
- case_001: `metrics`（9 项全过）+ `sobol_ranking` + `equilibration`（D=0 下 1000 步）
- case_002: `diagnosis`（陷阱 15 定位）+ `fix`（修复参数）+ `rerun_metrics`（修复后 9 项全过）

### 通过标准（判定规则）
1. `metrics` 中 9 项指标全部达到阈值（R²>0.90、AUC>0.85、ablation≥2.0x、MAPE<10%、accuracy>0.85 等）
2. `equilibration.steps >= 1000` 且 `equilibration.D == 0`（ODE-001）
3. `ablation.coupling_removed` 含全部耦合机制（ODE-002）
4. 错误路径 case：`diagnosis.trap` 精确匹配陷阱编号，`fix.rerun_metrics` 9 项全过

## pass_threshold: 1.00

机械原子（atom_type=mechanical），指标为确定性数值阈值 → 全部 case 必须通过。

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-13 | 初始自设金标准，2 个 case（正常 + 错误） | Synthos Agent |
