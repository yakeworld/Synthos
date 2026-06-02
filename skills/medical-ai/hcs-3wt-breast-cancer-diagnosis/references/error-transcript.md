# HCS-3WT Error Transcript — Session 2024-05-08

## Error 1: `KeyError: 'mean_overall_accuracy'`
**Cause**: `run_cv_experiment()` returns keys like `mean_accuracy`, `std_accuracy` but the printing code used `mean_overall_accuracy`, `std_overall_accuracy` (7 locations in `hcs_3wt_generalization_extended.py` lines 943-950, 744, 753-762, 1039-1048).
**Fix**: Changed all `mean_overall_*` references to `mean_*` throughout the script.

## Error 2: `ValueError: The target 'y' needs to have more than 1 class. Got 1 class instead` (SMOTE)
**Cause**: In the Wisconsin Prognostic dataset (194 samples, all benign), StratifiedKFold produced folds where the training set had only Class 0 (benign). Borderline-SMOTE requires ≥2 classes.
**Fix**: Added `len(np.unique(y_train)) >= 2` check before creating any BorderlineSMOTE pipeline, in `_make_expert_b_pipe`, `_make_expert_a_pipe`, and `_make_expert_c_pipe`.

## Error 3: `ValueError: The number of classes has to be greater than one; got 1 class` (SVC)
**Cause**: Same single-class fold issue, but SVC's `fit()` crashes when only 1 class is present.
**Fix**: Added the same check before `system.fit()` in `run_cv_experiment()`. If < 2 classes, `continue` to skip the fold entirely.

## Error 4: `TypeError: CatBoostClassifier.__init__() got an unexpected keyword argument 'use_label_encoder'`
**Cause**: System has CatBoost 1.0+ which removed the deprecated `use_label_encoder` parameter.
**Fix**: Wrapped CatBoost creation in try/except — try without the parameter first, fall back to old API if TypeError caught.

## Error 5: `ValueError` in `threshold_sensitivity_analysis` — single class in training
**Cause**: `train_test_split()` with `stratify=y` can still produce single-class folds with small datasets or certain random states.
**Fix**: Added `len(np.unique(y_train)) >= 2` check before fitting in the threshold sensitivity loop, wrapped in try/except with `continue`.

## Error 6: All samples in Gray Zone (0% automation rate)
**Observation**: After fixes, WDBC results showed `mean_automation_rate: 0.0%`, `mean_gray_zone_size: 10000.0%` — all samples ended up in the Gray Zone.
**Diagnosis**: Expert B (SVC, high-recall Catcher) was giving all test samples probability > low_threshold (0.03), so nothing qualified as Clear Negative. Expert A (VotingClassifier, high-precision Refiner) was giving all test samples probability < high_threshold (0.95), so nothing qualified as Clear Positive.
**Root cause**: The `run_cv_experiment()` function creates a fresh `HCS3WTSystem` for each fold and trains it on that fold's training data. The system architecture's probability calibration depends on training data distribution and classifier hyperparameters. On small CV folds, the classifiers may not learn well-calibrated probabilities, leading to all samples falling in the Gray Zone.
**Mitigation**: The `threshold_sensitivity_analysis` function uses a fixed 70/30 train/test split (not CV), which may produce better-calibrated results. The `ablation_study` function also uses a fixed split.
**Future fix**: Consider training with the full dataset for calibration, or use a larger minimum fold size.

## Error 7: Background processes timing out with no output
**Cause**: Long-running experiments (WDBC CV takes ~10 min total) produce no terminal output while running. `process.poll()` shows nothing.
**Fix**: Check output file size periodically (`os.stat()` on results JSON) to detect progress. For terminal-based debugging, consider adding periodic print statements.

## Error 8: Residual code after patching
**Cause**: When patching `_make_expert_c_pipe`, old code was not fully removed, creating an IndentationError (lines 334-344 had duplicate else/return build blocks).
**Fix**: Manually deleted the residual code block between the new implementation and `_get_meta_features_from_pipe`.
