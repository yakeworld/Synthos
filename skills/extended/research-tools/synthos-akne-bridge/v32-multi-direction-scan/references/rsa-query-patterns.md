# Respiratory Sinus Arrhythmia (RSA) — Query Patterns & False Positives

## Status (2026-06-21)
- **Domain**: Cardiopulmonary — Respiratory Sinus Arrhythmia (RSA)
- **Expansion candidate**: respiratory-sinus-arrhythmia-PINN (cycle-148)
- **Literature scan verdict**: ABSOLUTE_WHITE (14 queries, 0 PINN/NeuralODE/ODE competitors)
- **Score**: 22/25 (CANDIDATE, feasibility 4/5)
- **Query date**: 2026-06-21T23:50:00Z
- **Extension from**: K-010 (Baroreflex Regulation PINN — BP→HR closed-loop) → K-011 (RSA Cardiopulmonary — respiration-gated vagal HR modulation)

## Domain Expansion Rationale
1. **Natural kernel extension**: K-009 (cardiac autonomic SNS/PNS) + K-010 (baroreflex BP→HR) → RSA (respiratory-modulated HRV). All share PNS vagal efferent pathway. RSA is the "respiratory gate" on vagal tone — completing the autonomic triad: baseline HRV (K-009), BP-driven HRV (K-010), respiration-driven HRV (K-011 RSA).
2. **Abundant clinical data**: PhysioNet 50+ datasets with simultaneous ECG/respiratory — MGH/MF, Fantasia, CAP Sleep, MIT-BIH Polysomnographic, Apnea-ECG.
3. **Zero equipment barrier**: ECG-derived respiration (EDR) from single-lead ECG amplitude modulation is validated — pure software upgrade.
4. **High clinical impact**: RSA is gold-standard PNS vagal biomarker for DAN, post-COVID dysautonomia, HF, COPD, sleep apnea, panic disorder.

## False Positive Patterns for RSA/Cardiopulmonary Queries

### Pattern R1: "RSA" abbreviation collision (OpenAlex critical)
**All bare "RSA" queries**: `RSA PINN`, `RSA ODE`, `RSA computational model`
**Result**: OpenAlex returns 1000+ cryptography papers (Rivest-Shamir-Adleman encryption). PubMed handles it better but still risks cross-domain noise.

**Diagnostic rule**: Never use bare "RSA" in any query, especially OpenAlex. Always use the full term "respiratory sinus arrhythmia" in ALL queries. This is more severe than the VCR abbreviation collision (v133) because RSA cryptography is an entire subfield with millions of papers.

### Pattern R2: Classical cardiopulmonary CV models ≠ PINN (inherited from C2)
**Broad ODE queries**: `"respiratory sinus arrhythmia" AND "differential equation"` → 2 hits
**Result**: Both are classical models — model-based assessment of cardiopulmonary regulation (Methods, 2022) and RR interval-respiratory signal waveform modeling (Respir Physiol Neurobiol, 2014). Hand-tuned fitting, NOT PINN/NeuralODE.

**Diagnostic rule**: Same as C2 (cardiac-query-patterns.md): classical mechanistic models ≠ PINN competition. Hits referencing "model-based", "waveform modeling", "parameter estimation" without "learning", "neural network", or "physics-informed" are classical.

### Pattern R3: Clinical/observational RSA studies dominate PubMed
**Broad query**: `"respiratory sinus arrhythmia" AND model` → 255 hits
**Result**: Top titles: ARMA denoising, ML cognition prediction, developmental psychology, cardiovascular causality, psychotherapy synchrony. ALL clinical/statistical, 0 PINN/ODE.

**Diagnostic rule**: Same as C3 (cardiac-query-patterns.md): any PubMed result mentioning "denoising", "prediction", "classification", "association", or "synchrony" without an ODE formulation is a clinical/signal-processing study, NOT computational model competition.

### Pattern R4: RSA is traditionally signal-processing, not parameter inference
RSA is quantified via:
- Spectral analysis (LF/HF ratio, HF peak power)
- Peak-to-trough amplitude (expiratory-inspiratory difference)
- ARMA/ARX modeling of RR interval-respiratory coupling
- Time-frequency analysis (wavelet, Hilbert-Huang)

