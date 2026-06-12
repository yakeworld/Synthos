# Non-Paper Directory Taxonomy
**Class**: Paper library audit, directory classification.
**Source**: 2026-06-12 D8/D10a scan revealed 33 non-paper dirs in `/media/yakeworld/sda2/Synthos/outputs/papers/`.

## Categories

### 1. ML/Data Science Projects
- `kaggle-wdbc-classification` — Kaggle breast cancer dataset classification
- `stroke-prediction` — ML prediction project
- `cleveland-heart-disease` — UCI heart disease dataset

### 2. Old/Archived Papers (pre-pipeline)
- `paper-91-fixation-stability-PINN` — Old numbering format
- `paper-127-macular-thermo-ODE` — Old numbering format
- `paper-128-retinal-oxygen-metabolism-ODE` — Old numbering format
- `choroidal-hemodynamics-ODE` — Old paper, no pipeline
- `scc-mathematical-morphology` — Old paper
- `scc-pd-biomarker` — Old paper
- `scf-paper` — Old paper
- `gap-paper-35-neuromorphic-eye-tracking` — Old gap paper

### 3. Project Subdirectories (not papers)
- `individualized-bppv-simulation` — Simulation project
- `scale-space-feature-tensor` — ML feature engineering
- `110-direction-scan` — Scan tool, not a paper

### 4. Standard Subdirs Misplaced in papers/
- `01-manuscript` (×4 occurrences) — Manuscript subdir duplicated at root
- `09-manuscript` (×6 occurrences) — Manuscript subdir duplicated at root
- `references` — Reference directory misplaced in papers/

### 5. Gap Analysis Subdirs
- `01-gap-analysis` — Gap analysis project dir
- `01-gap_analysis` — Variant naming

## Rule for Directory Classification

A directory in `papers/` is a valid paper IF AND ONLY IF:
1. It has `01-manuscript/paper.tex`, OR
2. It has a root-level `.tex` file (not a draft/template variant)

Otherwise it is NOT a paper and should be excluded from D8/D10a scanning.

## Historical Count
- 2026-06-11: ~151 papers (before 33 non-paper dirs were fully identified)
- 2026-06-12: 153 papers, 33 non-paper dirs explicitly classified above
