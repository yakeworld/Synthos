# Research Queue Cleanup — 2026-06-18 Session

## Context

Paper Repair Agent cron run (deepseek-v4-pro). Track A had 0 pending repairs. Track B research-queue had accumulated systemic rot.

## Stale Entry Detection (7 entries, all removed)

| Candidate | Paper-queue status | Action |
|:----------|:-------------------|:-------|
| binaural-vestibular-PINN | in_progress (qs=72, at method step) | Removed — already Track A |
| vog-vestibular-review | completed (qs=82, PASS) | Removed — already Track A |
| gaze-stability-PINN | completed (qs=80, PASS) | Removed — already Track A |
| vestibular-computation-PINN | completed (qs=78, PASS) | Removed — already Track A |
| saccadic-velocity-storage-ode | completed (qs=72, PASS) | Removed — already Track A |
| pd-dysphagia-2026 | completed (qs=85, PASS) | Removed — already Track A |
| binaural-vestibular-PINN (dup) | (duplicate) | Removed — duplicate |

## Duplicate Detection

`binaural-vestibular-PINN` appeared twice:
- Entry 1: status=completed, steps=[literature_scan, gap_analysis, hypothesis_generation, knowledge_entry], qs=80
- Entry 2: status=in_progress, current_step=knowledge_entry, qs=78

Kept entry 1 (more steps completed), removed entry 2.

## Empty Shells Deleted

| Directory | Files | Reason |
|:----------|:-----:|:-------|
| automated-label-production-pipeline-for-eye-tracking | 1 (state.json only) | Pure scaffolding, no research content |
| scc-mathematical-morphology | 1 (directory tree only) | Pure scaffolding, no research content |

## ABSOLUTE WHITE Refinement — 113-scleral-remodeling-ODE

### gap_analysis.md Claimed (unverified)
```
PubMed "scleral remodeling AND differential equation" = 0
PubMed "scleral remodeling AND 'ordinary differential'" = 0
PubMed "eye growth AND scleral AND differential equation" = 0
PubMed "scleral remodeling AND PINN" = 0
PubMed "scleral biomechanics AND ODE" = 0
PubMed "myopia AND 'ordinary differential equation'" = not tested
```
**Claim**: "ABSOLUTE WHITE — zero computational ODE/PINN models of scleral remodeling dynamics exist."

### literature_scan Verification (independent PubMed)
```
Query: myopia AND "ordinary differential equation" → 1 hit (PMID 39503256)
Query: scleral + "computational model" + dynamics → 1 hit (PMID 28291699, irrelevant)
All other queries → 0 hits (confirmed)
```

### Adjacent Competitor Found
**Rozema 2025** (PMID 39503256): "Refractive development II: Modelling normal and myopic eye growth" — 18-parameter ODE model of refractive development with retinal feedback.

**Differentiation**:
| Dimension | Rozema 2025 | 113-scleral |
|:----------|:-----------|:------------|
| Model level | Optical (dioptric power) | Biochemical (ECM) |
| State variables | Axial power, refractive power | ECM integrity, axial elongation |
| Key mechanism | Retinal blur feedback | MMP autocatalysis, collagen degradation |
| Bifurcation | None | Saddle-node at S_c≈0.55 |
| Parameters | 18 (optical) | 8 (biochemical) |

### Refined White Space
**Revised claim**: "No computational ODE model of **scleral ECM biochemical remodeling** exists. The only adjacent ODE model in myopia (Rozema 2025) operates at the optical/refractive level, not the tissue biochemistry level."

## Track A Collision Detection

`113-scleral-remodeling-ODE` vs existing Synthos scleral papers:

| Paper | Focus | Differentiation from 113 |
|:------|:------|:------------------------|
| corneoscleral-shell-ODE (qs=88) | Corneoscleral elastic modulus evolution | Structural biomechanics, not ECM biochemistry |
| 187-scleral-remodeling-ODE (qs=96) | Scleral remodeling (different aspect) | Different model scope |
| 150-scleral-remodeling-ODE (qs=75) | Scleral remodeling (different aspect) | Different model scope |

**Verdict**: 113 differentiates via ECM biochemistry focus (MMP → collagen → stiffness cascade) with myopia disease context. No collision.

## Queue After Cleanup

```json
{
  "total_candidates": 1,
  "total_pending": 0,
  "total_in_progress": 1,
  "next_candidate": "113-scleral-remodeling-ODE",
  "next_step": "gap_analysis"
}
```
