# Knowledge Entry: 6-Dimension Quality Scoring Rubric

> Part of the knowledge-extraction skill. Used during the knowledge_entry generation step (step 4/4 of the research pipeline).

## Overview

Each knowledge entry receives a **6-dimension weighted quality score** (0.0-1.0). The composite score must be ≥ 0.70 for PASS (T2 quality). This is the final quality gate before the candidate leaves the pipeline.

## Dimension Weights & Scoring Criteria

| # | Dimension | Weight | Score 0.0-0.3 | 0.3-0.6 | 0.6-0.8 | 0.8-1.0 |
|:-:|:----------|:------:|:-------------|:--------|:--------|:--------|
| 1 | **Gap Significance** | 0.25 | Gap poorly characterized or non-existent | Gap identified but boundaries unclear | Gap well-defined but prior art overlap | ABSOLUTE_WHITE with thorough query evidence |
| 2 | **Methodological Soundness** | 0.20 | Architecture unspecified or wrong | Architecture specified but weak confound analysis | Strong architecture with identified confounds | All confounds resolved with principled mitigations |
| 3 | **Result Completeness** | 0.20 | < 2 pipeline steps completed | 2-3 steps completed, sparse content | All 4 steps, adequate depth | All 4 steps with thorough documentation in each |
| 4 | **Clinical Translation** | 0.15 | No clinical path identifiable | Vague clinical potential | Phase 1-4 pathway sketched | Phase 1-4 pathway + zero-equipment + market sizing |
| 5 | **Reproducibility** | 0.10 | No data sources identified | Data sources named but inaccessible | Public datasets exist but need licensing | Public datasets available with clearly reproducible protocol |
| 6 | **Narrative Quality** | 0.10 | Incoherent or missing narrative | Basic structure but gaps | Clear story arc with minor issues | Compelling story arc — clinical problem → gap → solution → impact |

## Composite Calculation

```
Weighted Total = Σ(score_i × weight_i)
Threshold for PASS = 0.70
```

## Scoring Guidelines Per Dimension

### 1. Gap Significance (0.25)
- **0.90-1.00**: ABSOLUTE_WHITE — zero PINN/NeuralODE/ODE-inverse papers across 4+ narrow and 5+ broad queries. Classical models exist (confirming well-characterized domain) but all are forward-only. Clinical need is quantified with prevalence and current diagnostic gap.
- **0.80-0.89**: ABSOLUTE_WHITE but fewer queries or weaker clinical quantification. Patient-specific parameter inference clearly absent.
- **0.70-0.79**: CONDITIONAL_WHITE — some PINN-adjacent work exists (data-driven NN = PINN, forward PINN = inverse PINN). Need to document false positives.
- **< 0.70**: Gap is occupied or poorly characterized.

### 2. Methodological Soundness (0.20)
- **0.85-1.00**: All confounds resolved with principled, testable mitigations. Multi-scale assessment GREEN or YELLOW with clear mitigation. Architecture maps cleanly to established physiology.
- **0.75-0.84**: Major confounds identified with partial resolution. Some residual ambiguity accepted as clinically meaningful composite.
- **0.65-0.74**: Architecture sound but multiple unresolved confounds. Identifiability concerns not fully addressed.
- **< 0.65**: Architecture weakness or unaddressed fundamental issues.

Common confound patterns to assess:
- **Multiplicative confounds**: N parameters that multiply into the same observable → need external anchor (F0, EGG, DPOAE)
- **Ratio confounds**: m:k ratio → F0 anchor
- **Additive confounds**: baseline + modulation → DC/AC decomposition
- **Multi-scale temporal gap**: RED > 100×, YELLOW 10-100×, GREEN < 10×

