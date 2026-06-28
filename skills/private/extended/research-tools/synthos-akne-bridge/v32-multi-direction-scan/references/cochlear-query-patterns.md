# Cochlear Mechanics Query Patterns (Domain Expansion #5)

**Candidate**: cochlear-mechanics-PINN
**Cycle**: 156 (2026-06-24)
**Kernel**: K-013 — Cochlear Traveling Wave (first auditory kernel in Synthos catalog)
**Structural Analog**: K-003 cupula torsion-pendulum (both inner ear hydromechanical systems)

## Query Results (Literature Scan)

| Query Type | Source | Count | Verdict |
|:-----------|:------:|:-----:|:--------|
| `(cochlear OR "basilar membrane") AND ("physics-informed" OR PINN OR "neural ODE" OR NeuralODE)` | PubMed | 0 | ✅ ABSOLUTE_WHITE |
| `(cochlea OR "inner ear") AND ("differential equation" AND "neural network")` | PubMed | 0 | ✅ ABSOLUTE_WHITE |
| `(hearing OR audiometry) AND ("physics-informed neural" OR "PINN" AND model) AND 2020:2026[dp]` | PubMed | 0 | ✅ ABSOLUTE_WHITE |
| `cochlear mechanics differential equation model` | OpenAlex | 16 | ✅ Classical analytical/FEM only |
| `basilar membrane traveling wave computational model` | OpenAlex | 29 | ✅ Classical models only |
| `hearing loss personalized model patient-specific` | OpenAlex | 77 | ✅ General genetics — NOT PINN |

## False Positive Patterns

Five distinct patterns detected:

### C1: Classical Cochlear Analytical Models ≠ PINN Competition

**Detection**: OpenAlex broad queries on cochlear mechanics return 16-29 results with titles referencing "higher-order differential equations" (1982), "elastic shells immersed in fluid" (2003), "hydromechanical biomimetic cochlea" (2006).

**Diagnostic Rule**: If the OpenAlex result's title references classical mechanics terminology — "differential equation" without "neural network", "elastic shell", "FEM", "finite element", "hydromechanical", "analytical solution" — it is NOT PINN/NeuralODE competition. These are hand-tuned analytical models with known anatomical parameters, not learnable patient-specific parameter inference.

**Worked Example**: The 1982 paper "Solving cochlear mechanics problems with higher-order differential equations" (34 citations) uses classical numerical methods — no neural network, no parameter learning from clinical data.

**Cupula Parallel**: Identical pattern to K-003 cupula (Steinhausen 1933, singular perturbation 1996, poroelastic 1999). Classical hydromechanical models of a physical system ≠ PINN competition.

### C2: Clinical Hearing Loss Literature Dominance

**Detection**: PubMed broad queries for "hearing loss" or "auditory" return 50K+ results. Clinical diagnostic studies (audiometry, OAE, ABR, hearing aid outcomes) dominate.

**Diagnostic Rule**: Screen for computational/modeling terms. If the title references "prevalence", "risk factor", "screening", "quality of life", "hearing aid benefit" — it is a clinical study, NOT a PINN competitor. True PINN competition requires a parameterized ODE formulation of cochlear mechanics trained on clinical data.

### C3: Precision Medicine / Genetics Noise (OpenAlex)

**Detection**: OpenAlex query "hearing loss personalized model patient-specific" returns 77 results with top hits about "Genetic Heterogeneity in Human Disease" (1004 cit), "Delivering precision medicine in oncology" (125 cit) — completely unrelated to cochlear mechanics.

**Diagnostic Rule**: OpenAlex cross-domain noise is worse than cardiac or baroreflex because "personalized" and "hearing" are clinical terms with broad index coverage. Check top-3 titles before counting any result as computational competition.

### C4: Data-Driven DNN ≠ PINN (Forward Model Pattern)

**Predicted Pattern** (not yet observed in probe but expected): Cochlear mechanics may have data-driven DNN papers (e.g., deep learning for audiogram prediction, DNN-based hearing aid algorithms).

**Diagnostic Rule**: If the title contains "deep learning" or "neural network" WITHOUT "physics-informed", "ODE", or "differential equation":
- It is a forward model (input → output mapping), NOT an inverse PINN (observation → parameters)
- The domain is still ABSOLUTE_WHITE for PINN/ODE approaches
- This pattern is documented in v136 (Pupillary Light Reflex) — Zandi 2021 forward DNN model

### C5: OAE/ECochG Signal-Processing Dominance

**Detection**: Broad queries for otoacoustic emissions (OAE) or electrocochleography (ECochG) return hundreds of signal-processing papers — spectral analysis, time-frequency decomposition, artifact removal.

**Diagnostic Rule**: Signal-processing of cochlear responses ≠ PINN/ODE modeling of cochlear mechanics. OAE papers analyze the output signal (otoacoustic emissions), not the underlying mechanical parameters (BM stiffness, damping, OHC gain). True PINN competition requires an inverse problem that infers mechanical parameters from the output signal.

## 2-ODE+PINN Architecture (Proposed)

| Component | ODE | State Variables | Parameters (Target) | Clinical Observable |
|:----------|:---:|:---------------|:--------------------|:--------------------|
| **ODE-1**: BM Traveling Wave | `dx/dt = -omega(x)/Q(x)*x + k(x)*P(t)` | BM displacement x(f,t) | omega_res [100-20K Hz], Q [5-20], k_gain [0.1-1.0] | Audiogram thresholds, DPOAE |
| **ODE-2**: Hair Cell Transduction | `dy/dt = (g*H(x) - y)/tau_a` | IHC receptor potential y(t) | g_gain [0.1-1.0], tau_a [1-50 ms], H_sat [0.5-1.0] | OAE phase, ECochG, ABR wave I |

**Structural Analogy to K-003**: Basilar membrane is a frequency-tuned mechanical oscillator (like cupula), but distributed across the cochlear spiral (frequency-place map). Key difference: BM has ~3,500 IHCs along the spiral, creating a 2D spatial system — dimensionality challenge for PINN.

## Query Strategy Template

```
# Narrow PINN (always returns 0 for ABSOLUTE_WHITE)
PubMed: (cochlear OR "basilar membrane") AND ("physics-informed" OR PINN OR "neural ODE" OR NeuralODE)
OpenAlex: physics-informed neural network cochlea

# Broad ODE (returns classical analytical/FEM models)
PubMed: (cochlear OR cochlea) AND ("differential equation" OR "computational model" OR mathematical) AND (mechanics OR traveling wave)
OpenAlex: cochlear mechanics differential equation model

# Clinical (returns diagnostic studies — screen out)
PubMed: (hearing loss OR presbycusis) AND (computational model OR quantitative)
```

## Clinical Translation Summary

| Application | US Population | Current Standard | PINN Advantage | Data Source |
|:------------|:-------------:|:-----------------|:---------------|:------------|
| Hearing loss diagnosis | 48M | Audiogram (subjective) | Patient-specific mechanical parameters | NHANES, UKBB |
| Hidden hearing loss | ~15% young | No clinical test | Synaptopathy parameters from OAE+ABR | Research databases |
| Presbycusis progression | 30M (65+) | Annual audiogram | Quantitative aging trajectory | Longitudinal cohorts |
| Cochlear implant optimization | 150K implantees | Trial-and-error MAPping | Individualized BM+neural params | Clinical CI databases |
| Noise-induced hearing loss | 24M | OSHA thresholds | Individual vulnerability from OAE | NIOSH, OSHA records |
