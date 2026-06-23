# Session: chest-wall-mechanics-PINN (Cycle 173, 2026-06-22)

## Domain Expansion #8
- **From**: K-015 Lower Airway Lung Mechanics (R-C + Constant-Phase Model)
- **To**: K-016 Chest Wall / Diaphragm Active Mechanics
- **Rationale**: Respiratory system = passive (lung, K-015) + active (chest wall/diaphragm, K-016). Completes full respiratory mechanics hierarchy.

## Literature Scan
- **White space**: CONDITIONAL_WHITE (score 21/25, feasibility 3/5)
- **PINN/NeuralODE**: 0 hits across 6 narrow queries
- **Classical ODE**: ~15-42 forward models (Campbell 1958, Goldman-Mead 1973, Loring 2018)
- **Clinical burden**: COPD diaphragm dysfunction (30-50% of 16M), ICU weaning (400-600K/yr), ALS (30K/yr)

## Gap Analysis (composite 0.73, CONDITIONAL)

### Architecture: 2-ODE+PINN
- **ODE-1**: Chest wall passive mechanics (R-C-I, second-order)
  - Parameters: C_cw [0.04-0.20 L/cmH₂O], R_cw [1-8 cmH₂O·s/L], I_cw [0.005-0.02 cmH₂O·s²/L]
- **ODE-2**: Diaphragm active contraction (force-length-velocity + fatigue)
  - Parameters: P_di_max [80-200 cmH₂O], τ_fatigue [2-15 min], τ_recovery [30-120 min], k_neural [0.5-2.0], L_di_opt [%], θ_threshold [0.40]
- **PINN**: Multi-modal encoder (sEMG 64 + DE ultrasound 32 + RIP 32) → 7 params

### Key Challenge: Four-way multiplicative confound
- P_di_max × (1−F_di) × k_neural × L_di — most complex in Track B
- **Mitigation**: SNIP (P_di_max anchor, $0) + ultrasound (L_di anchor, $50-100/study)
- **Residual**: 2-parameter (F_di × k_neural), separable by timescale (F_di evolves over minutes)

### Multi-scale: RED (300-12000× gap)
- Fast manifold: breath-level (0.1-0.5 Hz, 2-10s)
- Slow manifold: fatigue (minutes-to-hours)
- **Mitigation**: Two-timescale PINN training (fast head → freeze → slow head)

## Hypothesis Generation (composite 0.85, PASS)

### H1 — τ_fatigue ICU Weaning Failure Predictor (0.88 HIGHEST)
- **Claim**: τ_fatigue from 5min SBT predicts 48h extubation success (AUC ≥ 0.80), outperforming RSBI (0.60-0.70)
- **Clinical Impact**: 0.95 — highest in Track B pipeline
- **Feasibility**: 0.85 (MIMIC-III retrospective + 100-subject prospective)

### H2 — P_di_max ALS Respiratory Progression Biomarker (0.79 HIGH)
- **Claim**: Monthly PINN P_di_max detects weakness 3-6 months before FVC < 50% (sensitivity ≥ 0.85)
- **Limitation**: Requires 24-month longitudinal study, rare population

### H3 — Diaphragm Health Index DHI — Pattern #4 Integration (0.85 HIGHEST ALT)
- **Formula**: DHI = (P_di_max/100)^0.4 × (1−F_di)^0.3 × (τ_fatigue/10)^0.3
- **Claim**: Cross-disease composite discriminates diaphragm weakness (AUC ≥ 0.85) from 30s tidal breathing
- **Novelty**: 0.92 — highest in this set

### Co-Primary Strategy (Pattern #6)
- **Phase 1** ($150K, 6mo): DHI cross-sectional validation (H3 — validates PINN technology)
- **Phase 2a** ($200K, 12mo): ICU weaning τ_fatigue prediction (H1 — highest clinical impact)
- **Total**: $850K across 4 years (ATS pilot → NIH R21 → NIH R01)

## Kernel Registration: K-016 Active Muscle Contraction + Fatigue
- **Type**: First active muscle fatigue kernel in Synthos catalog
- **Structural template for**: Cardiac contractility, skeletal muscle fatigue, bladder detrusor, esophageal peristalsis, uterine contraction
- **See**: `v32-multi-direction-scan/references/active-muscle-fatigue-kernel-k016.md`
