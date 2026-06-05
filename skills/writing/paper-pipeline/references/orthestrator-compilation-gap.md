# Paper-Orchestrator Compilation Gap

## Problem

The paper-orchestrator (v4 Hermes Agent mode) processes 8 IMRaD pipeline steps but **never compiles PDFs** for papers that reach 100% completion. It skips any paper where `progress >= 1.0`.

## Root Cause

In `paper-orchestrator.py` line 278:
```python
if paper["progress"] >= 1.0:
    continue  # 已完成，跳过
```

This means when all 8 steps (gap_analysis → quality_check) are done, the orchestrator considers the paper fully processed and never triggers `pdflatex` compilation.

## Affected Papers (as of 2026-06-05 13:19 UTC)

| Paper | Steps | Last Step |
|-------|-------|-----------|
| 3wd-framework-trustworthy-clinical-ai | 8/8 | quality_check |
| membranous-scc-reconstruction | 8/8 | quality_check |
| off-axis-iris-normalization-correction | 8/8 | quality_check |
| pima-crispdm | 8/8 | quality_check |
| crispdm-heart | 8/8 | quality_check |
| crispdm-wdbc | 8/8 | quality_check |
| data-leakage-breast-cancer-critical-audit | 8/8 | quality_check |
| dual-ellipse-fitting | 8/8 | quality_check |
| dual-ellipse-pupil-localization | 8/8 | quality_check |

## Workarounds

### Option A: Manual Compilation
```bash
cd /media/yakeworld/sda2/Synthos/outputs/papers/<paper_name>/
pdflatex 01-manuscript/paper.tex
bibtex 01-manuscript/paper
pdflatex 01-manuscript/paper.tex
pdflatex 01-manuscript/paper.tex
```

### Option B: Fix Orchestrator
Add a 9th step to the orchestrator for PDF compilation:
```python
STEPS["pdf_compile"] = {
    "name": "PDF Compilation",
    "prompt": "Compile the LaTeX paper to PDF.",
}
# Append to STEPS in order after quality_check
```

### Option C: Cron Job for PDF Batch
Create a cron job that runs pdflatex on all complete-but-uncompiled papers:
```bash
hermes cronjob create \
  --name "pdf-compile-batch" \
  --prompt "Compile missing PDFs for fully-complete papers" \
  --schedule "every 12h" \
  --skills paper-pipeline \
  --enabled-toolsets terminal,file
```

## Recommendation

Option B (add pdf_compile step) is the most sustainable fix. The orchestrator should compile PDFs as the final step, not leave it as a manual task.

## Related
## Related
- `references/batch-qc-workflow.md` — QC batch processing
- `references/paper-writing-via-notebooklm.md` — Manuscript generation
- `references/legacy-paper-rescue-workflow.md` — Legacy paper handling
- `references/pdf-compilation-silent-failure.md` — Second pdflatex pass returns exit 1 silently
