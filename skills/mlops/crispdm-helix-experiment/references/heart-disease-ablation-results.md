# Heart Disease CRISP-DM Helix Ablation Results

> 2026-05-26 experimental run. All numbers real and traceable.
> Source: `投稿文件汇总/crispdm-heart/experiment/results/heart_definitive.json`

## Dataset
- UCI Heart Disease (Cleveland subset, ID=45)
- 303 samples, 13 features
- No disease: 164 (54.1%), Disease: 139 (45.9%)
- 6 missing values: ca(4), thal(2) — median imputation inside fold
- Source: `ucimlrepo.fetch_ucirepo(id=45)`

## 7-Model Benchmark (10-fold CV, SMOTE inside fold)

| Model | F1 | Recall | Accuracy |
|:------|:--:|:------:|:--------:|
| GBC | 0.7886±0.0758 | 0.7692±0.0788 | 0.8083±0.0514 |
| LDA | 0.8026±0.0794 | 0.7692±0.1015 | 0.8277±0.0252 |
| SVC | 0.8114±0.0676 | 0.8055±0.0854 | 0.8281±0.0389 |
| LR | 0.8087±0.0737 | 0.7912±0.0814 | 0.8280±0.0253 |
| RF | 0.8188±0.0609 | 0.8126±0.0864 | 0.8348±0.0484 |
| GNB | **0.8377±0.0738** | **0.8264±0.0997** | **0.8544±0.0235** |
| KNN | 0.7909±0.0472 | 0.7978±0.0970 | 0.8084±0.0241 |
| **Ensemble** | **0.8206±0.0693** | **0.8055±0.0854** | **0.8381±0.0179** |

## 4-Level Ablation (GBC)

| Level | F1 | Recall | Precision | Accuracy |
|:------|:--:|:------:|:---------:|:--------:|
| No Leakage | 0.7886 | 0.7692 | 0.8207 | 0.8083 |
| Minor (global imp+scale) | 0.7939 | 0.7692 | 0.8315 | 0.8149 |
| Medium (global imp+scale) | 0.7939 | 0.7692 | 0.8315 | 0.8149 |
| Severe (global all+SMOTE) | **0.9004** | **0.8715** | **0.9349** | **0.8643** |
| **ΔF1** | **+0.1117 (+14.17%)** | | | |

## Key Finding: Small-Sample Vulnerability

**Heart Disease shows the WORST leakage damage of all 3 datasets tested** (+14.17% F1 inflation):

- PIMA (n=768, hard):  +6.71%  ← bad
- WDBC  (n=569, easy):  −0.10%  ← negligible
- **Heart (n=303, medium): +14.17% ← WORST**

Why? Small sample size (n=303) means SMOTE doubles the effective training set. The synthesized samples push the decision boundary when the original classes are only moderately separable.

**Recommendation**: Any study with n < 500 using SMOTE must report BOTH isolated and non-isolated metrics.
