---
date: 2026-06-10
version: 2.0
tool: d8-d10a-scan-v2.py
---

# D8/D10a Scan Results 2026-06-10

## Summary
- **Total papers scanned**: 196
- **Healthy**: 13 (D10a=100%, D8≥30)
- **Problem**: 183

## Key Observations
- **124 papers with bib=NONE** — cite keys exist but no .bib file found. Dominant failure mode.
- **42 papers with bib=NONE but 0 cites** — empty manuscripts (likely scaffolds), technically healthy but D8<30 triggers flag.
- **JabRef artifacts** (`<label>`, `lamport94`) cause false orphans in 4 papers: `3d-iris-normalization`, `dual-ellipse-fitting`, `3d-eyeball-iris-segmentation`, `dual-ellipse-pupil-localization`.
- **Only 10 papers have .bbl compiled**: `3d-eyeball-iris-segmentation`, `bppv-epley-semont-dizziness-mechanism`, `bppv-hc-repositioning-safety`, `bppv-mss-gufoni-epley-combined`, `bppv-mss-lsc-bppv`, `crispdm-wdbc`, `cuteye-model`, `iris-3d-anatomical-opt`, `membranous-scc-reconstruction`, `pima-crispdm` (plus a few others with small D8).
- **Root-level artifact**: `outputs/papers/paper.tex` exists with 17 orphan cites — not a real paper.
