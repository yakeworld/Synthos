# Reusable ODE Kernel Components — Shared Architecture Catalog

**Maintainer**: autonomous-core-researcher  
**Last Updated**: 2026-06-21  
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
| caloric-test-response-ODE | Canal-ocular response (VSI + thermal) | Thermal convection ODE-1 + VSI ODE-2 | 0.88 (gap_analysis done) |

**Clinical Domains Covered by VSI-Based Candidates**:
- Gaze stability / gaze holding (cerebellar ataxia, PSP, MS INO)
- Periodic alternating nystagmus (cerebellar nodulus/uvula dysfunction)
- Vestibular compensation post-UVL (neuritis, schwannoma, Meniere's)
- Visual-vestibular coupling dysfunction (concussion/TBI, aging fall risk)
- Caloric test response (Meniere's endolymphatic hydrops, canal dehiscence)

**Transfer Learning Notes**:
- PINN weights for the VSI kernel's 2-parameter output head can be initialized from any prior VSI candidate
- The VSI dynamics equation is identical across all five candidates — only ODE-1 and clinical context differ
- For new candidates: if ODE-2 matches VSI, skip re-derivation of state equations in gap analysis; reference this catalog entry
- Cross-candidate hypothesis testing: a single VSI parameter (tau_VS) can now be tested across 5+ clinical conditions

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
## Score Impact

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

The CupulaDeflection-PINN adds an independent axis of inference — not tau_VS (central), but tau_cupula (peripheral) — enabling multi-scale vestibular diagnostics: peripheral sensory transducer vs central neural integrator. The caloric-test-response-ODE further adds a second peripheral (thermophysical) axis — tau_therm (heat transfer dynamics) and beta (thermal-to-mechanical coupling) — enabling tri-level diagnostics: thermophysical (outer) → mechanical (middle) → neural (inner).
