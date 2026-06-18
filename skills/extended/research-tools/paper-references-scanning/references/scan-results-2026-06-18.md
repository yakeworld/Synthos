# Scan Data — 2026-06-18
**Daily automated scan** of paper library citation health.

## Summary: 72 papers scanned, 66 healthy (91.7%), 2 with D10a<95%

### Key Findings

| Metric | Value |
|--------|-------|
| Total directories | 72 |
| Valid papers | 72 |
| Healthy papers (D10a=100%, no orphans, D8>0) | 66 (91.7%) |
| D10a ≥ 95% | 70/72 (97.2%) |
| D10a = 100% | 70/72 (97.2%) |
| DOI ≥ 90% (d8>0) | 4/68 (5.9%) |
| Papers with orphans | 2 |
| Papers with zombies | 17 |
| Papers with DOI 0% (d8>0) | 59/68 (86.8%) |
| Papers with bib_source=none | 4 (empty papers) |

### D10a < 95% (2 papers)
- **086-endolymph-perilymph-coupling-ode**: D10a=88.9%, 1 orphan (`sculer1987`), 8 zombies
- **093-saccade-target-shift-PINN**: D10a=93.3%, 1 orphan (`vergence-accommodation-90`), 2 zombies

### Zombie-heavy papers (top 5)
1. **3d-eyeball-iris-segmentation**: 21 zombies
2. **pupillary-light-reflex-ODE**: 20 zombies
3. **Paper_101_optokinetic-reflex-PINN**: 15 zombies
4. **147-lens-capsule-biomechanics-ODE**: 14 zombies
5. **148-corneal-epithelial-wound-healing-ODE**: 12 zombies

### DOI Coverage Crisis
86.8% of papers (59/68 with d8>0) have **zero DOI coverage**. Only 7 papers achieve ≥70% DOI coverage, and only 4 achieve ≥90%.

- High DOI coverage papers: `3d-eyeball-iris-segmentation` (98.0%), `pima-crispdm` (97.0%), `3wd-framework-trustworthy-clinical-ai` (90.0%), `off-axis-iris-normalization-correction` (90.0%)
- All ODE/PINN paper series (1xx/0xx naming) have 0% DOI coverage — their bib files lack DOI fields entirely

### D8 Distribution
| D8 Range | Count |
|----------|-------|
| ≥ 30 | 12 |
| 15–29 | 49 |
| 10–14 | 3 |
| < 10 | 8 |

### bbl Status
13 papers have compiled `.bbl` files (compiled successfully), 59 do not.

### Empty Papers (bib_source=none, d8=0, cites=0)
- `bppv-pinn-canalolithiasis`
- `cupula-deflection-pinn`
- `smooth-pursuit-PINN`
- `vestibular-compensation-ODE`

These have no citations and no references — structural empty shells.

### Quality Gate G5 Assessment
- D10a ≥ 95%: **PASS** (97.2% pass rate)
- DOI coverage ≥ 90%: **FAIL** (5.9% pass rate)
- DOI coverage ≥ 70%: **FAIL** (10.3% pass rate)

**G5 critical weakness**: DOI coverage is the weakest quality dimension. The ODE/PINN paper series lack DOI metadata in their bib files, making references untrackable and unverifiable.
