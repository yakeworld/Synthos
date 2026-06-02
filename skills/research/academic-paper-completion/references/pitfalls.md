# Common Bugs and Fixes in HCS-3WT Generalization Scripts

## Bug #1: predict() Missing Feature Selection

### Symptom
`HCS3WTSystem.predict()` receives full X (30 columns) but `expert_b_pipe` was trained on feature-subset X (4 columns). `predict_proba(X)` fails with dimension mismatch.

### Root Cause
`fit()` trains pipelines on `X_train[:, b_idx]` (selected features), but `predict()` passes full X directly to `predict_proba()`.

### Fix
```python
# In predict():
X_for_b = X_arr[:, self.b_idx]  # Apply feature selection before predict_proba
X_for_a = X_arr[:, self.a_idx]
b_probs = self.expert_b_pipe.predict_proba(X_for_b)[:, 1]
a_probs = self.expert_a_pipe.predict_proba(X_for_a)[:, 1]
```

## Bug #2: _get_meta_features_from_pipe() Dimension Mismatch

### Symptom
`cross_val_predict(expert_pipe, X, np.zeros(n), cv=5, ...)` fails because X has 30 columns but `PowerTransformer` was fit on 4 columns.

### Root Cause
`cross_val_predict` clones the pipeline and calls `pipe.fit(X_fold, y_fold)` where X_fold has 30 columns. The cloned pipeline's `PowerTransformer` expects 4 columns (from original fit).

### Fix
```python
# In _get_meta_features_from_pipe():
def _get_meta_features_from_pipe(self, X, expert_pipe, feature_idx=None):
    """Get out-of-fold predictions from a pipeline using cross_val_predict."""
    n = len(X)
    X_for_pipe = X[:, feature_idx] if feature_idx is not None else X
    probs = np.zeros(n)
    try:
        probs = cross_val_predict(expert_pipe, X_for_pipe, np.zeros(n), cv=5, method='predict_proba')[:, 1]
    except Exception:
        try:
            expert_pipe.fit(X_for_pipe, np.zeros(n).astype(int))
            probs = expert_pipe.predict_proba(X_for_pipe)[:, 1]
        except Exception:
            probs = np.full(n, 0.5)
    return probs
```

**Critical**: Always pass `feature_idx` to `_get_meta_features_from_pipe()`.

## Bug #3: cross_val_predict with Single-Class Labels

### Symptom
`ValueError: The target 'y' needs to have more than 1 class. Got 1 class instead`

### Root Cause
`cross_val_predict(expert_pipe, X, np.zeros(n), ...)` — `np.zeros(n)` is all negative class labels.

### Fix
Always use actual `y` values, not zeros:
```python
# WRONG:
probs = cross_val_predict(pipe, X, np.zeros(n), cv=5, method='predict_proba')[:, 1]

# CORRECT:
probs = cross_val_predict(pipe, X, y, cv=5, method='predict_proba')[:, 1]
```

## Bug #4: @Comment Lines in Bib Files

### Symptom
Bib key `Ahmad2020Performance` not found in `reference_enhanced.bib` even though the entry exists.

### Root Cause
`@Comment{jabref-meta: databaseType:bibtex;}` line causes regex `r'^@\w+\{([^,]+),'` to greedily match from `@Comment{` through to the next `,` — which is the comma after `Ahmad2020Performance`. This "eats" the key.

### Fix
Strip `@Comment` lines before extracting keys:
```python
lines = content.split('\n')
filtered = [l for l in lines if not l.startswith('@Comment{')]
new_content = '\n'.join(filtered)
```

## Bug #5: Percentage Double-Counting

### Symptom
`mean_automation_rate: 7504.11` instead of `75.04`

### Root Cause
`get_automation_stats()` returns values already as percentages (`* 100`), then `run_cv_experiment()` multiplies by 100 again:
```python
summary[f'mean_{key}'] = round(float(np.mean(vals)) * 100, 2)  # Double count!
```

### Fix
Track which metrics are already percentages and handle separately:
```python
for key in all_metrics:
    vals = np.array(all_metrics[key], dtype=float)
    if key in ('automation_fp', 'automation_fn'):
        summary[f'mean_{key}'] = round(float(np.mean(vals)) * 100, 2)  # Already percentage
    else:
        summary[f'mean_{key}'] = round(float(np.mean(vals)), 4)  # Not percentage
```

## Bug #6: Missing cross_validate Import

### Symptom
`NameError: name 'cross_validate' is not defined`

### Root Cause
`cross_validate` is used in `run_sota_comparison()` but not imported.

### Fix
```python
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict, cross_validate
```

## Summary Checklist

Before running any HCS-3WT generalization script, verify:

1. [ ] `cross_validate` is imported
2. [ ] `predict()` applies feature selection before `predict_proba()`
3. [ ] `_get_meta_features_from_pipe()` receives `feature_idx` parameter
4. [ ] `cross_val_predict` receives actual `y` values, not `np.zeros(n)`
5. [ ] Bib files have `@Comment` lines stripped before key extraction
6. [ ] Percentage values are not double-multiplied by 100
