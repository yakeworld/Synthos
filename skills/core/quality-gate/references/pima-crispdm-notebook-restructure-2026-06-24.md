# PIMA CRISP-DM: Notebook结构重构 & 实验完整性审计

## 日期: 2026-06-24

## 问题诊断

### 1. Notebook + 独立脚本双轨冲突

原实验架构：
```
Notebook (crisp-dm-pima.ipynb)     独立脚本 (pima_definitive.py等)
  ├─ Block A: 教学演示 (Cells 2-17)  ├─ run_ensemble.py (GBC+LDA+LR)
  ├─ Block B: 手动CV原型 (Cell 18)   ├─ run_ablation.py (LDA 5x2 CV)
  ├─ Block C: Pipeline桥接 (Cell 20) ├─ run_cross_dataset.py
  ├─ Block D: 30模型基准 (Cell 21)   ├─ pima_definitive.py (8模型+消融)
  └─ Cells 22-25: 消融(重复4次)      └─ pima_correct_ablation.py
```

后果：
- 同一实验产生多个不一致JSON（definitive_ablation.json vs definitive_experiment.json）
- 论文作者手动转录数字时混淆GBC/LDA结果
- 论文Table 1说是30模型，definitive.py只跑8模型
- 论文说Ensemble=GBC+LDA+LR，实验跑的是GBC+LDA+SVC

### 2. EDA严重缺失

论文Methodology只有一段文字描述数据，无任何EDA可视化：
- 无零值分布柱状图
- 无特征分布直方图/KDE
- 无类别对比箱线图
- 无相关性热图
- 无缺失模式诊断

### 3. 无自动验证

- Notebook跑完后，没有人自动比对输出数字与论文声明的差异
- 论文修改数字后，旧数值残留在其他段落（如Abstract/Conclusion中的"catastrophic"叙事与新数值矛盾）

## 修复方案: 单一权威Notebook结构

```
crisp_dm_pima_unified.py → Run All → all_results.json → paper.tex数值参考
  │                                                                ↑
  ├─ Act 1: EDA (7张出版级矢量图)                                   │
  ├─ Act 2: 方法论教学演示                                           │
  ├─ Act 3: 生产实验 (27模型+Ensemble+消融+SHAP+XGBoost)            │
  ├─ Act 4: JSON汇总                                                │
  └─ Cell 24: 验证Cell — 输出paper.tex应匹配的权威数值 ───────────────┘
```

## 权威数值输出 (2026-06-24, sklearn 1.9.0, random_state=42, 10-fold CV)

### Baseline Top 5 (10-fold CV, fold-internal SMOTE)

| Model | Acc | Prec | Rec | F1 | AUC |
|:------|:---:|:----:|:---:|:--:|:---:|
| GradientBoostingClassifier | 0.7629 | 0.6420 | 0.7464 | **0.6868** | 0.8387 |
| LogisticRegression | 0.7603 | 0.6497 | 0.7165 | **0.6759** | 0.8373 |
| LinearDiscriminantAnalysis | 0.7629 | 0.6546 | 0.7091 | **0.6759** | 0.8370 |
| SVC | 0.7512 | 0.6250 | 0.7422 | **0.6758** | 0.8266 |
| RandomForestClassifier | 0.7616 | 0.6511 | 0.6973 | **0.6707** | 0.8228 |

### Ensemble (GBC+LDA+LR, soft voting)

| Metric | Mean | Std |
|:-------|:----:|:---:|
| F1 | 0.6857 | 0.0767 |
| Recall | 0.7389 | 0.1091 |
| Precision | 0.6493 | 0.0920 |
| Accuracy | 0.7642 | 0.0578 |
| AUC | 0.8467 | 0.0461 |

### Ablation Study (GBC, 4 Leakage Levels)

| Level | SMOTE | Impute | Scale | F1 | Rec | Prec | AUC |
|:------|:-----:|:------:|:-----:|:--:|:---:|:----:|:---:|
| No Leakage | fold | fold | fold | **0.6868** | **0.7464** | 0.6420 | 0.8387 |
| Minor Leakage | **global** | fold | fold | **0.6541** | **0.6269** | 0.6953 | 0.8344 |
| Medium Leakage | fold | **global** | **global** | **0.6743** | **0.7349** | 0.6276 | 0.8349 |
| Severe Leakage | **global** | **global** | **global** | **0.6439** | **0.6232** | 0.6771 | 0.8338 |

**Key finding**: Medium leakage (global impute+scale) was overstated in the original paper (claimed F1=0.6860 vs actual 0.6743). Only minor and severe leakage produce truly distinct patterns.

### SHAP Feature Importance (GBC TreeExplainer)

| Rank | Feature | Mean |SHAP| |
|:----:|:--------|:---:|
| 1 | Glucose | **1.073** |
| 2 | BMI | **0.631** |
| 3 | Age | **0.494** |
| 4 | DiabetesPedigreeFunction | 0.345 |
| 5 | Insulin | 0.226 |
| 6 | BloodPressure | 0.203 |
| 7 | Pregnancies | 0.172 |
| 8 | SkinThickness | 0.115 |

### Model Count Note (2026-06-24, updated with external frameworks)

- sklearn 1.9.0 `all_estimators(type_filter='classifier')` → **27 models** after filtering
  - AdaBoostClassifier and HistGradientBoostingClassifier: NOT meta-wrappers, work as standalone. Previous exclusion was a bug.
- External gradient boosting frameworks (all installed and benchmarked):
  - XGBoost (v3.3.0)
  - LightGBM (v4.6.0)
  - CatBoost (v1.2.10)
- **Total pool: 30 models** (27 sklearn + 3 external)

### CatBoost: Best Single Model

| Model | F1 | Rank |
|:------|:--:|:----:|
| **CatBoostClassifier** | **0.7067** | **1st** |
| GradientBoostingClassifier | 0.6882 | 2nd |
| Ensemble (GBC+LDA+LR) | 0.6857 | — |
| MLPClassifier | 0.6807 | 3rd |

**Finding**: CatBoost with default params significantly outperformed all sklearn classifiers and the hand-tuned ensemble. This suggests PIDD has non-linear patterns that CatBoost's ordered boosting captures better. Paper should mention CatBoost as the best single-model performer despite the ensemble being the primary proposed method.

**Note**: LightGBM (F1=0.6525) and XGBoost (F1=0.6237) underperformed GBC on this small dataset without hyperparameter tuning.

### Threshold Optimization

| Metric | Value |
|:-------|:-----:|
| Default threshold 0.50 F1 | 0.6868 |
| Best threshold 0.48 F1 | 0.6989 |
| Improvement | +0.0121 |

## 质量检查标准升级: G2.5实验完整性门

详见 quality-gate/SKILL.md 中的 G2.5 章节。

新增检查项：
| 子项 | 权重 | 检查内容 |
|:-----|:----:|:---------|
| 数值可追溯 | 10分 | 论文每个数字对应代码输出JSON |
| fold-level detail | 8分 | JSON包含每折完整记录 |
| 自动验证Cell | 7分 | Notebook有最终验证cell |
| EDA可视化 | 5分 | 至少3张实质性EDA图 |

不通过后果：总分上限50/100，不可标记可投稿。

## 与 ablation-leakage-implementation.md 的关系

本文件记录**具体实验数值和结果**（PIMA案例的画面）。`ablation-leakage-implementation.md` 记录**通用模式**（独立布尔开关控制泄漏级别）。两者互补：一个回答"PIMA具体值是什么"，一个回答"任何数据集的消融实验怎么做"。
