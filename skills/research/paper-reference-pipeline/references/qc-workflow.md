# Dual Quality Check Workflow

## Overview
Two-phase quality assessment for all Synthos papers:
- **Phase 1**: Compile LaTeX → upload PDF to NotebookLM
- **Phase 2**: Gemini 7-dimension review (D1-D7) + Reference count check (D8)

## Scripts

| Script | Path | Purpose |
|--------|------|---------|
| batch_qc_phase1.py | outputs/papers/ | Compile + Upload |
| batch_qc_phase2.py | outputs/papers/ | Gemini 7D review |
| batch_qc_rerun.py | outputs/papers/ | **Current**: Upload + Gemini review in one pass |
| clean_and_bib.py | outputs/papers/ | Project duplicate cleanup + BibTeX generation |

## Running

```bash
cd /media/yakeworld/sda2/Synthos/outputs/papers
python3 batch_qc_rerun.py
```

Takes ~3 hours for 42 papers (3-4 min/paper including 10s delay).

## D1-D7 Dimensions (Gemini)

| Dim | Name | Description |
|-----|------|-------------|
| D1 | Scientific Contribution | Novelty and significance of findings |
| D2 | Methodological Rigor | Soundness of methods |
| D3 | Results Credibility | Evidence quality, reproducibility |
| D4 | Completeness | Coverage of topic |
| D5 | Clarity | Writing quality |
| D6 | Novelty | Original contribution |
| D7 | Citation Quality | Reference relevance |

## D8 Reference Standard

| Score | Condition |
|-------|-----------|
| 1.00 | ≥30 references |
| <1.00 | <30 references (score = refs/30) |

Auto-fix: `tools/paper-manager/auto_fix_d8.py`

## Results from 2026-05-27 Run

- T1 (≥0.85): 31 papers
- T3 (≥0.75): 1 paper
- FAIL (<0.75): 11 papers
- Notable: pd-torsion-review went from 0.00 → 0.91 after reference supplementation
