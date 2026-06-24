# Single-Column Layout Pitfalls (2026-06-24)

## Discovery Context

PIMA-CRISP-DM paper converted from `elsarticle[3p,twocolumn]` to `elsarticle[3p]` (single-column). Three issues surfaced:

## 1. Ablation Table Overflows Column Width

**Symptom**: `Overfull \hbox (87pt too wide) in paragraph at lines 309--319`

**Root Cause**: 7-column `{llccccc}` table in single-column format has natural width exceeding `\columnwidth`. In twocolumn mode, the narrower `\columnwidth` (~250pt) constrained the table; in single-column mode, `\columnwidth` = `\textwidth` (~520pt) is wider, but the table's natural width exceeds even that.

**Fix**: Wrap every multi-column table with `\resizebox{\columnwidth}{!}{% ... %}`:

```latex
\begin{table}
\centering
\caption{...}
\label{tab:...}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{...}
...
\end{tabular}%
}
\end{table}
```

**Checklist**:
- [ ] Every `{tabular}` environment with ≥5 columns wrapped in `\resizebox`
- [ ] `\resizebox` uses `\columnwidth` (not `\textwidth` or `\linewidth`)
- [ ] Closing `%` after `\end{tabular}` to prevent stray spaces
- [ ] No stray blank lines inside the `\resizebox{}{}` braces

## 2. Figure Width Too Large in Single Column

**Symptom**: Figures rendered at `0.95\columnwidth` appear too wide (≈175mm for elsarticle `3p`), occupying nearly full page width.

**Fix**: Reduce `\includegraphics` width for single-column:

| Figure type | Previous (twocolumn) | Single-column |
|:-----------|:--------------------|:--------------|
| ROC curves | `0.95\columnwidth`  | `0.70\columnwidth` |
| Bar charts | `0.85\columnwidth`  | `0.60\columnwidth` |
| Multi-panel | `\textwidth`        | `\textwidth` |

```latex
% Before (twocolumn, too wide in single-column)
\includegraphics[width=0.95\columnwidth]{roc_curves.pdf}

% After (single-column)
\includegraphics[width=0.70\columnwidth]{roc_curves.pdf}
```

## 3. Table Column Header Overflow With Added Metrics

**Symptom**: Adding a column (e.g., F1-Score) to the comparison table causes overflow even with `\resizebox`.

**Fix**:
- Shorten column headers: "Claimed Accuracy" → "Accuracy", "Leakage Prevention" → "Leakage"
- Use `—` (em dash) for N/A values instead of "No" or "None"
- Use `\small` or `\footnotesize` before the tabular
- Keep `\resizebox{\columnwidth}{!}` as final safety net

## 4. `table*` vs `table` in Single-Column

In `elsarticle[3p, twocolumn]`, `table*` spans both columns. In `elsarticle[3p]` (single-column), `table*` is identical to `table`. Change `table*` to `table` for clarity (optional, no functional difference).

## Detection Commands

```bash
# Check for overfull hboxes in compilation log
strings paper.log | grep "Overfull.*hbox"

# Check figure widths in paper.tex
grep -n 'includegraphics' paper.tex

# Check tabulars without resizebox protection
grep -c '\\begin{tabular}' paper.tex
grep -c '\\resizebox' paper.tex
```
