---
name: hcs-3wt-breast-cancer-diagnosis
description: HCS-3WT (Hybrid Cascade-Stacking Three-Way Triage) breast cancer diagnostic AI system — architecture, evaluation, and troubleshooting.
signature: "data_path: str -> diagnosis_report: dict"
related_skills: [academic-paper-completion, adhd-eye-tracking-review, arxiv, biorxiv, blogwatcher]
allowed-tools: [terminal, read_file, write_file, search_files]
---

# HCS-3WT Breast Cancer Diagnostic AI System

Procedural knowledge for building, evaluating, and optimizing the HCS-3WT (Hybrid Cascade-Stacking Three-Way Triage) system for clinical breast cancer diagnosis.

## System Overview

HCS-3WT is a three-stage cascade classifier that structurally decouples diagnostic pathways:

- **Expert B (Catcher)**: High-recall SVC — Clear Negative if P(malignant) < 0.03
- **Expert A (Refiner)**: Voting Classifier (RF + CatBoost + ExtraTrees) — Clear Positive if P(malignant) > 0.95
- **Expert C (Arbiter)**: Meta-learning stacking classifier — handles Gray Zone cases

Key innovation: The system achieves 70.9% automation rate with 99.3% automation accuracy on WDBC (leakage-free 5x5 CV), while reducing false negatives by 41% relative to binary baselines. The gray zone (29.1% of cases) is enriched with 1.21x true malignancies. Under simulated data leakage (global SMOTE), the gray zone expands by 3.3 percentage points, absorbing uncertainty rather than producing overconfident errors — confirming the structural leakage-bounding property.

## Key Implementation Details

### Feature Engineering
Three novel features capture cytological atypia:
1. `size_shape_interaction`: cell_size_uniformity × cell_shape_uniformity
2. `nuclear_abnormality_score`: bare_nuclei + bland_chromatin + normal_nucleoli
3. `triple_product_score`: clump_thickness × marginal_adhesion × bare_nuclei

### Preprocessing Pipeline
- PowerTransformer (Yeo-Johnson) for distribution normalization
- SelectKBest (ANOVA F-stat) with domain-tailored feature subsets (4 for Expert B, 8 for Expert A)
- Borderline-SMOTE applied only to Expert B and Expert C training sets (NOT Expert A)

### Critical Pitfalls

**SMOTE Single-Class Crash**: Borderline-SMOTE requires at least 2 classes in training data. When running cross-validation on imbalanced or single-class datasets (e.g., Wisconsin Prognostic had 194 samples, 0 malignant), SMOTE will crash with `ValueError: The target 'y' needs to have more than 1 class`.

**Fix**: Before calling SMOTE, check `len(np.unique(y_train)) >= 2`. If only 1 class exists, skip SMOTE and train without resampling.

**SVC Single-Class Crash**: SVC also crashes when training data has only 1 class. Add the same check before `system.fit()`.

**Key check pattern**:\n```python\nn_train_classes = len(np.unique(y_train_cv))\nn_test_classes = len(np.unique(y_test_cv))\nif n_train_classes < 2 or n_test_classes < 2:\n    # Skip this fold\n    continue\n```\n\n**HCS-3WT All Samples in Gray Zone (0% Automation Rate)**: If all samples end up in the Gray Zone (`automation_rate: 0.0%`, `gray_zone_size: 10000.0%`), this means Expert B (high-recall Catcher) is giving all samples probability > low_threshold, and/or Expert A (high-precision Refiner) is giving all samples probability < high_threshold. This typically happens when:\n- Expert B is not trained to give LOW probabilities for benign cases (SVC with class_weight={0:1, 1:5} should produce low P(malignant) for clear benign cases)\n- Expert A is not trained to give HIGH probabilities for malignant cases (VotingClassifier should produce high P(malignant) for clear malignant cases)\n- Thresholds are inappropriate for the data distribution\n\n**Fix**: Verify Expert B's calibration on clear benign samples and Expert A's calibration on clear malignant samples. Check probability histograms. If Expert B gives high probabilities for benign cases, it may be too sensitive. If Expert A gives low probabilities for malignant cases, it may be too conservative. Adjust training objectives or thresholds accordingly.\n\n**Cross-Validate Meta-Features to Prevent Leakage**: When generating P_A and P_B for Expert C's training, use cross_val_predict to ensure each meta-feature was produced by a model that did NOT see the corresponding instance during training. Training meta-features on the same data used for testing creates data leakage.\n\n**Long-Running Experiments Block Terminal**: WDBC 5-fold CV with HCS-3WT can take 10+ minutes (113s per fold × 5 folds × multiple datasets). Always use background execution for long experiments. Check for output periodically rather than waiting indefinitely. If background process times out, check for silent errors (no output).\n\n### CatBoost API Compatibility
Newer versions of CatBoost removed the `use_label_encoder` parameter. Handle both versions with try/except:
```python
try:
    models['CatBoost'] = cb.CatBoostClassifier(iterations=300, depth=6, learning_rate=0.05, random_state=RANDOM_STATE, verbose=0)
except TypeError:
    models['CatBoost'] = cb.CatBoostClassifier(iterations=300, depth=6, learning_rate=0.05, random_state=RANDOM_STATE, verbose=0, use_label_encoder=False)
```

## Evaluation Framework

Four-component evaluation:
1. Triage workflow performance (automation rate, automation accuracy)
2. Control Group A: Expert A as standalone binary classifier
3. Control Group B: Full HCS-3WT system
4. Ablation study: meta-feature stacking, engineered features, class weighting

## Cross-Domain Validation (Real Experimental Data)

The system has been rigorously evaluated with leakage-free 5x5 stratified CV (Pipeline isolation):

- **WDBC** (Wisconsin Diagnostic Breast Cancer): 569 samples, 30 features. 70.9% automation rate, 99.3% automation accuracy, FN 1.0 (−41% vs binary LR). Gray zone 29.1% with 1.21x malignancy enrichment. Under global SMOTE leakage, gray zone expands to 32.4% (+3.3pp), confirming structural leakage robustness.
- **Pima Indians Diabetes**: 768 samples, 8 features (cross-domain). 72.8% automation rate, 99.1% automation accuracy, FN 29 (−27.5% vs binary SVM). Gray zone enriched with 42% of true diabetics.
- **WBC Original** (UCI): 699 samples, 9 features. Honest benchmark established at 96.6-96.8% (5x5 CV). Used for leakage pattern quantification (global SMOTE inflates +0.92%).
- **Wisconsin Prognostic**: 194 samples, 32 features (single-class — all benign — must be skipped)

## Files

- `hcs_3wt_generalization_extended.py` — Main experiment script (47KB)
- `generate_figures_v2.py` — Figure generation script (40KB)
- `generalization_results.json` — Experimental results
- `breast_cancer.ipynb` — Original implementation notebook (14MB)
- `article.md` / `article_v2.md` — Paper drafts

## References

- `references/error-transcript.md` — Common errors and fixes encountered during development
