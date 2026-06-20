# Notebook-to-Script Alignment: Model List Reconciliation

## Problem

Notebooks often build model lists via `sklearn.all_estimators()` or manual selection, while scripts use hardcoded `CLASSIFIERS` lists. These rarely match exactly.

## Reconciliation Method

### Step 1: Extract Notebook Model List

```python
import json
with open('notebook.ipynb') as f:
    nb = json.load(f)

# Find the cell that builds model_list (usually via all_estimators())
# Look for lines containing: all_estimators, model_list = {}, EstClass()

# Or find where models are defined manually:
# LogisticRegression(), RandomForestClassifier(), etc.
```

### Step 2: Extract Script Model List

```python
# For run_helix_benchmark.py:
with open('run_helix_benchmark.py') as f:
    code = f.read()

# Find CLASSIFIERS = [...] list and count entries
# Also check for external models appended later (XGBoost, LightGBM, CatBoost)
```

### Step 3: Compare Sets

```python
notebook_models = {
    "AdaBoostClassifier", "BaggingClassifier", "BernoulliNB", 
    "CalibratedClassifierCV", "DecisionTreeClassifier", 
    "DummyClassifier", "ExtraTreesClassifier", "ExtraTreeClassifier",
    "GaussianNB", "GaussianProcessClassifier", "GradientBoostingClassifier",
    "KNeighborsClassifier", "LabelPropagation", "LabelSpreading",
    "LinearDiscriminantAnalysis", "LinearSVC", "LogisticRegression",
    "LogisticRegressionCV", "MLPClassifier", "MultinomialNB",  # sometimes excluded
    "NearestCentroid", "NuSVC", "PassiveAggressiveClassifier",
    "Perceptron", "RadiusNeighborsClassifier",  # sometimes excluded
    "RidgeClassifier", "RidgeClassifierCV",
    "SGDClassifier", "SVC", "RandomForestClassifier", "HistGradientBoostingClassifier"
    # ... 30 total from notebook
}

script_models = {
    "LogisticRegression", "RidgeClassifier", "SGDClassifier", 
    "PassiveAggressive", "SVC", "NuSVC", "LinearSVC", "KNeighbors",
    "NearestCentroid", "DecisionTree", "ExtraTree", "RandomForest",
    "ExtraTrees", "GradientBoosting", "AdaBoost", "Bagging", "GaussianNB",
    "BernoulliNB", "LinearDiscriminant", "QuadraticDiscriminant",
    "MLPClassifier", "CalibratedSVC", "LabelPropagation", "LabelSpreading",
    "XGBoost", "LightGBM", "CatBoost"  # external models
    # ... varies by script
}

# Difference = notebook only - script only = missing from script
# Difference = script only - notebook only = extra in script
```

### Step 4: Apply Notebook Filters

The notebook applies these filters after `all_estimators()`:
```python
# Skip meta wrappers
meta_wrappers = ('MultiOutputClassifier', 'ClassifierChain', 
                 'OneVsRestClassifier', 'OneVsOneClassifier', 
                 'OutputCodeClassifier', 'SelfTrainingClassifier')

# Manually exclude (need special data formats)
excluded = ['RadiusNeighborsClassifier', 'CategoricalNB', 
            'ComplementNB', 'MultinomialNB']
```

### Step 5: Verify with Code

After reconciliation, run BOTH the notebook AND the script on the same data to verify:
- Same preprocessing pipeline
- Same CV settings (n_splits, random_state, stratify)
- Same evaluation metrics
- Same data splits

## Known Pitfalls

1. **CatBoost**: `get_params()` returns empty dict. Use `iterations` not `n_estimators`. Default 1000 iterations → slow. Set `iterations=100` for CV.
2. **LightGBM**: Also slow. Set `n_estimators=100` for CV.
3. **sklearn.metrics.make_scorer**: In sklearn 1.8+, must use `make_scorer(func, needs_proba=True)` for custom scorers. Direct function reference fails.
4. **GridSearchCV param prefix**: When searching on raw estimators (not Pipeline), use direct param names (`n_estimators`). When searching on Pipeline, use `clf__n_estimators`.
5. **PassiveAggressiveClassifier**: Deprecated in sklearn 1.8, use `SGDClassifier(loss='hinge', ...)` instead.
6. **DummyClassifier**: Default `strategy='most_frequent'` → F1=0 for minority class. Set `strategy='stratified'` for meaningful F1.

## PIMA Case Study

### Before Reconciliation

| Source | Model Count | Discrepancy |
|--------|-------------|-------------|
| Notebook (all_estimators) | 30 sklearn | Excludes RadiusNN, CategoricalNB, ComplementNB, MultinomialNB |
| Notebook (GridSearchCV) | +RF only | Hyperparameter tuning on RF only |
| Notebook (external) | +XGBoost | Cell 29-30 |
| Script (CLASSIFIERS) | 25 hardcoded | Missing Dummy, GPC, HistGB, Perceptron. Extra: LightGBM, CatBoost |
| Script (external) | +XGBoost, LightGBM, CatBoost | Same external models |

### After Reconciliation

**Aligned list: 33 models total**
- 30 sklearn classifiers (matching notebook `all_estimators()` output)
- XGBoost (external, from notebook Cell 29)
- LightGBM (external, added by user request)
- CatBoost (external, added by user request)

**Changes made to script:**
1. Replaced hardcoded `CLASSIFIERS` list with `all_estimators()` call (matching notebook Cell 17)
2. Added `DummyClassifier`, `GaussianProcessClassifier`, `HistGradientBoostingClassifier`, `Perceptron`
3. Removed `LightGBM` and `CatBoost` from primary list (kept as external models)
4. Replaced `CalibratedSVC` with `CalibratedClassifierCV` (notebook uses generic wrapper)

## Verification

After changes, verify alignment by:
1. Running notebook Cell 17 model list → get exact set of 30 names
2. Running script model list → get exact set of names
3. Set difference should be empty (or intentional additions only)
4. Run both on PIMA data → compare top-5 model rankings
