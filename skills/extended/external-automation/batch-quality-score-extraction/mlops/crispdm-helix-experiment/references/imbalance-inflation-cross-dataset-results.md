# 类不平衡驱动的F1膨胀——跨数据集实验结果

## 实验设计

- **日期**: 2026-05-31
- **方法**: 5×2 CV（Helix vs Leaky 对比）
- **模型**: LogisticRegression（基线）+ XGBoost（验证模型无关性）
- **数据集**: PIDD / Early Diabetes / CDC BRFSS 2015
- **Helix**: 折叠内fit(imputer + scaler + SMOTE)
- **Leaky**: 全局fit(全数据imputer + scaler + SMOTE)

## 结果：LogisticRegression

| 数据集 | n | 患病率 | Helix F1 | Leaky F1 | Inflation | Λ |
|:-------|:-:|:------:|:--------:|:--------:|:---------:|:-:|
| PIDD | 768 | 34.9% | 0.664 | 0.738 | **+11.1%** | 0.001 |
| Early Diabetes | 520 | 61.5% | 0.930 | 0.915 | -1.6% | 0.000 |
| CDC BRFSS | 50,000 | 13.8% | 0.444 | 0.768 | **+73.2%** | 0.000 |

## 结果：XGBoost

| 数据集 | n | 患病率 | Helix F1 | Leaky F1 | Inflation |
|:-------|:-:|:------:|:--------:|:--------:|:---------:|
| PIDD | 768 | 34.9% | 0.644 | 0.796 | **+23.6%** |
| Early Diabetes | 520 | 61.5% | 0.959 | 0.959 | +0.0% |
| CDC BRFSS | 30,000 | 13.8% | 0.394 | 0.906 | **+129.9%** |

## 关键发现

1. **模式模型无关**: LR和XGBoost均显示F1膨胀∝类不平衡
2. **XGBoost更脆弱**: CDC 129.9% > LR 73.2%；PIDD 23.6% > 11.1%
3. **平衡数据安全**: Early Diabetes（61.5%）两模型均无膨胀
4. **统计解释**: 少数类越小 → SMOTE合成样本比例越大 → 泄漏效应越强 → 树模型对局部密度更敏感

## 源代码

- `03-code/experiments/run_cross_dataset.py` — LR版本
- `03-code/experiments/run_xgb_cross.py` — XGBoost版本
- `03-code/experiments/cross_dataset_results.json` — LR结果
- `03-code/experiments/cross_dataset_xgb_results.json` — XGB结果
