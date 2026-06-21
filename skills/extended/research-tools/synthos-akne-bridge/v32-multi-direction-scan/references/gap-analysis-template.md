# Gap Analysis Template — 2-ODE + PINN Biomedical Domain

Use this structured template when producing `step_gap_analysis.md` for any 2-ODE+PINN biomedical candidate. Validated across 4+ domain expansions: oculomotor/vestibular (GazeStability-ODE, PAN-PINN, 8+ others), cardiac autonomic (K-009), baroreflex cardiovascular (K-010), and cardiopulmonary (K-011, Respiratory Sinus Arrhythmia). Works for any two-compartment physiological system requiring patient-specific parameter inference.

```
# Gap Analysis: <Candidate-Name>

**Analysis Date**: <YYYY-MM-DD>
**Cron Session**: <model-provider> (Hermes Agent)
**Previous Step**: literature_scan (<WHITE_STATUS>, score=<X>)

## 1. Research Gap Validation

### Table: Gap Dimensions
| Dimension | Value |
|:----------|:------|
| Domain | <physiological system> |
| White Space Status | ✅ ABSOLUTE_WHITE / CONDITIONAL / OCCUPIED |
| Classical Models Exist? | YES/NO — list key prior work with DOIs |
| PINN/ODE Gap | **One-sentence summary** of why existing work doesn't cover PINN/ODE |
| Clinical Need | <conditions> — why this matters for diagnosis/treatment |

### White Space Characterization
- Type: Methodological/Data/Mixed White Space
- Classical models: <what exists, how many parameters, what paradigm>
- What's missing: <precise PINN/ODE gap statement>
- Key distinction: <why classical models ≠ PINN competition>

## 2. Proposed Model Architecture

### ASCII Diagram (required)
```
┌─────────────────────────────────────────────────────────────┐
|                    <Model Name>                              |
├─────────────────────────────────────────────────────────────┤
|                                                               |
|  ODE-1: <Name>                                               |
|  ┌─────────────────────────────────────────────────────────┐  |
|  │ State: <state vars, units>                              │  |
|  │ Parameters: <p1>, <p2>, <p3>                            │  |
|  │ Equations:                                               │  |
|  │  dx/dt = ...                                             │  |
|  │  dy/dt = ...                                             │  |
|  └─────────────────────────────────────────────────────────┘  |
|                                                               |
|  ODE-2: <Name>                                               |
|  ┌─────────────────────────────────────────────────────────┐  |
|  │ State: <state vars, units>                              │  |
|  │ Parameters: <p1>, <p2>, <p3>                            │  |
|  │ Equations:                                               │  |
|  │  du/dt = ...                                             │  |
|  │  dv/dt = ...                                             │  |
|  └─────────────────────────────────────────────────────────┘  |
|                                                               |
|  PINN Layer                                                    |
|  ┌─────────────────────────────────────────────────────────┐  |
|  │ Inputs: <features>                                      │  |
|  │ Hidden: <layer sizes>                                   │  |
|  │ Outputs: <residuals>                                     │  |
|  │ Loss: physics_loss + data_loss + bc + <domain_loss>     │  |
|  └─────────────────────────────────────────────────────────┘  |
|                                                               |
└─────────────────────────────────────────────────────────────┘
```

### ODE-1 Detail
- **Purpose**: 1-2 sentence
- **Reusable Kernel Check**: Does this ODE match a kernel in `references/reusable-ode-kernels.md`? If yes, note the kernel ID and skip re-derivation; reference the catalog entry instead.
  - **⚠️ Structural Analog vs Direct Kernel Match**: If the ODE uses the same physiological system (e.g., same ANS branch) but different receptor subtype (β₁ vs α₁), target organ (SA node vs iris), or effector type (cardiac vs smooth muscle), classify as **Structural Analog** — NOT a direct kernel match. Document the differences explicitly: (a) what is shared (neurotransmitter, pathway), (b) what differs (receptor, target, timescale), (c) whether transfer learning is still beneficial (architecture weights may transfer even if parameter ranges don't). Structural analogs qualify for +0.05 Feasibility (partial transfer learning) but maintain full novelty.
- **State Variables Table**: (name, symbol, units, description)
- **Key Parameters Table**: (name, symbol, range, description)
- **Dynamics**: equations with comments
- **Key Behavior**: bullet list — normal vs pathological behavior

### ODE-2 Detail
Same structure as ODE-1
- **Reusable Kernel Check**: Does this ODE match a kernel in `references/reusable-ode-kernels.md`? If the entire 2-ODE structure is shared, verify white space distinctness (different clinical domain + different biomarker hypotheses).

### PINN Layer Detail
- **Purpose**: what residual dynamics it learns
- **Architecture Table**: (layer, type, size, activation)
- **Inputs/Outputs**: precise specification
- **Loss Function**: explicit formula with λ weights
- **Training Strategy**: pre-training, joint training, fine-tuning, transfer learning

### ⚡ Multi-Scale Temporal Dynamics Check

Detect whether ODE-1 and ODE-2 operate at **disparate timescales** (ratio > 10×). This is a critical architectural concern — a PINN must resolve both fast and slow dynamics simultaneously, and a naive architecture will prioritize the faster timescale at the expense of the slower one (or vice versa).

| Element | What to Examine | Example Pattern (CupulaDeflection-PINN) |
|:--------|:----------------|:----------------------------------------|
| **Detection** | Compare the intrinsic time constants (τ) of ODE-1 vs ODE-2. If one governs sub-second dynamics and the other governs tens-of-seconds dynamics, a multi-scale gap exists. | ODE-1: endolymph fluid dynamics (ζ, ω₀) → τ ~0.01-0.3s. ODE-2: cupula viscoelastic recovery (τ_cupula) → ~0.01-0.3s. Combined with VSI integration (τ_VS ~5-25s, downstream). Total gap: **100×** |
| **Assessment** | Quantify the ratio. Assign: Green (< 10×, no special action needed), Yellow (10-100×, staged pre-training recommended), Red (> 100×, multi-resolution architecture required). For acoustic/high-frequency biological systems, the carrier frequency (kHz) vs envelope modulation (Hz) ratio routinely exceeds 1000× — this is a **structural pattern**, not a pathological edge case. | Cupula: **100× → Yellow**. Cochlear mechanics: **2000× → Red** (acoustic carrier at 20 kHz vs OHC adaptation at 100 ms — structural pattern for any auditory domain). |
| **Mitigation: Staged Pre-training** | Pre-train on **short-window** data (fast dynamics dominant, t < 5τ_fast) and **long-window** data (slow dynamics dominant, t > 10τ_slow) separately. Fine-tune jointly on full-timespan data. | Cupula stage: 0-1s windows. VSI stage: 0-30s windows. Joint: 0-30s |
| **Mitigation: Loss Balancing** | Use frequency-separated loss terms with adaptive λ weights. Apply higher weight to the slower regime during joint training. | λ_slow = 2.0 · λ_fast during first 50% of joint epochs |
| **Mitigation: Multi-Resolution Input** | If Red (> 100×), use a dual-encoder PINN: one branch processes high-frequency (short-window) features via 1D-CNN, another processes low-frequency (long-window) features via MLP. Merge via cross-attention before the output layer. | Cochlear mechanics (2000×): 1D-CNN encoder (0-5ms, 50μs resolution) for BM envelope + IHC onset; MLP encoder (0-500ms, 1ms resolution) for adaptation + OHC dynamics. Cross-attention merge. |
| **Mitigation: Envelope Loss** | For acoustic/high-frequency domains (kHz carrier frequencies), fit the **Hilbert envelope** instead of the raw waveform. This reduces effective temporal resolution requirement by ~10× (envelope at 2 kHz vs carrier at 20 kHz) while preserving the amplitude modulation that carries physiological information. Suitable when the PINN target is amplitude-based parameters (gain, adaptation) rather than phase-based (delay, latency). | Cochlear mechanics: BM displacement envelope from DPOAE amplitude + ABR wave I envelope. Reduces temporal resolution from 50μs to 0.5ms — the difference between "infeasible" and "standard PINN training". |
| **Identifiability Impact** | Fast parameters are identifiable from early time points; slow parameters require the full time series. Document which parameters are estimable from short vs long windows. | tau_cupula → first 1s. zeta → first 5s. omega_0 → only if underdamped |

**Reference worked example**: See `K-003` in `references/reusable-ode-kernels.md` for the CupulaDeflection-PINN multi-scale analysis, including the staged pre-training strategy with short-window (0-1s) and long-window (0-30s) phases. When a multi-scale gap is detected, reference this worked example in the gap analysis and adapt the staged training protocol rather than re-deriving it.

### ⚡ Cross-ODE Parameter Identifiability Confound Check

Detect whether two or more ODEs each contribute a parameter that maps into the same observable. Four fundamentally different confound types exist:

| Confound Type | Mechanism | Example | Resolution |
|:-------------|:----------|:--------|:-----------|
| **🔴 Multiplicative** | Two scaling parameters from different ODEs multiply into the same output → only the product is identifiable | β (ODE-1) · g_VS (ODE-2) in caloric test | External anchor (vHIT) fixes one parameter → other becomes identifiable |
| **🔴 Additive** | Two ODE outputs sum/subtract to produce the observable → only the net sum/difference is identifiable, not individual contributions | s(t) − p(t) in cardiac autonomic HRV: g_SNS and g_PNS both scale HR amplitude | **Frequency-domain decomposition** — if the two signals operate at different timescales or frequency bands, spectral analysis can separate them from the same recording |
| **🔴 Coupling Interface** | Parameters from ODE-1 and ODE-2 merge at the inter-ODE coupling equation before reaching the final observable. One ODE's state feeds into the other through an equation with ≥2 multiplicative scaling parameters from different ODEs. | Vocal fold: A_g(t) = A_g0 + α·x(t) — α from ODE-2, x(t) depends on ODE-1 parameters (m,k,b), A_g0 from ODE-2. All three scale A_g jointly. | (a) External measurement of one ODE's internal state (EGG CQ anchors A_g0), (b) Frequency-separated anchor, (c) Accept composite as biomarker |
| **🔴 Input-Pattern** | The observable amplitude is confounded with the INPUT STIMULUS pattern, not another ODE parameter. A weak input produces low output that could be mistaken for low capacity. | RSA amplitude A_RSA depends on BOTH vagal tone AND respiratory mechanics (rate, depth, I:E ratio). | **Standardized input protocol** — paced breathing. **Input-compensated index**: divide output amplitude by input power. |

**Detection procedure**:
1. Trace each ODE's output pathway to the final observable
2. Determine the **combining operation** — multiplication (multiplicative), addition/subtraction (additive), or coupling equation (interface)?
3. Count how many parameters merge at the combining point
4. If ≥2: flag as confound, classify by type, and select resolution strategy

| Element | What to Examine | Example Pattern (caloric-test-response-ODE — multiplicative) |
|:--------|:----------------|:--------------------------------------------|
| **Detection** | Trace each ODE's output pathway to the final observable (SPV, force, displacement, etc.). If two different ODEs each contribute a multiplicative scaling parameter that reaches the same observable without an intermediate independent measurement, a confound exists. | ODE-1: θ_cupula(t) = β·T(t). ODE-2: SPV(t) = g_VS · ω(t) integrated by VSI. Both β and g_VS scale SPV amplitude → only β·g_VS is identifiable from SPV alone. |
| **Assessment** | Count the number of scaling parameters that merge into the same observable. If ≥2, flag as 🔴 CONFOUND. If 1, no action (the single scaling parameter absorbs all unknown gain). | β (thermal-to-mechanical, ODE-1) + g_VS (VSI gain, ODE-2) → **🔴 2-way confound** |
| **Mitigation: External Anchor** | Identify an independent measurement that fixes one parameter, making the other identifiable. Any of: (a) independent gold-standard test that isolates one ODE's parameters, (b) population-mean prior for one parameter with uncertainty propagation, (c) fixed value for the least-prioritized parameter. | vHIT (video head impulse test) measures VOR gain directly: g_VHIT ≈ g_VS. Set g_VS = g_VHIT → β is now identifiable from caloric SPV amplitude alone. |
| **Mitigation: Frequency-Separated Anchor** | For 3+ way multiplicative confounds, use a **measurement modality that isolates exactly one parameter** from the chain. Identify a clinical measurement whose amplitude depends preferentially on one parameter and negligibly on the others. | Cochlear 3-way confound (k_gain × g_gain × g_OHC): DPOAE amplitude depends on OHC function (g_OHC) + BM tuning — NOT on IHC transduction (g_gain). |
| **Mitigation: Bayesian Prior** | If no external anchor exists, use a population-level prior (mean ± SD from literature) for one parameter and infer the other with documented uncertainty. | Fix g_VS = 0.50 ± 0.15 (population mean) if vHIT unavailable. Report β as β̂ ± σ̂. |
| **Mitigation: Frequency-Domain Decomposition** (additive confounds only) | If the two ODEs operate at **different frequency bands**, decompose the observable by frequency. One ODE's contribution dominates at certain frequencies, the other at other frequencies — enabling separation from the SAME recording. | Cardiac autonomic HRV: PNS dominates HF band (0.15-0.4 Hz), SNS dominates LF band (0.04-0.15 Hz). LF/HF ratio provides built-in anchor. |
| **Mitigation: Clinical Protocol** | Modify the clinical protocol to create a condition where one parameter dominates and the other is negligible, enabling independent estimation. | Warm vs cold caloric: β scales both symmetrically. If SPV(warm)/SPV(cold) ≠ ΔT(warm)/ΔT(cold), the asymmetry reveals τ_therm dynamics decoupled from β. |
| **Mitigation: Breath-Hold Calibration** (input-driven modulation) | Instruct breath-hold at end-expiration. During breath-hold, input stimulus r(t) ≈ 0, causing the modulation term to vanish. The observable converges to the baseline parameter V0, providing an independent calibration point. | RSA vagal modulation: A_RSA drives AC component, V0 drives DC component. During breath-hold (r(t)=0), after ~3τ_vagal, p(t) ≈ V0. |
| **Identifiability Impact on Scoring** | Document in the Parameter Identifiability criterion of Section 5 score: every confounded parameter pair reduces score by -0.10 to -0.20. The external anchor mitigation restores 50-75% of the loss. | Without vHIT: Parameter Identifiability = 0.70. With vHIT: Parameter Identifiability = 0.85. |

**Reference worked examples**:
- Multiplicative: `caloric-test-response-ODE/step_gap_analysis.md`
- Additive: `cardiac-autonomic-regulation-PINN/step_gap_analysis.md`
- Coupling Interface: `vocal-fold-phonation-PINN/step_gap_analysis.md`

## 3. Parameter Count Estimation

| Component | Parameters | Notes |
|:----------|:----------:|:------|
| ODE-1: <name> | <N> | <p1, p2, ...> |
| ODE-2: <name> | <M> | <p1, p2, ...> |
| PINN weights & biases | ~N | layer-by-layer breakdown |
| **Total** | **~total** | Dominated by PINN |

### Data Requirements
- **Minimal**: X-Y trials/recordings
- **Target**: X-Y trials for robust training
- **Clinical feasibility**: time per patient, equipment needed

### Identifiability Analysis (table)
| Parameter | Identifiability | Clinical Information Carrier |
|:----------|:---------------:|:----------------------------|
| τ_X | ★★★★★ | Directly determines Y — most identifiable |
| λ_Y | ★★★★☆ | Governs Z decay slope |
| K_Z | ★★☆☆☆ | Requires experimental design |

## 4. Clinical Impact Assessment

### Clinical Conditions Table
| Condition | Prevalence | Domain Relevance | Current Assessment | PINN Gap |
|:----------|:----------:|:-----------------|:------------------|:--------:|
| <Disease> | <prevalence> | <mechanism> | <current method> | ✅ Open / ❌ Covered |

### Clinical Translation Pathway
1. **Phase 1** (Months 1-3): <model construction + synthetic validation>
2. **Phase 2** (Months 3-6): <retrospective data>
3. **Phase 3** (Months 6-9): <prospective validation>
4. **Phase 4** (Months 9-12): <biomarker study>

### Addressable Market
<patient population size, clinical value proposition>

## 5. Feasibility Assessment

### Multi-Criterion Scoring
| Criterion | Score | Justification |
|:----------|:-----:|:--------------|
| Model Complexity | 0-1 | Novel architecture needed? Comparable to prior work? |
| Data Availability | 0-1 | ⚠️ Often the weakest dimension — quantify available data |
| Parameter Identifiability | 0-1 | Can params be estimated from realistic data? |
| Clinical Translation | 0-1 | Clinical need + path to deployment |
| Novelty | 0-1 | True white space? Existing work? |
| **Overall** | **avg** | **VERDICT** |

### Comparison with Prior Candidates (if applicable)
| Dimension | Prior Domain X | Current Domain Y |
|:----------|:-------------:|:----------------:|
| Data availability | 0.80 | 0.40 |
| Clinical prevalence | 1.5M US | <1K US |
| Overall | 0.87 | 0.68 |

### Data Scarcity Mitigation (if score < 0.50)
1. Synthetic pre-training from <source model>
2. Transfer learning from <similar domain>
3. Self-supervised <technique>
4. Multi-center data pooling

## 6. Comparison with Existing Approaches (table)
| Approach | Type | Patient-Specific? | Param Count | Clinical Use | PINN Gap |
|:---------|:-----|:-----------------:|:-----------:|:------------:|:--------:|
| <prior work 1> | <type> | ❌/✅ | <N> | ⚠️/✅/❌ | ✅ Open |
| <prior work 2> | <type> | ❌/✅ | <N> | ⚠️/✅/❌ | ✅ Open |
| **<This work>** | **2-ODE+PINN** | **✅** | **~44K** | **✅ Quantitative** | **—** |

## 7. Key Challenges (numbered list, 5-8 items)
1. <Challenge 1> — mitigation
2. <Challenge 2> — mitigation
...

## 8. Next Step: Hypothesis Generation
3 candidate hypotheses to formulate in the next cron run:
1. **<H1>**: <core claim> with <quantitative target (ROC AUC ≥ X, R² ≥ Y)>
2. **<H2>**: <core claim> with <quantitative target>
3. **<H3>**: <core claim> with <quantitative target>

## Quality Assessment

| Dimension | Score | Criteria Met |
|:----------|:-----:|:-------------|
| Gap specificity | 0-1 | Precisely defined gap |
| Architecture soundness | 0-1 | Maps to known physiology |
| Parameter identifiability | 0-1 | Observability from data |
| Clinical relevance | 0-1 | Direct clinical need |
| Data feasibility | 0-1 | Data availability |
| Novelty | 0-1 | True white space |
| **Composite** | **avg** | **VERDICT — PASS / CONDITIONAL / FAIL** |

**Gate**: PASS / CONDITIONAL / FAIL
