# D8/D10a Scan Results — 2026-06-06

Scan script: `paper-references-scanning/scripts/d8d10a-scan.py`
Directory: `/media/yakeworld/sda2/Synthos/outputs/papers/`

## Summary

- **Total papers scanned**: 57
- **Healthy (D10a=100%, D8≥30)**: 45
- **Problem (D10a<100% or D8<30)**: 12

## Problem Papers

| 论文 | D8 | D10a | 孤儿 | 僵尸 | 状态 |
|:-----|:--:|:----:|:----:|:----:|:-----|
| fundus-cv-risk-prediction | 0 | 0.0% | 47个孤儿 | 无 | ❌ 无bib |
| pupil-response-dynamics-ode | 0 | 0.0% | 2个孤儿 | 无 | ❌ 无bib |
| vor-pinn-ode-gap-analysis | 0 | 0.0% | 23个孤儿 | 无 | ❌ 无bib |
| bppv-pinn-canalolithiasis | 0 | 100% | 无 | 无 | ❌ D8=0 |
| kappa-angle-calibration | 0 | 100% | 无 | 无 | ❌ D8=0 |
| bppv-nystagmus-pinn | 5 | 100% | 无 | 5个僵尸 | ❌ D8=5 <30 |
| portable-et-r2 | 10 | 100% | 无 | 无 | ❌ D8=10 <30 |
| optokinetic-reflex-pinn | 16 | 100% | 无 | 16个僵尸 | ❌ D8=16 <30 |
| bppv-epley-semont-dizziness-mechanism | 26 | 100% | 无 | 1个僵尸 | ❌ D8=26 <30 |
| bppv-hc-repositioning-safety | 29 | 100% | 无 | 3个僵尸 | ❌ D8=29 <30 |
| bppv-mss-gufoni-epley-combined | 29 | 100% | 无 | 7个僵尸 | ❌ D8=29 <30 |
| bppv-pc-repositioning-optimization | 44 | 75.0% | 3个孤儿 | 35个僵尸 | ❌ D10a<100 |

## Notes

1. **fundus-cv-risk-prediction, pupil-response-dynamics-ode, vor-pinn-ode-gap-analysis**: These papers have `\cite{}` in the tex but no `.bib` file found. They need external bib files.

2. **bppv-pinn-canalolithiasis, kappa-angle-calibration**: No tex content (no cites, no bibitems) — possibly empty/minimal papers.

3. **bppv-nystagmus-pinn**: Uses inline `\bibitem{}` (no `\cite{}`). D8=5 is below threshold.

4. **bppv-pc-repositioning-optimization**: Has 3 orphan cites (Baloh2003, Chang2004, Kim2012) not in `paper.bib`, and 35 zombie entries.

5. **scale-space-canny, vog-vestibular-review, pd-dysphagia-2026, optokinetic-reflex-pinn**: Have 100% D10a but use inline `\bibitem{}` without `\cite{}`. D8 < 30 triggers flag.

6. **healthy papers**: 45 papers with D10a=100% and D8≥30.
