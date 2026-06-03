# Data Leakage Audit Methodology — Reusable Protocol

## Purpose
Quantify how data leakage inflates ML performance metrics on biomedical datasets. Used for critical review papers (e.g., "Emperor's New Accuracy") and L0.5 honesty verification.

## Standard Protocol

### 1. Honest Baseline (Leakage-Free)
```python
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score

pipe = Pipeline([('scaler', StandardScaler()), ('clf', RandomForestClassifier())])
rkf = RepeatedStratifiedKFold(n_splits=5, n_repeats=5)  # 25 folds
scores = cross_val_score(pipe, X, y, cv=rkf, scoring='accuracy')
print(f"Honest: {scores.mean():.4f} ± {scores.std():.4f}")
```

**Critical**: ALL preprocessing must be INSIDE the Pipeline. No fit_transform on X before CV.

### 2. Leakage Patterns to Test

| Pattern | Code | Typical Inflation |
|:--------|:-----|:-----------------:|
| Global SMOTE | `SMOTE().fit_resample(X, y)` before CV | +0.7-0.9% |
| Global Scaling | `StandardScaler().fit_transform(X)` before CV | 0-0.1% |
| Global Feature Selection | `SelectKBest().fit_transform(X, y)` before CV | +0 to -1.5% |
| All Combined | Sequential SMOTE + Scale + FS | +0.7-1.5% |

### 3. Multi-Classifier Bootstrap
```python
import numpy as np
# Simulate evaluating N classifiers, reporting the best
n_classifiers = 30
n_sims = 10000
np.random.seed(42)
maxima = [np.max(np.random.normal(0.94, 0.02, n_classifiers)) for _ in range(n_sims)]
inflation = np.mean(maxima) - 0.94
print(f"Expected max of {n_classifiers} classifiers: {np.mean(maxima):.4f} (inflation: {inflation:.4f})")
```

### 4. Known Honest Benchmarks

| Dataset | Samples | Features | Honest Range | Suspicious Threshold |
|:--------|:-------:|:--------:|:------------:|:--------------------:|
| WBC Original (UCI) | 699 | 9 | 94.8-96.8% | >98.5% |
| WDBC (sklearn) | 569 | 30 | 93.4-97.8% | >98.5% |
| PIMA Diabetes | 768 | 8 | 74-78% | >82% |

### 5. Paper Audit Checklist

For each published paper claiming high accuracy:
1. Does it mention Pipeline isolation? If not → suspect leakage.
2. Does it apply SMOTE/oversampling? If yes, was it within CV folds or global?
3. Does it report best-of-N-classifiers without correction? If yes → likely inflated.
4. Does it match the OpenML benchmark range? If above → suspicious.

### 6. Three-Way Decision as Solution

HCS-3WT's leakage robustness theorem: The gray zone structurally bounds leakage inflation. Under bounded leakage (|ε(x)| < δ), the probability of remaining deferred is ≥ (τ_high - τ_low - 2δ) / (τ_high - τ_low), providing a structural buffer against overconfidence.
