# Pupillary Light Reflex Domain — Reference for gap_analysis

## Domain Overview

The Pupillary Light Reflex (PLR) is an **autonomic (parasympathetic) reflex** that constricts the pupil in response to light. It is fundamentally different from all 12 prior Track B candidates (which are somatic motor systems using striated extraocular muscles).

| Aspect | PLR | Prior Candidates (VOR, OKR, etc.) |
|:-------|:----|:----------------------------------|
| Effector | Iris sphincter (smooth muscle) | Extraocular muscles (striated) |
| Neural pathway | Pretectal ON → Edinger-Westphal → CN III (ciliary ganglion) | Vestibular/oculomotor nuclei → CN III, IV, VI |
| Muscle type | Smooth (autonomic, slower) | Striated (somatic, faster) |
| Time constant | ~0.2-2s constriction, ~1-30s recovery | 0.01-25s |
| Clinical standard | NPi (Neurological Pupil index, dimensionless) | VOG, vHIT, caloric (°/s) |
| Measured output | Pupil diameter (mm) | Eye position/velocity (°, °/s) |

## White Space Verification (Cycle 136)

**Verdict**: ABSOLUTE_WHITE — 0 PINN/NeuralODE/ODE competitors across 9 queries (7 PubMed + 2 OpenAlex).

### Query Results Summary

| Tier | Query | Count | Verdict |
|:-----|:------|:-----:|:--------|
| PINN narrow | "pupillary light reflex" + PINN/NeuralODE/physics-informed | 0 | ✅ ABSOLUTE_WHITE |
| ODE broad | "pupillary light reflex" + ODE/differential equation/computational model | 1 | Data-driven DNN (Zandi 2021) — NOT PINN |
| ML broad | "pupillary light reflex" + neural network/machine learning | 23 | All clinical diagnostic, no PINN |
| Reactivity | "pupil reactivity" + model/system/dynamics | 77 | All clinical (TBI, ICU), no PINN |
| OpenAlex PINN | "pupillary light reflex" + PINN | 1 | Irrelevant (Greek neurodevelopmental) |
| OpenAlex computational | "pupillary light reflex" + computational model | 5 | All behavioral/clinical, no PINN |

### Key Existing Model

Zandi et al. 2021, *Scientific Reports* (DOI: 10.1038/s41598-020-79908-5, 17 citations)
- Title: "Deep learning-based pupil model predicts time and spectral dependent light responses"
- Type: Data-driven DNN (forward model: light → pupil diameter)
- **NOT** PINN competition (no ODE constraints, no inverse parameter inference)

## Clinical Translation Advantage

Unlike vestibular candidates requiring specialized equipment (rotational chair, vHIT, caloric), pupillometry is:
- Available in every ICU, neurology clinic, and emergency department
- Standardized protocol (automated PLR with NPi-200 or similar)
- Retrospective datasets abundant: TBI, stroke, post-surgical, autonomic neuropathy
- **Zero new equipment** — pure software upgrade to existing pupillometers
- ~500K+ automated pupillometry sessions/year in the US alone

## Full Architecture Specification (Gap Analysis — Cycle 137)

### 2-ODE+PINN Architecture

Two novel kernels: **K-007** (Iris Sphincter Mechanics) and **K-008** (Autonomic Adaptation) — first smooth-muscle/autonomic kernels in the Synthos catalog.

