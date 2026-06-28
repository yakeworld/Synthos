# Baroreflex Regulation — Query Patterns & False Positives

## Status (2026-06-21)
- **Domain**: Cardiovascular baroreflex regulation (BP→HR closed-loop feedback)
- **Expansion candidate**: baroreflex-regulation-PINN (cycle-144)
- **Literature scan verdict**: ABSOLUTE_WHITE (15 queries, 0 PINN/NeuralODE/ODE competitors)
- **Score**: 22/25 (CANDIDATE, feasibility 4/5)
- **Query date**: 2026-06-21T11:00:00Z
- **Extension from**: K-009 (Cardiac Autonomic Regulation PINN — HRV SNS/PNS dynamics)

## Domain Expansion Rationale
1. **Natural kernel extension**: K-009 captures SNS/PNS dynamics from 5-min ECG. Baroreflex regulation extends this to the BP→HR feedback loop — same PNS vagal pathways (K-008 roots) but now with continuous non-invasive BP as a second observable.
2. **Abundant clinical data**: PhysioNet hosts 20+ baroreflex datasets — SupineSagittal, MGH/MF Waveform Database, Valsalva maneuver, head-up tilt.
3. **Zero equipment barrier**: Continuous non-invasive BP (Finapres, Portapres, CNAP) is standard in autonomic labs.
4. **High clinical impact**: Baroreflex sensitivity is the gold-standard biomarker for DAN, post-COVID dysautonomia, HF prognosis, and syncope risk.

## False Positive Patterns for Baroreflex/Cardiovascular Queries

### Pattern B1: Classical system identification ≠ PINN
**Query**: `"baroreflex" AND "system identification"`
**Result**: 32 PubMed hits
**Pattern**: Transfer-function models (ARX, ARMAX, parametric frequency-domain) that estimate baroreflex as a linear/nonlinear filter from spontaneous BP/HR fluctuations. These are NOT learnable patient-specific ODE systems.

**Diagnostic rule**: PubMed results referencing "ARX", "ARMAX", "transfer function", "parametric model", "coherence", or "cross-spectral" are system identification approaches — NOT PINN/ODE competition. They model the baroreflex as a signal-processing filter, not as a learnable 2-ODE system.

**Analogous to**: C2 (classical CV mechanistic models in cardiac-query-patterns.md). The baroreflex sysID literature is even denser (32 hits) than the cardiac ODE literature (5-20 hits) because baroreflex is traditionally analyzed via input-output methods rather than state-space models.

### Pattern B2: Model-based parameter estimation ≠ PINN
**Query**: `"baroreflex" AND "parameter estimation" AND "heart rate"`
**Result**: 7 PubMed hits
**Pattern**: Classical optimization (least-squares, MCMC) on lumped-parameter models (e.g., Olufsen 2005, "A practical approach to parameter estimation applied to model predicting heart rate regulation"). These formulate the model as a known ODE and estimate parameters — the **closest existing work** to a PINN approach — but still NOT physics-informed learning.

**Diagnostic rule**: Any hit mentioning "least-squares", "MCMC", "parameter estimation", "model fitting", or "optimization" with a known ODE structure is a classical model-fitting approach, NOT PINN competition. The distinction: these solve a forward optimization problem (given known ODE + sparse data → estimate parameters), whereas PINN solves an inverse learning problem (learn ODE dynamics + parameters from data).

**Clinical relevance**: The Olufsen et al. papers specifically model baroreflex during orthostatic stress and Valsalva maneuver — these are the closest methodological competitors. A PINN approach would differ by: (a) learning both the ODE dynamics AND parameters jointly, (b) handling sparse/noisy clinical data better, (c) providing patient-specific parameter posteriors.

### Pattern B3: OpenAlex cross-domain noise for baroreflex
**Queries**: `baroreflex sensitivity physics informed neural network`, `baroreflex regulation ODE model`, `baroreflex sensitivity parameter inference`, `baroreflex mathematical model cardiovascular`
**Results**: 143–2530 hits
**Pattern**: Massive cross-domain noise from general cardiovascular literature (HRV standards, obesity guidelines, pharmacology reviews, hormone studies) that mentions "baroreflex" in passing. Zero hits are baroreflex-specific PINN/ODE competition.