### 3. Result Completeness (0.20)
- **0.85-1.00**: All 4 pipeline steps completed. Literature scan with false-positive documentation. Gap analysis with full 8-section template. Hypothesis generation with ≥3 falsifiable hypotheses, evidence matrices, composite scoring, Pattern #5 discriminative design. Knowledge entry with all 9 required sections.
- **0.75-0.84**: All 4 steps complete but one step is superficial.
- **0.65-0.74**: Missing 1 step or multiple shallow steps.
- **< 0.65**: Pipeline significantly incomplete.

### 4. Clinical Translation (0.15)
- **0.85-1.00**: Zero new equipment needed. Software-only upgrade to existing clinical pipelines. Clear Phase 1-4 pathway with timeline and success criteria. Addressable population quantified (5M+ US patients). Multiple disease targets.
- **0.75-0.84**: Zero new equipment. Phase 1-3 pathway clear. Single disease target.
- **0.65-0.74**: Requires new equipment or specialized expertise. Pathway sketchy.
- **< 0.65**: Clinical path unclear or requires impractical infrastructure.

### 5. Reproducibility (0.10)
- **0.82-1.00**: Multiple public datasets available with coarse pathology labels. Synthetic pre-training feasible from forward ODE. Standard tooling (PyTorch+DeepXDE). Clear falsification criteria.
- **0.75-0.81**: Public data exists but without ground-truth parameter labels. Requires paired data collection (N=50-100 feasible at single center).
- **0.65-0.74**: No public data. Requires de novo data collection. Specialized equipment needed.
- **< 0.65**: Data essentially unobtainable or requires proprietary/hard-to-access resources.

### 6. Narrative Quality (0.10)
- **0.85-1.00**: Compelling story arc: clinical problem (quantified) → 40+ years of classical models/no PINN → 2-ODE+PINN captures key physiology → parameters as biomarkers for specific diseases → clinical translation path. Challenges presented honestly. Cross-domain connections highlighted.
- **0.75-0.84**: Clear story with minor disconnects.
- **0.65-0.74**: Functional but lacks compelling structure.
- **< 0.65**: Incoherent or missing narrative.

## Score Evolution Patterns

| Prior gap_analysis status | Typical KE score range | Notes |
|:--------------------------|:---------------------:|:------|
| PASS (0.85-0.92) | 0.85-0.90 | Δ = −1 to −3. 6D rubric adds conservative dimensions. |
| CONDITIONAL (0.78-0.84) | 0.80-0.86 | Δ = −2 to −4. Identifiability/data concerns penalized more in 6D. |
| CONDITIONAL (0.65-0.77) | 0.70-0.78 | Δ = −3 to −5. Highest recovery needed at HG step. |

## Historical Reference Scores

| Candidate | Gap Score | HG Score | KE 6D Score | Δ (HG→KE) | Key Mitigation |
|:----------|:---------:|:--------:|:----------:|:---------:|:--------------|
| cochlear-mechanics-PINN (K-013) | 0.87 | 0.91 | 0.88 | −3 | RED multi-scale (2000×), 3-way confound both penalized in 6D |
| respiratory-sinus-arrhythmia-PINN (K-011) | 0.92 | 0.89 | 0.88 | −1 | GREEN multi-scale, all confounds resolved; minimal penalty |
| baroreflex-regulation-PINN (K-010) | 0.81 | 0.87 | 0.88 | +1 | Closed-loop novelty counterbalanced 6D conservatism |
| vocal-fold-phonation-PINN (K-014) | 0.78 | 0.87 | 0.85 | −2 | CONDITIONAL gap recovery; 3-way confound accepted as composite |
| cardiac-autonomic-regulation-PINN (K-009) | 0.88 | 0.87 | 0.88 | +1 | Strongest clinical translation (0.92) counterbalanced conservative dims |
| PupillaryLightReflex-PINN (K-007/008) | 0.89 | 0.87 | 0.87 | 0 | First autonomic kernel, excellent clinical translation (0.92) |
| VestibularCollicReflex-PINN (K-006) | 0.79 | 0.83 | 0.82 | −1 | Ocular motor domain, moderate scoring across the board |
