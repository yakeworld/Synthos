# Cardiac Autonomic Regulation — Query Patterns & False Positives

## Status (2026-06-21)
- **Domain**: Cardiac Autonomic Regulation (HRV as 2-ODE+PINN)
- **First expansion candidate**: cardiac-autonomic-regulation-PINN
- **Literature scan verdict**: ABSOLUTE_WHITE (11 queries, 0 PINN/NeuralODE/ODE competitors)
- **Score**: 21/25 (CANDIDATE, feasibility 4/5)
- **Query date**: 2026-06-21T08:41Z

## False Positive Patterns for HRV/Cardiac Queries

### Pattern C1: "PINN" abbreviation collision (no valid usage)
**All queries**: `"heart rate variability" PINN`, `"HRV" PINN`, `"cardiac autonomic" PINN`
**Result**: 0 PubMed hits — EXCEPT if combined with "physics-informed" in a broad query, which then returns FALSE POSITIVES from non-cardiac domains (biomimetics, tactile comfort modeling).

**Diagnostic rule**: PubMed query `"HRV" AND "PINN"` returning 0 is a GENUINE zero, not an error. The abbreviation "PINN" has zero traction in the cardiac electrophysiology/autonomic regulation literature. This is **distinct** from the oculomotor pattern where "PINN" returns thousands of false positives from non-PINN contexts (v82 pattern).

### Pattern C2: Classical CV mechanistic models ≠ PINN competition
**Broad ODE queries** (`"heart rate" AND "differential equation" AND model`) return 5-20 PubMed hits. However, **ALL** are classical mechanistic cardiovascular models (closed-loop CV model, non-chaotic dynamical system driven by physiological noise). These are hand-tuned equations with known physiological parameters — NOT PINN/NeuralODE with learnable patient-specific parameter inference.

**Key distinction**: Classical CV models use known/measured parameters (heart rate, blood pressure, contractility) as inputs. A PINN formulation would INFER hidden patient-specific parameters (τ_SNS, τ_PNS, gain ratio) from observable outputs (RR interval time series).

**Diagnostic rule**: If a hit's title references "closed-loop model", "dynamical system", "mechanistic interpretation", or "cardiovascular model" WITHOUT "learning", "neural network", or "physics-informed", classify as classical model — NOT PINN competition. This is analogous to the cupula pattern (classical FEM/analytical ≠ PINN).

### Pattern C3: Clinical/observational HRV studies dominate PubMed
**Clinical queries** (`"HRV" AND "sympathetic" AND "model"`, `"HRV" AND "parameter inference"`) return 8-20 hits — but ALL are:
- Clinical diagnostic studies (HRV as outcome measure in hypertension, heart failure, diabetes)
- Statistical ML models (random forest, SVM predicting clinical outcomes from HRV features)
- None formulate HRV as an ODE system with learnable parameters

**Diagnostic rule**: Any PubMed result mentioning "prediction", "classification", "biomarker", "association", or "risk stratification" without an ODE/PDE formulation is a clinical study, NOT a PINN/ODE model.

### Pattern C4: OpenAlex broad queries return cross-domain noise
**OpenAlex `"HRV" + "ODE"`**: Returns 4 hits — CGM signal trends (continuous glucose monitoring), CETP activity (lipid metabolism), cardiovascular closed-loop model. Only the last is domain-relevant but it's a classical model (C2).

**Diagnostic rule**: OpenAlex broad queries on cardiac/autonomic topics have high cross-domain noise because "HRV" abbreviation appears in many contexts (heart rate variability, human rhinovirus, high-resolution video). Always check top-3 titles before declaring a non-zero count relevant.

### Pattern C5: "PINN" in OpenAlex returns ML-only false positives
**OpenAlex `"HRV" AND "PINN"`**: Count=2. One is "Machine Learning Techniques for Heart Rate Prediction" (no ODE, ML-only). The other is the tactile comfort model (C1).

This is the **reverse** of the oculomotor OA pattern where "PINN" returns classical physics papers. In cardiac, "PINN" returns pure ML papers — the physics-informed component is entirely absent.

## Summary Decision Matrix

| Query Pattern | PubMed Count | OpenAlex Count | Relevant PINN/ODE | Action |
|:-------------|:------------:|:--------------:|:-----------------:|:------|
| HRV PINN narrow | 0 | 2 (ML FP) | 0 | ✅ Assign 0 |
| HRV NeuralODE narrow | 0 | — | 0 | ✅ Assign 0 |
| HRV physics-informed | 5 (all FP) | — | 0 | ✅ Check top-3, assign 0 |
| Cardiac autonomic PINN | 0 | 0 | 0 | ✅ Assign 0 |
| HRV + ODE/differential eq | 9 (classical) | 4 (cross-domain) | 0 | ✅ Check top-3, classical ≠ PINN |
| Coupled oscillator PINN | 0 | — | 0 | ✅ Assign 0 |
| HRV + sympathetic model | 20 (clinical) | — | 0 | ✅ Clinical/statistical |

## Domain Expansion Lesson (Cycle 141)

The cardiac domain was chosen as the first non-oculomotor expansion because:

1. **Natural kernel extension**: K-008 (Autonomic Adaptation from PLR) maps directly to PNS vagal tone in ODE-2 of the HRV model. Shared autonomic physiology — muscarinic (PLR) → baroreflex (HRV).
2. **Abundant clinical data**: ECG is the most ubiquitous clinical signal — 12-lead, Holter, wearables (Apple Watch, Fitbit). PhysioNet has 100+ public HRV datasets.
3. **Zero equipment barrier**: Software-only upgrade to existing ECG analysis pipelines.

For any future domain expansion, document the same rationale: (a) which prior kernel extends, (b) data availability, (c) equipment required.
