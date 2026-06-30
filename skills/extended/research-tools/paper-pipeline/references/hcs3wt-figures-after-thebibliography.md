# HCS-3WT Compilation Trap: Figures After thebibliography

> 2026-06-29 实战: HCS-3WT breast cancer paper had 7 figure environments AFTER `\end{thebibliography}` at line 250, causing cascade LaTeX errors: `\caption outside float` and `\begin{document} ended by \end{figure}`.

## The Problem

In the HCS-3WT paper directory at `/media/yakeworld/sda2/Synthos/outputs/papers/hcs3wt-breast-cancer/01-manuscript/hcs3wt-breast-cancer.tex`:

- Lines 184-187: Conclusion section text
- Line 188: `\begin{thebibliography}{10}`
- Line 250: `\end{thebibliography}`
- Line 252-301: 7 figure environments (fig1-fig6, including duplicates)

The figures were placed **after** the bibliography, which is wrong. In LaTeX, figures should appear **before** the bibliography in the main body. The result was:

```
Line 508: ! LaTeX Error: \caption outside float.
Line 545: ! LaTeX Error: \begin{document} ended by \end{figure}.
Line 483: Overfull \hbox (16.7591pt too wide) at lines 186-187
Line 466-479: Package natbib Warning: Citation undefined (4 zombie cites from replaced refs)
Line 570: LaTeX Warning: Float too large for page
```

## Detection

```bash
# Check: are any figure environments after thebibliography?
grep -n '\\end{thebibliography}' paper.tex
grep -n '\\begin{figure}' paper.tex
# If figure line numbers > thebibliography line number → WRONG
```

## Fix

Move all figure environments to before the `\begin{thebibliography}`. The correct structure should be:

```
...Conclusion text...
[All figure environments here]
\begin{thebibliography}{10}
...bibitems...
\end{thebibliography}
\end{document}
```

## Related Traps

1. **Same pattern in any paper**: Any time a paper has `\begin{figure}` after `\end{thebibliography}`, it will fail to compile. This is a common LLM output error — LLMs tend to append content (including figures) after the bibliography rather than integrating them into the body.
2. **Duplicate figure labels**: HCS-3WT had two figures both using `fig6_threshold_sensitivity` as the label. Check for duplicate `\label{}` assignments.
3. **Thebibliography before figures is structural, not just aesthetic**: Unlike CSS where order doesn't matter, LaTeX enforces strict document structure. Thebibliography marks the end of the main body. Everything after it (except \end{document}) is structurally invalid.

## D10a Impact

This structural error means the paper compiles to PDF but with warnings/errors. The D10a scan still passes (20 bibitems, 19 cited = 95%), but the quality review fails because the PDF may be malformed or incomplete (missing figures in output).

## HCS-3WT Additional Findings

- D10a: 95.0% (19/20, 1 orphan: Hossin2023, 4 zombies from replaced references)
- No Code/Data Availability section
- 5 sections, 10 subsections — good IMRaD structure
- 7 figures (6 unique + 1 duplicate label), 6 tables, 0 equations
- 03-code/experiments/ has run_hcs3wt.py with 394 lines — code exists but not referenced in paper
- Compilation: 17 pages, 527KB, 0 errors after moving figures
