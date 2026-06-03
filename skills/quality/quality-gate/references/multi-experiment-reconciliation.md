# Multi-Experiment Result Reconciliation in L0.5 Audits

> A paper may draw from multiple experiment runs producing slightly different metrics.
> L0.5 must reconcile paper claims with available experimental data, not reject them outright.

## The Pattern

A paper claims:
- Dice = 0.9834
- IoU = 0.9676

Available CSVs produce:
- CSV v2 (maski ≥ 6000): dice = 0.9733, iou = 0.9499
- CSV step2v3 (maski ≥ 6000): dicei = 0.9898, ioui = 0.9800
- Notebook magnitude (maskp > 0): dice = 0.9825

**None exactly match the paper, but all are in the same ballpark.** The paper's numbers are plausible given different filtering regimes.

## Correct L0.5 Approach: NOT "All or Nothing"

| Wrong approach | Correct approach |
|:--------------|:----------------|
| "Paper claims don't match → fabricated" | "Paper claims from experiment version X, CSVs from version Y → plausible" |
| "Delete or correct the numbers" | "Flag as unverified but consistent; note experiment version difference" |
| "Single CSV is truth" | "Multiple CSVs = multiple experiment runs, each with different filtering" |

## Step-by-Step Reconciliation

### 1. Identify all available result files

```bash
find . -name "*.csv" -path "*openEDS*"  # Multiple CSVs
find . -name "*.ipynb" | xargs grep -l "dice\|IoU"  # Notebooks with metrics
```

### 2. Understand the column naming

Different CSV versions may have different metric columns:

| Suffix | Meaning | Example |
|:-------|:--------|:--------|
| `dicei` / `ioui` | Initial DL model prediction | 0.9898 / 0.9800 |
| `dice` / `iou` | After 3D model optimization | 0.9741 / 0.9638 |
| `diced` / `ioud` | Double (another variant) | 0.9739 / 0.9634 |
| `dice` / `iou` (v2) | Different experiment version | 0.9733 / 0.9499 |

**Rule**: ALWAYS check what each column means before comparing to paper claims. The paper may report `dicei` (initial) while you're looking at `diced` (double-optimized).

### 3. Check filtering thresholds

Paper says: "225 images (0.820%) lacking labels, 94 images (0.34%) mask < 6000"

```python
# Paper's filter vs actual data
maski == 0: 237 images (paper says 225 — close, 12 difference)
maski < 6000: 456 total (paper says 319 — larger discrepancy)
```

**Interpretation**: The paper may have used a different filtering criterion (e.g., iris label visibility, not just mask area) or a different version of the dataset. Don't reject the claim on a 12-image difference — it's within expected annotation variance.

### 4. Accept the variance range

For L0.5 purposes, define an acceptable variance:

```
Paper claim: 0.9834
Available experiments: [0.9733, 0.9825, 0.9898]
Variance: 0.0165 (1.65%)
Paper is within the range of experimental runs → PLAUSIBLE ✅
```

### 5. Write the audit entry

```markdown
| Dice = 0.9834 | 3 CSV versions: v2(0.9733), mag(0.9825), step2v3(0.9898) | 🟡 Within experimental range — paper uses specific filtering | 
```

## When to Actually Reject

| Signal | Action |
|:-------|:-------|
| All CSVs consistently below paper by >0.05 | ❌ Reject — paper inflated |
| Single CSV with exact match | ✅ PASS |
| Range straddles paper claim | 🟡 Flag as unverified but PLausible |
| No CSV/notebook exists at all | ❌ Reject — fabricated |
| Only 1 CSV but wildly different | ❌ Reject — cannot verify |
| Paper claim > max(CSVs) + 0.02 | ❌ Reject — discrepancy too large |

## Real Example (2026-05-26)

**Paper**: 3D Eyeball Model-Constrained Iris Segmentation
**Paper claims**: Dice=0.9834, IoU=0.9676

**Data available**:
| Source | Dice | IoU | Notes |
|:-------|:----:|:---:|:------|
| CSV v2 (mask≥6000) | 0.9733 | 0.9499 | Earlier experiment version |
| CSV step2v3 (mask≥6000) | dicei=0.9898 | ioui=0.9800 | Later version, metric prefix unknown |
| magnitude notebook (mask>0) | 0.9825 | — | Different filtering |
| doublev1 notebook (mask>0) | 0.9733 | — | Different method variant |
| single_dobule notebook (mask>0) | 0.9825 | — | Closest to paper claim |

**Verdict**: 🟡 Paper claim within experimental range → plausible. Recommend future L0.5 check to trace exact filtering criteria.

## Key Principle

> **Absence of exact match ≠ fabrication.**
> **Absence of any traceable data = fabrication.**
> The paper may use a specific experiment version not in the current filesystem — flag as unverified but consistent, not as wrong.