```
┌──────────────────────────────────────────────────────────────────┐
|              Pupillary Light Reflex PINN (PLR-PINN)               |
├──────────────────────────────────────────────────────────────────┤
|                                                                    |
|  ODE-1: Iris Sphincter Mechanics (Constriction) — K-007           |
|  ┌──────────────────────────────────────────────────────────────┐  |
|  │ State: d(t) [mm] — pupil diameter                           │  |
|  │ Parameters: v_max [2,8] mm/s, τ_c [0.15,0.5]s,             │  |
|  │            d_min [2,4] mm, t_delay [0.18,0.35]s             │  |
|  │ Constriction: d(t)=d_rest-(d_rest-d_min)·S(t)              │  |
|  │  dd/dt=-v_max·exp(-t/τ_c)·σ(I(t)-θ)  for t≥t_delay         │  |
|  └──────────────────────────────────────────────────────────────┘  |
|                                                                    |
|  ODE-2: Autonomic Adaptation (Recovery / PIPR) — K-008            |
|  ┌──────────────────────────────────────────────────────────────┐  |
|  │ State: a(t) [mm] — recovery offset                          │  |
|  │ Parameters: τ_r [1,30]s, K_gain [0.5,2.0],                  │  |
|  │            τ_mel [10,60]s, A_mel [0.5,2.0] mm               │  |
|  │ Recovery: da/dt=-(a-a_0)/τ_r-K_gain·(d-d_rest)/τ_r         │  |
|  │ Melanopsin: d_mel(t)=A_mel·[1-exp(-t/τ_mel)]               │  |
|  │ Combined: d_total=d_rest+a(t)+d_mel(t)                      │  |
|  └──────────────────────────────────────────────────────────────┘  |
|                                                                    |
|  PINN Layer (4-layer FC)                                          |
|  ┌──────────────────────────────────────────────────────────────┐  |
|  │ Inputs: [t, I(t)]    FC: 2→64→128→128→64→1                   │
|  │ Outputs: d̂(t) — predicted pupil diameter                     │  |
|  │ Loss: λ_phy·L_physics+λ_data·L_data+λ_ic·L_ic               │  |
|  │       +λ_constraint·L_constraint                             │  |
|  └──────────────────────────────────────────────────────────────┘  |
|                                                                    |
|  Post-PINN Parameter Extraction                                    |
|  ┌──────────────────────────────────────────────────────────────┐  |
|  │ θ = {v_max, τ_c, d_min, d_rest, t_delay,                    │  |
|  │       τ_r, K_gain, τ_mel, A_mel}                             │  |
|  │ → Disease-signature:                                         │  |
|  │   AD:τ_c↑30-60%  DAN:v_max↓20-40%  TBI:τ_r↑50-100%  PD:A_mel↓│
|  └──────────────────────────────────────────────────────────────┘  |
└──────────────────────────────────────────────────────────────────┘
```

### Parameter Count & Identifiability

**Total**: ~45K params (PINN dominated; 8 inferred ODE params + 1 measured baseline)

| Parameter | Identifiability | Clinical Window |
|:----------|:---------------:|:------------------------|
| d_rest | ★★★★★ | Directly measured — dark-adapted baseline |
| v_max | ★★★★★ | [0, 2s] constriction slope |
| τ_c | ★★★★☆ | [0, 2s] constriction curvature |
| d_min | ★★★★☆ | Directly observed steady-state |
| t_delay | ★★★☆☆ | Requires ≥30Hz for precise estimation |
| τ_r | ★★★★☆ | [2, 30s] recovery from light offset |
| K_gain | ★★★☆☆ | Recovery depth — confounded with τ_r from single protocol |
| τ_mel | ★★☆☆☆ | Requires ≥30s post-stimulus recording |
| A_mel | ★★☆☆☆ | Same as τ_mel — extended recording needed |

**Multi-scale**: 7-60× ratio → **YELLOW** (staged pre-training). Stage 1: [0,2s] constriction params. Stage 2: [0,10s] recovery. Stage 3: [0,60s] melanopsin.

**Cross-ODE confound**: ✅ **NONE** — d_rest appears in both ODEs but is directly measured, not inferred. All other parameters are temporally separated (constriction 0-2s vs recovery 2-60s).

### Comparison with Existing Approaches
| Approach | Type | Patient-Specific? | Clinical Use | PINN Gap |
|:---------|:-----|:-----------------:|:------------:|:--------:|
| NPi-200 (Neuroptics) | Proprietary algorithm | ❌ (single index) | ✅ Standard ICU | ✅ Open |
| Zandi 2021 (Sci Rep) | Data-driven DNN | ❌ (forward only) | ❌ Research | ✅ Open |
| Loewenfeld 1993 | Qualitative physiology | ❌ (descriptive) | ❌ Historical | ✅ Open |
| **PLR-PINN** | **2-ODE+PINN** | **✅** | **✅ SW upgrade** | **—** |

