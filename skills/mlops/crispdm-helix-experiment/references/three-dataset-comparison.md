# Three-Dataset CRISP-DM Helix Comparison

> Generated 2026-05-26 from real experiments. All numbers traceable to code in `投稿文件汇总/crispdm-{pima,wdbc,heart}/experiment/`.

## Dataset Profiles

| Property | PIMA | WDBC | Heart Disease |
|:---------|:----:|:----:|:-------------:|
| UCI ID | — (CSV) | — (sklearn) | 45 |
| Samples | 768 | 569 | 303 |
| Features | 8 | 30 | 13 |
| Missing | 374 zeros (48.7%) | 0 | 6 (1.3% imputed) |
| Negative class | 500 (65.1%) | 357 (62.7%) | 164 (54.1%) |
| Positive class | 268 (34.9%) | 212 (37.3%) | 139 (45.9%) |
| Source | Kaggle PIDD | sklearn `load_breast_cancer` | `ucimlrepo.fetch_ucirepo(id=45)` |

## Best Single Model (Strict Isolation + SMOTE)

| Metric | PIMA (GNB) | WDBC (LR) | Heart (GNB) |
|:-------|:----------:|:---------:|:-----------:|
| F1 | 0.6857 | 0.9789 | 0.8377 |
| Recall | 0.7464 | 0.9775 | 0.8264 |
| Accuracy | 0.7616 | 0.9737 | 0.8544 |

## Ensemble (GBC + LDA + SVC, Soft Voting)

| Metric | PIMA | WDBC | Heart |
|:-------|:----:|:----:|:-----:|
| F1 | 0.6986 | 0.9806 | 0.8206 |
| Recall | 0.7500 | 0.9860 | 0.8055 |
| Precision | 0.6625 | 0.9759 | 0.8416 |
| Accuracy | 0.7746 | 0.9754 | 0.8381 |
| AUC | 0.8481 | 0.9962 | — |

## Ablation Study (GBC, 10-fold CV)

### PIMA

| Level | F1 | Recall | Precision | Accuracy |
|:------|:--:|:------:|:---------:|:--------:|
| No Leakage | 0.6986 | 0.7500 | 0.6625 | 0.7746 |
| Minor (global imp) | 0.7050 | 0.7648 | 0.6615 | 0.7772 |
| Medium (global imp+scale) | 0.7015 | 0.7611 | 0.6586 | 0.7746 |
| Severe (global all+SMOTE) | **0.7657** | 0.6364 | 0.9632 | 0.6749 |
| **ΔF1** | **+0.0671 (+6.71%)** | | | |

### WDBC

| Level | F1 | Recall | Precision | Accuracy |
|:------|:--:|:------:|:---------:|:--------:|
| No Leakage | 0.9693 | 0.9719 | 0.9678 | 0.9614 |
| Minor (global scale) | 0.9692 | 0.9719 | 0.9676 | 0.9614 |
| Medium (global scale) | 0.9692 | 0.9719 | 0.9676 | 0.9614 |
| Severe (global all+SMOTE) | **0.9683** | 0.9775 | 0.9600 | 0.9596 |
| **ΔF1** | **-0.0010 (-0.10%)** | | | |

### Heart Disease

| Level | F1 | Recall | Precision | Accuracy |
|:------|:--:|:------:|:---------:|:--------:|
| No Leakage | 0.7886 | 0.7692 | 0.8207 | 0.8083 |
| Minor (global imp+scale) | 0.7939 | 0.7692 | 0.8315 | 0.8149 |
| Medium (global imp+scale) | 0.7939 | 0.7692 | 0.8315 | 0.8149 |
| Severe (global all+SMOTE) | **0.9004** | 0.8715 | 0.9349 | 0.8643 |
| **ΔF1** | **+0.1117 (+14.17%)** | | | |

## Key Insight: Small-Sample Vulnerability

Leakage damage is **NOT** monotonic with dataset difficulty:

```
WDBC (n=569, easy):     ΔF1 = -0.10%   ← negligible
PIMA (n=768, hard):     ΔF1 = +6.71%   ← bad  
Heart (n=303, medium):  ΔF1 = +14.17%  ← WORST
```

The worst case is **small sample + moderate separability**:
- SMOTE doubles effective training size → synthesized samples dominate
- Decision boundary not robust enough to resist global SMOTE distortion
- N<500 is the critical threshold for mandatory dual reporting
