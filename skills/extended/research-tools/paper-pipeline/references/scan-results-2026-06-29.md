# Scan Results — 2026-06-29

## Summary Statistics

- **125 bib files** across paper directories
- **2,802 total entries**
- **74.4% DOI coverage** (2,085 with DOI)
- **158 suspicious entries**
- **524 cross-file duplicate keys**

## Paper State Overview

- **93 papers** with state.json
- **89 PASS**, **3 VERIFIED**, **1 BLOCKED** (crispdm-heart)
- **Score distribution**: <60: 10, 60-70: 5, 70-80: 21, 80-90: 33, ≥90: 24
- **Median score**: ~82

## Papers Below Score 60

1. 137-ciliary-body-ODE (45) — bib entries: 0
2. 104-perilymph-fistula-ODE (55) — no bib in 01-manuscript
3. 105-lacrimal-drainage-ODE (55) — no bib in 01-manuscript
4. concussion-oculomotor-PINN (55) — no bib in 01-manuscript
5. membranous-scc-reconstruction (55) — bib: 33 entries, DOI 87.9%
6. ocular-torsion-ODE (55) — no bib in 01-manuscript
7. paper-91-fixation-stability-PINN (55) — no bib in 01-manuscript
8. smooth-pursuit-PINN (55) — no bib in 01-manuscript
9. tinnitus-pinn-ode (55) — no bib in 01-manuscript
10. 146-vitreous-cortex-structural-ODE (58) — bib: 16 entries, DOI 100%

## Zero-DOI Papers

- 150-scleral-remodeling-ODE: 20 entries, 0 DOI
- 162-corneal-hydration-dynamics-ODE: 26 entries, 0 DOI (3 copies)
- 189-vem-pinn: 29 entries, 0 DOI (3 copies, 2 suspicious)

## Stale Papers (>14 days)

| Paper | Days | Score | Last Step |
|:---|:---|:---|:---|
| saccade-burst-neuron-neuralode | 15 | 84 | recompile |
| 112-presbyopia-lens-stiffening-ODE | 15 | 85 | root_tex_sync |
| corneal-biomechanics-ODE | 15 | 96 | publication |
| ocular-blood-flow-ODE-paper-116 | 15 | 92 | g6_first_mover_verification |
| VEMP-PINN | 15 | 78 | recompile |
| 187-scleral-remodeling-ODE | 15 | 96 | none (steps=0 anomaly) |
| 189-vem-pinn | 15 | 78 | recompile |

## Key Cross-File Duplicate Inconsistencies (98 of 524)

Most impactful:
- **ref1-ref5**: 21 locations each, mixed titles/years across papers
- **Wang2023**: 3 locations with completely different titles
- **Raissi2019**: 4 locations with "Unknown" title/year in some copies
- **Li2017**: 2 locations with "Unknown" title/year in some copies

## Zero-DOI Papers

- 150-scleral-remodeling-ODE: 20 entries, 0 DOI
- 162-corneal-hydration-dynamics-ODE: 26 entries, 0 DOI (3 copies)
- 189-vem-pinn: 29 entries, 0 DOI (3 copies, 2 suspicious)

## Stale Papers (>14 days)

| Paper | Days | Score | Last Step |
|:---|:---|:---|:---|
| saccade-burst-neuron-neuralode | 15 | 84 | recompile |
| 112-presbyopia-lens-stiffening-ODE | 15 | 85 | root_tex_sync |
| corneal-biomechanics-ODE | 15 | 96 | publication |
| ocular-blood-flow-ODE-paper-116 | 15 | 92 | g6_first_mover_verification |
| VEMP-PINN | 15 | 78 | recompile |
| 187-scleral-remodeling-ODE | 15 | 96 | none (steps=0 anomaly) |
| 189-vem-pinn | 15 | 78 | recompile |

## Key Cross-File Duplicate Inconsistencies (98 of 524)

Most impactful:
- **ref1-ref5**: 21 locations each, mixed titles/years across papers
- **Wang2023**: 3 locations with completely different titles (eye science, epidemiology, nutrition)
- **Raissi2019**: 4 locations with "Unknown" title/year in some copies
- **Li2017**: 2 locations with "Unknown" title/year in some copies

## Suspicious Entry Types

| Type | Estimated Count |
|:---|:---|
| arXiv preprint without arXiv:ID | ~60 |
| Missing author field | 4 |
| URL in year field | 5 |
| Other (non-standard formats) | ~90 |

## Duplicate Bib Files

- 162-corneal-hydration-dynamics-ODE: 3 copies (01-manuscript/, 06-references/, root)
- 189-vem-pinn: 3 copies (01-manuscript/, 02-submission/06-references/, root)
- 113-nystagmus-compensatory-ODE: 2 copies
- 146-vitreous-cortex-structural-ODE: 2 copies

## Notes

- 7/10 low-score papers lack `01-manuscript/references.bib` — references are in subdirectories but scan checks 01-manuscript/ first.
- 09-manuscript is a subdirectory of 02-corneal-tension-ODE, not a top-level paper — it's an artifact.
- 187-scleral-remodeling-ODE has quality_score=96 but steps=0: likely state.json was reset.
- crispdm-heart is BLOCKED despite score=80: need to check which gate blocked it.
