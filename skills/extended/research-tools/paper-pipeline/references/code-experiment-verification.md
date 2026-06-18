# Code Experiment Verification Pattern

> For papers with public datasets + experiment code: verify numerical claims by reviewing, fixing, and running experiment code. L0.5 requires this before trusting any paper values.

## Workflow (6 steps)

1. **FIND experiment code** — Check `experiment/`, `*.ipynb`, `*.py` in the paper directory
2. **REVIEW code logic** — Don't trust JSON outputs blindly. Check for bugs: variable name errors, incorrect SMOTE order, wrong metric computations, loop variable scoping
3. **FIX bugs found** — Document each fix
4. **RUN experiments** — Get real numerical results (use CV for robustness)
5. **COMPARE** paper claims vs JSON output. Check direction: a positive claim (e.g., "FN reduction 67%") must match sign in experiment JSON
6. **REWRITE** paper with real data. If narrative no longer supports original claim, restructure — don't force-fit

## HCS-3WT Case Study (2026-05-26)

| Paper Claim | Experiment (after fix) | Problem |
|:------------|:----------------------|:--------|
| Automation rate: 84.76% | 79.07% ± 4.19% | Overstated |
| Auto accuracy: 100% | 99.35% ± 0.71% | Overstated |
| FN reduction: 67% (3→1) | **-28%** (FN increased!) | **Directionally wrong** |

**Bugs found in experiment code (3):**
1. Undefined variable: `X_test_raw` → `X_test`
2. SMOTE applied to subset of features (6 selected) instead of full feature set (6+3 engineered)
3. FN reduction computed against last model in dict (`LR`) instead of min across all models

**Narrative restructuring**: When experiment shows FN increased instead of decreased, pivot from "error reduction" to "uncertainty concentration" — the real value is Gray Zone malignant enrichment (1.22×), not aggregate metric improvement.

## Detection command
```bash
# Quick check: does paper claim contradict experiment?
grep -oP 'fn_red|fn_reduction|auto_rate|automation' experiment/*.json | head -3
grep -oP '84\\.76|67%|100%' paper.tex  # LLM typical inflated markers
python3 -c "import json; d=json.load(open('experiment/*.json')); print(d.get('hcs3wt',{}).get('fn_reduction_pct'))"
```
