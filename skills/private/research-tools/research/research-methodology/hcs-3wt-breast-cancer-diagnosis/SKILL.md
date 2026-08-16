---
name: hcs-3wt-breast-cancer-diagnosis
description: 1. 确认输入参数完整
signature: 'hcs-3wt-breast-cancer-diagnosis -> research-methodology: synthetic skill for hcs 3wt breast cancer diagnosis'
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
    description: 1. 确认输入参数完整
    signature: 'hcs-3wt-breast-cancer-diagnosis -> research-methodology: synthetic skill for hcs 3wt breast cancer diagnosis'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 
category: research-tools
signature: "hcs-3wt-breast-cancer-diagnosis -> research-tools: HCS-3WT (Hybrid Cascade-Stacking Three-Way Triage) breast cancer diagnostic"
description: HCS-3WT (Hybrid Cascade-Stacking Three-Way Triage) breast cancer diagnostic
author: Synthos
license: MIT
version: 1.1.0
allowed-tools:
- terminal
- read_file
- write_file
- search_files
metadata:
  synthos:
    signature: 'data_path: str -> diagnosis_report: dict'
    related_skills:
    - academic-paper-completion
    - adhd-eye-tracking-review
    - arxiv
    - biorxiv
    - blogwatcher

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

# HCS-3WT Breast Cancer Diagnostic AI System

Procedural knowledge for building, evaluating, and optimizing the HCS-3WT (Hybrid Cascade-Stacking Three-Way Triage) system for clinical breast cancer diagnosis.

## System Overview

HCS-3WT is a three-stage cascade classifier that structurally decouples diagnostic pathways:

- **Expert B (Catcher)**: High-recall SVC — Clear Negative if P(malignant) < 0.03
- **Expert A (Refiner)**: Voting Classifier (RF + CatBoost + ExtraTrees) — Clear Positive if P(malignant) > 0.95
- **Expert C (Arbiter)**: Meta-learning stacking classifier — handles Gray Zone cases

Key innovation: The system achieves 70.9% automation rate with 99.3% automation accuracy on WDBC (leakage-free 10x5 CV), with consistent risk-aligned gray zone enrichment across multiple datasets.

## Key Implementation Details

### Feature Engineering
Three novel features capture cytological atypia:
1. `size_shape_interaction`: cell_size_uniformity x cell_shape_uniformity
2. `nuclear_abnormality_score`: bare_nuclei + bland_chromatin + normal_nucleoli
3. `triple_product_score`: clump_thickness x marginal_adhesion x bare_nuclei

### Preprocessing Pipeline
- PowerTransformer (Yeo-Johnson) for distribution normalization
- SelectKBest (ANOVA F-stat) with domain-tailored feature subsets (4 for Expert B, 8 for Expert A)
- Borderline-SMOTE applied only to Expert B and Expert C training sets (NOT Expert A)

### Critical Pitfalls

**SMOTE Single-Class Crash**: Borderline-SMOTE requires at least 2 classes in training data. When running cross-validation on imbalanced or single-class datasets (e.g., Wisconsin Prognostic had 194 samples, 0 malignant), SMOTE will crash.

**Fix**: Before calling SMOTE, check `len(np.unique(y_train)) >= 2`. If only 1 class, skip SMOTE.

**SVC Single-Class Crash**: SVC also crashes when training data has only 1 class.

**Key check pattern**:
```python
n_train_classes = len(np.unique(y_train_cv))
n_test_classes = len(np.unique(y_test_cv))
if n_train_classes < 2 or n_test_classes < 2:
    continue
```

**HCS-3WT All Samples in Gray Zone (0% Automation Rate)**: If all samples end up in the Gray Zone, Expert B is giving all samples probability > low_threshold, and/or Expert A is giving all samples probability < high_threshold. Typically: thresholds are inappropriate for the data distribution. Fix: check probability histograms and adjust thresholds.

**Fixed Thresholds Fail on Low-Separability Datasets**: The default thresholds (theta_low=0.03, theta_high=0.95) calibrated on breast cancer data produce near-zero automation rates on datasets with overlapping feature distributions. PIMA diabetes confirmed this: only 8.58% automation rate with fixed thresholds vs 70-79% on breast cancer datasets. Root cause: SVC/VotingClassifier probability estimates on overlapping clinical data rarely reach 0.95 or 0.03. The architecture correctly defers (0 auto FN) but auto rate collapses.

