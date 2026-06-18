# PIDD 模型耗时存档（29模型 × 2折CV）

> 测得于 2026-06-01，Intel CPU本地环境。用于估算远程(Docker/GPU)执行耗时。
> 数据：PIDD (768行 × 8特征，患病率 34.9%)

## 原始计时

| 模型 | 耗时/折 | 失败 | 备注 |
|:-----|:-------:|:----:|:-----|
| XGBoost | 18.216s | | default n_estimators=100 |
| LightGBM | 9.871s | | default n_estimators=100 |
| MLPClassifier | 4.104s | | max_iter=2000 |
| CatBoost | 1.791s | | default iterations=1000 |
| Bagging | 0.758s | | n_estimators=10 default |
| RandomForest | 0.489s | | n_estimators=100 |
| ExtraTrees | 0.379s | | n_estimators=100 |
| GradientBoosting | 0.172s | | n_estimators=100 |
| AdaBoost | 0.100s | | n_estimators=50 |
| KNeighbors | 0.097s | | n_neighbors=5 |
| CalibratedSVC | 0.076s | | SVC + cv=3 |
| NuSVC | 0.045s | | probability=True |
| SVC | 0.040s | | probability=True |
| LabelSpreading | 0.026s | | |
| LabelPropagation | 0.018s | | |
| GaussianNB | 0.014s | | |
| LogisticRegression | 0.009s | | |
| DecisionTree | 0.009s | | |
| RidgeClassifier | 0.008s | | |
| SGDClassifier | 0.008s | | |
| NearestCentroid | 0.008s | | |
| BernoulliNB | 0.008s | | |
| LinearDiscriminant | 0.008s | | |
| PassiveAggressive | 0.007s | | |
| LinearSVC | 0.007s | | |
| ExtraTree | 0.007s | | |
| QuadraticDiscriminant | 0.007s | | |
| **RadiusNeighbors** | FAIL | ✅ | StandardScaler后固定半径内无邻居 |
| **ComplementNB** | FAIL | ✅ | 输入含负数（StandardScaler后） |

## 5×2 CV总耗时估算（PIDD）

| 模型 | 总耗时(10折) | 判断 |
|:-----|:-----------:|:----:|
| XGBoost | ~182s (3min) | 可接受 |
| LightGBM | ~99s (1.6min) | 可接受 |
| MLPClassifier | ~41s | 可接受 |
| CatBoost | ~18s | 可接受 |

## CDC 25K行放大估算

基于O(n)~O(n log n)复杂度估算：
- XGBoost: ~18s × (25000/768) ≈ **~10min+**
- LightGBM: ~10s × (25000/768) ≈ **~5min+**
- MLPClassifier: ~4s × (25000/768) × 迭代数 ≈ **~2-5min**
- 树模型(RF/ET): ~0.5s × (25000/768) ≈ **~16s+**
- 线性模型: ~0.008s × (25000/768) ≈ **~0.26s**

建议 CDC 策略：
- 快速模型（<1s/折 in PIDD）→ 全量5×2 CV
- 慢模型（XGBoost/LightGBM/MLP/CatBoost）→ 3×2 CV 或降采样到10K
- RadiusNeighbors/ComplementNB → 跳过

## 速率分类

| 类别 | 阈值 | 含哪些 |
|:-----|:----:|:-------|
| 🚀 极速 | <0.01s/折 | PassiveAggressive, LinearSVC, ExtraTree, QDA, Ridge, SGD, NearestCentroid, BernoulliNB, LDA |
| ⚡ 快速 | 0.01-0.1s/折 | LogisticRegression, DecisionTree, GaussianNB, LabelPropagation, LabelSpreading, SVC, NuSVC, CalibratedSVC, KNeighbors, AdaBoost |
| 🐢 中等 | 0.1-1.0s/折 | GradientBoosting, ExtraTrees, RandomForest, Bagging |
| 🐌 慢速 | >1.0s/折 | CatBoost, MLPClassifier, LightGBM, XGBoost |
| ❌ 失败 | — | RadiusNeighbors, ComplementNB |
