# Auto-Gate Inflation: Observed Patterns (2026-06-24)

> Empirical findings from the 2026-06-24 Layer B session where 3 core-direction papers were manually reviewed against their auto-gated pipeline scores.

## Summary of Findings

| Paper | Pipeline QS | Layer B Score | Delta | Verdict |
|:------|:-----------:|:-------------:|:-----:|:-------:|
| ocular-torsion-ODE | 95 | 0.585 | 36.5 | FAIL |
| tonic-VOR-PINN | 93 | 0.664 | 26.6 | FAIL |
| cerebellar-VOR-adaptation-PINN | 90 | 0.75 | 15.0 | T2 (borderline) |

**Average Delta: 26.0 points** — systematic over-scoring across all reviewed papers.

## Root Cause: Pattern L Blind Spot

The auto-gate pipeline checks:
- D10a completeness (cites ↔ bibitems) ✅
- Metric consistency between abstract and results ✅
- Compilation health (0 errors) ✅
- Code/Data section presence ✅

But it does NOT check **metric appropriateness** — specifically, whether classification metrics (AUC, Accuracy, Sensitivity, Specificity) are being used on regression tasks (ODE/PINN continuous outputs).

**All 3 papers** had this exact issue. The auto-gate passes them with QS=90-95 because all formal checks pass, but the fundamental metrics choice is invalid.

## The Blind Spot Mechanism

```
Pipeline auto-gate logic:
  1. Extract all metrics from Abstract → [MAPE, R², AUC, Accuracy]
  2. Extract all metrics from Results → [MAPE, R², AUC, Accuracy]
  3. If Abstract metrics ⊆ Results metrics → "G4: Metric consistency PASS"
  4. If no compile errors → "G7: Quality PASS"
  5. QS = 90-95 → "ready for publication"

What's MISSING:
  - For each metric, determine: is this task regression or classification?
  - If ODE/PINN outputs are continuous values, RMSE/MAE/R² apply
  - AUC/Accuracy require binary labels — where are they coming from?
```

## How to Detect Inflation in Any Paper

1. **Read the Abstract** — note all reported metrics. If you see AUC, Accuracy, Sens, Spec, ask: "What is being classified?"
2. **Trace the metrics** — find where AUC/Accuracy are computed in the Methods/Results. Is the computation described, or is it just stated as "AUC = 0.91"?
3. **Distinguish valid from invalid**:
   - **VALID**: AUC reported for a separately described SVM/RF on inferred PINN parameters (classifier: alg, features, split, labels all specified)
   - **INVALID**: AUC reported directly on ODE output values C(t), Z(t) without any classifier description — threshold undefined
4. **Compute inflation suspicion**: If a paper has Pattern L + pipeline QS ≥ 80, expect the true Layer B score to be 15-37 points lower.

## Who Should Read This

- G7 reviewers: Flag Pattern L in Phase 2 scoring (D2 Methodology and D6 Results Integrity)
- Layer B reviewers: Use the Delta formula as cross-check — if pipeline QS - LayerB*100 ≥ 10, document the inflation
- Paper repair agents: Pattern L papers need more than bib fixes — they need methodological correction before they can be genuinely submission-ready
