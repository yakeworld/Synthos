# Two-Regime Leakage Model — 三数据集实验发现 (2026-06-04)

## 核心发现

泄漏损伤不仅存在**量**的差异（难度比例损伤），还存在**质**的区别（Recall 方向）。三数据集实验揭示了三种不同泄漏模式：

| 数据集 | N | 患病率 | 基线F1 | 泄漏F1 | ΔF1 | ΔRecall | 泄漏模式 |
|:-------|:-:|:------:|:------:|:------:|:---:|:-------:|:---------|
| PIDD | 768 | 34.9% | 0.6986 | 0.7657 | **+9.6%** | **-11.4% ↓** | **Recall悖论** |
| Heart | 303 | 45.9% | 0.7886 | 0.9004 | **+14.2%** | **+10.2% ↑** | **统一膨胀** |
| WDBC | 569 | 37.3% | 0.9693 | 0.9683 | **-0.1%** | +0.6% | **可忽略** |

## 三区域定义

### 区域1：Recall悖论（PIDD模式）
- F1↑, Recall↓
- 最危险的泄漏模式——指标看似改善，临床敏感度实则下降
- 触发条件：基线模型在**决策边界附近**运行 + 中等类不平衡
- 模型依赖：LR 触发，Ensemble(GBC+LDA+SVC) 不触发（见表3）

### 区域2：统一膨胀（Heart模式）
- 所有指标同步上升（F1↑, Rec↑, Prec↑）
- 产生乐观但不矛盾的结果
- 触发条件：小样本(n<500) + 中等可分离性
- 小样本脆弱性：SMOTE合成样本占比大，决策边界易被全局预处理偏移

### 区域3：可忽略（WDBC模式）
- 无显著变化（ΔF1 ≈ 0）
- 触发条件：高可分离性（基线F1>0.95）
- 高信噪比使全局预处理无法带来额外信息增益

## 模型选择陷阱（P0级）

**相同数据、不同模型 → 不同泄漏模式。**

PIDD 上 LR 和 Ensemble 的 Recall 方向完全相反：

| 模型 | No Leakage F1 | Severe F1 | ΔF1 | No Leakage Rec | Severe Rec | ΔRec | 模式 |
|:-----|:-------------:|:---------:|:---:|:--------------:|:----------:|:----:|:----:|
| LR | 0.6759 | 0.7338 | +8.6%↑ | 0.7165 | 0.7080 | **-1.2%↓** | 悖论 |
| Ensemble | 0.6986 | 0.8140 | +16.5%↑ | 0.7500 | 0.8340 | **+11.2%↑** | 膨胀 |

**铁律**：消融表所有行必须来自同一模型。不得用 LR 的 Severe 值混入 Ensemble 基线的消融表。

## 实验验证方法

始终使用**双模型消融**（LR + 论文主模型）以检测模型依赖的 Recall 方向：

```python
# 对每个数据集，跑两个模型的消融
models_to_test = {
    'LR': LogisticRegression(max_iter=1000),
    'Ensemble': VotingClassifier([('gbc', GBC()), ('lda', LDA()), ('svc', SVC(probability=True))], voting='soft')
}
for model_name, model_fn in models_to_test.items():
    for level in ['isolated', 'global_scale', 'global_smote']:
        results = run_ablation(model_fn, level)
        # 检查 Recall 方向
        rec_delta = results['severe_recall'] - results['no_leakage_recall']
        if rec_delta < 0:
            print(f'⚠ {model_name}: Recall悖论 (ΔRec={rec_delta:.1%})')
        else:
            print(f'  {model_name}: 统一膨胀 (ΔRec=+{rec_delta:.1%})')
```

## 参考实验

- PIDD: `pima-crispdm/03-code/experiments/` + `results_wdbc/wdbc_definitive.json`
- Heart: `crispdm-heart/03-code/results/heart_definitive.json`
- WDBC: `crispdm-wdbc/03-code/results_wdbc/wdbc_definitive.json`
- 三数据集对比：`crispdm-wdbc/01-manuscript/paper.tex` (Table 3 / Discussion)
