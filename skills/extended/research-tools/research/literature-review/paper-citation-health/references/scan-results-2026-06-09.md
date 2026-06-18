# Paper Library D8/D10a Scan — 2026-06-09 (v2: fixed bib resolution)

Run: python3 d8-d10a-scan-v2.py (paper-citation-health skill)
Total: 147 papers scanned (excluding "." root directory)

## Summary

| Metric | Value |
|--------|-------|
| Total papers | 147 |
| Healthy (D10a=100%, D8>=30) | 13 |
| Problem | 134 |
| BBL compiled | 18 |
| No bib file at all | 61 |
| Orphan cites | 1921 |
| Zombie cites | 183 |
| No cite references (D8>0, D10a=100%, 0 cites) | 39 |

## Comparison: 2026-06-08 vs 2026-06-09

| Metric | 2026-06-08 | 2026-06-09 | Change |
|--------|-----------|-----------|--------|
| Total papers | 88 | 147 | +59 |
| Healthy | 45 | 13 | -32 |
| Problem | 43 | 134 | +91 |
| BBL compiled | 7 | 18 | +11 |
| No bib file | 11 | 61 | +50 |
| Orphan cites | 10 | 1921 | +1911 |
| Zombie cites | 36 | 183 | +147 |

## Critical Issues

### Papers with 0.0% D10a (orphan cites, no bib) — 61 papers

Top orphan counts:
1. **kappa-pd-calibration-artifacts**: 82 orphan cites, no bib file (D8=0)
2. **myopia-ai-screening**: 76 orphan cites, no bib file (D8=0)
3. **rvo-ai-screening**: 75 orphan cites, no bib file (D8=0)
4. **kappa-bppv-nystagmus**: 73 orphan cites, no bib file (D8=0)
5. **corneal-ai-review**: 68 orphan cites, no bib file (D8=0)
6. **octa-ai-review**: 68 orphan cites, no bib file (D8=0)
7. **vor-pd-systematic-review**: 68 orphan cites, no bib file (D8=0)
8. **cataract-ai-review**: 67 orphan cites, no bib file (D8=0)
9. **vor-bppv-diagnosis**: 65 orphan cites, no bib file (D8=0)
10. **kappa-vor-calibration**: 64 orphan cites, no bib file (D8=0)

### D10a < 100% (partial match) — 6 papers

1. **bppv-pc-repositioning-optimization**: D10a=75% (3 orphans: Baloh2003, Chang2004, Kim2012; 34 zombies)
2. **papers/97-smooth-pursuit-ODE**: D10a=86% (1 orphan: Luo2023cerebellar; 11 zombies)
3. **3d-iris-normalization**: D10a=94% (2 orphans: <label>, lamport94; 0 zombies)
4. **dual-ellipse-fitting**: D10a=94% (2 orphans: <label>, lamport94; 1 zombie: jabref-meta)
5. **3d-eyeball-iris-segmentation**: D10a=95% (2 orphans: <label>, lamport94; 1 zombie: jabref-meta)
6. **dual-ellipse-pupil-localization**: D10a=95% (2 orphans: <label>, lamport94; 1 zombie: jabref-meta)

Note: `<label>`, `lamport94`, `jabref-meta: databaseType:bibtex;` are JabRef artifacts.

### Papers with D8 < 30 but D10a=100% — 39 papers

Most are lit-reviews (5-10 entries each) and some PINN/ODE papers with minimal reference counts.

## Healthy Papers (D10a=100%, D8>=30) — 13 papers

| Paper | D8 | BBL | Zombies |
|-------|:--:|:---:|--------:|
| 3d-eyeball-iris-segmentation | 38 | ✅ | 1 |
| 3d-pupil-localization | 35 | ✅ | 11 |
| 3wd-framework-trustworthy-clinical-ai | 30 | ❌ | 0 |
| bppv-epley-semont-dizziness-mechanism | 26 | ✅ | 1 |
| bppv-hc-repositioning-safety | 29 | ✅ | 3 |
| bppv-mss-gufoni-epley-combined | 29 | ✅ | 7 |
| bppv-mss-lsc-bppv | 35 | ✅ | 4 |
| crispdm-wdbc | 31 | ❌ | 0 |
| cuteye-model | 30 | ✅ | 0 |
| iris-3d-anatomical-opt | 30 | ✅ | 0 |
| membranous-scc-reconstruction | 33 | ❌ | 0 |
| pima-crispdm | 33 | ❌ | 0 |
| vog-vestibular-review | 33 | ✅ | 33 |
| vor-digital-twin/paper | 30 | ✅ | 0 |
| vor-sparse-modular | 31 | ✅ | 0 |

## Key Findings

1. **No-bib is the dominant failure mode**: 61/147 papers (41%) have no `.bib` file at all.
2. **Compilation rate is very low**: Only 18/147 papers (12%) have been compiled with BibTeX.
3. **Healthy ratio dropped from 51% to 9%**: Library grew from 88 to 147 papers with mostly unmanaged papers.
4. **JabRef artifacts persist**: `<label>`, `lamport94`, and `jabref-meta` entries cause false orphans/zombies in 4 papers.
5. **Duplicate directories**: Some papers have `paper.tex` in both `01-manuscript/` and `09-manuscript/` subdirs, creating entries like `name/09-manuscript` in the scan.