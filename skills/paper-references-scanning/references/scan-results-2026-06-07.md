# Paper Library D8/D10a Scan — 2026-06-07

Run: python3 d8d10a-scan.py
Total: 82 papers scanned

## Summary

| Metric | Value |
|--------|-------|
| Total papers | 82 |
| Healthy (D10a=100%, D8>=30) | 45 |
| Problem | 37 |
| BBL compiled | 7 |
| No bib file at all | 9 |

## Critical Issues

### 4 papers with 0.0% D10a (orphan cites, no bib)
- **fundus-cv-risk-prediction**: 47 orphan cites, no bib file
- **bppv-canalith-relocation-ode**: 12 orphan cites, no bib file
- **vor-pinn-ode-gap-analysis**: 23 orphan cites, no bib file
- **nystagmus-neutral-PINN**: 8 orphan cites, no bib file
- **pupil-response-dynamics-ode**: 2 orphan cites, no bib file

### D10a < 100% (partial match)
- **bppv-pc-repositioning-optimization**: D10a=75.0% (3 orphans: Baloh2003, Chang2004, Kim2012)
- **ocular-torsion-PINN**: D10a=91.7% (1 orphan: oveson20)
- **semicircular-canal-PINN**: D10a=92.3% (1 orphan: caldwell2014)
- **vhit-pinn-ode**: D10a=94.1% (1 orphan: laureys2001)

### Papers with D8 < 30
29 papers have fewer than 30 bibliography entries (many are PINN/ODE scaffolds with inline bib items).

### Papers with no bib file at all (D8=0)
9 papers: bppv-canalith-relocation-ode, fundus-cv-risk-prediction, nystagmus-neutral-PINN, pupil-response-dynamics-ode, vor-pinn-ode-gap-analysis, cupula-deflection-pinn, kappa-angle-calibration, pan-PINN, smooth-pursuit-PINN, vestibular-compensation-ODE

## Healthy Papers (D10a=100%, D8>=30)

| Paper | D8 | BBL |
|-------|:--:|:---:|
| 3d-eye-bppv-diagnosis | 62 | NO |
| 3d-eyeball-iris-segmentation | 37 | NO |
| 3d-iris-normalization | 30 | OK |
| 3d-pupil-localization | 35 | NO |
| 3wd-framework-trustworthy-clinical-ai | 30 | NO |
| amd-ai-screening | 56 | NO |
| bppv-epley-semont-dizziness-mechanism | 26 | NO |
| bppv-hc-repositioning-safety | 29 | NO |
| bppv-mss-gufoni-epley-combined | 29 | NO |
| bppv-mss-lsc-bppv | 35 | NO |
| bppv-pd-clinical-review | 57 | NO |
| cataract-ai-review | 67 | NO |
| corneal-ai-review | 68 | NO |
| crispdm-heart | 30 | NO |
| crispdm-wdbc | 31 | OK |
| cuteye-model | 30 | NO |
| data-leakage-breast-cancer-critical-audit | 30 | NO |
| ded-ai-screening | 55 | NO |
| dr-ai-screening | 40 | NO |
| dual-ellipse-fitting | 30 | OK |
| dual-ellipse-pupil-localization | 42 | OK |
| glaucoma-ai-screening | 59 | NO |
| hcs3wt-breast-cancer | 32 | NO |
| iris-3d-anatomical-opt | 30 | NO |
| iris-yolo | 30 | NO |
| kappa-3d-eye-tracking | 52 | NO |
| kappa-bppv-nystagmus | 73 | NO |
| kappa-pd-calibration-artifacts | 82 | NO |
| kappa-vor-calibration | 64 | NO |
| membranous-scc-reconstruction | 33 | OK |
| myopia-ai-screening | 76 | NO |
| octa-ai-review | 68 | NO |
| off-axis-iris-normalization-correction | 30 | OK |
| pd-dysphagia-2026 | 48 | NO |
| pd-ocular-biomarkers | 53 | NO |
| pd-torsion-review | 46 | NO |
| pima-crispdm | 33 | OK |
| rop-ai-screening | 49 | NO |
| rvo-ai-screening | 75 | NO |
| strabismus-ai-screening | 39 | NO |
| synthos-system-paper | 49 | NO |
| vor-3d-eye-tracking | 53 | NO |
| vor-bppv-diagnosis | 65 | NO |
| vor-pd-systematic-review | 68 | NO |
| vor-sparse-modular | 31 | NO |
