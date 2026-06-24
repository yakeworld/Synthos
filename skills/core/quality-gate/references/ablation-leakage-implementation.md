# Ablation Study: 4-Level Leakage Implementation

## Pattern: Independent Boolean Switch Design

The correct way to implement a multi-level ablation study for data leakage is with **independent boolean flags** for each preprocessing step, not hardcoded scenario branches.

### When to Use This Pattern

- Any experiment comparing "clean" vs "leaky" preprocessing pipelines
- Clinical ML papers needing to quantify the cost of protocol violations
- Reproducibility audits checking whether data leakage truly inflates metrics

### Core Implementation

```python
def run_ablation_level(smote_global=False, impute_global=False, scale_global=False, X, y, cv):
    """
    Independent control over which steps leak.
    
    smote_global=True  → SMOTE fitted on train+val combined (leakage)
    impute_global=True  → Imputer fitted on train+val combined (leakage)
    scale_global=True   → Scaler fitted on train+val combined (leakage)
    """
    metrics = {'f1':[], 'recall':[], 'precision':[], 'accuracy':[], 'auc':[]}
    
    for train_idx, val_idx in cv.split(X, y):
        X_tr, X_va = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_va = y.iloc[train_idx], y.iloc[val_idx]
        
        # 1. Zero replacement (always on fold data — no leakage pattern for this)
        zr = ZeroReplacer(cols_to_replace=ZERO_COLS)
        
        # 2. Imputation
        if impute_global:
            X_all = pd.concat([X_tr, X_va])
            imp = SimpleImputer(strategy='median')
            X_all_i = pd.DataFrame(imp.fit_transform(zr.fit_transform(X_all)), columns=X.columns)
            X_tr_i = X_all_i[:len(X_tr)]
            X_va_i = X_all_i[len(X_tr):]
        else:
            # Fold-internal impute
            ...
        
        # 3. Scaling (same pattern)
        if scale_global: ...
        else: ...
        
        # 4. SMOTE
        if smote_global:
            # Fit SMOTE on train+val combined → generation uses val distribution
            X_all_sm = np.concatenate([X_tr_s, X_va_s])
            y_all = np.concatenate([y_tr, y_va])
            X_res, y_res = SMOTE().fit_resample(X_all_sm, y_all)
            X_tr_res = X_res[:len(X_tr)]  # Take only training portion
        else:
            # Fold-internal SMOTE
            X_tr_res, y_tr_res = SMOTE().fit_resample(X_tr_s, y_tr)
        
        # 5. Train & evaluate
        ...
    
    return mean_metrics
```

### Mapping to 4 Leakage Levels

```python
config = {
    'no_leakage':     (False, False, False),   # Everything in fold
    'minor_leakage':  (True,  False, False),   # Only SMOTE leaks
    'medium_leakage': (False, True,  True),    # Impute + scale leak (as a pair)
    'severe_leakage': (True,  True,  True),    # Everything leaks
}

for sc, (smote_g, impute_g, scale_g) in config.items():
    results[sc] = run_ablation_level(smote_g, impute_g, scale_g, X=X, y=y, cv=cv)
```

### Key Design Decisions

| Decision | Why | Tradeoff |
|:---------|:----|:---------|
| Separate booleans, not enum | Allows testing arbitrary combinations | More verbose setup |
| `medium` = impute+scale both leak | Paper convention; they rarely occur separately | Can add `impute_only` if needed |
| Global SMOTE: fit on ALL data, take training portion | SMOTE generation uses val distribution → true leakage | After resampling, training data includes synthetic samples influenced by val |

### Common Pitfalls

1. **ALL booleans set to the same value** → original PIMA code had `global_preproc=True` for all 3 leakage levels, making them identical. ALWAYS verify that each level produces distinct metrics.
2. **Deprecated/removed estimators** — PassiveAggressiveClassifier deprecated in sklearn 1.8, removed in 1.10. Use `try/except` when dynamically building model pools.
3. **AdaBoostClassifier/HistGradientBoostingClassifier** are NOT meta-wrappers. They work as standalone classifiers. Don't put them in the meta-wrappers skip list.
4. **XGBoost** needs separate import; not in sklearn's `all_estimators()`. Install with `pip install xgboost`.

### PIMA Case Study (2026-06-24)

| Level | SMOTE | Impute | Scale | F1 | Rec | Prec |
|:------|:-----:|:------:|:-----:|:--:|:---:|:----:|
| No Leakage | fold | fold | fold | 0.6868 | 0.7464 | 0.6420 |
| Minor Leakage | **global** | fold | fold | 0.6541 | 0.6269 | 0.6953 |
| Medium Leakage | fold | **global** | **global** | 0.6743 | 0.7349 | 0.6276 |
| Severe Leakage | **global** | **global** | **global** | 0.6439 | 0.6232 | 0.6771 |

**Pattern**: Global SMOTE consistently drops Recall by ~12-16% while elevating Precision. Global impute+scale alone has minimal effect. The combination (severe) doesn't compound the effect on Recall but further degrades F1.

**Lesson**: "Global SMOTE" is the dominant leakage driver for this dataset. Imputation+scale leakage alone is negligible for PIDD due to its small size and relatively complete non-zero features.

For cross-dataset comparison (PIDD vs CDC BRFSS vs Early Diabetes), the leakage inflation magnitude follows class imbalance severity: CDC BRFSS (13.8% prevalence) → +73.2% F1 inflation; PIDD (34.9%) → +11.1%; Early Diabetes (61.5%) → -1.6%.

### Reference

Full experiment code: `crisp_dm_pima_unified.py` in the pima-crispdm project directory.
Detailed session report: `quality-gate/references/pima-crispdm-notebook-restructure-2026-06-24.md`.
