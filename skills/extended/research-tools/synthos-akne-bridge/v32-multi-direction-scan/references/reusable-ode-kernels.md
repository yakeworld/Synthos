# Reusable ODE Kernel Components — Shared Architecture Catalog

**Maintainer**: autonomous-core-researcher  
**Last Updated**: 2026-06-21 (K-013 hypothesis_generation 0.91 — first auditory kernel. Complete 13-kernel catalog spanning auditory, cerebrovascular, cardiovascular, autonomic, and oculomotor/vestibular domains.)  
**Purpose**: Track ODE subsystems that are shared across multiple Track B candidates, enabling transfer learning and reducing gap analysis redundancy.

## Kernel Catalog

### K-001: Velocity Storage Integrator (VSI)

**Definition**: First-order lag filter that prolongs VOR time constant beyond canal cupula dynamics.

**Mathematical Formulation**:
```
State:      x(t) [°/s] — VSI internal signal
Parameters: tau_VS [5,25]s — VSI time constant
            g_VS [0.1,1.0] — VSI gain
Dynamics:   dx/dt = (g_VS · v_in(t) − x(t)) / tau_VS
Output:     VOR(t) = x(t) · g_mod(t)   (g_mod from candidate-specific ODE-2)
```

**Physiological Basis**: Velocity storage mechanism in vestibular nuclei (medial vestibular nucleus, nucleus prepositus hypoglossi). Medial vestibular nucleus type I and type II neurons form a positive-feedback loop that extends the vestibular time constant from ~5s (cupula) to ~15s (perceived rotation).

**Used By**:
| Candidate | ODE-2 | Specific Feature | Knowledge Score |
|:----------|:------|:----------------|:---------------:|
| GazeStability-ODE | Neural integrator (tau_NI, lambda) | Leaky integrator + saccadic correction | 0.88 |
| PAN-PINN | Cerebellar adaptation (tau_osc, eta) | Slow oscillation (60-120s period) | 0.88 |
| VestibularCompensation-ODE | Compensation dynamics (tau_comp, eta, alpha) | Two-tier learning rate | 0.87 |
| VOR-OKR-Coupling-PINN | Coupled VOR-OKR (VSI + OKR + coupling) | Dual subsystem + K-004 coupling | 0.88 |
| caloric-test-response-ODE | Canal-ocular response (VSI + thermal) | Thermal convection ODE-1 + VSI ODE-2 | 0.86 |
| VestibularCollicReflex-PINN (completed) | K-006 otolith transduction (static) + K-001 variant (torsional VSI) | 0.82 (knowledge_entry) |

