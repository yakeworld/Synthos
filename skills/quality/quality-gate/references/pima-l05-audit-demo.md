# Pima CRISP-DM L0.5 Audit — Complete Chain

## Type A (2026-05-26): Ensemble value fabrication

| Claimed | Actual | Diff |
|:--------|:------:|:----:|
| Ensemble F1=0.7541 | 0.6986 | -0.0555 |
| Severe Leakage F1=0.7338 | 0.7657 | +0.0319 |
| Inflation +8.6% | +6.71% | -1.89% |

**Fix**: Re-ran experiments → JSON output → corrected paper

## Type B (2026-05-30): Reference chain propagation

See `scc-paper-reference-correction-2026-05-30.md`

## Type C (2026-06-03): Mixed-model ablation table ✨ NEW

**Problem**: Paper Table 2's 4-level ablation mixed models. No/Minor/Medium used Ensemble values, Severe used fabricated values that matched neither LR nor Ensemble.

**Detection**: Re-ran the ablation with both LR and Ensemble. Created `pima_definitive_experiments.py` and `cross_dataset_final.py` that output JSON. Then wrote a Python verification script to compare each value.

**Key insight**: LLM-generated papers often have "mostly correct" tables where most cells match one experiment but 1-2 cells are "borrowed" from a different experiment or simply fabricated to make the narrative more dramatic.

**Prevention check**:
```python
# Ablation table integrity check
for each row in table:
    trace all 5 metrics to a SINGLE experiment run
    verify all rows come from the same model configuration
```

## Tools

`pima_definitive_experiments.py` — LR + Ensemble dual ablation, JSON output
`cross_dataset_final.py` — LR × 3 datasets, same protocol
`results_definitive/summary.json` — all verified values
`results_cross_dataset/summary_all.json` — cross-dataset
