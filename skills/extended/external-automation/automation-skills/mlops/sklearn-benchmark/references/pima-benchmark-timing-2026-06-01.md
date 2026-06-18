# Pima PIDD 28-model 时序检测报告（2026-06-01）

**数据**：PIDD (768 rows, 8 features, 34.9% prevalence)
**协议**：5×2 CV (10 folds per model), ImbPipeline [Impute→Scale→SMOTE→clf]

## 预赛结果

### ❌ 失败模型（永久删除）

| 模型 | 失败原因 | 详情 |
|:-----|:---------|:------|
| RadiusNeighbors | 标准化后无邻居 | StandardScaler将特征映射到[-2,3]，默认radius=1.0，无点在半径内 |
| ComplementNB | 输入含负值 | StandardScaler产生负数，ComplementNB要求非负输入 |

### 🐌 慢模型分级（耗时/折）

| 模型 | 耗时(s)/折 | 5×2总耗时 | 分级 | CDC 25K判定 |
|:-----|:----------:|:---------:|:----:|:-----------:|
| XGBoost | 18.2 | ~182s (3min) | 🔴极慢 | ❌跳过 |
| LightGBM | 9.9 | ~99s (1.6min) | 🔴极慢 | ❌跳过 |
| MLPClassifier | 4.1 | ~41s | 🐌慢 | ❌跳过 |
| CatBoost | 1.8 | ~18s | 🐌慢 | ❌跳过 |
| Bagging | 0.76 | ~7.6s | ⚠️中 | ✅保留 |
| RandomForest | 0.49 | ~5s | ⚠️中 | ✅保留 |

### ⚡ 快模型（<0.5s/折，22个）

LogisticRegression, RidgeClassifier, SGDClassifier, PassiveAggressive,
SVC, NuSVC, LinearSVC, KNeighbors, NearestCentroid,
DecisionTree, ExtraTree, ExtraTrees, GradientBoosting, AdaBoost,
GaussianNB, BernoulliNB, LinearDiscriminant, QuadraticDiscriminant,
CalibratedSVC, LabelPropagation, LabelSpreading

### 最终模型清单（PIDD + ED共用 27个，CDC 23个）

```
PIDD/ED: 27 models (all except RadiusNeighbors, ComplementNB)
CDC:     23 models (skip XGBoost, LightGBM, MLPClassifier, CatBoost, CalibratedSVC)
```

## 基准结果摘要

| 数据集 | n | Prev | Top Model | F1 |
|:-------|:-:|:----:|:----------|:--:|
| PIDD | 768 | 34.9% | LinearSVC | 0.668 |
| Early Diabetes | 520 | 61.5% | ExtraTrees | 0.972 |
| CDC BRFSS | 25,368 | 13.8% | AdaBoost | 0.451 |