**Clinical Domains Covered by VSI-Based Candidates**:
- Gaze stability / gaze holding (cerebellar ataxia, PSP, MS INO)
- Periodic alternating nystagmus (cerebellar nodulus/uvula dysfunction)
- Vestibular compensation post-UVL (neuritis, schwannoma, Meniere's)
- Visual-vestibular coupling dysfunction (concussion/TBI, aging fall risk)
- Caloric test response (Meniere's endolymphatic hydrops, canal dehiscence)
- VCR / otolith-ocular reflex (Meniere's saccular hydrops, otolith dysfunction) — completed (knowledge_entry 0.82)

**Transfer Learning Notes**:
- PINN weights for the VSI kernel's 2-parameter output head can be initialized from any prior VSI candidate
- The VSI dynamics equation is identical across all five candidates — only ODE-1 and clinical context differ
- For new candidates: if ODE-2 matches VSI, skip re-derivation of state equations in gap analysis; reference this catalog entry
- Cross-candidate hypothesis testing: a single VSI parameter (tau_VS) can now be tested across 5+ clinical conditions
- **Torsional VSI variant**: VCR candidates with torsional VOR dynamics (ω_torsion, g_VCR) may use a VSI-like filter operating in the torsional axis. The state equation structure (first-order lag) may be identical to K-001 but with different parameter ranges due to otolith vs canal dynamics. Formal kernel matching is determined during gap_analysis.

### K-002: Cerebellar Adaptation (ode-2 variant)

**Definition**: VOR gain plasticity mediated by flocculus/paraflocculus Purkinje cell simple-spike modulation.

**Common Formulation Across Candidates**:
```
State:      g(t) [0.1, 1.0] — VOR gain modulation
Parameters: eta [0.001, 0.1] — learning rate (LTD/LTP)
            tau_comp [1, 720]h — compensation time constant
            alpha [0, 0.5] — directional asymmetry
Dynamics:   dg/dt = eta · (g_target − g(t)) − alpha · g(t)
            dalpha/dt = −alpha / tau_comp
```

**Used By**:
| Candidate | Adaptation Specificity | Key Parameter Difference |
|:----------|:----------------------|:------------------------|
| PAN-PINN | Slow oscillation (tau_osc) | No alpha term; tau_osc governs 60-120s period |
| VestibularCompensation-ODE | Compensation recovery | Full g, alpha, tau_comp; alpha models directional preponderance |

**Note**: Unlike K-001 (VSI kernel which is structurally identical across all three), the cerebellar adaptation ODE varies by candidate. PAN-PINN has no asymmetry term; VestibularCompensation-ODE has the full 3-parameter set. This is not a shared kernel — it's a shared physiological concept with candidate-specific parameterizations.

### K-003: Endolymph-Cupula Torsion-Pendulum (CupulaDeflection-PINN Unique)

**Definition**: Second-order overdamped oscillator model of endolymph fluid dynamics in the toroidal semicircular canal, coupled with first-order cupula viscoelastic recovery. This is the ONLY Track B candidate that does NOT share the VSI kernel (K-001).

**Mathematical Formulation**:
```
ODE-1 (Endolymph dynamics — torsion-pendulum):
  State:      theta(t) [rad] — cupula angular displacement
  Parameters: zeta [0.5, 2.0] — damping ratio (canal geometry dependent)
              omega_0 [20, 100] rad/s — natural frequency
              K [0.1, 1.0] — mechanical gain
  Dynamics:   theta_ddot + 2·zeta·omega_0·theta_dot + omega_0^2·theta = K·u(t)
  Derived:    omega_0^2 = (2·gamma·g)/(rho·R^2), zeta = c·eta/(2·sqrt(I·kappa))

ODE-2 (Cupula viscoelastic recovery):
  State:      C(t) [rad] — cupula viscoelastic displacement
  Parameter:  tau_cupula [0.01, 0.3]s — cupula time constant
  Dynamics:   dC/dt = (theta − C) / tau_cupula

PINN target: infer zeta, omega_0, tau_cupula from clinical VOR step response
(crotational chair or caloric test nystagmus decay)
```

**Physiological Basis**: Steinhausen (1933) torsion-pendulum model of endolymph flow within the semicircular canal torus. The cupula acts as a viscoelastic partition that deflects proportionally to endolymph velocity. Second-order dynamics arise from endolymph inertia + cupular stiffness + viscous damping. Canal geometry (radius R, duct cross-section, cupula stiffness kappa) sets the natural frequency and damping ratio.

**Used By**:
| Candidate | Application | Clinical Domain |
|:----------|:-----------|:----------------|
| CupulaDeflection-PINN | Patient-specific cupula parameter inference from VOR | Meniere's (tau_cupula elevated), SSCD (zeta reduced), presbyvestibulopathy (tau_cupula decreased) |

**Why It Does NOT Share VSI Kernel**: The torsion-pendulum model describes the **peripheral** cupula-endolymph mechanics (the mechanical transducer), whereas VSI describes the **central** velocity storage neural integrator (the neural filter). These are fundamentally different physiological levels — mechanical (K-003) vs neural (K-001). The cupula's time constant (~0.01-0.3s) is two orders of magnitude faster than VSI (~5-25s). A PINN trained on full VOR output would need to resolve both timescales simultaneously — a multi-scale challenge not present in VSI-only candidates. **See `references/gap-analysis-template.md` → `### ⚡ Multi-Scale Temporal Dynamics Check` for the general detection/assessment/mitigation template applicable to any candidate with a ≥10× timescale gap between ODE-1 and ODE-2.**

**Transfer Learning Notes**: No transfer from VSI candidates (different ODE structure, different parameter domain). However, the torsion-pendulum ODE-1 is analytically solvable for step inputs, providing exact training data for PINN pre-training without clinical data. This is a unique advantage — the physics is so well-characterized that synthetic data is essentially ground-truth.

**Implication for Score**:
| Shared Component | Feasibility Impact | Novelty Impact |
|:----------------|:------------------:|:--------------:|
| No shared kernel (unique K-003) | No change (base) | Full novelty preserved |
| Physical system analytically solvable | +0.10 Feasibility | No change |

### K-004: VOR-OKR Coupling (VOR-OKR-Coupling-PINN)

**Definition**: Coupling term between the VOR and OKR subsystems, describing how visual and vestibular inputs interact during natural gaze stabilization.

**Mathematical Formulation**:
```
State vector:     [x_VSI(t), x_OKR(t)]^T — VSI internal state [°/s], OKR internal state [°/s]
Parameters:       w_V→O [0.1, 0.9] — VOR-to-OKR coupling weight
                  w_O→V [0.1, 0.9] — OKR-to-VOR coupling weight
                  beta [0.5, 2.0] — coupling nonlinearity exponent
                  tau_c [5, 30]s — coupling decay time constant
Dynamics:
  dx_VSI/dt = (g_VS · v(t) − x_VSI(t))/tau_VS + w_O→V · sigma(x_OKR) · beta(t)
  dx_OKR/dt = (K_gain · e(t) − x_OKR(t))/tau_OKR + w_V→O · sigma(x_VSI) · beta(t)
  dbeta/dt = (beta_0 − beta)/tau_c
Output:           SPV(t) = x_VSI(t) + w_O→V · x_OKR(t)
```

**Physiological Basis**: The VOR and OKR systems interact at multiple levels — the velocity storage integrator receives both vestibular and visual inputs; the cerebellar flocculus modulates both systems; and in natural head movements, both systems contribute to gaze stabilization simultaneously. The coupling weight w_V→O represents how much vestibular information influences OKR-mediated responses (e.g., vestibular stimulation drives OKR-like slow phases), while w_O→V represents visual influence on VOR (e.g., retinal slip modulates VOR gain). The nonlinearity beta captures the saturating nature of the interaction — at low velocities, coupling is nearly linear; at high velocities, the cross-modal influence saturates.

**Used By**:
| Candidate | Application | Clinical Domain |
|:----------|:-----------|:----------------|
| VOR-OKR-Coupling-PINN | Patient-specific visual-vestibular coupling parameters | Concussion (w_V→O elevation), aging fall risk (beta decay), vestibular migraine (sigma_w instability) |

**Why It Is a Unique Kernel**: The coupling term between VSI (K-001) and OKR (K-002) subsystems is fundamentally different from either subsystem alone. The coupling parameters w_V→O, w_O→V, beta, and tau_c have no analog in any other candidate's ODE-1 or ODE-2. This is a second-order effect (interaction between two primary systems), requiring its own parameter identifiability analysis and clinical interpretation framework.

**Transfer Learning Notes**: 
- No direct transfer from prior candidates (unique coupling structure)
- VSI kernel (K-001) and OKR kernel (K-002) components can be initialized from GazeStability-ODE and OKR-adaptation-PINN respectively
- Coupling parameters (K-004) must be learned from scratch — no prior anywhere in the literature
- Synthetic data generation: run the coupled system with known parameters + noise

**Score Impact**:
| Shared Component | Feasibility Impact | Novelty Impact |
|:----------------|:------------------:|:--------------:|
| VSI (K-001) initializable | +0.05 Model Complexity | No change |
| OKR (K-002) initializable | +0.05 Model Complexity | No change |
| K-004 coupling term unique | No change | Full novelty preserved |

**Implication for Oculomotor Coverage**: With K-004, Synthos now covers subsystem INTERACTIONS, not just isolated subsystems. This enables modeling the complete gaze stabilization network.

### K-005: Endolymph Thermal Convection (caloric-test-response-ODE)

**Definition**: First-order thermal dynamics of endolymph temperature gradient during caloric irrigation, governing buoyancy-driven convection that deflects the cupula and triggers caloric nystagmus. The second "physical" kernel (after K-003's torsion-pendulum) and the first thermodynamically-driven oculomotor kernel.

**Mathematical Formulation**:
```
ODE-1 (Endolymph thermal convection):
  State:      T(t) [°C] — temperature gradient across horizontal SCC
  Parameters: tau_therm [5, 30]s — thermal time constant
              Delta_T₀ [2, 14]°C — applied temperature gradient
              alpha [0.01, 0.05]°C⁻¹ — thermal expansion coeff.
              beta [0.01, 0.1] rad/°C — thermal-to-cupula conversion
  Dynamics:   dT/dt = -(T − Delta_T₀ · H(t)) / tau_therm
  Output:     theta_cupula(t) = beta · T(t)

ODE-2 (Canal-ocular response — shared VSI K-001 kernel):
  State:      x(t) [°/s] — VSI internal signal
  Parameters: tau_VS [5, 25]s, g_VS [0.1, 1.0]
  Dynamics:   dx/dt = (g_VS · d(theta_cupula)/dt − x) / tau_VS
  Output:     SPV(t) = x(t)
```

**Physiological Basis**: Barany's caloric test (1906, Nobel Prize 1914) — warm/cold water creates endolymph density gradients driving buoyancy convection that deflects the cupula. "COWS" mnemonic describes nystagmus direction. Despite 120 years as the gold standard peripheral vestibular test, never formulated as a learnable 2-ODE+PINN system.

**Used By**:
| Candidate | Application | Clinical Domain |
|:----------|:-----------|:----------------|
| caloric-test-response-ODE | Patient-specific thermal + VOR pathway params from caloric test | Meniere's, canal dehiscence, presbyvestibulopathy |

**Why It Is Unique**: Thermodynamically-driven (first-order), not mechanically-driven (second-order like K-003) nor neurally-driven (like K-001). tau_therm determined by bone conductivity & blood perfusion — entirely different from neural time constants.

**Transfer Learning Notes**: ODE-1 is novel (no prior). ODE-2 (VSI) initializable from K-001 candidates. Synthetic data from thermal ODE + VSI ODE is ground-truth quality due to well-characterized physics.

**Score Impact**:
| Shared Component | Feasibility Impact | Novelty Impact |
|:----------------|:------------------:|:--------------:|
| VSI (K-001) initializable | +0.05 Model Complexity | No change |
| K-005 unique thermal kernel | No change | Full novelty preserved |
| Physics analytically tractable | +0.10 Feasibility | No change |

### ⚠️ Cross-ODE Identifiability Trap

K-005's β parameter (thermal-to-mechanical conversion, ODE-1) and K-001's g_VS parameter (VSI gain, ODE-2) both scale the same SPV output. From SPV data alone, only the product β·g_VS is identifiable — they are individually confounded. **This is the first documented scaling-parameter confound across two kernels in the catalog.** Future gap analyses that combine K-005 (or any scaling kernel in ODE-1) with K-001 (scaling gain in ODE-2) must check this.

**Mitigation protocol** (established in caloric-test-response-ODE gap analysis):
1. Obtain independent VOR gain measurement (e.g., vHIT) as external anchor → fix g_VS
2. If vHIT unavailable, use population prior g_VS = 0.50 ± 0.15 → propagate uncertainty
3. Document in the gap analysis's Parameter Identifiability section

See the `### ⚡ Cross-ODE Parameter Identifiability Confound Check` section in `references/gap-analysis-template.md` for the full detection/assessment/mitigation procedure.

### K-006: Otolith Transduction (VestibularCollicReflex-PINN — confirmed)

**Status**: ✅ **COMPLETED** — all 4 pipeline steps done (knowledge_entry 0.82, T2 PASS, cycle 136). First otolith-specific kernel in the catalog. Queue EMPTY after completion — all 12 knowledge candidates done. See `outputs/papers/_knowledge_only/VestibularCollicReflex-PINN/knowledge_entry_VestibularCollicReflex-PINN.md`.

**Definition**: First-order mechanoelectrical transduction of otolith shear force into hair cell depolarization. The first otolith-specific kernel in the catalog. Unlike canal-mediated kernels (K-001 through K-005) which model angular velocity sensing via cupula deflection, K-006 models linear acceleration sensing via otolithic membrane shear.

**Key findings (cycle 134-136)**:
- ODE-1 (Otolith transduction) simplified to **static gain** — τ_hc [1-10ms] is unidentifiable from standard 60-120Hz clinical VOG (Nyquist-limited). V_hc(t) = K_mac · F_s(t) — instantaneous shear-force transduction.
- ODE-2 (Torsional VOR) classified as **K-001 variant** with modified parameter ranges: τ_NI_torsion [1-10]s (shorter than horizontal VSI τ_VS [5-25]s), g_VCR [0.1-0.6] (lower than VOR gain g_VS [0.1-1.0]).
- **G_total = K_mac · ρ_oto · g · g_VCR** — cross-ODE scaling-parameter confound (#2 after K-005 β/g_VS). Only the product is identifiable from VOG. Mitigation: treat G_total as combined "otolith-ocular coupling gain"; clinical biomarker is VCR asymmetry, not absolute values.
- **Multi-scale**: RED tier (1000× ratio) resolved by static ODE-1 — effectively a 1-ODE+PINN system.
- True clinical value: **zero new equipment** — torsional VOG analysis is a software upgrade to existing VOG systems.

**Architecture (clinical-realistic, validated in gap_analysis)**:
```
ODE-1 (Otolith transduction — STATIC, no dynamics):
  State:      V_hc(t) [mV] — hair cell depolarization (instantaneous)
  Parameters: K_mac [1, 10] mV/Pa — macula compliance gain
              ρ_oto [2.0, 2.5] g/cm³ — otoconia density (fixed)
  Dynamics:   V_hc(t) = K_mac · ρ_oto · g · sin(θ_tilt(t))
              Note: τ_hc [1-10ms] is BELOW clinical VOG Nyquist frequency
              (60-120Hz → 8-17ms sampling interval).
              → Static approximation is VALID and NECESSARY.
  
ODE-2 (Torsional VOR dynamics — K-001 variant):
  State:      ω_torsion(t) [°/s] — torsional slow-phase velocity
  Parameters: g_VCR [0.1, 0.6] — VCR gain (lower than horizontal VOR)
              τ_NI_torsion [1, 10]s — torsional NI time constant (shorter than horizontal VSI)
  Dynamics:   dω_torsion/dt = (g_VCR · dV_hc/dt − ω_torsion(t)) / τ_NI_torsion
  Output:     ω_torsion(t) → measured by VOG torsional analysis
  
Combined:     G_total = K_mac · ρ_oto · g · g_VCR [°/s per °/s tilt velocity]
              Only G_total is identifiable from VOG. Individual factors confounded.
              VCR asymmetry = |G_total_R − G_total_L| / (G_total_R + G_total_L)
```

**Clinical VOG sampling limitation**: The hair cell time constant τ_hc (1-10ms) operates at a timescale that cannot be resolved by standard clinical VOG (60-120Hz, 8-17ms sampling period). This is a FUNDAMENTAL limitation — even with the fastest clinical VOG, the hair cell transduction is too fast to measure without ultra-high-speed (>1000Hz) systems not available in clinical practice. Therefore, ODE-1 must be simplified to a static gain in any clinical-realistic architecture.

**ODE-2 (Torsional VOR dynamics — K-001 variant confirmed in gap_analysis)**:
  - Formula confirmed: Identical first-order lag structure to K-001
  - Parameter ranges: τ_NI_torsion [1, 10]s, g_VCR [0.1, 0.6] — modified from horizontal VSI
  - Torsional neural integrator is intrinsically leakier than horizontal VSI

**Physiological Basis**: The utricular and saccular maculae contain otoconia (calcium carbonate crystals) embedded in a gelatinous otolithic membrane. Head tilt applies shear force to the otolithic membrane, deflecting hair cell stereocilia and modulating afferent firing rate. The VCR (vestibular collic reflex) generates compensatory torsional eye movements (ocular counter-roll) to stabilize the visual axis during head tilt. Unlike the angular VOR (canal-mediated), the VCR is otolith-mediated and operates with a torsional VSI that has a shorter time constant than the horizontal VSI (τ_NI_torsion [1-10]s vs τ_VS [5-25]s).

**Used By**:
| Candidate | Application | Clinical Domain |
|:----------|:-----------|:----------------|
| VestibularCollicReflex-PINN (completed — knowledge_entry 0.82) | Patient-specific otolith parameter inference from VOG during head tilt | Meniere's saccular hydrops, otolith dysfunction, SSCD, presbyvestibulopathy |

**Why It Would Be Unique**: No existing kernel models otolith transduction. K-001 through K-005 are all canal-mediated (angular velocity) or visual (retinal slip). K-006 fills the otolith/gravity-sensing gap. The hair cell time constant (1-10ms) is 3 orders of magnitude faster than VSI (5-25s) and 2 orders faster than the cupula (0.01-0.3s). This creates a multi-scale challenge comparable to K-003 but in the opposite direction (fast ODE-1 + slow ODE-2, vs K-003's slow ODE-1 + fast ODE-2).

**Transfer Learning Notes**:
- ODE-1 is novel (K-006) — no prior otolith transduction kernel exists
- ODE-2 (K-001 variant) can be initialized from GazeStability-ODE — torsional VSI shares first-order lag structure but has different parameter range (τ_NI_torsion [1-10]s vs τ_VS [5-25]s). **Use scaled initialization**: set τ_NI_torsion = 5s (midpoint), g_VCR = 0.3 (midpoint of 0.1-0.6 range).
- No synthetic data advantage for static ODE-1 (trivial to simulate — just θ_tilt(t) input)
- PINN architecture: 4-layer [128-128-64-64] tanh — ~180K parameters (smaller than prior 1.2M candidates)
- **VSI parameter range mismatch**: Transfer learning requires parameter re-scaling because torsional VSI is intrinsically leakier. The HORIZONTAL VSI (τ_VS [5-25]s) is NOT identical to the torsional VSI (τ_NI_torsion [1-10]s). Use transfer learning only for architecture weights, NOT for parameter values.

**Open Questions (RESOLVED in gap_analysis)**:

**Open Questions (RESOLVED in gap_analysis)**:

1. **ODE-2 kernel matching**: ✅ **K-001 variant** — torsional VSI shares identical first-order lag structure. Parameter ranges differ (τ_NI_torsion [1-10]s, g_VCR [0.1-0.6] vs horizontal τ_VS [5-25]s, g_VS [0.1-1.0]).
2. **ODE-2 distinctiveness**: ✅ VSI variant with modified ranges — not a distinct kernel. The torsional neural integrator is leakier (shorter time constant) due to faster otolith velocity signal decay.
3. **F_s(t) ODE necessity**: ✅ **No** — shear force is directly proportional to sin(θ_tilt), which is clinically measured. No additional ODE needed; ODE-1 is static.
4. **Multi-scale handling**: ✅ **RED tier mitigated** by static ODE-1. The ms-level τ_hc is unidentifiable from 60-120Hz VOG. Architecture simplified to 1-ODE+PINN (static gain + torsional VSI dynamics).
5. **G_total confound**: ✅ **Second documented scaling-parameter confound** (after K-005 β/g_VS in caloric test). Only product K_mac · ρ_oto · g · g_VCR identifiable. **Resolution**: treat G_total as combined parameter; clinical biomarker is VCR asymmetry, not absolute values.

## Kernel Matching Procedure

### K-007: Iris Sphincter Mechanics (PupillaryLightReflex-PINN — Completed)

**Status**: ✅ **COMPLETED** — knowledge_entry completed (six-dimension score 0.87, T2 PASS, cycle 140). First autonomic/smooth-muscle kernel in the Synthos catalog. All 6 prior kernels (K-001 through K-006) are striated muscle / neural systems — this is a fundamental paradigm shift.

**Definition**: First-order parasympathetic-mediated pupil constriction dynamics in response to light onset. Governed by pretectal olivary nucleus → Edinger-Westphal nucleus → ciliary ganglion → iris sphincter muscle (M3 muscarinic).

**Mathematical Formulation**:
```
ODE-1 (Iris sphincter constriction):
  State:      d(t) [mm] — pupil diameter
  Parameters: v_max [2, 8] mm/s — max constriction velocity
              tau_c [0.15, 0.5]s — constriction time constant
              d_min [2, 4] mm — light-adapted minimum diameter
              t_delay [0.18, 0.35]s — afferent+efferent conduction latency
  Dynamics:   dd/dt = -v_max · exp(-t/tau_c) · H(I(t) - theta)
  Output:     d_constriction = d_rest - (d_rest - d_min) · S(t)
              where S(t) = 1 - exp(-(t - t_delay)/tau_c) for t >= t_delay

Kernel class: First-order relaxation from resting diameter to light-adapted minimum
Physiological basis: Parasympathetic cholinergic M3 activation of iris sphincter
```

**Physiological Basis**: Light stimulation activates intrinsically photosensitive retinal ganglion cells (ipRGCs) → pretectal olivary nucleus → bilateral Edinger-Westphal nuclei → ciliary ganglia → iris sphincter muscles. The constriction reflects parasympathetic efferent integrity. This is the FIRST smooth-muscle kernel — all prior kernels describe striated extraocular muscles (VOR, OKR, pursuit) or neural integration (VSI). Smooth muscle has fundamentally different pharmacomechanical coupling (muscarinic → IP3 → Ca²⁺ release → contraction) with slower dynamics (τ ~0.15-0.5s vs extraocular ~0.005-0.01s).

**Used By**:
| Candidate | Application | Clinical Domain |
|:----------|:-----------|:----------------|
| PupillaryLightReflex-PINN (completed — knowledge_entry 0.87) | Patient-specific PLR parameter inference | Alzheimer's, diabetic neuropathy, TBI, Parkinson's, MS, post-COVID |

**Why It Is Unique**: First autonomic/smooth-muscle kernel. Different effector type (smooth vs striated), different signaling pathway (muscarinic vs nicotinic/cholinergic), different temporal scale (hundreds of ms vs ms), and different clinical paradigm (pupillometry vs VOG). No overlap with any prior kernel's state variables, equations, or parameter ranges.

**Transfer Learning Notes**:
- No transfer from prior candidates (fundamentally different physiology — smooth muscle vs striated muscle)
- PINN architecture: FC 2→64→128→128→64→1 (~45K params) — smaller than vestibular candidates (~120K-1.2M)
- Synthetic data: ODE-1 + ODE-2 are analytically tractable — synthetic ground-truth is high quality
- Unique advantage: pupillometry data is ABUNDANT (standard ICU procedure), enabling richer PINN training than any prior candidate

### K-008: Autonomic Adaptation / Pupil Recovery (PupillaryLightReflex-PINN — Completed)

**Status**: ✅ **COMPLETED** — knowledge_entry completed (six-dimension score 0.87, T2 PASS, cycle 140). First multi-system (parasympathetic + sympathetic + melanopsin) autonomic kernel.

**Definition**: Multi-component recovery dynamics governing pupil redilation after light offset, incorporating sympathetic input, post-illumination pupil response (PIPR), and melanopsin-driven sustained constriction.

**Mathematical Formulation**:
```
ODE-2 (Autonomic adaptation / recovery):
  State:      a(t) [mm] — recovery offset from baseline
  Parameters: tau_r [1, 30]s — recovery time constant
              K_gain [0.5, 2.0] — recovery gain factor
              tau_mel [10, 60]s — melanopsin time constant
              A_mel [0.5, 2.0] mm — PIPR amplitude
  Dynamics:   da/dt = -(a - a_0)/tau_r - c(t)·K_gain·(d - d_rest)/tau_r
  Melanopsin: d_mel(t) = A_mel·[1 - exp(-t/tau_mel)] for t > t_off
  Combined:   d_total(t) = d_rest + a(t) + d_mel(t) for recovery phase

Kernel class: Slow recovery from light-adapted minimum to dark-adapted baseline
              with melanopsin-mediated sustained constriction
Physiological basis: Sympathetic α1-adrenergic → iris dilator (recovery)
                     + melanopsin ipRGC → sustained ON signal (PIPR)
```

**Physiological Basis**: Three separate mechanisms govern pupil recovery: (a) Sympathetic input (superior cervical ganglion → iris dilator, α1-adrenergic) — actively redilates the pupil after light offset, (b) Intrinsic melanopsin phototransduction in ipRGCs — maintains a sustained constriction for 30-60s after bright light offset, (c) Parasympathetic withdrawal — constrictor input ceases. The recovery time constant τ_r is dominated by sympathetic tone, while the melanopsin parameters (τ_mel, A_mel) reflect inner retinal ipRGC function. This is the ONLY kernel in the catalog with THREE distinct physiological control systems contributing to a single observable.

**Used By**:
| Candidate | Application | Clinical Domain |
|:----------|:-----------|:----------------|
| PupillaryLightReflex-PINN (completed — knowledge_entry 0.87) | Patient-specific recovery parameter inference | Diabetic neuropathy (τ_r↑), Parkinson's (A_mel↓), TBI (τ_r↑↑) |

**Why It Is Unique**: Three-system (parasympathetic + sympathetic + melanopsin) integrative ODE — no prior kernel has more than two. The multi-timescale range (τ_r [1-30]s + τ_mel [10-60]s creates a 10-60× ratio vs ODE-1's τ_c [0.15-0.5]s). The melanopsin component introduces a novel physiological mechanism (intrinsically photosensitive retinal ganglion cells) absent from all 7 prior kernels.

**Transfer Learning Notes**:
- No transfer from prior candidates — novel ODE structure
- ODE-1 (K-007) and ODE-2 (K-008) are temporally separated (constriction 0-2s vs recovery 2-60s), enabling staged pre-training
- Clinical data is abundant (NPi-200, 30Hz, standard ICU protocol) — synthetic pre-training not critical

**Score Impact**:
| Shared Component | Feasibility Impact | Novelty Impact |
|:----------------|:------------------:|:--------------:|
| No shared kernels (K-007+K-008 unique) | No change (base) | Full novelty preserved |
| Abundant clinical data | +0.10 Feasibility | No change |
| Zero new equipment | +0.10 Clinical Translation | No change |

### K-009: Cardiac Autonomic SNS/PNS Regulation (cardiac-autonomic-regulation-PINN — proposed)

**Status**: 🔶 **HYPOTHESIS_GENERATION** — proposed in cycle-142 (2026-06-21). Completed literature_scan (ABSOLUTE_WHITE, 21/25, feasibility 4/5) + gap_analysis (composite 0.88, T2 PASS). 4 falsifiable hypotheses formulated. Next step: knowledge_entry.

**Definition**: A 2-ODE+PINN system modeling heart rate variability (HRV) as the dynamic interaction of sympathetic (SNS, ODE-1) and parasympathetic (PNS, ODE-2) drive to the sinoatrial node, enabling patient-specific autonomic parameter inference from a single 5-min resting ECG.

**Mathematical Formulation**:
```
ODE-1 (Sympathetic β-adrenergic drive):
  State:      s(t) [bpm] — SNS contribution to heart rate
  Parameters: tau_SNS [2, 10]s — SNS time constant
              g_SNS [0.5, 2.0] — SNS max gain (β-adrenergic)
              SR_baseline [0.3, 1.0] — resting SNS tone
  Dynamics:   ds/dt = (g_SNS · u_SNS(t) − s(t)) / tau_SNS
              where u_SNS(t) ∈ [0, 1] is normalized sympathetic drive

ODE-2 (Parasympathetic vagal modulation):
  State:      p(t) [bpm] — PNS contribution to heart rate
  Parameters: tau_PNS [0.5, 3]s — PNS time constant (faster than SNS)
              g_PNS [1.0, 3.0] — PNS max gain (vagal tone)
              PR_baseline [0.5, 1.0] — resting PNS tone
  Dynamics:   dp/dt = (g_PNS · u_PNS(t) − p(t)) / tau_PNS

Heart Rate Output:
  HR(t) = HR_baseline + s(t) − p(t) + ε(t)
  where ε(t) ~ OU(σ_HR) captures residual RR variability

Kernel class: First-order opposing drive system (SNS ↑HR, PNS ↓HR)
Physiological basis: SNS → β₁-adrenergic → SA node (↑HR)
                     PNS → M₂ muscarinic → SA node (↓HR)
```

**Physiological Basis**: Heart rate is continuously modulated by the autonomic nervous system. Sympathetic activation (stellate ganglia → β₁-adrenergic receptors → SA node) increases HR with a time constant of 2-10s. Parasympathetic/vagal activation (vagus nerve → M₂ muscarinic receptors → SA node) decreases HR with a faster time constant of 0.5-3s. The balance between SNS and PNS tone is captured by the LF/HF ratio from spectral analysis, which provides a built-in anchor resolving the additive gain confound (g_SNS and g_PNS both scale the same output, but LF = SNS-dominated, HF = PNS-only). This is the FIRST non-oculomotor/vestibular kernel — branching from somatic motor to cardiac autonomic regulation.

**Built-in Confound Resolution** (unique advantage over all prior kernels):
Unlike K-005's β·g_VS product confound (which requires an external vHIT measurement), the SNS/PNS additive gain confound is partially resolved by **frequency-domain HRV analysis from the exact same 5-min ECG recording**. LF power (0.04-0.15 Hz) correlates with SNS activity, HF power (0.15-0.4 Hz) correlates with PNS activity. The LF/HF ratio provides an independent estimate of g_SNS/g_PNS. This means:
- Parameter Identifiability: 0.80 with standard LF/HF anchor (vs 0.55 without)
- No external measurement, no extra equipment, no additional clinical time
- With Ewing battery protocol (Valsalva + deep breathing): Parameter Identifiability → 0.90

**Structural Analog to K-008**: K-008 (Autonomic Adaptation from PLR) uses a similar first-order recovery dynamics structure (da/dt = −(a−a₀)/τ_r) for iris dilator α₁-adrenergic sympathetic recovery. The cardiac ODE-1 SNS drive uses the same mathematical form (first-order approach to steady state) and the same neurotransmitter (norepinephrine) but different effector (SA node vs iris dilator) and different receptor (β₁ vs α₁). Classify as **Structural Analog**, NOT a direct kernel match — the input modalities (baroreflex/respiratory vs light-induced pupil response) and timescales (τ_SNS [2-10]s vs τ_r [1-30]s) differ enough to warrant a distinct kernel entry.

**Used By**:
| Candidate | Application | Clinical Domain |
|:----------|:-----------|:----------------|
| cardiac-autonomic-regulation-PINN (proposed — hypothesis_generation 0.87) | Patient-specific SNS/PNS parameter inference from 5-min resting ECG | DAN (diabetic autonomic neuropathy), PD (autonomic dysfunction), HF (heart failure), post-COVID dysautonomia |

**Why It Is Unique**: 
- First cardiac autonomic kernel — no prior kernel models sinoatrial pacemaker dynamics
- First non-motor, non-striated-muscle, non-oculomotor/vestibular kernel
- First kernel with OPPOSING drive architecture (SNS ↑ vs PNS ↓) rather than additive/sequential
- Largest addressable population — 38M US diabetics, 6M HF, 1M PD, 20-60M post-COVID survivors
- Zero new equipment — ECG is the most ubiquitous clinical signal worldwide

**Transfer Learning Notes**:
- K-008 (Autonomic Adaptation) provides a structural analog but not direct weight transfer — same mathematical family (first-order recovery) but different receptor (β₁ vs α₁), different effector (SA node vs iris dilator), and different input modality (baroreflex vs light)
- PINN weights for the first-order dynamics head can be initialized from K-008's architecture, but parameter ranges must be re-scaled
- Clinical data is ABUNDANT — PhysioNet has 100+ public HRV datasets (MIT-BIH, Fantasia, PTB-XL, MIMIC-III)
- Synthetic data from first-order ODEs is high-quality (analytically tractable)

**Score Impact**:
| Shared Component | Feasibility Impact | Novelty Impact |
|:----------------|:------------------:|:--------------:|
| K-008 structural analog (architecture, not weights) | +0.05 Architecture Design | No change — distinct receptor/dynamics/domain |
| Unique cardiac ODE-1 + ODE-2 (K-009) | No change | Full novelty preserved |
| Abundant clinical data (PhysioNet, 100+ datasets) | +0.10 Feasibility | No change |
| Zero new equipment (ECG is standard of care) | +0.10 Clinical Translation | No change |
| Built-in LF/HF confound anchor | +0.10 Parameter Identifiability | No change |

## Recommended Primary Hypothesis (from gap_analysis)

**H1: τ_PNS as Early DAN Biomarker** (composite 0.87, HIGHEST)
- τ_PNS from single 5-min ECG predicts subclinical DAN with ROC AUC ≥ 0.85
- Most identifiable parameter (5/5 stars) — directly measurable from HF band
- Largest addressable population (38M US T2DM, ~50% with undiagnosed DAN)
- Zero new equipment — software-only upgrade to existing ECG analysis

### K-010: Windkessel BP Dynamics (baroreflex-regulation-PINN — proposed)

**Status**: ✅ **KNOWLEDGE_ENTRY** — completed cycle-147 (2026-06-21). Full pipeline done: literature_scan (22/25, feasibility 4/5, ABSOLUTE_WHITE) → gap_analysis (0.81) → hypothesis_generation (0.87) → knowledge_entry (0.88, T2 PASS). K-010 now a registered kernel. Queue EMPTY — all 15 candidates processed.

**Definition**: First-order Windkessel model of arterial pressure dynamics driven by cardiac output (from heart rate) and modulated by arterial compliance and peripheral resistance. First cardiovascular hemodynamics kernel — branching from autonomic regulation (K-009) to the closed-loop BP-HR system.

**Mathematical Formulation**:
```
ODE-1 (Windkessel BP dynamics):
  State:      P(t) [mmHg] — arterial pressure
  Parameters: C [0.5, 2.0] mL/mmHg — arterial compliance
              R [10, 30] mmHg*s/mL — peripheral resistance
              SV [50, 100] mL — stroke volume (fixed per-patient)
  Derived:    tau = R*C [5, 60]s — Windkessel time constant
  Dynamics:   dP/dt = (H(t)*SV/(1000*C) - P(t)/(R*C))
              where H(t) from ODE-2 (baroreflex-modulated HR)

ODE-2 (Baroreflex HR modulation — structural analog to K-009):
  State:      H(t) [bpm] — heart rate
  Parameters: G_BRS [5, 30] ms/mmHg — baroreflex gain
              P0 [80, 120] mmHg — set point
              tau_BR [0.5, 3]s — response time constant
              delta [0.2, 0.5]s — conduction delay
              H_base [50, 90] bpm — baseline HR
  Dynamics:   dH/dt = (H_base + G_BRS*(P(t-delta)-P0) - H(t))/tau_BR
              Saturation: Delta_H in [-30, +30] bpm

PINN target: infer C, R, G_BRS, P0, tau_BR, delta from spontaneous or induced BP/HR oscillations
(Finapres + ECG, dual-observable)
```

**Physiological Basis**: Frank's Windkessel model (1899) — arterial pressure determined by cardiac output (inflow) and peripheral runoff (outflow). First CLOSED-LOOP kernel in the catalog — ODE-1 (BP) drives ODE-2 (HR) via baroreflex, and ODE-2 feeds back via cardiac output. Dual-observable (both state variables independently measurable) provides strongest identifiability of any candidate.

**Used By**:
| Candidate | Application | Clinical Domain |
|:----------|:-----------|:----------------|
| baroreflex-regulation-PINN (proposed — gap_analysis 0.81) | Patient-specific BRS + vascular params from BP+ECG | DAN, post-COVID dysautonomia, HF prognosis, syncope risk |

**Why It Is Unique**: First hemodynamic kernel (fluid dynamics of blood in elastic vessels vs neural/mechanical dynamics of all prior kernels). First closed-loop kernel (BP-to-HR-to-BP feedback). First kernel with explicit time-delay parameter (delta, 0.2-0.5s conduction delay).

**Cross-ODE Confound**: STRUCTURAL confound (closed-loop coupling), not multiplicative/additive like prior kernels. Mitigated by Valsalva maneuver perturbation. Parameter Identifiability: 0.75 spontaneous, 0.90 with Valsalva.

**Transfer Learning Notes**:
- ODE-2: Structural analog to K-009 (same vagal pathways, different drive)
- K-009 provides weak architecture initialization for ODE-2 only
- No prior kernel for ODE-1 (Windkessel is new)

### K-011: Respiratory Drive Oscillator (respiratory-sinus-arrhythmia-PINN — Completed)

**Status**: ✅ **KNOWLEDGE_ENTRY** — completed cycle-151 (2026-06-21). Full pipeline done: literature_scan (22/25, ABSOLUTE_WHITE) → gap_analysis (0.92) → hypothesis_generation (0.89) → knowledge_entry (0.88, T2 PASS). K-011 now a registered kernel. Queue EMPTY — all 16 candidates processed. Autonomic triad complete.

**Hypothesis Portfolio** (from cycle-150 hypothesis_generation):

| ID | Hypothesis | Target | Composite | Priority |
|:---|:----------|:-------|:---------:|:-------:|
| **H1** | **A_RSA as Subclinical DAN Screening Biomarker** | **ROC AUC ≥ 0.85 from 5-min spontaneous ECG** | **0.891** | **HIGHEST** |
| H3 | CVHI Multi-Parameter Composite Index | Multi-class F1 ≥ 0.80 (DAN vs post-COVID vs healthy) | 0.836 | HIGH |
| H2 | τ_vagal as Post-COVID Recovery Predictor | ROC AUC ≥ 0.80 for 6-month COMPASS-31 improvement | 0.814 | HIGH |

**Recommended Primary**: H1 (A_RSA DAN biomarker) — highest composite (0.891), largest addressable population (38M US T2DM, 8-19M undiagnosed DAN), zero-equipment (EDR from single-lead ECG), clearest falsifiability test (n=100 case-control cross-sectional).

**Discriminative Experiment (Pattern #5)**: Single 5-min protocol × 4 time phases tests all 3 hypotheses: Phase I spontaneous (H1), Phase II paced deep breathing (H1+H2), Phase III breath-hold (H3 V0 calibration), Phase IV recovery (H3 α dynamics).

**Six-Dimension Scoring**: Gap Sig=0.88, Meth Sound=0.88, Result Complete=0.89, Clin Transl=0.92, Reproducibility=0.83, Narrative=0.88 → **Weighted 0.88 (T2 PASS)**.

**Cross-ODE Scaling Confound**: Partial additive confound — A_RSA (modulation amplitude) and V0 (baseline tone) both scale p(t). Resolved by **built-in frequency-domain decomposition** — V0 governs DC (zero-frequency mean vagal tone), A_RSA governs AC (at respiratory frequency). No external measurement needed. This is the most clinically practical confound resolution of any cardiovascular candidate — the frequency anchor comes from the SAME ECG recording, not an additional test.

**K-011 closes the autonomic triad**: With all three cardiovascular kernels complete, Synthos now covers the complete autonomic PINN stack — spontaneous HRV (K-009), baroreflex BP-HR closed-loop (K-010), and respiratory-gated vagal modulation (K-011). This is the first fully-consolidated multi-kernel domain in the catalog.

**Definition**: Sinusoidal/physiologically-realistic oscillator model of respiratory drive, generating the respiratory phase-gated vagal modulation that produces Respiratory Sinus Arrhythmia (RSA) — the periodic variation in heart rate synchronized with breathing.

**Mathematical Formulation**:
```
ODE-1 (Respiratory drive oscillator):
  State:      φ(t) [rad] — respiratory phase (0→2π, 0 = start inspiration)
  Parameters: RR [12, 20] bpm — respiratory rate at rest
              VT [0.3, 1.0] L — tidal volume
              IE [1:1, 1:3] — inspiratory-to-expiratory ratio
              τ_exp [0.5, 2.0] s — expiratory time constant
  Dynamics:   ω_0 = 2π · RR/60 [rad/s]
              φ(t) = ω_0 · t mod 2π
              V_insp(t) = VT · sin²(φ/2) · H(sin φ > 0)
              V_exp(t) = VT · [1 − exp(−t_phase/τ_exp)] · H(sin φ < 0)
              r(t) = V(t)/max(V)
  
ODE-2 (Vagal HR modulation — structural analog to K-009):
  State:      p(t) [bpm] — PNS contribution to HR
  Parameters: A_RSA [10, 30] ms — RSA amplitude (max modulation depth)
              τ_vagal [0.5, 2.0] s — vagal activation time constant
              V0 [10, 30] bpm — baseline vagal tone
              α [0.5, 2.0] — respiratory coupling exponent
  Dynamics:   dp/dt = −(p − V0)/τ_vagal + A_RSA · r(t)^α
  Output:     HR(t) = HR_basal − p(t)

Kernel class: Phase-gated oscillatory drive + first-order vagal modulation
Physiological basis: Respiratory brainstem (preBötzinger → NTS → nucleus ambiguus)
                      → vagus → SA node M₂ muscarinic ↓HR
```

**Physiological Basis**: Respiration gates vagal efferent outflow at the brainstem level. During inspiration, the preBötzinger complex and NTS suppress cardiac vagal preganglionic neuron activity → vagal withdrawal → HR accelerates. During expiration, vagal outflow resumes → HR decelerates. This respiratory-gated vagal modulation produces RSA — a 5-15 bpm oscillation in HR locked to breathing frequency. RSA amplitude (A_RSA) is the gold-standard measure of cardiac vagal tone.

**Used By**:
| Candidate | Application | Clinical Domain |
|:----------|:-----------|:----------------|
| respiratory-sinus-arrhythmia-PINN (proposed — gap_analysis 0.92) | Patient-specific vagal parameter inference from 5-min ECG + respiratory/EDR | DAN, post-COVID dysautonomia, HF, COPD, OSA, panic disorder |

**Why It Is Unique**: First respiratory/cardiopulmonary kernel — no prior kernel models respiratory mechanics or respiratory-gated cardiac modulation. All 10 prior kernels (K-001 through K-010) model either vestibular/somatic motor or cardiovascular hemodynamics — this is the FIRST kernel connecting the respiratory and cardiac systems. Also the first oscillator-with-threshold kernel (sin² inspiratory waveform, expiratory decay), distinct from all existing first-order-relaxation kernels.

**Structural Analog Check — ODE-2 vs K-009**: ODE-2 (Vagal HR modulation) is a structural analog to K-009's PNS kernel — same vagal efferent pathway (PNS → M₂ muscarinic → SA node), same first-order relaxation dynamics (`dp/dt = −(p − V₀)/τ`). The differences: (a) K-009 PNS is driven by spontaneous baroreflex fluctuations, (b) K-011 ODE-2 is driven by respiratory phase-gated vagal withdrawal — fundamentally different input modality (phase-gated vs amplitude-modulated). Classification: **Structural Analog**, NOT direct kernel match.

**Transfer Learning Notes**:
- ODE-1: Novel oscillator — no prior architecture to transfer from
- ODE-2: Structural analog to K-009 — K-009 provides weak architecture initialization for the first-order dynamics head, but parameter ranges differ (τ_vagal [0.5-2]s vs τ_PNS [0.5-3]s)
- Clinical data is ABUNDANT — PhysioNet 50+ datasets with simultaneous ECG+respiratory
- EDR (ECG-derived respiration) from single-lead ECG is validated — zero additional hardware

**Score Impact**:
| Shared Component | Feasibility Impact | Novelty Impact |
|:----------------|:------------------:|:--------------:|
| K-009 structural analog (architecture, not weights) | +0.05 Architecture Design | No change — distinct oscillator+phase-gated modulation |
| Unique ODE-1 (K-011 respiratory oscillator) | No change | Full novelty preserved |
| Abundant clinical data (PhysioNet 50+ datasets) | +0.10 Feasibility | No change |
| Zero new equipment (EDR from single-lead ECG) | +0.10 Clinical Translation | No change |
| Built-in frequency-domain DC/AC anchor | +0.10 Parameter Identifiability | No change |

**Cross-ODE Scaling Confound**: Partial additive confound — A_RSA (modulation amplitude) and V0 (baseline tone) both scale p(t). Resolved by **built-in frequency-domain decomposition** — V0 governs DC (zero-frequency mean vagal tone), A_RSA governs AC (at respiratory frequency). No external measurement needed. This is the most clinically practical confound resolution of any cardiovascular candidate — the frequency anchor comes from the SAME ECG recording, not an additional test.

## Kernel Matching Procedure

When designing a new candidate's architecture:
1. Compare ODE-1 state variables, parameters, and equations against K-001 through K-00N
2. Match is confirmed when: (a) at least 2 state variables match, (b) equation structure is identical up to parameter names, (c) parameter ranges overlap
3. If match found: add the new candidate to the "Used By" table and update transfer learning notes
4. If no match: the kernel is potentially new — consider adding K-00N entry

## Cross-Candidate Hypothesis Matrix

The VSI kernel's parameter tau_VS can now be tested across multiple clinical domains:

| Condition | Candidate | tau_VS Signature | Clinical Value |
|:----------|:----------|:-----------------|:--------------|
| Cerebellar ataxia | GazeStability-ODE | tau_VS down (leaky integrator) | Diagnostic marker |
| Periodic alternating nystagmus | PAN-PINN | tau_VS modulation by oscillation phase | Disease staging |
| UVL compensation | VestibularCompensation-ODE | tau_VS asymmetry (directional preponderance) | Recovery prediction |
| Concussion visual-vestibular coupling | VOR-OKR-Coupling-PINN | tau_VS elevation + w_V→O elevation | Return-to-play decision |
| Meniere's vs dehiscence | caloric-test-response-ODE | tau_VS from caloric nystagmus decay + tau_therm from thermal rise time | Differential diagnosis |
| Otolith dysfunction | VestibularCollicReflex-PINN (completed — knowledge_entry 0.82) | g_VCR asymmetry during head tilt (G_total asymmetry >25%) | Saccular hydrops screening (ROC AUC ≥ 0.80) |

The CupulaDeflection-PINN adds an independent axis of inference — not tau_VS (central), but tau_cupula (peripheral) — enabling multi-scale vestibular diagnostics: peripheral sensory transducer vs central neural integrator. The caloric-test-response-ODE further adds a second peripheral (thermophysical) axis — tau_therm (heat transfer dynamics) and beta (thermal-to-mechanical coupling) — enabling tri-level diagnostics: thermophysical (outer) → mechanical (middle) → neural (inner).

The VestibularCollicReflex-PINN adds a FOURTH axis — otolith-mediated transduction — completing canal + otolith + thermal coverage of the peripheral vestibular system. This enables multi-parameter diagnostic frameworks that simultaneously assess canal function (VOR gain, VSI time constant), otolith function (VCR gain asymmetry), and thermal dynamics (caloric rise time).

### K-012: Cerebrovascular Resistance Dynamics (cerebral-autoregulation-PINN — Completed)

**Status**: ✅ **KNOWLEDGE_ENTRY** — completed cycle-155 (2026-06-21). Full pipeline done: literature_scan (22/25, feasibility 4/5, ABSOLUTE_WHITE) → gap_analysis (0.84) → hypothesis_generation (0.88) → knowledge_entry (0.88, T2 PASS). K-012 now a registered kernel. Queue EMPTY — all 17 candidates processed (16 full + 1 cancelled). Entire pipeline complete across 6 physiological domains.

**Definition**: First-order myogenic resistance regulation model of cerebral arterioles, driven by cerebral perfusion pressure (CPP) through a Lassen-curve sigmoid, coupled with a dual-input metabolic/neurogenic modulation ODE. First cerebrovascular kernel — branching from cardiovascular hemodynamics (K-010) to the BP→CBF closed-loop.

**Mathematical Formulation**:
```
ODE-1 (Cerebrovascular resistance dynamics):
  State:      R(t) [mmHg·s/mL] — cerebrovascular resistance
  Parameters: τ_R [3, 30]s — myogenic time constant
              R₀ [0.5, 2.0] mmHg·s/mL — baseline resistance
              α [0.1, 0.5] — autoregulatory gain (sigmoid slope)
  Dynamics:   dR/dt = (R₀ · f(CPP(t)) − R(t)) / τ_R
              where CPP(t) = MAP(t) − ICP(t) (ICP ≈ 10 mmHg assumed)
              f(CPP) = 1 / (1 + exp(−α · (CPP − CPP₅₀)))  (Lassen sigmoid)
              CPP₅₀ ≈ 75 mmHg

ODE-2 (Metabolic/neurogenic modulation):
  State:      M(t) [unitless] — active modulation factor
  Parameters: τ_M [5, 60]s — metabolic time constant
              β [0.2, 0.8] — CO₂ reactivity gain
              γ [0.1, 0.5] — neurovascular coupling gain
  Dynamics:   dM/dt = (β · CO₂(t) + γ · CMRO₂(t) − M(t)) / τ_M

CBF Output:
  CBF(t) = (MAP(t) − ICP(t)) / (R(t) · M(t)) [mL/100g/min]
  Measured by TCD (MCA CBFV [cm/s], transtemporal 2MHz)

PINN target: infer τ_R, R₀, α, τ_M, β, γ from spontaneous or induced BP+TCD oscillations
(BP from arterial line/Finapres + TCD CBFV, dual-observable)
```

**Physiological Basis**: Lassen curve (1959) — cerebral autoregulation maintains constant CBF across CPP 50-150 mmHg via pial arteriolar myogenic constriction/dilation. CO₂ reactivity (β) reflects vasodilatory capacity of cerebral resistance vessels. Neurovascular coupling (γ) links neural activity to CBF increase. The system is a BP→CBF closed-loop that closes the cardiovascular feedback hierarchy: sinoatrial node (K-009) → baroreflex BP→HR (K-010) → RSA cardiopulmonary (K-011) → CA BP→CBF (K-012).

**Structural Analog Check — ODE-1 vs K-010**: Both are first-order relaxation toward a BP-dependent target. K-010 (Windkessel): dP/dt = (CO/C − P/(R·C)) — linear pressure dynamics. K-012 (CA): dR/dt = (R₀·f(CPP) − R)/τ_R — sigmoid-modulated resistance dynamics. **Classification**: Structural Analog — same mathematical family (first-order relaxation), different state variable (R vs P), different input function (sigmoid vs linear). Transfer learning: architecture weights for first-order dynamics head may transfer weakly, but the sigmoid input creates a different gradient landscape requiring rescaling.

**Used By**:
| Candidate | Application | Clinical Domain |
|:----------|:-----------|:----------------|
| cerebral-autoregulation-PINN (proposed — gap_analysis 0.84) | Patient-specific CA parameter inference from TCD+BP | TBI (2.5M/yr US), stroke, SVD, dementia, post-COVID, hypertension |

**Why It Is Unique**: First cerebrovascular kernel — all 11 prior kernels (K-001 through K-011) model oculomotor/vestibular, autonomic, or cardiovascular systems. CA is a fundamentally different physiological compartment (cerebral vs systemic circulation). The Lassen curve sigmoid is a unique non-linear input function not present in any prior kernel (all prior kernels use linear, exponential, or threshold inputs). Also: **best multi-scale profile of any candidate (GREEN 2-20×)** and **strongest data position in the 17-candidate pipeline (MIMIC-III 40K+ ICU patients)**.

**Cross-ODE Confound**: 🔴 Multiplicative R×M confound — both ODEs output into CBF = CPP / (R·M). Only the product R·M is identifiable from CBF alone. **Mitigation**: frequency-domain decomposition (myogenic >0.1 Hz vs metabolic <0.05 Hz) provides a built-in anchor — same paradigm as K-009's LF/HF and K-011's DC/AC decomposition, NO external measurement needed. Parameter Identifiability: 0.75 spontaneous, 0.90 with CO₂ challenge.

**Transfer Learning Notes**:
- ODE-1: Structural analog to K-010 (first-order relaxation) — weak architecture initialization possible
- ODE-2: Dual-input metabolic modulator — NO prior kernel with this structure
- Clinical data is the MOST ABUNDANT of any candidate — MIMIC-III (40K+ ICU patients with continuous ABP, often TCD) provides 10-100× more training data than any prior cardiovascular candidate
- TCD is non-invasive, FDA-cleared, standard in neuro-ICU (50K+ US units)
- PINN architecture: ~195K params (4× FC [128-256-256-128] + 3× ResBlock)

**Score Impact**:
| Shared Component | Feasibility Impact | Novelty Impact |
|:----------------|:------------------:|:--------------:|
| K-010 structural analog (ODE-1, first-order) | +0.05 Architecture Design | No change — distinct cerebrovascular domain |
| Unique ODE-2 dual-input metabolic modulator | No change | Full novelty preserved |
| MIMIC-III 40K+ ICU patients (strongest data position) | +0.10 Feasibility | No change |
| Zero new equipment (TCD standard in neuro-ICU) | +0.10 Clinical Translation | No change |
| Built-in frequency-domain R×M confound anchor | +0.10 Parameter Identifiability | No change |
| GREEN multi-scale (2-20× — best profile) | +0.05 Model Complexity | No change |

**Clinical Impact**: TBI (2.5M/yr US — NO quantitative CA biomarker for bedside outcome prediction). Current standard (PRx) is a moving correlation, not a model-based parameter. CA PINN fills this gap with τ_R (myogenic speed), R₀ (baseline resistance), and α (autoregulatory integrity) — all from standard NICU TCD+BP monitoring. Stroke, SVD, dementia, post-COVID, and hypertension add 150M+ US addressable patients.

**Recommended Primary Hypothesis (from gap_analysis)**:

**H1: τ_R as TBI Outcome Prediction Biomarker** (composite 0.87, HIGHEST)
- τ_R from single 5-min TCD+BP recording within 24h of NICU admission predicts 6-month GOS-E outcome (ROC AUC ≥ 0.82)
- Most identifiable parameter (5/5 stars) — directly measurable from myogenic band (>0.1 Hz)
- Addresses highest clinical urgency: 2.5M/yr US TBI with NO quantitative CA biomarker

### K-013: Cochlear Traveling Wave + Hair Cell Transduction (cochlear-mechanics-PINN — in progress)

**Status**: 🔶 **HYPOTHESIS_GENERATION** — completed cycle-158 (2026-06-21). 3/4 pipeline steps done: literature_scan (22/25, CANDIDATE, feasibility 4/5, ABSOLUTE_WHITE) → gap_analysis (0.87, T2 PASS) → hypothesis_generation (0.91, T2 PASS). Next step: knowledge_entry. K-013 now a registered kernel — first auditory kernel in the Synthos catalog.

**Definition**: 2-ODE+PINN system modeling basilar membrane traveling wave mechanics (second-order acousto-mechanical oscillator, structural analog to K-003 cupula) coupled with hair cell transduction and adaptation dynamics (unique ODE-2), enabling patient-specific cochlear mechanical parameter inference from non-invasive clinical measurements (audiogram + DPOAE + ABR wave I).

**Mathematical Formulation**:
```
ODE-1 (Basilar Membrane Traveling Wave):
  State:      x(f,t) [nm] — BM displacement at characteristic frequency f at time t
  Parameters: ω_res [100, 20000] Hz × 2π — resonance frequency (tonotopic mapping)
              Q [5, 20] — mechanical quality factor
              k_gain [0.1, 1.0] — stapes-to-BM pressure transfer efficiency
              α_comp [0.2, 0.6] — OHC compressive nonlinearity exponent
  Dynamics:   d²x/dt² + (ω_res/Q)·dx/dt + ω_res²·x =
              k_gain·P(t)·(1 + α_comp·|x|^(α_comp-1))⁻¹
  Note:       Second-order damped oscillator with compressive nonlinearity,
              structurally analogous to K-003 but distributed across ~30K
              spatial elements (tonotopic frequency-position mapping)

ODE-2 (Hair Cell Transduction + Adaptation):
  State:      y(t) [mV] — IHC receptor potential
              g_OHC(t) [—] — OHC slow electromotile gain
              a(t) [—] — neurotransmitter adaptation
  Parameters: g_gain [0.1, 1.0] — BM displacement → IHC potential transduction
              τ_a [1, 50] ms — IHC/ANF adaptation time constant
              τ_OHC [10, 100] ms — OHC electromotility response time
              H_sat [0.5, 1.0] — OHC saturation fraction
              y_sat [10, 40] mV — IHC saturation threshold
  Dynamics:   dy/dt = (g_gain·H(x/f_sat) − y) / τ_a
              dg_OHC/dt = (G₀·|x|·s(x) − g_OHC) / τ_OHC
              da/dt = (α·y/(y+y₅₀) − a) / τ_adapt

PINN target: infer ω_res(f), Q(f), k_gain(f), g_gain, τ_a, g_OHC(f)
             from audiogram + DPOAE + ABR wave I
```

**Physiological Basis**: The basilar membrane (BM) is a frequency-tuned mechanical waveguide — high frequencies at the base, low frequencies at the apex (tonotopy, Greenwood 1961). Sound enters via stapes footplate, creating a traveling wave that peaks where BM resonant frequency = stimulus frequency. Outer hair cells (OHCs) provide active amplification (cochlear amplifier, ~40 dB gain) via electromotility — the OHC lateral wall contracts/depolarizes at acoustic frequencies, pumping energy into the BM. Inner hair cells (IHCs) transduce BM displacement into receptor potentials that trigger auditory nerve fiber (ANF) firing. OHC degeneration is the primary pathomechanism of presbycusis (30M US 65+). Cochlear synaptopathy (hidden hearing loss, ~15% young adults) involves ANF synapse loss with preserved OHC function — detectable only via ABR wave I amplitude reduction.

**Used By**:
| Candidate | Application | Clinical Domain |
|:----------|:-----------|:----------------|
| cochlear-mechanics-PINN (in progress — hypothesis_generation 0.91) | Patient-specific cochlear parameter inference from audiogram+DPOAE+ABR | Presbycusis (30M US), hidden hearing loss (15%), NIHL (24M exposed), Meniere's, CI optimization (150K) |

**Why It Is Unique**: First auditory kernel — all 12 prior kernels (K-001 through K-012) model oculomotor/vestibular or cardiovascular/autonomic/cerebrovascular systems. Cochlear mechanics operates at acoustic frequencies (100-20,000 Hz) — 3-6 orders of magnitude faster than any prior kernel. Two unique challenges:
1. **RED multi-scale (2000×)**: BM oscillation at 20 kHz (50 μs) vs OHC adaptation (100 ms) — worst in 18-candidate pipeline. Resolution: dual-encoder PINN + envelope loss.
2. **3-way multiplicative confound**: k_gain × g_gain × g_OHC → ABR amplitude. Resolution: DPOAE isolates g_OHC, audiogram isolates k_gain, ABR isolates g_gain.

**Structural Analog — K-003 vs K-013**: Both are second-order underdamped oscillators. K-003: single lumped canal pendulum. K-013: distributed acoustic waveguide. Architecture-level transfer possible (+0.05 Feasibility). K-013 ODE-2 is entirely novel (no prior kernel matches hair cell transduction).

**Recommended Primary Hypothesis**: H1: τ_OHC as Presbycusis Progression Biomarker (0.89) — DPOAE-only 5-min test for 30M US age-related HL, zero existing progression biomarker.

**Transfer Learning Notes**:
- ODE-1 structural analog to K-003: architecture-level weight transfer possible (second-order ODE encoder), requires τ-normalization layer (3-6 orders faster)
- ODE-2: NO prior kernel matches — entirely new structure
- Synthetic data: classical BM models (Zweig 1991, Neely 1987) provide analytical ground truth for PINN pre-training
- Clinical data: NHANES (10K+), UK Biobank hearing (250K+), DPOAE subset (~2K), ABR limited to clinical studies`
