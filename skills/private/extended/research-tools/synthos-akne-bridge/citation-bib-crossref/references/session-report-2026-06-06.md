# Session Report: 2026-06-06 Scan Results

## Scan Context

- **Scan target**: `/media/yakeworld/sda2/Synthos/outputs/papers/`
- **Total dirs found**: 86 (excluding `_docs`, `_todo`, `lit-reviews`)
- **Paper dirs with BibTeX**: 65
- **Scan script**: `scripts/d8-d10a-scan.py` (created in this session)

## Key Findings

### Healthy (D10a=100%, D8≥30): 16 papers

| Paper | D8 |
|-------|----|
| 3d-sobel-edge-detection | 32 |
| 3d-pupil-localization | 35 |
| crispdm-wdbc | 31 |
| cuteye-model | 30 |
| membranous-scc-reconstruction | 33 |
| off-axis-iris-normalization-correction | 30 |
| pima-crispdm | 33 |
| scale-space-canny | 30 |
| scale-space-feature-tensor | 30 |
| vor-digital-twin | 30 |
| vor-sparse-modular | 31 |
| bppv-mss-lsc-bppv | 35 |
| bppv-otoconia-simulation | 32 |
| iris-3d-anatomical-opt | 30 |
| vog-vestibular-review | 33 |

### Critical (D8=0, cite keys present but no bib): 31 papers

Mostly `*-ai-screening`, `*-review`, `kappa-*` series. These papers have
`\cite{}` calls but no `.bib` files — likely skeleton papers that were never
populated with references.

### Moderate (D10a<100%, D8≥30): 12 papers

- `3d-eyeball-iris-segmentation` (94.9%): orphans `<label>`, `lamport94`
- `3d-iris-normalization` (93.8%): orphans `<label>`, `lamport94`
- `dual-ellipse-fitting` (93.8%): orphans `<label>`, `lamport94`
- `dual-ellipse-pupil-localization` (95.5%): orphans `<label>`, `lamport94`
- `bppv-pc-repositioning-optimization` (75.0%): 3 orphans + 35 zombies
- `scc-mathematical-morphology` (78.9%): 8 orphans + 4 zombies

### Low (D8<30, D10a=100%): 6 papers

`bppv-epley-semont` (26), `bppv-hc-repositioning` (29),
`bppv-mss-gufoni-epley-combined` (29), `eye-tracking-4d` (13),
`portable-et-r2` (10)

### Mixed (significant orphans AND zombies): 3 papers

- `hcs3wt-breast-cancer`: 30 orphans + 30 zombies (D8=30, completely misaligned)
- `iris-yolo`: 34 orphans + 30 zombies
- `pd-dysphagia-2026`: 0 orphans + 29 zombies

## Technique Notes

1. **Non-standard layouts**: `paper.tex` at root, named manuscript files,
   different reference dir names — always use recursive fallback search.

2. **Symlinked bib**: `references.bib -> 06-references/references.bib` is
   common. Python follows symlinks by default — no special handling needed.

3. **Enumerate references**: Some papers use `\begin{enumerate}` instead of
   `\bibliography{}`. Zero `\cite{}` — correctly excluded.

4. **Non-paper dirs**: `_docs`, `_todo`, `lit-reviews` must be filtered.

5. **False positive `<label>`**: Keys matching `\label{}` or `fig:`, `tab:`
   patterns are being matched as cite keys. Fix: exclude these patterns.
