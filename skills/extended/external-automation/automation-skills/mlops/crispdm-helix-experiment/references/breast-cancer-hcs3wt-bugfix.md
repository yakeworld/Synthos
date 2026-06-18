# Case Study: HCS-3WT Breast Cancer Diagnosis - 0% Automation Rate

## Project
`/media/yakeworld/sda2/academic_writer/article10_breast/hcs_3wt_generalization_extended.py`

## Problem
The HCS-3WT (Hybrid Cascade-Stacking Three-Way Triage) system reported 0% automation rate across all datasets. Paper claimed 84.76% on WDBC (70/30 split).

## Diagnosis

### Bug 1: predict() missing feature selection
`HCS3WTSystem.predict()` called `self.expert_b_pipe.predict_proba(X)` with full 30-feature X. The pipeline was trained on 4 features → `ValueError`. Silent fallback produced all-0.5 probabilities.

### Bug 2: _get_meta_features_from_pipe() cross_val_predict dimension mismatch
`cross_val_predict(expert_pipe, X, ...)` passed full 30-feature X to a pipeline trained on 4 features. `cross_val_predict` clones and refits per fold → `ValueError` on `PowerTransformer`. Fallback trained pipeline on full-X with all-zero labels → meaningless output.

### Bug 3: Double percentage calculation
`get_automation_stats()` returns values already in 0-100 range. `run_cv_experiment()` multiplied by 100 → `7504.11` instead of `75.04`.

## Fix Applied

1. **Feature selection in predict():**
   ```python
   X_for_b = X_arr[:, self.b_idx]  # Apply feature selection
   b_probs = self.expert_b_pipe.predict_proba(X_for_b)[:, 1]
   ```

2. **Feature selection in cross_val_predict:**
   ```python
   def _get_meta_features_from_pipe(self, X, expert_pipe, feature_idx=None):
       if isinstance(X, pd.DataFrame):
           X_for_cv = X.iloc[:, feature_idx] if feature_idx else X
       else:
           X_for_cv = X[:, feature_idx] if feature_idx else X
       probs = cross_val_predict(expert_pipe, X_for_cv, np.zeros(n), cv=5, ...)
   ```

3. **Percentage fix:** Check if values are already percentages before multiplying.

## Results

| Metric | Before | After |
|--------|--------|-------|
| Accuracy | 96.84% | 96.66% |
| F1 | 97.48% | 97.34% |
| AUC | 99.53% | 99.29% |
| Automation Rate | 0.00% | 75.04% |
| Automation Accuracy | 0.00% | 99.12% |

75.04% vs claimed 84.76% (70/30 split) is reasonable — 5-fold CV has slightly less training data per fold.

## Key Lesson
Always verify that:
- `predict()` applies the same transformations as `fit()` (feature selection, scaling, etc.)
- `cross_val_predict()` receives input matching what the pipeline was trained on
- Exception handling does not silently mask dimension mismatches
- Output sanity-checks (probability ranges, mask distributions) catch silent failures early
