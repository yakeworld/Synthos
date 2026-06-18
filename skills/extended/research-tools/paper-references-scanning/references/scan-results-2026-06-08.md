# Paper Library D8/D10a Scan — 2026-06-08 (v2: fixed bib key parsing)

Run: python3 d8d10a-scan.py
Total: 88 papers scanned

## Summary

| Metric | Value |
|--------|-------|
| Total papers | 88 |
| Healthy (D10a=100%, D8>=30) | 45 |
| Problem | 43 |
| BBL compiled | 7 |
| No bib file at all | 11 |
| Orphan cites | 10 |
| Zombie cites | 36 |
| No cite references | 22 |

## Critical Issues

### Papers with 0.0% D10a (orphan cites, no bib):
1. **bppv-canalith-relocation-ode**: 12 orphan cites, no bib file (D8=0)
2. **nystagmus-neutral-PINN**: 8 orphan cites, no bib file (D8=0)
3. **vor-pinn-ode-gap-analysis**: 23 orphan cites, no bib file (D8=0)
4. **fundus-cv-risk-prediction**: 47 orphan cites, no bib file (D8=0)
5. **pupil-response-dynamics-ode**: 2 orphan cites, no bib file (D8=0)

### D10a < 100% (partial match):
- **bppv-pc-repositioning-optimization**: D10a=75.0% (3 orphans: Baloh2003, Chang2004, Kim2012; 35 zombies)
- **086-endolymph-perilymph-coupling-ode**: D10a=88.9% (1 orphan: sculer1987; 8 zombies, D8=16)
- **ocular-torsion-PINN**: D10a=91.7% (1 orphan: oveson20; 5 zombies, D8=16)
- **semicircular-canal-PINN**: D10a=92.3% (1 orphan: caldwell2014; 3 zombies, D8=15)
- **vhit-pinn-ode**: D10a=94.1% (1 orphan: laureys2001; D8=16)

### Papers with D8 < 30 (clean cite/bib, just few references):
- bppv-nystagmus-pinn: D8=5, 100% D10a, 5 zombies
- portable-et-r2: D8=10, 100% D10a, 0 issues (just small bib)
- binaural-vestibular-PINN, caloric-nystagmus-ODE, endolymph-hydropressure-ode, gaze-stability-PINN, head-impulse-ODE, nystagmus-computational-ODE, okan-dynamics-PINN, okr-adaptation-pinn, saccade-adaptation-pinn, saccadic-suppression-PINN, saccadic-velocity-storage-ode, tinnitus-pinn-ode: all D8=15
- cochlear-vestibular-coupling-PINN, optokinetic-reflex-pinn, saccade-burst-neuron-neuralode, saccade-kinematic-ODE, vestibular-computation-PINN: all D8=16
- perilymph-hydropressure-ODE: D8=17
- vestibular-adaptation-PINN: D8=17
- cerebellar-VOR-adaptation-PINN: D8=18
- saccade-generation-PINN: D8=20
- torsional-VOR-PINN: D8=24
- bppv-epley-semont-dizziness-mechanism: D8=26, 1 zombie
- bppv-hc-repositioning-safety: D8=29, 3 zombies
- bppv-mss-gufoni-epley-combined: D8=29, 7 zombies

### No bib file at all (D8=0, bib_source=none):
bppv-canalith-relocation-ode, nystagmus-neutral-PINN, vor-pinn-ode-gap-analysis, fundus-cv-risk-prediction, pupil-response-dynamics-ode, bppv-pinn-canalolithiasis, cupula-deflection-pinn, kappa-angle-calibration, pan-PINN, smooth-pursuit-PINN, vestibular-compensation-ODE

## Fixed Papers (compared to previous scan run)

