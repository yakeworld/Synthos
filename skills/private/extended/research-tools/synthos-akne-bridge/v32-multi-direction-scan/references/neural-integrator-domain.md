# Neural Integrator Domain — Knowledge Bank for GazeStability-ODE

## Domain Overview
The neural integrator (NI) is a brainstem/cerebellar network that converts velocity-coded eye movement commands into sustained position-coded signals for gaze holding. Leaky NI → gaze-evoked nystagmus.

## Key Classical References (not PINN/ODE competition)
| Reference | Contribution | Model Type | Why Not PINN Competition |
|-----------|-------------|------------|--------------------------|
| Seung 1996, *PNAS* | Recurrent network theory of neural integrator | Abstract attractor model | No differential equations; firing rate population model |
| Major & Tank 2004, *Curr Opin Neurobiol* | Persistent neural activity mechanisms | Review | No computational model |
| Aksay et al. 2007, *Nat Neurosci* | Functional dissection of NI circuitry | Biophysical conductance-based | Too many parameters for clinical inference |
| Laurens & Angelaki 2017, *J Neurosci* | Velocity storage integrator model | Continuous attractor | Vestibular velocity storage ≠ oculomotor NI for gaze holding |

## Query Strategy for White Space Verification

### Recommended Query Set (8+3 pattern)
| # | Query | Expected Count | Notes |
|---|-------|---------------|-------|
| 1 | `gaze stability ODE` | 0 | Direct PINN/ODE query |
| 2 | `gaze stability PINN` | 0 | Direct PINN/ODE query |
| 3 | `gaze stability neural network model` | 10-15 | Returns velocity storage, PD diagnosis — irrelevant |
| 4 | `gaze holding neural network` | 20-30 | Serotonergic suppression, GANs for gaze velocity — irrelevant |
| 5 | `gaze stabilization computational model` | 50-70 | Velocity storage, poly-equilibrium theory — irrelevant |
| 6 | `gaze stability differential equation` | 0-2 | Returns CNS conference proceedings, saccadic nonlinear dynamics — irrelevant |
| 7 | `neural integrator gaze PINN` | 0 | Direct PINN query |
| 8 | `gaze holding ODE model` | 0 | Direct ODE query |

Plus 3 OpenAlex broad queries with title screening.

### False Positive Patterns to Watch
- **Velocity Storage Integrator (VSI)**: Laurens & Angelaki model — continuous attractor model for vestibular velocity storage, NOT gaze holding NI. Do not count as competition.
- **Saccadic nonlinear dynamics**: Optican & Zee models — model nystagmus generation/burst, not gaze holding.
- **"gaze" in non-oculomotor contexts**: Human-robot interaction, social cognition, infant attention tracking — all irrelevant.
- **Computational anatomy/psychosis papers**: "Gaze-centered remapping" in pointing tasks — not NI dynamics.

## Clinical Significance
| Condition | NI Deficit | Biomarker Potential |
|-----------|-----------|-------------------|
| Cerebellar ataxia | Downbeat/rebound nystagmus | τ_NI leak rate |
| PSP | Vertical gaze palsy | τ_NI asymmetry (vertical vs horizontal) |
| Brainstem stroke | INO, one-and-a-half syndrome | α asymmetry between eyes |
| MS | Internuclear ophthalmoplegia | τ_NI difference in adduction vs abduction |
| Acute vestibular syndrome | Spontaneous + gaze-evoked nystagmus | Combined τ_NI + VOR gain |

## Gap Assessment
- **Gap type**: Methodological white space — NI physiology is well-characterized, but 0 PINN/ODE formulations exist for patient-specific parameter inference
- **2-ODE design**: P(t) position NI state + V(t) velocity NI state, with leak term λ, coupling α, noise σ
- **PINN advantage**: Learns from irregular clinical VOG sampling (60-250 Hz vs laboratory 1000 Hz)
- **Clinical data source**: Routine VOG (video-oculography) from neurology/ENT clinics — widely available

## Related Directions Not Yet Scanned
- Velocity Storage Integrator PINN (VSI-PINN) — Laurens & Angelaki model as PINN learnable system
- Vestibular-only neural integrator (tilt vs translation discrimination ODE)
