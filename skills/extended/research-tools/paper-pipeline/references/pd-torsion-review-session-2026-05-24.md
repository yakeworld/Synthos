# PD Torsion Review Writing Session — 2026-05-24

## What Happened

Wrote a critical review paper on 3D torsional oculomotor biomarkers for PD screening. The paper was initially written directly (bypassing NotebookLM), then revised through Gemini 7D review.

## Key Lessons for Future Paper-Pipeline Runs

### 1. NotebookLM is NOT optional
Initial draft was written directly from literature references + knowledge graph. Gemini found:
- **H1.5 missing middle state** — the three-pronged hypothesis (H₁/H₂/H₃) had a critical gap: what if torsion alone is weak (AUC<0.80) but orthogonal to 2D (r<0.3)? This synergistic incremental value state was completely missed.
- **D3 (results credibility) initially scored 6.0** — no data honesty statement distinguishing empirical values from theoretical thresholds.
- **D4 (completeness) needed TRIPOD-AI/XAI addition** — ML fusion section lacked explainability requirements.

**Lesson: Every paper section must pass through `notebooklm ask` before being finalized.**

### 2. Citation Cross-Referencing Works
Gemini cross-referenced all 33 citations against the notebook's 266 sources:
- 32/33 citations confirmed (directly found in sources)
- 1 citation (Gologorsky 2009) was an "orphan" — the only torsion-in-PD study, not directly available in the notebook's existing sources. This honestly confirmed the paper's core argument that torsion in PD is nearly unexplored.

### 3. Version Management
- Old PDF (source e2d65c09) must be deleted before uploading new version
- Command: `echo "y" | notebooklm source delete <id>`
- After deletion, upload new PDF: `notebooklm source add paper.pdf`

### 4. Re-Verification after Fixes
After applying H1.5 fix, L0.5 data honesty statement, and TRIPOD-AI section:
- Re-uploaded as source 2428bf91
- Gemini re-review confirmed all 3 fixes: D2 9.0→9.8, D3 6.0→8.5, D4 8.0→9.5
- **Must do re-verification** — otherwise don't know if fixes actually worked.

## Paper Stats
- Final: 15 pages, 36 references, 4 hypotheses (H₁/H₁.₅/H₂/H₃)
- Path: `/media/yakeworld/sda2/Synthos/outputs/papers/pd-torsion-review/paper.pdf`
- NotebookLM project: 4a0f1345 (Ocular Biomarkers for Early Parkinson's Disease Diagnosis)
