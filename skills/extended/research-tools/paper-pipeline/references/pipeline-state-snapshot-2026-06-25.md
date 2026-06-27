# Pipeline State Snapshot — 2026-06-25

**Purpose**: Authoritative state reference for cron jobs running quality-gate scans.

## Summary (as of 2026-06-25 08:31 UTC)

**Location**: `/media/yakeworld/sda2/Synthos/outputs/papers/`

**Total papers**: 157 with state.json

**Gate distribution**:
| Status | Count |
|:-------|------:|
| PASS | 147 |
| CONDITIONAL | 2 |
| HARD_FAIL | 2 |
| FAIL | 1 |
| SOFT_FAIL | 1 |
| ? (parse error) | 4 |

## Blocking Papers (need immediate action)

| Paper | Score | Gate | Key Issue |
|:------|------:|:-----|:----------|
| 3wd-framework-trustworthy-clinical-ai | 25 | FAIL | G4/G5/G7 FAIL: metric inconsistencies, empty code/data/figures dirs, 3 hard fails |
| okr-adaptation-pinn | 26 | HARD_FAIL | G3: 8/8 key references failed CrossRef exact match (fake: shinomoto2004, tanne2005, berman2010, takahashi2011, gauthier2004, mays1986, robinson1968) |
| intraocular-pressure-ODE | 75 | HARD_FAIL | G5: 2 hard fails |
| crispdm-wdbc | 55 | SOFT_FAIL | Multiple SOFT_FAIL across G1-G4, G6-G7 |
| eye-tracking-4d | 68 | CONDITIONAL | — |
| cuteye-model | 78 | CONDITIONAL | — |

## Low-Score PASS Papers (NOT blocking per cron protocol)

24 PASS papers with quality_score < 75 are not treated as blocking:
- 137-ciliary-body-ODE: 45.0
- Several at 55.0 (perilymph-fistula-ODE, paper-91-fixation-stability-PINN, smooth-pursuit-PINN, tinnitus-pinn-ode, 3d-pupil-localization, concussion-oculomotor-PINN, ocular-torsion-ODE, membranous-scc-reconstruction, 105-lacrimal-drainage-ODE)
- 153-choroidal-blood-flow-ODE: 60.0
- BPPV-canalith-ODE: 60.0
- 146-vitreous-cortex-structural-ODE: 58.0

Per cron decision tree: `gate_status=PASS && quality_score < 75` → no Codex dispatch.

## State Anomalies

| Paper | Issue |
|:------|:------|
| 3d-eyeball-iris-segmentation | state.json exists but quality_score=? (parse issue) |
| vestibular-compensation-ODE | quality_score=4.9, gate_status=? (orphaned) |
| papers/ | state.json in non-paper directory |
| 09-manuscript/ | state.json in sub-directory |

## Related

- `paper-pipeline` SKILL.md — Filesystem Layout section (three paths)
- `quality-gate` — Cron Job Execution Mode