The bib key regex fix (stripping `@Article{` prefix) resolved false positives:
- 3d-eyeball-iris-segmentation: 37→0 orphans, 37→0 zombies (was false 0% D10a, now 100%)
- 3d-iris-normalization: 30→0 orphans, 30→0 zombies (was false 0%, now 100%)
- 3d-pupil-localization: 24→0 orphans, 35→11 zombies (was false 0%, now 100%)
- 3wd-framework-trustworthy-clinical-ai: 60→30 D8, 30→0 zombies (was false 30 zombies)
- bppv-epley-semont-dizziness-mechanism: 25→0 orphans, 26→1 zombies (was false 0%, now 100%)
- bppv-hc-repositioning-safety: 26→0 orphans, 29→3 zombies (was false 0%, now 100%)
- bppv-mss-gufoni-epley-combined: 22→0 orphans, 29→7 zombies (was false 0%, now 100%)
- bppv-mss-lsc-bppv: 30→0 orphans, 35→5 zombies (was false 0%, now 100%)
- crispdm-wdbc: 31→0 orphans, 31→0 zombies (was false 0%, now 100%)
- cuteye-model: 30→0 orphans, 30→0 zombies (was false 0%, now 100%)
- dual-ellipse-fitting: 30→0 orphans, 30→0 zombies (was false 0%, now 100%)
- dual-ellipse-pupil-localization: 42→0 orphans, 42→0 zombies (was false 0%, now 100%)
- hcs3wt-breast-cancer: 62→32 D8, 32→2 zombies (was inflated)
- iris-3d-anatomical-opt: 30→0 orphans, 30→0 zombies (was false 0%, now 100%)
- iris-yolo: 30→0 orphans, 30→0 zombies (was false 0%, now 100%)
- membranous-scc-reconstruction: 33→0 orphans, 33→0 zombies (was false 0%, now 100%)
- off-axis-iris-normalization-correction: 30→0 orphans, 30→0 zombies (was false 0%, now 100%)
- pima-crispdm: 33→0 orphans, 33→0 zombies (was false 0%, now 100%)
- portable-et-r2: 10→0 orphans, 10→0 zombies (was false 0%, now 100%)
- scale-space-canny: 30→0 orphans, 30→0 zombies (was false 100% but 30 zombies)
- vog-vestibular-review: 33→0 orphans, 33→0 zombies (was false 100% but 33 zombies)
- vor-sparse-modular: 31→0 orphans, 31→0 zombies (was false 0%, now 100%)
- pd-dysphagia-2026: 48→0 orphans, 48→48 zombies (correctly identified)

**Net change**: 57 problems → 43 problems; 31 healthy → 45 healthy

## Healthy Papers (D10a=100%, D8>=30)

| Paper | D8 | BBL | Cites | Zombies |
|-------|:--:|:---:|------:|--------:|
| 3d-eye-bppv-diagnosis | 62 | NO | 62 | 0 |
| 3d-iris-normalization | 30 | OK | 30 | 0 |
| 3wd-framework-trustworthy-clinical-ai | 30 | NO | 30 | 0 |
| amd-ai-screening | 56 | NO | 56 | 0 |
| bppv-minimal-stimulus | 30 | NO | 30 | 0 |
| bppv-pd-clinical-review | 57 | NO | 57 | 0 |
| cataract-ai-review | 67 | NO | 67 | 0 |
| corneal-ai-review | 68 | NO | 68 | 0 |
| crispdm-heart | 30 | NO | 30 | 0 |
| crispdm-wdbc | 31 | OK | 31 | 0 |
| data-leakage-breast-cancer-critical-audit | 30 | NO | 30 | 0 |
| ded-ai-screening | 55 | NO | 55 | 0 |
| dr-ai-screening | 40 | NO | 40 | 0 |
| dual-ellipse-fitting | 30 | OK | 30 | 0 |
| dual-ellipse-pupil-localization | 42 | OK | 42 | 0 |
| glaucoma-ai-screening | 59 | NO | 59 | 0 |
| hcs3wt-breast-cancer | 32 | NO | 30 | 2 |
| kappa-3d-eye-tracking | 52 | NO | 52 | 0 |
| kappa-bppv-nystagmus | 73 | NO | 73 | 0 |
| kappa-pd-calibration-artifacts | 82 | NO | 82 | 0 |
| kappa-vor-calibration | 64 | NO | 64 | 0 |
| membranous-scc-reconstruction | 33 | OK | 33 | 0 |
| myopia-ai-screening | 76 | NO | 76 | 0 |
| octa-ai-review | 68 | NO | 68 | 0 |
| off-axis-iris-normalization-correction | 30 | OK | 30 | 0 |
| pima-crispdm | 33 | OK | 33 | 0 |
| strabismus-ai-screening | 39 | NO | 39 | 0 |
| synthos-system-paper | 49 | NO | 49 | 0 |
| vor-3d-eye-tracking | 53 | NO | 53 | 0 |
| vor-bppv-diagnosis | 65 | NO | 65 | 0 |
| vor-pd-systematic-review | 68 | NO | 68 | 0 |
| vor-sparse-modular | 31 | NO | 31 | 0 |

## Note on pd-dysphagia-2026

pd-dysphagia-2026 has D8=48, D10a=100%, but **48 zombies** and 0 cites. This is a paper where the bib file contains all references but the paper.tex has no `\cite` commands. D10a reports 100% (vacuously, since all_cites is empty), but the bib file is entirely zombie.

## Script Fix Applied

Fixed `d8d10a-scan.py` bib_key_re to strip the `@EntryType{` prefix from keys. Before: keys captured as `@Article{key,` leading to false orphan/zombie mismatches. After: keys properly extracted as `key` only.
