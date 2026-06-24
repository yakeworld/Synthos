# Notebook-Script Reconciliation Workflow

## Problem: Divergent Experiment Sources

When a project has both a `.ipynb` and several `.py` scripts producing experiment results:

```
Notebook (teaching narrative, old/approximate numbers)
  + run_ensemble.py (different model config)
  + run_ablation.py (5x2 CV LDA, different from paper's 10-fold GBC)
  + pima_definitive.py (most accurate but gets out of sync)
  + definitive_ablation.json vs definitive_experiment.json (contradictory)
  = paper.tex with values that match NO source exactly
```

**Root cause**: The notebook tells a pedagogical story (step-by-step explanation). The scripts produce authoritative numbers. They are written by different people at different times and diverge.

## Resolution Steps

### Step 1: Identify every executable source

List all files that produce numeric output (notebooks, Python scripts, R scripts).

### Step 2: Trace each paper claim to its source

For each number in the paper, find which script/notebook produced it. If a number appears to match no source exactly → mark DATA_FABRICATION.

### Step 3: Understand each block's DESIGN INTENT

Before merging or deleting, understand WHY each block exists:

| Block type | Design intent | What it produces |
|:-----------|:-------------|:-----------------|
| Pedagogical notebook cells | Step-by-step explanation, teaching | `print()` outputs with approximate values |
| Prototype/exploratory scripts | Proof-of-concept, testing | Non-authoritative numbers |
| Production script | Authoritative experiment | JSON/CSV with definitive values |

**Rule**: Do not blindly merge pedagogical and production code. They serve different purposes.

### Step 4: Build a single authoritative source

Create ONE file that produces all paper numbers:

```
Structure:
  Act 1: EDA — visualizations, statistics, data understanding
  Act 2: Methodology — pedagogical narrative with a working example
  Act 3: Production — all experiments producing paper's tables/figures
  Act 4: Verification — save all_results.json, output authoritative values for paper.tex
```

### Step 5: Reconcile contradictory JSONs

When two result files disagree on the same metric:

1. Run the authoritative source (Step 4) to get ground truth
2. Trust ONLY the output of the single authoritative source
3. Delete or archive old result files (they cause confusion)
4. Update paper.tex values to match

### Step 6: Validate every number after every edit

Each time paper.tex is patched, re-run verification to ensure no drift.

## PIMA Case (2026-06-24)

| File | What it claimed | What was true |
|:-----|:----------------|:-------------|
| `definitive_ablation.json` | Severe F1=0.6451, Rec=0.6232 | **Authority** — matches unified script |
| `definitive_experiment.json` | Severe F1=0.6743, Rec=0.7349 | Old — same name, different implementation |
| `paper.tex` (pre-fix) | Severe: Rec=0.5030, Prec=1.000 | Complete fabrication — no code produced this |
| `paper.tex` (post-fix) | Severe: F1=0.6451, Rec=0.6232, Prec=0.7243 | ✅ Matches unified script |

**Lesson**: When contradictory JSON files exist with near-identical names (`definitive_ablation` vs `definitive_experiment`), their metadata (experiment_date, methodology field, model list) is the ONLY way to tell which one is current. Always check the date and parameter fields before trusting.

## Workflow Decision Tree

```
Found multiple experiment sources?
  │
  ├─ All agree on numbers?
  │   └─ Yes → Use any, document the single source
  │
  ├─ Contradictory?
  │   ├─ Can determine which is newer/better?
  │   │   └─ Yes → Use that one, archive others
  │   └─ No → Build unified script from scratch
  │       └─ Use unified output as THE source of truth
  │
  └─ Some numbers appear in NO source?
      └─ Mark as DATA_FABRICATION, delete from paper
```
