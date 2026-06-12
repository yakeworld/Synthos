# Synthos-AKNE Bridge Fix — Session 2026-06-10

## What Was Fixed

### 1. Directory Normalization (32 papers)
Files with flat structure moved to subdirectories:
- 01-scleral-remodeling-ODE → 01-manuscript + 06-references
- 02-corneal-tension-ODE → 01-manuscript + 06-references
- 092-dissociated-ocular-torsion-PINN → 01-manuscript only
- ... (32 total)

Script: `/tmp/fix_bridge.py` — scans all dirs, identifies flat-manuscript files, creates subdirs.

### 2. Skill Connections (25 → 0 isolated)
Each skill connected to:
- 2-3 AKNE source categories via `skill_source_domain` (42 edges total)
- 2-3 wiki concepts via `skill_concept` (18 edges total)

Script: `/tmp/fix_skill_connections.py`

### 3. Bidirectional Edges (281 new)
- `concept_paper` (281): wiki concept → synthos paper
- `source_category` (1145): source file → category (reverse of source_category_membership)
- `category_paper` (255): category → synthos paper (reverse of paper_source_domain)
- `paper_category` (255): synthos paper → category

Scripts: `/tmp/fix_reverse_and_clean.py`, `/tmp/fix_bidirectional.py`

### 4. Isolated Papers Mapped (9 papers)
Manual mapping for domain="其他":
- fundus-cv-risk-prediction → 眼动研究
- iris-3d-anatomical-opt → 眼动研究
- memoranous-scc-reconstruction → 半规管空间姿态研究
- ... etc.

Script: `/tmp/fix_isolated.py`

### 5. Non-paper Nodes Reclassified (7 nodes)
Reclassified from `synthos_paper` to `synthos_misc`:
lit-reviews, 01-gap_analysis, 09-manuscript, 110-direction-scan, papers, references, scripts

### 6. Bridge Script Updated
Excluded non-paper dirs from synthos-akne-bridge-v2.py line 109.

### 7. Wiki Garbage Cleaned
Removed `[核心技术, 知识点]:: 核心技术, 知识点` lines from index.md, log.md, CATALOG.md.

### 8. Auto-Evolve Daemon Restarted
pkill → nohup python3 scripts/auto_evolve_daemon.py

## Results

| Metric | Before | After |
|--------|--------|-------|
| Synthos papers isolated | 37/155 (24%) | 0/148 (0%) |
| Synthos skills isolated | 25/25 (100%) | 0/25 (0%) |
| Total edges | ~4050 | 6130 |
| Reverse flow | 0 | 281+1145+255+255 = 1936 |
| Wiki garbage lines | 56+ | 0 |
| Bidirectional paths | 0 | 4 patterns |
