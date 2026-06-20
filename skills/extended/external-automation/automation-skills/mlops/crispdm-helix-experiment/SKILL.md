---


name: crispdm-helix-experiment
description: CRISP-DM Helix methodology — strict CV-fold-isolated preprocessing for clinical ML experiments on public datasets. Generates real, traceable L0.5-compliant data.
version: 1.0.0
license: MIT
author: Synthos
allowed-tools:
- terminal
- read_file
- write_file
- search_files
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
    signature: 'dataset: str -> experiment_results: dict'
    related_skills:
    - experiment-recipes



---



## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# CRISP-DM Helix Experiment Pipeline

## 核心原则

**Helix隔离**：预处理必须严格在CV fold内部执行，防止数据泄漏。

```
原始数据
  ↓
CV Fold分割 (StratifiedKFold, n_splits=5-10)
  ↓
每折内部: 预处理(归一化/降采样/特征选择) → 训练 → 评估
  ↓
跨折汇总指标: mean ± std
```

## 标准模板

```python
import pandas as pd
from sklearn.model_selection import StratifiedKFold

df = pd.read_csv('data.csv')
X = df.drop(columns=['target'])
y = df['target']
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    # 预处理（在fold内部！）
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)  # 只用train拟合

    # 训练+评估
    # ...
```

## 泄漏模式对比实验

| 模式 | 预处理位置 | 预期效果 |
|:-----|:----------|:---------|
| Helix (正确) | 每折内部fit | 真实泛化性能 |
| No Leakage (理论) | 全部fit | 同上（预处理不影响CV） |
| Medium Leakage | 部分fit | 轻微高估 |
| Severe Leakage | 全局fit | F1虚高5-15% |

## 多数据集验证

同一代码管线运行于3+数据集，记录Helix vs Leaky对比：

| 数据集 | N | 患病率 | Helix F1 | Leaky F1 | 差异 |
|:-------|:-:|:------:|:--------:|:--------:|:----:|
| PIDD | 768 | 34.9% | 0.6986 | 0.7657 | +9.6% |
| Cleveland Heart | 303 | 45.9% | 0.8274 | 0.8106 | -2.0% |
| WDBC | 569 | 37.3% | 0.8140 | 0.8220 | +1.0% |

**注意**: 同一泄漏机制在不同数据集上表现截然不同（PIDD: Recall Paradox +9.6%, Cleveland: Negligible/反向 -2.0%, WDBC: Universal Inflation +1.0%）。不可跨数据集推广泄漏损伤模式。

## Notebook-to-Script Alignment Methodology

当用户要求「按照jupyter notebook流程和论文需要，认真完成每一个步骤的实验」时：

1. **完整读取notebook**：用`json.load()`读取.ipynb文件，遍历`nb['cells']`
2. **逐Cell解析**：区分markdown（跳过）和code（提取完整source）
3. **按顺序映射步骤**：Cell 0→N，记录每个Cell的输入/输出关系
4. **忠实还原**：不添加、不删除任何实验步骤；参数必须与notebook完全一致
5. **输出验证**：生成JSON + CSV + Python脚本，与notebook单元格一一对应

**关键陷阱**：
- 外部模型（XGBoost、LightGBM、CatBoost）不在sklearn.all_estimators()中，需单独添加
- `sklearn.metrics.make_scorer()`在sklearn 1.8+中required：不能直接传递函数引用，必须用`make_scorer(func, needs_proba=True)`
- CatBoost的`get_params()`返回空字典——使用`iterations`而非`n_estimators`
  - CatBoost默认1000次迭代→33模型×10折≈950秒。设`iterations=100`提速
  - **NumPy生态锁步升级**：shap/scipy/pandas/numexpr/bottleneck/numba等C扩展包必须numpy版本一致。升级numpy会同时破坏所有依赖（`AttributeError: module 'numpy' has no attribute 'long'`），降级numpy会破坏shap（`numpy.dtype size changed`）。遇到numpy相关ImportError时：①检查pip list中numpy版本 ②检查系统包`/usr/lib/python3/dist-packages/`中的numexpr/bottleneck是否也编译自旧numpy ③统一回退到兼容版本组合（numpy 1.26.4 + scipy 1.11.4 + pandas 2.1.4是已知安全组合） ④shap必须用虚拟环境隔离运行，因为系统numexpr（Debian包）无法通过pip移除且始终编译自旧numpy

## PIDD (PIMA) 基准结果

**33个模型 10-Fold CV Top 10 (F1排序):**

| 排名 | 模型 | F1 | Acc | AUC | Recall |
|:----:|:-----|:---|:----|:----|:-------|
| 1 | CatBoostClassifier | 0.7067±0.0794 | 0.7759 | 0.8422 | 0.7756 |
| 2 | GradientBoostingClassifier | 0.6857±0.0626 | 0.7616 | 0.8378 | 0.7464 |
| 3 | MLPClassifier | 0.6806±0.0584 | 0.7617 | 0.8286 | 0.7316 |
| 4 | LogisticRegression | 0.6759±0.0848 | 0.7603 | 0.8373 | 0.7165 |
| 5 | LinearDiscriminantAnalysis | 0.6759±0.0862 | 0.7629 | 0.8370 | 0.7091 |
| 6 | RidgeClassifier | 0.6759±0.0862 | 0.7629 | 0.8369 | 0.7091 |
| 7 | SVC | 0.6758±0.0654 | 0.7512 | 0.8266 | 0.7422 |
| 8 | AdaBoostClassifier | 0.6758±0.0337 | 0.7500 | 0.8287 | 0.7426 |
| 9 | NuSVC | 0.6756±0.0679 | 0.7512 | 0.8241 | 0.7420 |
| 10 | LogisticRegressionCV | 0.6749±0.0900 | 0.7589 | 0.8366 | 0.7164 |

**关键发现：** Top 10 F1差异极小（0.6749-0.7067），CatBoost领先约3%。LogisticRegression、LDA、Ridge的F1完全一致（0.6759）。Ensemble (LDA+GBC+LR soft voting) F1=0.6878，略优于单模型。PIMA数据太小（768样本），所有模型性能差异极小。

## 参考文件

- `references/helix-pipeline-template.py` — 完整Helix实验代码
- `references/cross-dataset-protocol.md` — 跨数据集验证协议
- `references/leakage-patterns.md` — 四种泄漏模式详解
- `references/cleveland-heart-leakage-experiment.md` — Cleveland Heart 泄漏消融实验（Negligible/反向模式）
- `references/notebook-to-script-alignment.md` — Notebook→Script对齐方法论
- `references/model-list-reconciliation.md` — Notebook模型清单与script硬编码清单的对齐方法论（含PIMA 33模型案例、已验证陷阱列表）
- `references/notebook-models-33-models-alignment.md` — PIMA 33模型对齐案例：notebook all_estimators()动态生成 vs helix硬编码清单的差异发现与修复过程