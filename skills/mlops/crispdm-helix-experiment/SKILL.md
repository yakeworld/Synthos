---
name: crispdm-helix-experiment
description: CRISP-DM Helix methodology — strict CV-fold-isolated preprocessing for clinical ML experiments on public datasets. Generates real, traceable L0.5-compliant data.
version: 1.0.0
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

## 参考文件

- `references/helix-pipeline-template.py` — 完整Helix实验代码
- `references/cross-dataset-protocol.md` — 跨数据集验证协议
- `references/leakage-patterns.md` — 四种泄漏模式详解
- `references/cleveland-heart-leakage-experiment.md` — Cleveland Heart 泄漏消融实验（Negligible/反向模式）