Fix options:
1. Dataset-specific threshold optimization via cost function grid search
2. Adaptive thresholds via calibration curves (Platt scaling)
3. Relax thresholds (e.g. 0.20/0.80) for low-separability data
4. Document as honesty signal: low auto rate = feature space has poor class separation

Diagnostic: if auto rate drops below 10% on a new dataset, check probability histograms. If >90% of probabilities fall in [0.03, 0.95], the feature space lacks separation for the default thresholds.

**Cross-Validate Meta-Features to Prevent Leakage**: Use cross_val_predict for P_A and P_B features fed to Expert C. Training meta-features on the same data used for testing creates data leakage.

**Long-Running Experiments**: WDBC 10x5 CV (50 folds) takes ~190s. PIMA 10x5 CV takes ~189s. Always use background execution for long experiments.

**SVC probability=True Deprecated in sklearn 1.9+**: Use `CalibratedClassifierCV(SVC(), ensemble=False)` instead. Handle both old and new APIs:
```python
try:
    from sklearn.calibration import CalibratedClassifierCV
    base = SVC(kernel='rbf', class_weight='balanced', random_state=RS)
    catcher = CalibratedClassifierCV(base, ensemble=False)
except ImportError:
    catcher = SVC(kernel='rbf', probability=True, ...)
```

## Cross-Domain Validation (Confirmed Experimental Data, 2026-06-25)

The system has been rigorously evaluated with leakage-free 10x5 stratified CV, all with fixed thresholds theta_low=0.03, theta_high=0.95:

- **WBC Original** (UCI): 699 samples, 9 features. 79.07%+-4.19% automation rate, 99.35%+-0.71% auto accuracy. Gray zone (20.93%) with 1.22x malignant enrichment. HCS-3WT accuracy 0.9657. FN reduction vs best single (SVC): -28.0%.
- **WDBC** (Wisconsin Diagnostic Breast Cancer, sklearn): 569 samples, 30 features. 70.93%+-6.44% automation rate, 99.26%+-0.95% auto accuracy. Gray zone (29.07%) with 1.21x enrichment. HCS-3WT accuracy 0.9475. FN reduction vs best single (SVC): -47.7%.
- **Pima Indians Diabetes** (auxiliary): 768 samples, 8 features. **8.58%+-2.03% auto rate** with fixed thresholds. Shows threshold sensitivity (see pitfall above). Auto accuracy 99.38% with 0 auto FN. Gray zone 1.77x enrichment.
- **Wisconsin Prognostic**: 194 samples, 32 features. Single class (all benign) — must be skipped.

## Files

- `run_hcs3wt.py` — Main WDBC experiment script (10x5 CV, 50 folds)
- `run_hcs3wt_wbc_original.py` — WBC Original experiment script
- `run_hcs3wt_pima.py` — PIMA cross-domain experiment script
- `experiment_results.json` — WDBC results
- `experiment_results_wbc_original.json` — WBC Original results
- `experiment_results_pima.json` — PIMA results

## References

- `references/error-transcript.md` — Common errors and fixes encountered during development

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

# Hcs 3Wt Breast Cancer Diagnosis---

> (P032 去重: 以下为合并前第二份中的 1 行独有内容, 保留以防丢失)
# Hcs 3Wt Breast Cancer Diagnosis
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[HCS-001]** 训练数据仅包含单一类别 → 跳过 SMOTE 和 SVC 训练步骤，直接跳过该折以避免崩溃
- **[HCS-002]** 自动化率低于 10% 且概率分布集中在 [0.03, 0.95] → 判定特征空间分离度不足，需调整阈值或记录为诚实信号
- **[HCS-003]** 构建 Expert C 的元特征 (P_A, P_B) → 必须使用 cross_val_predict 生成特征以防止数据泄漏
- **[HCS-004]** 执行 10x5 交叉验证等长耗时实验 → 始终使用后台执行以避免会话超时
- **[HCS-005]** 使用 sklearn 1.9+ 版本且需 SVC 概率输出 → 使用 CalibratedClassifierCV 替代已弃用的 probability=True 参数
- **[HCS-006]** 应用 Borderline-SMOTE 预处理 → 仅应用于 Expert B 和 Expert C 的训练集，严禁应用于 Expert A
- **[HCS-007]** 面对低可分性数据集（如 PIMA） → 采用数据集特定的阈值优化或放宽阈值（如 0.20/0.80）而非固定默认阈值