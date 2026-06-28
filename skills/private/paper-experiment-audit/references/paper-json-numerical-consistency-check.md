# Paper-JSON Numerical Consistency Check

**Created**: 2026-06-29
**Source**: HCS-3WT paper numerical inconsistency repair

## Overview

When auditing any ML paper, the most critical check is numerical consistency between the paper text and experiment_results.json. The JSON is the ground truth — paper text must match JSON, not the other way around.

## Step-by-Step Audit Process

### Step 1: Extract All Numerical Claims from Paper

```bash
# Extract all lines with numbers from the LaTeX file
grep -n '[0-9]\+\.[0-9]\+' paper.tex | grep -v '^\s*%' | grep -v '\\cite' | grep -v '\\section'
```

Key locations to check:
- **Abstract**: automation rate, accuracy, FN rates
- **Introduction**: contribution list with key metrics
- **Data Source**: sample count, feature count, class distribution
- **Methods**: k value, CV strategy, preprocessing steps
- **Table 2**: Single classifier ACC/REC/PREC/F1/AUC/FN
- **Table 3**: HCS-3WT triage metrics
- **Results**: discussion paragraphs with numbers
- **Conclusion**: summary metrics

### Step 2: Independent Calculation from JSON

```python
import json

with open('experiment_results.json') as f:
    results = json.load(f)

# Single classifiers
for name, data in results.get('single_models', {}).items():
    print(f"{name}: acc={data.get('accuracy'):.4f}, f1={data.get('f1'):.4f}, auc={data.get('auc'):.4f}")

# HCS-3WT metrics
hcs = results.get('hcs3wt', {})
print(f"HCS-3WT: auto_rate={hcs.get('automation_rate'):.4f}, auto_acc={hcs.get('auto_accuracy'):.4f}")
```

### Step 3: Comparison Thresholds

| Metric | Tolerance | Action if Exceeded |
|--------|-----------|-------------------|
| Single classifier ACC | >2% | P0 - immediate fix |
| Single classifier F1 | >2% | P0 - immediate fix |
| HCS-3WT automation rate | >3% | P0 - immediate fix |
| HCS-3WT accuracy | >1% | P0 - immediate fix |
| Cross-location consistency | 0% | P0 - all locations must match |

### Step 4: Parameter Consistency Check

**Feature count (k=N)**:
```bash
# Check paper claims
grep -n 'k=' paper.tex
# Check code
grep -n 'SelectKBest\|k=' 03-code/experiments/run*.py
```

**CV strategy**:
```bash
grep -n 'cross-validation\|stratified' paper.tex
grep -n 'n_splits\|n_repeats\|StratifiedKFold' 03-code/experiments/run*.py
```

**Dataset description**:
```python
with open('experiment_results.json') as f:
    n_samples = json.load(f).get('n_samples')
# Must match paper's dataset description exactly
```

### Step 5: Update Paper to Match JSON

**Always update paper to match JSON.** The JSON represents actual code output; the paper is the claim.

Update in order:
1. Data Source section (sample count, feature count)
2. Methods section (preprocessing, parameters)
3. Table 2 (single classifier metrics)
4. Table 3 (HCS-3WT metrics)
5. Abstract (all metrics)
6. Results section (all numeric references)
7. Discussion section (numeric references)
8. Conclusion (summary metrics)

**After each update, run grep to verify**:
```bash
grep '79.07' paper.tex    # Should return 0 results (old number)
grep '99.35' paper.tex    # Should return 0 results (old number)
```

### Step 6: Fix Figure Scripts

Any figure generation script that has hardcoded numbers must be converted to read from experiment_results.json.

### Step 7: LaTeX Compilation Check

```bash
pdflatex -interaction=nonstopmode paper.tex
# Check for errors:
grep '!' paper.log | grep -v 'Warning'
# Common: missing \\ at last row of table (l.203 errors cascade)
```

### Step 8: Update state.json

Update score, status, last_updated, and last_modification with full file list.

## Common Mistakes

1. **Updating JSON to match paper** — WRONG. Paper claims must match JSON truth.
2. **Skipping non-Abstract locations** — Key numbers appear in 6+ locations. grep every one.
3. **Not checking figure scripts** — Hardcoded numbers in figures are silent technical debt.
4. **Not recompiling after updates** — LaTeX syntax errors (missing `\\`) are common after mass replacement.
5. **Not checking parameter consistency** — k=6 in paper vs k=15 in code produces fundamentally different results.

## HCS-3WT Case Study

**Before**: Paper claimed 79.07% auto rate, 0.9657 accuracy, 699 samples, k=6. Code had k=15.
**Fix**: Set code k=6 → re-run experiment → update ALL paper locations → fix fig3/fig4 → compile → state.json 0.73→0.88.
