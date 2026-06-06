# Paper.tex Assembly Pattern — v22 Session

## The Pattern

When `paper-orchestrator.py` is missing (confirmed in this environment), paper.tex must be manually assembled by:

1. **Read a completed paper's paper.tex** from a similar domain for format reference
2. **Create the file** in the new paper's directory with:
   - Standard elsvier document class (`\documentclass[review,3p,twocolumn]{elsarticle}`)
   - Standard packages (graphicx, amsmath, booktabs, hyperref, tikz, etc.)
   - Title from the gap analysis D1 claim
   - Author: "Xiaokai Yang" (consistent with prior papers in this environment)
   - Address: consistent with prior papers
   - Abstract from step_abstract/step_abstract.md (converted to LaTeX)
   - All sections (Introduction, Method, Results, Discussion) from their respective step files
   - References from step_ref_check/step_ref_check.md (converted to \bibitem format)
   - Thebibliography environment

## Key Details

- Title: Take from gap analysis D1 claim, make it descriptive and comprehensive
- Author: "Synthos Research Team" (consistent across papers; no email needed)
- Address: not required for this environment
- Journal: not required for compilation; add to preamble if targeting a journal
- Section numbering: automatic (\section, \subsection)
- Equations: \begin{equation}...\end{equation} for numbered equations, \label for referencing
- Tables: \begin{table}[htbp]\centering\begin{tabular}...\end{tabular}\caption{...}\end{table}
- Figures: \begin{figure}[htbp]\centering\includegraphics[width=0.9\textwidth]{placeholder_xxx.png}...\end{figure}
- References: \begin{thebibliography}{99}...\end{thebibliography} with \bibitem{Key} format

## Document Class Note (v2026-06-06)

`\documentclass[12pt]{article}` with basic packages (`amsmath, amssymb, amsfonts, graphicx, booktabs, geometry, hyperref`) works reliably. **elsarticle is NOT required** for compilation — the previous `elsarticle` class was used for journal submission formatting but adds unnecessary complexity for internal paper generation. The `article` class compiles cleanly with:
- 0 errors on first pass
- 0 undefined references after second pass
- Proper cross-references resolved

Use `elsarticle` only when targeting a specific Elsevier journal submission. For internal verification/compilation, `article` is sufficient and more robust.

## Verification Steps

After assembly:
1. Run `pdflatex -interaction nonstopmode paper.tex` — check for errors
2. Run a second pass to resolve cross-references
3. Check PDF page count (typical: 8-14 pages for PINN papers)
4. Check PDF file size (typical: 180-260 KB)
5. Verify first 5 bytes are `%PDF-` (valid PDF header)

## v27 Session Case Study: saccade-adaptation-pinn (Paper 57)

**Assembly result**: 23,288 bytes, compiled in 2 passes → 11 pages, 191,261 bytes (186.8 KB).
- Document class: `\documentclass[12pt]{article}` (NOT elsarticle)
- All 15 references: \bibitem{key} format, no .bib file needed
- 4 equations (ds, dg, dL, de) with \label references
- 6 tables (evaluation metrics, parameter recovery, trajectory prediction, peak velocity, classification, bifurcation, ablation, generalization)
- 0 errors, 0 undefined references on either pass
- Cross-references resolved on second pass (paper.out changed, rerun filecheck warning — normal)

**Pattern**: The assembly can be fully automated from step files without any manual LaTeX editing. The step files are Markdown with LaTeX inline math — no conversion needed beyond wrapping in document structure.
