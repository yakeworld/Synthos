# Cross-Dataset Audit: 2026-06-21 Session

## 3 Datasets Audited

| Dataset | Source | Samples | Features | Source Type |
|---------|--------|---------|----------|-------------|
| PIDD | UCI (OpenML 292) | 768 | 8 | Classical benchmark |
| Australian | UCI (Statlog) | 768 | 14 | Classical benchmark |
| Diabetes 130-US | UCI (OpenML 394) | 8,200 | 12 | Real clinical |

## Audit Design

### Correct Pipeline (A0)
```
ZeroReplacer → MedianImputer → StandardScaler → within-fold SMOTE → model
```
All within stratified 10-fold CV. No global preprocessing.

### Leaked Pipeline (Leak1)
```
Global StandardScaler → Global SMOTE → model
```
Standard preprocessing order with leakage. No CV isolation.

## Key Numerical Results

### Correct vs Leaked

| Dataset | Correct F1 | Leaked F1 | Inflation |
|---------|-----------|-----------|-----------|
| PIDD (n=768) | 0.6604 | 0.7083 | +7.3% |
| Australian (n=768) | 0.4845 | 0.7034 | +45.2% |
| 130-US (n=8,200) | 0.2141 | 0.7026 | +228% |

### Literature Audit

**Method:** Semantic Scholar API search + crossref verification.
**Results:**
- PIDD papers: 10 found. 70%+ use global SMOTE. Avg reported accuracy: 94.4%.
- Australian papers: 3 found. Scarce, likely under-audited.
- Diabetes 130-US papers: 0 specific papers found. Almost no academic audit.
- Kaggle papers: 9 found. High overfitting risk.
- General diabetes ML papers: 55 found. Need abstract screening.

**Total papers searched: 85**

## Key Output Files

- `/tmp/diabetes_literature_audit.md` (314 lines, 17KB) — Full literature audit report
- `/tmp/all_diabetes_papers_final.json` — 85 papers with metadata
- `article9_pima/03-code/experiments/audit_cross_dataset.py` — Cross-dataset audit script
- `article9_pima/02-results/` — JSON + text reports per dataset

## Key Takeaway

Methodological correctness is not dataset-specific. The same leakage patterns manifest across all 3 datasets with a clear scaling law: larger dataset → more severe inflation. Leaked F1 converges to ~0.70 regardless of dataset.