### Feasibility Scoring
| Criterion | Score | Rationale |
|:----------|:-----:|:----------|
| Model Complexity | 0.80 | Novel kernels (K-007+K-008), simpler than vestibular candidates |
| Data Availability | **0.90** | ⭐ Abundant ICU data, FDA-cleared device |
| Parameter Identifiability | 0.85 | 6/8 from standard protocol; temporally separated ODEs |
| Clinical Translation | **0.95** | ⭐ **Highest in Track B** — zero new equipment |
| Novelty | 0.85 | First PINN for PLR; first autonomic subsystem |
| **Composite** | **0.87** | **T2 PASS — STRONG RECOMMEND** |

### Clinical Translation Pathway
1. **Phase 1** (Months 1-3): Synthetic validation — generate data from known ODE ranges, recover parameters
2. **Phase 2** (Months 3-6): Retrospective clinical — NPi-200 recordings from ICU databases (TBI, stroke, post-surgical)
3. **Phase 3** (Months 6-9): Prospective — 3-protocol pupillometry (flash + sustained + dark) on 250 patients across 5 diseases + 50 controls
4. **Phase 4** (Months 9-12): Longitudinal — annual PLR-PINN on 500 cognitively normal adults 65+ for 5-year MCI/AD conversion prediction

### Addressable Market
- 55M Alzheimer's patients globally (screening), 37M US diabetics (autonomic neuropathy), 2.5M US TBI/year (triage)
- ~6,000 US hospitals with pupillometers — software upgrade, $0 marginal cost per test
- Replaces or supplements $500-3,000 biomarker/imaging tests

### Key Challenges (8 identified)
1. **Melanopsin identifiability from standard NPi** (5s protocol) → Two-tier diagnostic
2. **d_min vs K_gain trade-off** → Temporal separation resolves
3. **Subject variability in d_rest** → Normalize by d_rest
4. **Afferent vs efferent separation** → Bilateral recording
5. **NPi clinical adoption** → Head-to-head AUC comparison
6. **Disease specificity overlap** → Multi-parameter signatures
7. **Light intensity calibration** → Normalize by % device max
8. **Age-stratified references** → 5 age bins, z-scores

### Hypothesis Seeds (for next step)
1. **H1: τ_c as Alzheimer's Preclinical Biomarker** — AUC ≥ 0.82 for 5-yr MCI-to-AD conversion
2. **H2: Multi-Parameter DAN Signature** — (v_max↓+d_min↑+τ_r↑) AUC ≥ 0.85 vs Ewing battery
3. **H3: PLR-PINN TBI Prognosis** — (τ_r+K_gain+t_latency) ΔAUC ≥ 0.08 vs NPi

## Domain-Specific Query Strategy for Future Scans

When querying any autonomic/non-motor subsystem:

1. **Tier 1 — Narrow PINN**: `"<reflex_name>" AND (PINN OR physics-informed OR NeuralODE)` → typically 0
2. **Tier 2 — ODE/computational**: `"<reflex_name>" AND (ODE OR "differential equation" OR "computational model")` → may return DNN forward models — check carefully
3. **Tier 3 — ML broad**: `"<reflex_name>" AND ("neural network" OR "machine learning" OR "deep learning")` → mostly clinical diagnostic — read top-3 titles
4. **Tier 4 — Reactivity dynamics**: `"<reflex_name>" AND ("model" OR "system" OR "dynamics")` → highest clinical count, all diagnostic

**Key diagnostic rule for autonomic subsystems**: If the only "computational model" found is a data-driven DNN (forward, not inverse), the space is still white for PINN/ODE.

## False Positive Patterns

1. **Data-driven DNN false positive**: Forward model (light → pupil) is NOT PINN competition
2. **Clinical diagnostic false positive**: Automated measurement devices (NPi) generate scores, not computational models
3. **Physiological description false positive**: Papers characterizing reflex latency/amplitude in disease populations are clinical studies, not computational models