ALL are signal-processing features or filter-based approaches. NONE formulate RSA as a learnable 2-ODE+PINN system for patient-specific vagal parameter extraction.

**Diagnostic rule**: Any hit mentioning "spectral analysis", "ARMA", "ARX", "wavelet", "Hilbert", "time-frequency", or "peak-to-trough" is a signal-processing approach, NOT PINN competition. This is analogous to B1 (baroreflex sysID) but for RSA's spectral tradition.

### Pattern R5: ECG-derived respiration (EDR) ≠ PINN
EDR algorithms extract respiratory signals from ECG amplitude/frequency modulation. These are deterministic signal-processing methods (R-peak amplitude demodulation, QRS area modulation, principal components). They extract a respiratory signal, NOT model the cardiopulmonary interaction dynamics.

**Diagnostic rule**: Any hit referencing "ECG-derived respiration", "EDR", "R-peak amplitude", or "QRS area modulation" is a signal extraction method, NOT a cardiopulmonary model. RSA model ≠ EDR algorithm.

## Summary Decision Matrix

| Query Pattern | PubMed Count | Relevant PINN/ODE | Action |
|:-------------|:------------:|:-----------------:|:-------|
| RSA PINN narrow | 0 | 0 | ✅ Assign 0 |
| RSA NeuralODE narrow | 0 | 0 | ✅ Assign 0 |
| RSA physics-informed | 0 | 0 | ✅ Assign 0 |
| RSA ODE narrow | 0 | 0 | ✅ Assign 0 |
| RSA + differential equation | 2 (classical) | 0 | ✅ Classical ≠ PINN |
| RSA + computational model | 2 (classical/review) | 0 | ✅ Classical closed-loop + review |
| RSA + model (broad) | 255 (clinical) | 0 | ✅ Clinical/statistical/signal-processing |
| OA RSA PINN | 0 | 0 | ✅ Confirm zero |
| OA RSA + computational model | 1369 (all crypto) | 0 | ✅ R1: RSA abbreviation collision |

## Two-ODE Architecture Pre-gap

RSA maps naturally to a 2-ODE+PINN system:

- **ODE-1**: Respiratory drive — sinusoidal or physiologically realistic airflow/respiratory phase model. State variable: respiratory phase φ(t) or lung volume V(t). Parameters: respiratory rate RR [12-20 bpm], tidal volume VT [500 mL], I:E ratio [1:2].
- **ODE-2**: Vagal HR modulation — PNS efferent activity gated by respiratory phase via brainstem respiratory centers (NTS, nucleus ambiguus). State variable: instantaneous heart rate HR(t) or RR interval [ms]. Parameters: RSA amplitude A_RSA [10-30 ms], respiratory frequency coupling strength α, vagal time constant τ_vagal [0.5-2s], baseline vagal tone V0.
- **PINN target**: Patient-specific vagal parameters (A_RSA, τ_vagal, V0, α) from routine 5-min ECG + respiratory recording (or EDR).
- **Unique challenge**: Respiratory rate creates a time-varying baseline that differs from constant-baseline models (baroreflex, cardiac) — PINN must handle non-stationary HR dynamics.
- **Clinical scenarios**: Resting spontaneous breathing, paced deep breathing (6 breaths/min — standard autonomic test), Valsalva maneuver, head-up tilt, exercise recovery.
- **Data sources**: PhysioNet — Fantasia (young/old, 120 min ECG+respiration, n=40), CAP Sleep Database (polysomnography, n=108), MGH/MF Waveform (ICU, n=250+), Apnea-ECG Database (sleep apnea, n=70).

## Cross-Reference to Existing Patterns

| Pattern | Domain | Reference File | Key Distinction |
|:--------|:-------|:---------------|:----------------|
| C1-C5 | Cardiac HRV | cardiac-query-patterns.md | HRV-specific: PINN gap, classical CV models, clinical HRV dominance |
| B1-B3 | Baroreflex BP-HR | baroreflex-query-patterns.md | Baroreflex-specific: sysID (32 hits), param estimation (7 hits), OA noise |
| R1-R5 | RSA Cardiopulmonary | This file | RSA-specific: abbreviation collision (crypto), signal-processing tradition, EDR vs model, non-stationary baseline |
| V1-V? | Vestibular | vestibular-domain-query-patterns.md | VOR/OKR/PAN: animal model dominance, abbreviation collisions |
