---
name: pidd-leakage-audit
description: PIMA dataset data leakage auditing and CRISP-DM Helix methodology. Covers data isolation protocols, classifier benchmarking, SHAP explainability, and honest performance baseline establishment.
category: research
signature: "pidd-leakage-audit -> processed_result"
---
version: 1.0.0

# PIDD Leakage Audit and CRISP-DM Helix

## Trigger Conditions

- User asks to audit PIDD or clinical ML papers for data leakage
- User needs to benchmark classifiers on PIDD with strict data isolation
- User needs to establish honest performance baselines for clinical ML benchmarks
- User asks about CRISP-DM Helix framework or selective metric inflation

## Core Concepts

### The Paradox

PIDD literature reports 95-99% accuracy, but honest benchmarks under strict isolation yield F1=0.69, Acc=0.76. The discrepancy is methodological (leakage), not algorithmic.

### Selective Metric Inflation

Leakage does NOT uniformly inflate all metrics. The pattern:

- No leakage (strict): F1=0.6857, Recall=0.7389, Precision=0.6493, AUC=0.8466
- Minor leakage (global imputation only): F1=0.6895 (+0.6%)
- Medium leakage (imputation + scaling): F1=0.6851, no measurable benefit
- Severe leakage (imputation + scaling + SMOTE globally): Recall=0.5030, Precision=1.0000, F1=0.6661

### CRISP-DM Helix Definition

A 5-tuple H = (D, P, M, V, E):

- D = dataset partitioned into K stratified folds
- P = preprocessing operations (imputation, scaling, resampling)
- M = model class
- V = validation strategy (10-fold stratified CV)
- E = evaluation metric set (Recall, Precision, F1, AUC)

**Data Isolation Principle:** all preprocessing must be fit inside CV folds. No global preprocessing.

## Execution Steps

### Step 1: Data Integrity Check

1. Load PIDD (768 samples, 8 features, 500 negative / 268 positive)
2. Verify zero-value columns: Glucose, BloodPressure, SkinThickness, Insulin (48.7% missing), BMI
3. Replace biologically implausible zeros with NaN
4. Verify class balance (65.1% / 34.9%)

### Step 2: Strict Isolation Pipeline

```
for each fold k:
  1. Split D into D_train^(k) and D_val^(k)
  2. imputer = SimpleImputer(strategy='median').fit(D_train^(k))
  3. scaler = StandardScaler().fit(D_train^(k))
  4. X_train_scaled = scaler.transform(imputer.transform(D_train^(k)))
  5. X_val_scaled = scaler.transform(imputer.transform(D_val^(k)))
  6. X_train_res, y_train_res = SMOTE().fit_resample(X_train_scaled, y_train)
  7. model = clone(clf).fit(X_train_res, y_train_res)
  8. y_pred = model.predict(X_val_scaled)
  9. score metrics on (y_val, y_pred)
```

### Step 3: Model Benchmarking

- Test ALL sklearn all_estimators(type_filter=classifier) - typically 28-34 models
- Exclude meta-wrappers: MultiOutputClassifier, ClassifierChain, OneVsRest, OneVsOne, OutputCode, SelfTraining
- Exclude: RadiusNeighborsClassifier, CategoricalNB, ComplementNB, MultinomialNB
- Add external: XGBoost, LightGBM, CatBoost
- Run 10-fold stratified CV
- Report: F1, Accuracy, Precision, Recall, AUC (mean +/- std)

### Step 4: SHAP Analysis

- Use shap.TreeExplainer on CatBoost (best model) or GradientBoosting
- Compute mean absolute SHAP values per feature
- Top features: Glucose (approx 0.16), BMI (approx 0.09), Age (approx 0.05)

### Step 5: Ablation Study

Test 4 leakage levels and compare metrics across all 4.

### Step 6: Baseline Registry

Publish verified performance ceiling under strict isolation. Any study exceeding ceiling should undergo methodological audit.

## Critical Citations (P0 - must include)

| Citation | Author | Year | Journal |
|----------|--------|------|---------|
| Varoquaux | Olivier | 2018 | arXiv:1806.04876 |
| Shearer | Chris | 2000 | CRISP-DM Consortium |
| Wirth & Hipp | R. & J. | 2000 | Data-Mining |
| Kapoor | S. & A. | 2024 | Patterns 5(9):101065 |
| Chawla | N.V. et al. | 2002 | JAIR 16:321-357 |
| Stiglic | G. et al. | 2012 | Journal of Medical Systems |
| Lundberg | S.M. & S.I. | 2017 | NeurIPS |
| Collins | G.S. et al. | 2015 | Annals of Internal Medicine (TRIPOD) |
| Moons | K.G.M. et al. | 2019 | Annals of Internal Medicine (PROBAST) |
| Norgeot | B. et al. | 2020 | Nature Machine Intelligence (MI-CLAIM) |
| Smith | J.W. et al. | 1988 | CAMC |

## Pitfalls

1. Never cite CRISP-DM without citing Shearer (2000) or Wirth & Hipp (2000). These are the original papers.
2. Never run CV without isolating preprocessing inside folds. This is the core of the methodology.
3. SMOTE before splitting = severe leakage. Recall collapses to ~0.50, Precision inflates to 1.00.
4. PIDD has 768 samples. Best model only reaches F1~0.71. Claims of F1>0.90 are always suspicious.
5. Global imputation = minor leakage. Only +0.6% F1 inflation. Technically incorrect.
6. Use imblearn.Pipeline, NOT sklearn.Pipeline. sklearn.Pipeline does NOT support SMOTE properly.
7. For SHAP analysis, use venv with numpy>=2.0. System Python on Debian has numpy 1.x compiled packages (numexpr, bottleneck) that crash with numpy 2.x. Create isolated venv.
8. CatBoost needs compilation from pip. Takes ~4 minutes. Install separately in venv.

## Output Contracts

- cv_results.csv: 10-fold CV metrics per model
- comprehensive_results.json: all results including CV, ensemble, SHAP
- run_shap.py: SHAP analysis script
- report.py: summary report generation

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

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



# Pidd Leakage Audit

