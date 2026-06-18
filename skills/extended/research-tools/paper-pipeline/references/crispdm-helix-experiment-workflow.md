# CRISP-DM Helix Experiment Workflow

> Data-first remediation for papers with LLM-generated numerical claims.
> Pattern from: PIMA CRISP-DM → ported to HCS-3WT WDBC (2026-05-24).

## Problem

Papers written by LLM often contain "looks real" numerical claims — specific values with ±SD, p-values, N counts — that have never been executed. Standard quality checks (Layer A + Layer B) cannot detect this because both evaluate "does it look correct?" not "was it actually run?"

## Detection

Before entering quality pipeline, check for experiment executables:

```bash
ls *.py *.ipynb 2>/dev/null | wc -l     # Python scripts
ls *.json *.csv *.tsv 2>/dev/null | wc -l  # data logs
grep -r "executed\|trained\|tested" *.log 2>/dev/null | wc -l  # execution logs
```

If all zero → all "OURS" numerical values are unverified.

Check for circular self-citation: if every numerical result cites `Article_v2` or the paper's own title, the numbers are LLM-generated.

## Remediation Workflow

### Step 0: Mine NotebookLM for existing code

Before writing new code, **check NotebookLM teaching/course materials first**. The paper's code may already exist as part of a teaching project.

```bash
# 1. Find relevant NotebookLM projects
notebooklm list | grep -i <topic>   # e.g., breast cancer, WDBC, 数据分析

# 2. Check each project's sources for code
notebooklm use <project_id>
notebooklm source list | grep -i -E "code|python|notebook|script|teaching|课程|教学|AutoML"

# 3. Extract full code
notebooklm source fulltext <source_id> -o /tmp/code.txt

# 4. Check if the code uses the same dataset as the paper
# Key: WBC Original (699×9, UCI) vs WDBC (569×30, sklearn) are DIFFERENT datasets
grep -n "load_breast_cancer\\|wisc\\|breast-cancer" /tmp/code.txt
grep -n "699\\|569\\|samples" /tmp/code.txt
```

**Dataset identity verification** — the most common mismatch:

| Dataset | Source | Samples | Features | Common Mistake |
|:--------|:-------|:-------:|:--------:|:---------------|
| WBC Original | UCI `breast-cancer-wisconsin.data` | 699 | 9 | Paper says "WDBC" but actually used WBC Original |
| WDBC | `sklearn.datasets.load_breast_cancer()` | 569 | 30 | Paper says "WBC" but actually used WDBC (no bare_nuclei) |

Check which one the paper references (look for "699", "9 features", "bare_nuclei" vs "30 features", "mean radius").

### Step 1: Adapt or write experiment code

Follow the CRISP-DM Helix pattern:

```python
# Phase 1: Load public dataset (UCI/OpenML/sklearn)
# Phase 2: Leakage-free preprocessing (all transforms fitted within CV folds)
# Phase 3: Baseline models (sklearn/PyTorch/scipy)
# Phase 4: Proposed method implementation
# Phase 5: Rigorous CV (RepeatedStratifiedKFold 10x5 or bootstrapping)
# Phase 6: Aggregate results with mean ± std across folds
# Phase 7: Ablation study
# Phase 8: Save to JSON + console print
```

Key design principles:
- **All preprocessing inside CV folds** — no leakage
- **Fixed random seed** — reproducibility (set `RANDOM_STATE = 42`)
- **Record per-fold results**, not just aggregates — enables confidence intervals
- **Print to stdout + save to JSON** — both human-readable and machine-parsable

### Step 2: Run experiment

```bash
cd <paper_dir>/experiment/
python3 run_<method>.py 2>&1 | tee experiment.log
```

Expected runtime for tabular ML (WDBC-level, 569 samples, 50 folds): ~2 minutes.

### Step 3: Update paper

- Replace all LLM-generated numbers with experimental results
- Adjust narrative: results may differ from original claims (e.g., "FN reduction 67%" may become "no improvement vs baseline")
- Add data honesty statement near Abstract:

```latex
\textbf{Data honesty statement:} every experimental number in this paper
is traceable to Python code output (10$\times$5 CV, 50 folds total).
No LLM-generated numerical claims are included.
```

- Add code availability section with repository URL
- Remove circular self-citations (Article_v2)

### Step 4: Verify

```bash
grep -c 'Article_v2' paper.tex       # should be 0
grep -n 'estimated\|simulated\|pending' paper.tex  # all flagged claims
```

### Step 5: Update L0.5 QUALITY.md

Create a traceability table:

```markdown
| Claim | Paper Value | Code Source | Status |
|:------|:-----------:|:-----------|:-------|
| N samples | 569 | `load_breast_cancer().data.shape[0]` | ✅ |
| Automation rate | 70.93% | `experiment/run_hcs3wt.py` line 287 | ✅ |
| FN count | 1.7 | `hcs3wt_fn.mean()` | ✅ |
```

## Cross-Dataset Portability

The CRISP-DM Helix methodology is dataset-agnostic. The same code template used for PIMA diabetes was adapted for WDBC breast cancer:

| Component | PIMA | WDBC |
|:----------|:-----|:------|
| Dataset source | UCI | sklearn.datasets |
| N samples | 768 | 569 |
| N features | 8 | 30 |
| CV scheme | RepeatedStratifiedKFold 10x5 | same |
| Baseline models | LDA/RF/GBC/SVC | SVC/RF/CatBoost/ET/LR |
| Key metric | F1, Recall, Leakage Λ | Automation Rate, Auto Acc, FN |

To port to a new dataset, change only:
1. `load_data()` function
2. Feature engineering (domain-specific)
3. Model list (dataset-dependent)
4. Primary metric (clinical question-dependent)

## Known Pitfalls

1. **SVC + large datasets** — O(n²) or worse. Use LinearSVC or subsample for >10K rows.
2. **SMOTE in CV** — apply ONLY inside training fold. Borderline-SMOTE is safer than vanilla SMOTE for overlapping classes.
3. **Aggregate reporting** — report mean ± std across folds, not single split. 10×5 gives 50 measurements for robust CI.
4. **Feature engineering leakage** — if engineered features involve scaling or combining raw features, fit scalers on training folds only.
5. **Narrative honesty** — LLM-generated papers often overclaim (e.g., "67% FN reduction"). Real results may be less dramatic. The honest narrative is more publishable.
6. **"Not belonging here" ≠ "fictional"** — Before marking a paper's claim as "fabricated," search NotebookLM first. The work may exist in a separate project (e.g., ADHD screening found in NotebookLM project `d5d2e76a` as part of head-mounted eye tracking, not as a standalone Synthos pipeline output). If it exists but wasn't produced by this pipeline: remove from paper but do NOT call it fabricated.
