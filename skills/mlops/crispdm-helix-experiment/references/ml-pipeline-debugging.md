---
name: ml-pipeline-debugging
category: debugging
description: Debug ML pipeline failures from feature selection × cross_val_predict dimension mismatch, silent exception swallowing, and cascading coordination logic failures.
---

# ML-Pipeline Debugging: Feature Selection × Cross-Val Predict Dimension Mismatch

## Context
Debugging ML pipeline failures caused by external feature selection combined with `cross_val_predict` (or any clone-then-refit mechanism). This is a common but hard-to-spot pattern in HCS-3WT-style architectures where feature subsets are selected outside the pipeline.

## Root Cause Pattern

**The scenario:**
1. Feature selection is performed **outside** the sklearn pipeline (e.g., `SelectKBest` on full dataset, then `b_idx` saved for later use)
2. The pipeline (e.g., `PowerTransformer` + `SVC`) is built and fitted on the **feature-subsetted** data
3. `cross_val_predict(pipe, X, y, ...)` is called with **full X** (not feature-subsetted)
4. `cross_val_predict` clones the pipeline and refits on each fold's training subset
5. The clone receives full-X but the pipeline's internal state (e.g., `PowerTransformer.n_input_`) expects the feature-subsetted dimension
6. **Result:** `ValueError` with mismatched feature counts

**The cascade effect:**
- `pipe.predict(X)` fails → falls to backup path
- `cross_val_predict(pipe, X, ...)` fails → falls to another backup path  
- Fallback might train on wrong data (e.g., full-X with all-zero labels) → produces meaningless output
- Downstream logic interprets meaningless output as "all in gray zone" or similar catastrophic failure
- **Silent degradation:** No exception bubbles to the top-level caller if all failures are caught

## Common Symptom
- Script completes with "success" (exit code 0)
- Metrics look wrong but not obviously broken (e.g., 0% automation, all NaN, or all same value)
- Individual model accuracy is fine (the classifier itself works)
- Only the **coordination logic** (cascades, stacking, meta-features, three-way triage) fails

## Debugging Steps

### Step 1: Check the predict path
```python
# Before:
probs = pipe.predict_proba(X)[:, 1]  # X might have wrong dimension

# After (ensure feature selection applied):
X_sub = X[:, b_idx]  # or X.iloc[:, b_idx]
probs = pipe.predict_proba(X_sub)[:, 1]
```

### Step 2: Check cross_val_predict calls
```python
# Before:
probs = cross_val_predict(pipe, X_full, y, cv=5, method='predict_proba')

# After (pass feature-subsetted X):
probs = cross_val_predict(pipe, X_subset, y, cv=5, method='predict_proba')
```

### Step 3: Add dimension assertions
```python
# In fit:
n_features_after_sel = X_sel.shape[1]

# In predict:
assert X_for_pred.shape[1] == n_features_after_sel, \
    f"predict got {X_for_pred.shape[1]} features, expected {n_features_after_sel}"
```

### Step 4: Check exception swallowing
```python
# BEFORE (silent failure):
try:
    probs = pipe.predict_proba(X)
except Exception:
    probs = np.full(n, 0.5)  # ← Hides the bug

# AFTER (visible failure):
try:
    probs = pipe.predict_proba(X)
except Exception as e:
    print(f"ERROR: pipe.predict_proba failed: {e}")  # ← Must see this
    raise  # or use a sentinel that's obviously wrong
```

### Step 5: Verify probability distributions
```python
# After fixing, check:
print(f"b_probs: min={b_probs.min():.4f}, max={b_probs.max():.4f}, mean={b_probs.mean():.4f}")
print(f"a_probs: min={a_probs.min():.4f}, max={a_probs.max():.4f}, mean={a_probs.mean():.4f}")

# Sanity checks:
# - min < 0.1 and max > 0.9 (models should have confident predictions)
# - mean should not be exactly 0.5 (means all-same or all-fail)
# - clear_neg_mask and clear_pos_mask should have some True values
```

### Step 6: Check sklearn imports
```python
import sklearn.model_selection as ms
available = [x for x in dir(ms) if 'validate' in x.lower() or 'predict' in x.lower()]
print(f"Available: {available}")
# Common missing: cross_validate (often called in SOTA comparison but forgotten)
# Also: cross_val_predict, train_test_split, StratifiedKFold
```

## Common Pitfalls

### PITFALL 1: DataFrame.iloc with integer list
```python
# If feature_idx = np.array([5, 12, 20, 27])
df.iloc[:, feature_idx]  # Works: selects columns at positions 5, 12, 20, 27
df.loc[:, feature_idx]  # BUG: looks up column NAMES [5, 12, 20, 27]
```

### PITFALL 2: cross_val_predict with already-fitted pipeline
`cross_val_predict` clones and refits. If the pipeline has stateful steps trained on a specific dimension, the clone starts fresh but receives the same input X. If X doesn't match the trained dimension, it fails.

### PITFALL 3: SMOTE in small folds
In 5-fold CV, each fold's training set is ~80% of total. If total is small (e.g., 194 samples), a minority class might have <2 samples in a fold → SMOTE fails → pipeline silently skips or errors.

### PITFALL 4: Double-percentage calculation
```python
# Bug: get_stats returns 75.04 (already %), then multiplied by 100 → 7504
summary['mean_rate'] = round(np.mean(vals) * 100, 2)  # vals already percentages

# Fix: check if vals are already in 0-100 range
if vals.max() <= 1.0:
    vals *= 100  # only multiply if already fraction
```

### PITFALL 5: cross_val_predict with all-zero labels
```python
probs = cross_val_predict(pipe, X, np.zeros(n), cv=5, ...)
# Will fail with: "The target 'y' needs to have more than 1 class. Got 1 class instead"
# This is a useful diagnostic signal — uniform labels cause cross_val_predict to fail.
# The fallback path then trains on wrong data, producing meaningless output.
```

### PITFALL 6: Missing import for cross_validate
SOTA comparison or CV evaluation code may call `cross_validate()` but forget to import it. Verify: `import sklearn.model_selection as ms; 'cross_validate' in dir(ms)`.

## Anti-Pattern: External Feature Selection
Instead of selecting features outside the pipeline, consider embedding feature selection inside:
```python
pipe = Pipeline([
    ('feature_select', SelectKBest(k=4)),  # Internal, safe for cross_val_predict
    ('scaler', PowerTransformer()),
    ('classifier', SVC(probability=True)),
])
# Now cross_val_predict(pipe, X_full, y, ...) works correctly
```

## Related Files
- `references/breast-cancer-hcs3wt-bugfix.md` — Detailed case study from HCS-3WT breast cancer diagnosis project.