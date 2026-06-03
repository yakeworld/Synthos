# Cross-Dataset Definitive Ablation Results (2026-06-03)

## Method

- **Model**: LogisticRegression (同一模型跨数据集可比)
- **CV**: 10-fold Stratified (PIDD, Early Diabetes) / 3-fold Stratified (CDC 25K subsample)
- **4-level ablation**: No Leakage → Minor (global impute) → Medium (+global scale) → Severe (+global SMOTE before split)
- **Code**: `cross_dataset_final.py` → `results_cross_dataset/summary_all.json`

## LR Ablation

| Dataset | N | Prevalence | F1 Helix | F1 Leaky | **F1 Inflation** | Rec Helix | Rec Leaky | Rec Change | Prec Change |
|:-------|--:|:----------:|:--------:|:--------:|:----------------:|:---------:|:---------:|:----------:|:-----------:|
| **CDC BRFSS 2015** | 25,000 | 13.8% | 0.4376 | 0.7626 | **+74.27%** 🚀 | 0.7571 | 0.7859 | +3.80% | +140.61% 🚀 |
| **PIDD** | 768 | 34.9% | 0.6759 | 0.7338 | **+8.57%** | 0.7165 | 0.7080 | -1.19% ↓ | +17.64% |
| **Early Diabetes** | 520 | 61.5% | 0.9346 | 0.9381 | **+0.37%** | 0.9187 | 0.9281 | +1.02% | -0.51% |

## Ensemble Ablation (PIDD only, paper main table)

| Level | F1 | Recall | Precision | Accuracy | AUC |
|:------|:--:|:------:|:---------:|:--------:|:---:|
| No Leakage | 0.6986 | 0.7500 | 0.6625 | 0.7746 | 0.8481 |
| Minor Leakage | 0.7050 | 0.7648 | 0.6615 | 0.7772 | 0.8493 |
| Medium Leakage | 0.7015 | 0.7611 | 0.6586 | 0.7746 | 0.8475 |
| **Severe Leakage** | **0.8140** | **0.8340** | **0.7959** | **0.8090** | **0.8837** |
| Inflation | **+16.52%** | **+11.20%** | **+20.14%** | +4.44% | +4.19% |

## Key Finding

F1 inflation is inversely proportional to class imbalance severity. Low prevalence (13.8%) yields massive inflation (+74%), balanced data (61.5%) yields near-zero inflation (+0.4%). This is **Universal Metric Inflation** — all metrics rise simultaneously under global SMOTE (no Recall trade-off for most models).

## Trap

The paper's Table 2 originally had fabricated Severe Leakage values (F1=0.7657, Rec=0.6364) that were neither LR (0.7338, 0.7080) nor Ensemble (0.8140, 0.8340) values. **Always verify ALL cells of an ablation table against experiment output, not just the baseline row.**
