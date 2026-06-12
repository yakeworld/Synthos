# Paper Library D8/D10a Scan — 2026-06-09 (v3: latest)

Run: `python3 scripts/d8d10a-scan.py` in paper-references-scanning skill directory.
Total: 107 papers scanned.

## Summary

| Metric | Value |
|--------|-------|
| Total papers | 107 |
| Healthy (D10a=100%, D8>=30) | 45 |
| Problem | 62 |
| BBL compiled | 7 (7%) |
| No bib file at all | 5 |
| Orphan cites | 93 |
| Zombie cites | 46 papers with zombies |
| Zero-cite papers (D8>0) | 29 |
| Low citation (D8<30) | 61 |

## Critical Issues

### Papers with 0% D10a (orphan cites, no bib) — 5 papers

1. **fundus-cv-risk-prediction**: 47 orphan cites, no bib file (D8=0)
2. **vor-pinn-ode-gap-analysis**: 23 orphan cites, no bib file (D8=0)
3. **bppv-canalith-relocation-ode**: 12 orphan cites, no bib file (D8=0)
4. **nystagmus-neutral-PINN**: 8 orphan cites, no bib file (D8=0)
5. **pupil-response-dynamics-ode**: 2 orphan cites, no bib file (D8=0)

### D10a < 100% (partial match) — 7 papers

1. **bppv-pc-repositioning-optimization**: D10a=75% (3 orphans: Baloh2003, Chang2004, Kim2012; 35 zombies)
2. **086-endolymph-perilymph-coupling-ode**: D10a=88.9% (1 orphan: sculer1987; 8 zombies)
3. **093-saccade-target-shift-PINN**: D10a=88.9% (1 orphan: vergence-accommodation-90; 8 zombies)
4. **111-pupillary-light-reflex-ODE**: D10a=87.5% (2 orphans: nemeyer2019, wong2007; 1 zombie)
5. **ocular-torsion-PINN**: D10a=91.7% (1 orphan: oveson20; 5 zombies)
6. **semicircular-canal-PINN**: D10a=92.3% (1 orphan: caldwell2014; 3 zombies)
7. **vhit-pinn-ode**: D10a=94.1% (1 orphan: laureys2001; 0 zombies)

### Papers with D8 < 30 but D10a=100% — 24 papers (clean, low refs)

Most are PINN/ODE papers with inline thebibliography. Acceptable for small studies.

## Healthy Papers (D10a=100%, D8>=30) — 45 papers

| Paper | D8 | BBL | Zombies |
|-------|:--:|:---:|--------:|
| 3d-eye-bppv-diagnosis | 62 | ❌ | 0 |
| 3d-eyeball-iris-segmentation | 37 | ❌ | 0 |
| 3d-iris-normalization | 30 | ✅ | 0 |
| 3d-pupil-localization | 35 | ❌ | 11 |
| 3wd-framework-trustworthy-clinical-ai | 30 | ❌ | 0 |
| amd-ai-screening | 56 | ❌ | 0 |
| bppv-minimal-stimulus | 30 | ❌ | 0 |
| bppv-mss-lsc-bppv | 35 | ❌ | 5 |
| bppv-pd-clinical-review | 57 | ❌ | 0 |
| cataract-ai-review | 67 | ❌ | 0 |
| corneal-ai-review | 68 | ❌ | 0 |
| crispdm-heart | 30 | ❌ | 0 |
| crispdm-wdbc | 31 | ✅ | 0 |
| cuteye-model | 30 | ❌ | 0 |
| data-leakage-breast-cancer-critical-audit | 30 | ❌ | 0 |
| ded-ai-screening | 55 | ❌ | 0 |
| dr-ai-screening | 40 | ❌ | 0 |
| dual-ellipse-fitting | 30 | ✅ | 0 |
| dual-ellipse-pupil-localization | 42 | ✅ | 0 |
| glaucoma-ai-screening | 59 | ❌ | 0 |
| hcs3wt-breast-cancer | 32 | ❌ | 2 |
| iris-3d-anatomical-opt | 30 | ❌ | 0 |
| iris-yolo | 30 | ❌ | 0 |
| kappa-3d-eye-tracking | 52 | ❌ | 0 |
| kappa-bppv-nystagmus | 73 | ❌ | 0 |
| kappa-pd-calibration-artifacts | 82 | ❌ | 0 |
| kappa-vor-calibration | 64 | ❌ | 0 |
| membranous-scc-reconstruction | 33 | ✅ | 0 |
| myopia-ai-screening | 76 | ❌ | 0 |
| octa-ai-review | 68 | ❌ | 0 |
| off-axis-iris-normalization-correction | 30 | ✅ | 0 |
| pd-dysphagia-2026 | 48 | ❌ | 48 |
| pd-ocular-biomarkers | 53 | ❌ | 0 |
| pd-torsion-review | 46 | ❌ | 0 |
| pima-crispdm | 33 | ✅ | 0 |
| rop-ai-screening | 49 | ❌ | 0 |
| rvo-ai-screening | 75 | ❌ | 0 |
| strabismus-ai-screening | 39 | ❌ | 0 |
| synthos-system-paper | 49 | ❌ | 0 |
| vog-vestibular-review | 33 | ❌ | 33 |
| vor-3d-eye-tracking | 53 | ❌ | 0 |
| vor-bppv-diagnosis | 65 | ❌ | 0 |
| vor-pd-systematic-review | 68 | ❌ | 0 |
| vor-sparse-modular | 31 | ❌ | 0 |

## Zombie-Heavy Papers (>20 zombies)

1. **pd-dysphagia-2026**: 48 zombies (zero cites!)
2. **bppv-pc-repositioning-optimization**: 35 zombies
3. **vog-vestibular-review**: 33 zombies (zero cites!)
4. **scale-space-canny**: 30 zombies (zero cites!)

## Key Observations

1. **Compilation rate very low**: Only 7/107 (7%) have been compiled with BibTeX.
2. **Massive zombie collection**: 29 papers have D8>0 but zero cites — these are papers with reference libraries but no actual text citations. This is likely from papers that were started and then abandoned or heavily refactored.
3. **Inline references dominate**: Most "healthy" papers use `thebibliography` environment (bib_source=inline), not external .bib files.
4. **Only 7 papers use external .bib files**: 3d-iris-normalization, crispdm-wdbc, dual-ellipse-fitting, dual-ellipse-pupil-localization, membranous-scc-reconstruction, off-axis-iris-normalization-correction, pima-crispdm — and these 6 are the ones with BBL compiled.
5. **The real bottleneck**: Papers with 5 orphan cites but no bib at all are the most actionable fixes.
