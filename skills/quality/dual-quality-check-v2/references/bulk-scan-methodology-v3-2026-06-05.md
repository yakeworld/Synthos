# Bulk D8/D10a Scan Methodology v3 — 2026-06-05

## Overview

This reference documents the v3 scan that achieved **96.2% accuracy** (51/53 papers correctly classified) after fixing 3 critical traps found in v2.

## Traps Fixed

| Trap | Symptom | Papers Affected | Fix |
|:-----|:--------|:---------------:|:----|
| `\input{file.tex}` double `.tex` | D10a=0%, 48 zombies (pd-dysphagia) | 2 (pd-dysphagia, vog-vestibular) | Check `.endswith('.tex')` before appending |
| thebibliography + .aux ↔ bib_collect | D8=0, D10a=0% for 25+ papers with `.aux` | ~25 (all thebib papers w/ aux) | Detect thebibliography FIRST |
| Directory-name .tex not in priority | D8=10 instead of 30 (hcs3wt) | 1 (hcs3wt) | Add `dir_name + '.tex'` to priority |

## Scan Results (53 papers, 2026-06-05)

```
论文总数: 53
健康(CLEAN): 51 (96.2%)
P0 孤儿: 1 (_todo 存档目录, 非活跃论文)
僵尸: 0
D8<30 (但D10a=100%): 0
其他问题: 1 (pd-dysphagia-2026: D8=48, D10a=81.2%, 9 zombies)
```

## Priority File Selection

```python
dir_name = os.path.basename(paper_dir)
priority = [
    dir_name + '.tex',         # NEW: directory name match
    'article_improved.tex',    # restore latest
    'v4-paper.tex',            # v4 standard
    'paper.tex',               # generic
    'main.tex',                # generic
    'article.tex',             # old version
]
```

## Exclude List

```python
SKIP_DIRS = {
    '_todo', '_docs', '_archive_scripts', 'lit-reviews',
    'scf-paper',  # qc files only, no active tex
    # Non-paper dirs:
    'gap-paper-35-neuromorphic-eye-tracking',
    'individualized-bppv-simulation',
    'scc-pd-biomarker',
    'pinn-operator-learning-generalization',
}
```
