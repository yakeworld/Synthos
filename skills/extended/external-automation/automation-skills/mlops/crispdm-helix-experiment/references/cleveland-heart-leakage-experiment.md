# Cleveland Heart Disease — CRISP-DM Helix 泄漏消融实验

## 实验日期
2026-06-05

## 数据集
| 属性 | 值 |
|:-----|:---|
| 来源 | UCI Machine Learning Repository |
| 样本量 | 303 |
| 特征数 | 13 |
| 患病率 | 45.9% (139/303) |
| 缺失值 | ca: 4个, thal: 2个 (用中位数填充) |

## 实验设计
4级泄漏梯度 × 3个模型 (LR, RF, GB) × 5折StratifiedCV

## 结果摘要

### LR (LogisticRegression)
| 泄漏等级 | F1 | Recall | AUC |
|:---------|:---|:-------|:----|
| Helix_Isolated | 0.8170 | 0.8056 | 0.9114 |
| SMOTE_Global | 0.8067 | 0.7984 | 0.9110 |
| SMOTE_Scale_Global | 0.8112 | 0.8056 | 0.9108 |
| All_Global | 0.8112 | 0.8056 | 0.9108 |

**泄漏效应**: Helix → All_Global: F1 **下降** -0.0058 (-0.7%)
**模式**: Negligible/反向 — 泄漏不增加F1，反而略降

### RF (RandomForest, n_estimators=100, max_depth=5)
| 泄漏等级 | F1 | Recall | AUC |
|:---------|:---|:-------|:----|
| Helix_Isolated | 0.8274 | 0.7984 | 0.9162 |
| SMOTE_Global | 0.8113 | 0.7910 | 0.9038 |
| SMOTE_Scale_Global | 0.8106 | 0.7907 | 0.9062 |
| All_Global | 0.8106 | 0.7907 | 0.9062 |

**泄漏效应**: Helix → All_Global: F1 **下降** -0.0168 (-2.0%)

### GB (GradientBoosting, n_estimators=100, max_depth=3)
| 泄漏等级 | F1 | Recall | AUC |
|:---------|:---|:-------|:----|
| Helix_Isolated | 0.7889 | 0.7907 | 0.8853 |
| SMOTE_Global | 0.7789 | 0.7619 | 0.8868 |
| SMOTE_Scale_Global | 0.7738 | 0.7545 | 0.8868 |
| All_Global | 0.7738 | 0.7545 | 0.8868 |

**泄漏效应**: Helix → All_Global: F1 **下降** -0.0151 (-1.9%)

## 与已有数据集对比

| 数据集 | N | 患病率 | Helix F1 | Leaky F1 | 差异 | 模式 |
|:-------|:-:|:------:|:--------:|:--------:|:----:|:----|
| PIDD | 768 | 34.9% | 0.6986 | 0.7657 | +9.6% | Recall Paradox |
| Cleveland Heart | 303 | 45.9% | 0.8274 | 0.8106 | -2.0% | Negligible/反向 |
| WDBC | 569 | 37.3% | 0.8140 | 0.8220 | +1.0% | Universal Inflation |

**关键发现**: 同一泄漏机制在不同数据集上表现截然不同。PIDD上泄漏产生 Recall Paradox (F1虚高+9.6%)；Cleveland Heart上影响 Negligible/反向 (F1略降-2.0%)；WDBC上仅轻微正向(+1.0%)。不可跨数据集推广泄漏损伤模式。

## 实验代码
Cleveland实验脚本: `/home/yakeworld/.hermes/scripts/cleveland-helix-experiment.py`
(已整合到主脚本，直接运行 `python3 cleveland-helix-experiment.py` 即可复现)

## 数据位置
原始数据: `/media/yakeworld/sda2/Synthos/outputs/papers/cleveland-heart-disease/data/processed.cleveland.data`
实验输出: `/media/yakeworld/sda2/Synthos/outputs/papers/cleveland-heart-disease/data/experiments.json`
