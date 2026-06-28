# PIMA论文 CatBoost 声称性数值验证实战（2026-06-25）

## 背景

审稿意见第②条要求统一跨数据集CV方案。修复中在 paper.tex line 229 写入了：

> "We verified that the selective distortion pattern holds for CatBoost under 5x2 CV (Helix F1=0.698, Leaky F1=0.655)"

**但该声明从未被代码运行验证过** — 这是典型的数据伪造。

## 发现过程

1. 用户问"修改后需要重新跑代码吗" → 触发数值真实性检查
2. 搜索 03-code/experiments/ 发现只有 `run_cross_dataset.py`（只跑 LogisticRegression）
3. cross_dataset_results.json 只有 LR 的 5×2 CV 结果，无 CatBoost 记录
4. SHAP 代码 `run_shap.py` 的 comprehensive_results.json 确认 SHAP 分析实际是 CatBoost（不是 GBC）
5. SHAP 特征值也需修正（代码输出 0.829/0.562/0.453 vs 论文声称 1.073/0.631/0.494）

## 实际实验结果

写 `run_catboost_10fold_cv.py`（10-fold 而非 5×2，因为主基准就是 10-fold）：

| 方案 | F1 | Recall | Precision | AUC |
|:-----|:---|:-------|:----------|:----|
| **Helix** | **0.7067±0.084** | 0.7756 | 0.6543 | 0.8422 |
| **Leaky** | **0.6346±0.070** | 0.5972 | 0.6872 | 0.8444 |
| F1 Δ | −10.2% | −23.0%↓ | +5.0%↑ | — |

Helix F1=0.7067 完美匹配主基准 CatBoost F1=0.7067。模式确认：Leaky 下 Recall 暴跌、Precision 虚高。

## 修复总结

| 问题 | 修复前 | 修复后 |
|:-----|:-------|:-------|
| CatBoost 5×2 CV 声称 | "Helix F1=0.698, Leaky F1=0.655"（未验证） | "Helix F1=0.707, Leaky F1=0.635"（代码验证）|
| CV 方案 | 5×2 CV（与主基准不一致） | 10-fold CV（与主基准一致） |
| SHAP 模型名 | "GBC component" (论文文本) | "CatBoost"（实际代码输出） |
| SHAP 特征值 | Glucose=1.073, BMI=0.631, Age=0.494 | Glucose=0.829, BMI=0.562, Age=0.453 |
