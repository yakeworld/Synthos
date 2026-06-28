# Jupyter Notebook ↔ Helix Benchmark 对齐检查清单

## 对齐原则
helix_benchmark.py 的模型清单必须与 Jupyter notebook 的 `all_estimators(type_filter='classifier')` 输出完全一致。

## 完整模型清单（Notebook 30 个 sklearn 分类器）

```
1.  AdaBoostClassifier          16. LogisticRegression
2.  BaggingClassifier           17. LogisticRegressionCV
3.  BernoulliNB                 18. MLPClassifier
4.  CalibratedClassifierCV      19. NearestCentroid
5.  DecisionTreeClassifier      20. NuSVC
6.  DummyClassifier             21. PassiveAggressiveClassifier
7.  ExtraTreeClassifier         22. Perceptron
8.  ExtraTreesClassifier        23. QuadraticDiscriminantAnalysis
9.  GaussianNB                  24. RandomForestClassifier
10. GaussianProcessClassifier   25. RidgeClassifier
11. GradientBoostingClassifier  26. RidgeClassifierCV
12. HistGradientBoostingClassifier 27. SGDClassifier
13. KNeighborsClassifier       28. SVC
14. LabelPropagation           29. LinearDiscriminantAnalysis
15. LabelSpreading             30. LinearSVC
```

## Notebook 过滤规则
1. 跳过 `_` 前缀的类
2. 跳过 meta wrappers：MultiOutputClassifier, ClassifierChain, OneVsRestClassifier, OneVsOneClassifier, OutputCodeClassifier, SelfTrainingClassifier
3. 跳过 sklearn.multiclass 和 sklearn.multioutput 模块
4. 手动移除：RadiusNeighborsClassifier, CategoricalNB, ComplementNB, MultinomialNB
5. 实例化失败的自动跳过

## 常见不一致模式

| Notebook 有 | Helix 缺 | 原因 |
|-------------|----------|------|
| DummyClassifier | — | Notebook 用 all_estimators() 自动包含，helix 手写清单漏掉 |
| GaussianProcessClassifier | — | 同上 |
| HistGradientBoostingClassifier | — | 同上 |
| Perceptron | — | 同上 |
| LogisticRegressionCV | — | 同上（与 LogisticRegression 成对） |
| RidgeClassifierCV | — | 同上（与 RidgeClassifier 成对） |

| Helix 有 | Notebook 无 | 原因 |
|----------|-------------|------|
| LightGBM | — | Helix 自行添加的外部库 |
| CatBoost | — | 同上 |

| Notebook | Helix | 需替换 |
|----------|-------|--------|
| CalibratedClassifierCV | CalibratedSVC | Notebook 用通用包装器，helix 写成了具体封装 |

## 对齐后正确清单（30 sklearn 模型）
1-24. 上述 notebook 的 30 个 sklearn 分类器（按字母序）
+ 外部库：XGBoost（notebook Cell 29-30 运行）
+ 集成：VotingClassifier（notebook Cells 24-28 运行）