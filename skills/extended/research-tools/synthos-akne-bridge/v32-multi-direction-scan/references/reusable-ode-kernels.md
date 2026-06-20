# Reusable ODE Kernel Components — Shared Architecture Catalog

**Maintainer**: autonomous-core-researcher  
**Last Updated**: 2026-06-21 (added K-006 placeholder)  
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
| VestibularCollicReflex-PINN (confirmed) | K-006 otolith transduction (static) + K-001 variant (torsional VSI) | 0.79 (gap_analysis) |

**Clinical Domains Covered by VSI-Based Candidates**:
- Gaze stability / gaze holding (cerebellar ataxia, PSP, MS INO)
- Periodic alternating nystagmus (cerebellar nodulus/uvula dysfunction)
- Vestibular compensation post-UVL (neuritis, schwannoma, Meniere's)
- Visual-vestibular coupling dysfunction (concussion/TBI, aging fall risk)
- Caloric test response (Meniere's endolymphatic hydrops, canal dehiscence)
- VCR / otolith-ocular reflex (Meniere's saccular hydrops, otolith dysfunction) — pending gap_analysis

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

**Status**: ✅ **CONFIRMED** — gap_analysis (2026-06-21, cycle 134) completed formal kernel matching. Novel kernel: 0 of 5 prior kernels match state variables, equation structure, or parameter ranges. See `outputs/papers/_knowledge_only/VestibularCollicReflex-PINN/step_gap_analysis.md`.

**Definition**: First-order mechanoelectrical transduction of otolith shear force into hair cell depolarization. The first otolith-specific kernel in the catalog. Unlike canal-mediated kernels (K-001 through K-005) which model angular velocity sensing via cupula deflection, K-006 models linear acceleration sensing via otolithic membrane shear.

**Key gap analysis findings (cycle 134)**:
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
| VestibularCollicReflex-PINN (gap_analysis complete) | Patient-specific otolith parameter inference from VOG during head tilt | Meniere's saccular hydrops, otolith dysfunction, SSCD, presbyvestibulopathy |

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
| Otolith dysfunction | VestibularCollicReflex-PINN (confirmed) | g_VCR asymmetry during head tilt (G_total asymmetry >25%) | Saccular hydrops screening (ROC AUC ≥ 0.80) |

The CupulaDeflection-PINN adds an independent axis of inference — not tau_VS (central), but tau_cupula (peripheral) — enabling multi-scale vestibular diagnostics: peripheral sensory transducer vs central neural integrator. The caloric-test-response-ODE further adds a second peripheral (thermophysical) axis — tau_therm (heat transfer dynamics) and beta (thermal-to-mechanical coupling) — enabling tri-level diagnostics: thermophysical (outer) → mechanical (middle) → neural (inner).

The VestibularCollicReflex-PINN adds a FOURTH axis — otolith-mediated transduction — completing canal + otolith + thermal coverage of the peripheral vestibular system. This enables multi-parameter diagnostic frameworks that simultaneously assess canal function (VOR gain, VSI time constant), otolith function (VCR gain asymmetry), and thermal dynamics (caloric rise time).
