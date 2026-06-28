# Staleness Guard Deep-Dive — Cycle 237 Proven Pattern

## Background

After 51+ consecutive frozen cycles, the standardized PLR-H1 dual probe was the **only** probe running. It detected no landscape changes for 58+ cycles. However, running a broad deep-dive with 9 fresh queries across ALL core directions (instead of just the PLR-H1 probe) discovered **6 new relevant publications** in a single cycle.

## The Problem

The PLR-H1 probe monitors only one sub-direction (pupil + Alzheimer's biomarker). It cannot detect:
- New SCC modeling papers (perilymph debate)
- New BPPV ML classification papers
- New XR CRM reviews
- New VSI reviews
- New ocular torsion papers
- New 3D gaze tracking publications

**The staleness guard is blind to anything outside its single-query scope.**

## The Solution

Override the staleness guard every 10 cycles (at frozen counter = 20, 30, 40…) with the full 9-query deep-dive.

## Discovered Publications (Cycle 237, 2026-06-24)

| PMID | Paper | Journal | Date | Relevance |
|:----|:------|:--------|:----:|:----------|
| 42268297 | Should perilymph be considered when modeling the lateral SCC? | Biomech Model Mechanobiol | 2026-06-10 | 🟡 Directly relevant to SCC 3D reconstruction |
| 42265236 | XR for precision guidance in canalith repositioning: scoping review | Eur Arch Otorhinolaryngol | 2026-06-10 | 🟡 Directly relevant to BPPV simulation direction |
| 42151355 | Automated BPPV classification from VNG using delay-aware NN | Sci Rep | 2026-05-18 | 🟡 New ML competition in BPPV space |
| 42019191 | VSI: mechanisms, circuits, clinical implications (review) | Am J Otolaryngol | 2026 May-Jun | 🟡 External validation of K-001 kernel |
| 42008696 | Third-window numerical modeling PRISMA review | J Vestib Res | 2026 Apr 20 | 🟡 Computational SCC active, 0 PINN |
| 41658975 | 3DeepVOG: Open-source 3D gaze tracking with DL | Digit Biomark | 2026 Jan-Dec | 🟡 Known competitor now peer-reviewed |
| 42155894 | Markerless 3D mouse eye movements via stereo vision | J Neurosci Methods | 2026 Sep | 🟢 Methods paper, rodent model |

## PINN Cross-Cut Query

The single most efficient query for determining if the competitive landscape has changed:

```
'(physics-informed neural[Title/Abstract] OR neural ODE[Title/Abstract]) AND (eye[Title/Abstract] OR gaze[Title/Abstract] OR pupil[Title/Abstract] OR retina[Title/Abstract] OR fovea[Title/Abstract]) AND (YYYY[dp] OR YYYY[dp])'
```

This returns 0 hits if PINN/NeuralODE remains absent across ALL eye/vision/vestibular domains. **Run this first** — if 0, short-circuit all other PINN checks.
