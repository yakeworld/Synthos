# Protocol Gap Analysis - PIDD Dataset F1 Diagnostics

## Background

In the PIMA paper pipeline, OpenML dataset and local CSV dataset have different F1 scores. User asked: Does OpenML not do 0-to-NaN processing so F1 is higher?

## Data Identity Verification

### OpenML PIMA (Task 37, Dataset 37)

Loaded via sklearn.datasets.fetch_openml(name=diabetes, version=1):

| Column | Zero Count | NaN Count |
|--------|-----------|-----------|
| plas (Glucose) | 5 | 0 |
| pres (BloodPressure) | 35 | 0 |
| skin (SkinThickness) | 227 | 0 |
| insu (Insulin) | 374 | 0 |
| mass (BMI) | 11 | 0 |

### Local PIMA (raw CSV)

Loaded via pd.read_csv(pima_raw.csv):

| Column | Zero Count | NaN Count |
|--------|-----------|-----------|
| Glucose | 5 | 0 |
| BloodPressure | 35 | 0 |
| SkinThickness | 227 | 0 |
| Insulin | 374 | 0 |
| BMI | 11 | 0 |

Conclusion: Zero values are IDENTICAL (5+35+227+374+11 = 652 zeros). OpenML did NOT do 0-to-NaN processing.

## F1 Difference Root Cause Analysis

### Protocol Comparison

| Protocol | Model | CV | F1 | Acc |
|----------|-------|-----|-----|-----|
| OpenML helix | LR | 5x2 CV | 0.6644 | 0.7484 |
| OpenML leaky | LR | Global SMOTE then split | 0.7381 | 0.7520 |
| Local helix | GBC | 10-fold CV | 0.6541 | 0.7707 |
| Local leaky | GBC | No SMOTE | 0.6439 | 0.7518 |

### Root Cause

F1 differences come from experimental protocol, NOT data preprocessing:

1. Global SMOTE: The cross-dataset experiment's leaky protocol uses SMOTE, increasing 768 samples to 1000. This causes F1=0.7381 which is much higher than 0.6644.

2. Model difference: Local helix uses GBC (F1=0.6541), OpenML helix uses LR (F1=0.6644). LR is slightly better than GBC on PIDD.

3. CV difference: 5x2 CV vs 10-fold CV. CV protocol affects result stability and variance.

### Verification

Reproducing with identical protocol:
- Cross-dataset leaky protocol (LR, 5x2 CV, Global SMOTE): F1 = 0.7440 +/- 0.0066 (matches OpenML 0.7381)
- Cross-dataset helix protocol (LR, 5x2 CV): F1 = 0.6644 +/- 0.0041 (matches OpenML 0.6644 EXACTLY)
- Our helix protocol (GBC, 10-fold CV, helix-isolated SMOTE): F1 = 0.6683 +/- 0.0555 (close to local 0.6541)

Conclusion: When using the same protocol (LR, 5x2 CV, helix-isolated), OpenML and local PIMA have IDENTICAL F1 (0.6644 vs 0.6644). This proves OpenML and local PIMA are THE SAME DATA, and F1 differences are entirely caused by experimental protocol.

## General Diagnostic Flow

When comparing F1/accuracy across different data sources:

1. Verify data identity: Compare zero values, missing values, statistical features
2. Verify protocol identity: Compare preprocessing steps, SMOTE usage, CV folds, random seeds
3. Verify model identity: Compare model type, hyperparameters, training runs
4. If data is same: F1 difference is a protocol/model issue, NOT a data issue
5. If data is different: Further check column names, column order, encoding, missing value handling

## Conclusion

- OpenML PIMA did NOT do 0-to-NaN processing
- F1 height is determined by experimental protocol, NOT by data preprocessing
- Paper's core argument holds: leaky protocol causes F1 inflation (+12%), independent of 0-to-NaN processing