**Diagnostic rule**: For baroreflex queries, OpenAlex returns >100 counts for almost any query, but >90% are false positives from general cardiology/endocrinology. This is WORSE than the cardiac pattern (C4: 4 hits for HRV+ODE) because "baroreflex" appears in a broader range of cardiovascular literature as a secondary topic.

**Recommendation**: Never rely on OpenAlex for baroreflex-specific narrow queries. Use PubMed narrow PINN/NeuralODE queries exclusively for white-space confirmation. OpenAlex broad queries should only be used to check for classical model existence, not for PINN competition.

## Summary Decision Matrix

| Query Pattern | PubMed Count | Relevant PINN/ODE | Action |
|:-------------|:------------:|:-----------------:|:-------|
| Baroreflex PINN narrow | 0 | 0 | ✅ Assign 0 |
| Baroreflex NeuralODE narrow | 0 | 0 | ✅ Assign 0 |
| Baroreflex physics-informed | 1 (cerebral hemodynamics FP) | 0 | ✅ Check title, assign 0 |
| Baroreflex + ODE/differential eq | 2 (classical) | 0 | ✅ Classical ≠ PINN |
| Baroreflex sysID (close-but-no) | 32 (transfer-function) | 0 | ✅ Classical sysID ≠ PINN |
| Baroreflex param estimation | 7 (lumped model) | 0 | ✅ Classical fitting ≠ PINN |
| Baroreflex + ML | 5 (data-driven) | 0 | ✅ ML ≠ PINN |
| OA baroreflex PINN | 143 (FP only) | 0 | ✅ Cross-domain noise |
| OA baroreflex ODE | 386 (FP only) | 0 | ✅ Pharmacology noise |

## Two-ODE Architecture Pre-gap

Baroreflex regulation maps naturally to a 2-ODE+PINN system:
- **ODE-1**: BP dynamics — Windkessel-type arterial pressure model driven by cardiac output (CO) and total peripheral resistance (TPR). State variable: arterial pressure P(t). Parameters: arterial compliance C, peripheral resistance R, characteristic time τ = RC.
- **ODE-2**: Baroreflex-mediated HR modulation — same PNS/SNS pathways from K-009, but driven by baroreceptor afferent signal (P(t) - P0) rather than intrinsic HRV. State variable: heart rate H(t) or vagal efferent activity. Parameters: baroreflex gain G_BRS [ms/mmHg], set point P0, response time constant τ_BR.
- **PINN target**: Patient-specific baroreflex sensitivity (BRS = G_BRS), arterial compliance, peripheral resistance, set point — from spontaneous or induced BP/HR oscillations.
- **Clinical scenarios**: Supine resting (spontaneous BRS), Valsalva maneuver (phase II_late / IV), head-up tilt (70°), forced BP oscillation protocols.
- **Data sources**: PhysioNet — SupineSagittal (supine+sitting+sagittal tilt + Valsalva, n=30), MGH/MF Waveform (ICU multi-signal, n=250+), Valsalva maneuver datasets.

## Cross-Reference to Existing Patterns

| Pattern | Domain | Reference File | Key Distinction |
|:--------|:--------|:---------------|:----------------|
| C1-C5 | Cardiac HRV | cardiac-query-patterns.md | HRV-specific: PINN abbreviation gap, classical CV models, clinical HRV dominance |
| B1-B3 | Baroreflex BP-HR | baroreflex-query-patterns.md | Baroreflex-specific: sysID dominance (32 hits), param estimation (7 hits), OA noise (worse than cardiac) |
| V1-V? | Vestibular | vestibular-domain-query-patterns.md | VOR/OKR/PAN: animal model dominance, abbreviation collisions, gynecological FPs |
| P1-P6 | General PINN | pinn-false-positives.md | Cross-domain: keyword collisions, abbreviation collisions, domain-mismatch |
