# Session Reference: vocal-fold-phonation-PINN (Cycle 164, 2026-06-22)

**Domain**: Domain Expansion #6 — auditory → laryngeal/phonation biomechanics
**Kernel**: K-014 Vocal Fold Oscillator (structural analog to K-003 cupula)
**Architecture**: 2-ODE+PINN — ODE-1 mass-spring-damper, ODE-2 Bernoulli airflow coupling
**Model**: deepseek-v4-flash (Hermes cron job)

## Input from gap_analysis

The gap_analysis (Cycle 161) scored 0.78 (CONDITIONAL) and listed 3 drafted hypotheses as bullet points:
- H1: k stiffness as MTD biomarker
- H2: A_g0 glottal rest area as presbyphonia progression marker
- H3: K_c collision stiffness as nodule severity marker

Key gap analysis findings relevant to hypothesis generation:
- **Structural analog**: ODE-1 (second-order oscillator) transfers from K-003 cupula. ODE-2 (Bernoulli airflow) has NO analog — new kernel type.
- **Confounds**: 3-way multiplicative (α, A_g0, amplitude) + 2-way ratio (m:k). F0 anchor resolves m:k (strong). CQ anchor partially resolves A_g0 (moderate).
- **Multi-scale**: Steady phonation GREEN (all same ms timescale). Phonatory modulation YELLOW (50-1000× gap for tremor) — confirm this is NOT modeled.

## Hypothesis Output (4 hypotheses)

| ID | Title | Composite | Priority | Key Metric |
|:---|:------|:--------:|:--------:|:----------|
| H1 | k stiffness → MTD diagnostic | 0.866 | HIGHEST | ROC AUC ≥ 0.82 vs GRBAS |
| H2 | A_g0 → presbyphonia progression | 0.794 | HIGH | ROC AUC ≥ 0.78 for VHI-10 ≥ 5 |
| H3 | K_c → nodule severity | 0.748 | HIGH | Spearman ρ ≥ 0.72 with size |
| H4 | VHI-PINN multi-parameter framework | 0.762 | HIGH | 3-way accuracy ≥ 75% |

## Patterns Applied

- **Pattern #4 (Integration)**: Added H4 because 3 hypotheses share the same 30s vowel protocol. H4 novelty=0.95 (highest), integration hypothesis always justified when ≥3 parameters from same measurement.
- **Pattern #5 (Intrinsic Cyclic, new variant)**: Glottal-cycle phase segmentation — opening/peak/closing/closed/sustained oscillation/phonatory modulation phases. This is the first application of intrinsic-cyclic segmentation (not perturbation-based).

## Gate Recovery

gap_analysis 0.78 (CONDITIONAL) → hypothesis_generation 0.87 (PASS). +9 points achieved by:
1. Formalizing 3 drafted hypotheses with falsifiability tests, evidence matrices, 5-dim scoring
2. Adding H4 integration hypothesis (+novelty)
3. Adding Pattern #5 discriminative design (+testability)
4. Adding 4-phase clinical translation pathway (+feasibility)

## Pitfalls Avoided

- **Not assuming full structural analog**: ODE-1 transfers from K-003 but ODE-2 (Bernoulli) is entirely new — checked independently per ODE, not at model level.
- **Not ignoring the CQ anchor**: Closed Quotient from EGG selectively resolves the 3-way confound — documented as moderate mitigation, not ignored.
- **Three equally-parameterized model families**: Titze 2-mass vs Ishizaka-Flanagan 2-mass vs Story-Titze 3-mass. Committed to Titze (most clinically referenced) and documented the model-selection problem as a future extension.

## Scoring Details Per Hypothesis

| Dimension (weight) | H1 | H2 | H3 | H4 |
|:-------------------|:-:|:-:|:-:|:-:|
| Novelty (0.20) | 0.88 | 0.90 | 0.92 | 0.95 |
| Plausibility (0.20) | 0.82 | 0.75 | 0.70 | 0.72 |
| Testability (0.20) | 0.90 | 0.78 | 0.65 | 0.70 |
| Clinical Impact (0.25) | 0.88 | 0.82 | 0.85 | 0.80 |
| Feasibility (0.15) | 0.85 | 0.68 | 0.55 | 0.58 |
| **Composite** | **0.866** | **0.794** | **0.748** | **0.762** |
