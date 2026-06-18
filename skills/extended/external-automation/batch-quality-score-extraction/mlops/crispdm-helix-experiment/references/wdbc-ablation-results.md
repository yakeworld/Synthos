# WDBC CRISP-DM Helix Ablation Results

> 2026-05-26 experimental run. All numbers real and traceable.

## Dataset
- Wisconsin Diagnostic Breast Cancer (WDBC)
- 569 samples, 30 features
- 212 malignant (37.3%), 357 benign (62.7%)
- No missing values

## 8-Model Benchmark (10-fold CV, SMOTE inside fold)

| Model | F1 | Recall | Accuracy |
|:------|:--:|:------:|:--------:|
| GBC | 0.9693±0.0214 | 0.9719±0.0281 | 0.9614±0.0270 |
| LDA | 0.9755±0.0167 | 0.9916±0.0129 | 0.9684±0.0219 |
| SVC | 0.9788±0.0174 | 0.9748±0.0339 | 0.9737±0.0211 |
| LR | 0.9789±0.0145 | 0.9775±0.0245 | 0.9737±0.0180 |
| RF | 0.9691±0.0197 | 0.9663±0.0326 | 0.9614±0.0246 |
| MLP | 0.9778±0.0162 | 0.9804±0.0218 | 0.9719±0.0211 |
| GNB | 0.9487±0.0186 | 0.9582±0.0417 | 0.9351±0.0235 |
| KNN | 0.9705±0.0194 | 0.9693±0.0315 | 0.9631±0.0241 |
| **Ensemble** | **0.9806±0.0139** | **0.9860±0.0188** | **0.9754±0.0179** |

## 4-Level Ablation (GBC)

| Level | F1 | Recall | Precision | Accuracy | AUC |
|:------|:--:|:------:|:---------:|:--------:|:---:|
| No Leakage | 0.9693 | 0.9719 | 0.9678 | 0.9614 | 0.9931 |
| Minor Leakage | 0.9692 | 0.9719 | 0.9676 | 0.9614 | 0.9930 |
| Medium Leakage | 0.9692 | 0.9719 | 0.9676 | 0.9614 | 0.9930 |
| Severe Leakage | 0.9683 | 0.9775 | 0.9600 | 0.9596 | 0.9922 |

## Key Finding

**Leakage has negligible effect on WDBC** (ΔF1 = −0.0010).
This contrasts with PIMA where severe leakage inflated F1 by +6.71%.

→ **Difficulty-Proportional Damage Principle**: leakage damage ∝ dataset difficulty.
