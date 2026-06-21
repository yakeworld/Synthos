# Vocal Fold / Phonation Biomechanics — Domain-Specific Query Patterns

> Domain Expansion #6 (auditory → vocal fold/phonation). Cycle 160 (2026-06-22).
> K-014 Vocal Fold Oscillator kernel proposed. Structural analog to K-003 cupula (mechanical oscillator).

## Domain Overview

| Property | Value |
|:---------|:------|
| Physiological system | Laryngeal / phonatory |
| First Synthos candidate | vocal-fold-phonation-PINN |
| Kernel | K-014 Vocal Fold Oscillator |
| Clinical prevalence | Voice disorders ~30M US adults |
| Addressable diseases | VF paralysis, nodules, presbyphonia, MTD, Reinke's edema, cancer |
| Non-invasive data | Acoustic analysis, neck-surface acceleration (ACCEL) |
| Gold-standard data | Videostroboscopy (semi-invasive, requires scope) |
| Existing computational models | Classical FEM, Bernoulli flow models, inverse filtering (1980s-) |

## 2-ODE+PINN Architecture

- **ODE-1**: Vocal fold oscillation — mass-spring-damper (m, k, b)
- **ODE-2**: Airflow-glottis coupling — Bernoulli pressure-flow (P_sub, A_g, P_tra)
- **PINN target**: Patient-specific biomechanical parameters from acoustic signal or neck acceleration
- **Inverse problem**: Acoustic spectrum → biomechanical parameters (classically solved via linear inverse filtering, now via PINN)

## False Positive Patterns

### VF1 — Forward PINN ≠ Inverse PINN (Critical)

Narrow PINN queries return 2 hits, BOTH forward mechanics PINN models:
1. "Physics-informed neural network for predicting in vacuo vocal fold eigenmodes" (PMID 41940750, JASA Express Lett 2026) — **forward eigenvalue solver** for vocal fold structural vibration. Solves PDE, does NOT infer patient-specific clinical parameters.
2. "Predicting 3D soft tissue dynamics from 2D imaging using physics informed neural networks" (PMID 37208428, Commun Biol 2023) — **forward reconstruction** of 3D tissue deformation from 2D images. Not inverse parameter inference.

**Classification**: Both are forward PINN models (PINN used as numerical PDE solver). NOT competition for inverse clinical parameter inference. Same pattern as PLR data-driven DNN (v136) and classical FEM models (v121).

**Detection**: If a PINN paper title contains "predicting", "solving", "reconstruction", "eigenmode" without "parameter inference", "patient-specific", or "clinical", classify as forward PINN — NOT competition.

### VF2 — Data-Driven NN ≠ PINN

The closest competitor found: "Neural network-based estimation of biomechanical vocal fold parameters" (PMID 38449783) — a standard data-driven neural network. No physics-informed component, no ODE constraints. Same pattern as Zandi 2021 PLR DNN.

**Detection**: Title contains "neural network" without "physics-informed", "ODE", or "differential equation" → classify as data-driven DNN.

### VF3 — Bayesian Inference ≠ PINN

Two Bayesian inference papers found:
1. "Bayesian Inference of Vocal Fold Material Properties from Glottal Area Waveforms Using a 2D Finite Element Model" (PMID 34046213) — FEM + MCMC
2. "Effect of high-speed videoendoscopy configuration on reduced-order model parameter estimates by Bayesian inference" (PMID 31472542) — reduced-order + Bayesian

Both are MCMC/VI approaches, NOT PINN/ODE learning. Same distinction as classical lumped-parameter models ≠ PINN competition.

### VF4 — Clinical Dominance

Broad query "(vocal fold OR phonation OR voice) AND (biomechanical model) AND clinical" returns 644 hits. ALL are:
- Clinical outcome studies after voice therapy/surgery
- Diagnostic classification studies (ML-based dysphonia detection)
- Epidemiological voice disorder surveys

**Diagnostic rule**: 600+ hits on broad computational + clinical query → scan top-3. If all three are diagnostic/clinical studies (not computational models of the underlying physiology), the count is a false positive. Only counts as competition if a paper proposes an ODE/PINN/parameter-inference model of vocal fold dynamics.

## Domain-Specific Challenges

### CF1 — Laryngoscopy Requirement for Gold Standard
Unlike VOG (oculomotor, non-invasive) or ECG/BP (autonomic, non-invasive), the gold standard for vocal fold assessment requires videostroboscopy — a semi-invasive procedure requiring a transoral or transnasal scope. This limits clinical translation for screening applications.

**Mitigation**: (a) Acoustic analysis and neck acceleration are fully non-invasive and provide rich spectral/temporal data. (b) The PINN inverse problem can be solved from acoustic signal alone (inverse filtering is well-studied). (c) Videostroboscopy is routine in ENT clinics — data access is feasible for retrospective studies.

### CF2 — Multiple Equally-Parameterized Models
Vocal fold biomechanics has at least 3 well-established lumped-parameter models:
- Titze 2-mass model (1984) — widely used for pathological simulation
- Ishizaka-Flanagan 2-mass (1972) — original asymmetric model
- Story-Titze 3-mass (1995) — added arytenoid coupling

This is unlike oculomotor (VSI kernel is the consensus model). The PINN formulation must commit to one model family for identifiability.

### CF3 — Subjectivity in Acoustic Analysis
Acoustic feature extraction (jitter, shimmer, HNR, cepstral peak prominence) is sensitive to recording conditions, microphone placement, and ambient noise. This adds variance not present in oculomotor VOG (which operates in controlled clinical settings).

## Query Template

### Narrow PINN/NeuralODE
```
# PubMed
(vocal fold OR phonation OR voice production) AND (physics-informed neural network OR PINN)
(vocal fold OR phonation) AND NeuralODE
(vocal fold OR phonation OR laryngeal) AND (differential equation) AND (neural network) AND (learning)

# OpenAlex
"vocal fold" "physics-informed neural network"
vocal fold PINN
"vocal fold biomechanics" "neural network" parameter
```

### Broad Computational/ODE
```
# PubMed
(vocal fold OR phonation) AND "differential equation" AND model
(vocal fold OR phonation OR voice) AND (biomechanical model) AND clinical
(vocal fold OR phonation) AND inverse AND (parameter inference OR parameter estimation)

# OpenAlex (avoid "voice" — too broad for 3D printing/robotics hits)
"vocal fold" inverse problem patient-specific
"vocal fold biomechanics" computational model
"vocal fold oscillation" model
```

## See Also

- `references/cochlear-query-patterns.md` — prior inner-ear auditory domain (structural analog K-003 → K-013)
- `references/pinn-false-positives.md` — general PINN false positive patterns
- `references/gap-analysis-template.md` — cross-ODE confound detection
