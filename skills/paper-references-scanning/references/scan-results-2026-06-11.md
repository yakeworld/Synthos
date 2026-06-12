# 📊 Synthos 论文全库 D8/D10a 扫描报告

**扫描时间**: 2026-06-11 12:00 UTC
**脚本**: `paper-references-scanning/scripts/d8d10a-scan.py` (v7)

---

## 汇总

- **总计**: 147篇
- **健康**: 45篇 (D10a=100% 且 D8≥30)
- **问题**: 102篇
- **总引用数**: 2,737
- **总孤儿**: 115
- **总僵尸**: 1,057
- **总D8**: 3,679
- **已编译(.bbl)**: 7 ✅ | 140 ❌

---

## D10a 分布

| 区间 | 数量 |
|:-----|:----:|
| 100% | 135 |
| 90-99% | 3 |
| 50-89% | 3 |
| 0-49% | 6 |

## D8 分布

| 区间 | 数量 |
|:-----|:----:|
| 0-9 | 15 |
| 10-29 | 86 |
| 30-49 | 28 |
| 50-99 | 18 |
| 100+ | 0 |

## Bib 来源分布

| 来源 | 数量 |
|:-----|:----:|
| inline (内嵌bibitem) | 108 |
| references.bib | 20 |
| none (无bib) | 12 |
| paper.bib | 6 |
| synthos-paper.bib | 1 |

---

## 关键问题论文

### ⛔ 无bib文件（孤儿率100%）— 6篇

| 论文 | 孤儿数 |
|:-----|:------:|
| bppv-canalith-relocation-ode | 12 |
| fundus-cv-risk-prediction | 47 |
| nystagmus-neutral-PINN | 8 |
| orthokeratology-corneal-remodeling-ODE-paper-117 | 15 |
| pupil-response-dynamics-ode | 2 |
| vor-pinn-ode-gap-analysis | 23 |

### ⛔ 有引用但D8=0 — 6篇

bppv-pinn-canalolithiasis, cupula-deflection-pinn, kappa-angle-calibration, pan-PINN, smooth-pursuit-PINN, vestibular-compensation-ODE

### ⚠️ D10a < 100% — 6篇

| 论文 | D10a | 孤儿 | 僵尸 |
|:-----|:----:|:----:|:----:|
| bppv-pc-repositioning-optimization | 75% | 3 | 35 |
| 086-endolymph-perilymph-coupling-ode | 88.9% | 1 | 8 |
| 093-saccade-target-shift-PINN | 88.9% | 1 | 8 |
| ocular-torsion-PINN | 91.7% | 1 | 5 |
| semicircular-canal-PINN | 92.3% | 1 | 3 |
| vhit-pinn-ode | 94.1% | 1 | 0 |

### ⚠️ D8 < 30 但 D10a=100% — 86篇

主要为ODE/PINN管线论文（D8=15~25，引用数偏低，僵尸条目多）。

### ⚠️ 未编译 — 140篇

仅7篇有 `.bbl`:
`3d-iris-normalization`, `crispdm-wdbc`, `dual-ellipse-fitting`, `dual-ellipse-pupil-localization`, `off-axis-iris-normalization-correction`, `membranous-scc-reconstruction`, `pima-crispdm`

---
