# TikZ Figure Tips for Paper Pipeline

## Multi-line Node Text

`\\` in `\node{...}` requires **both** of these:
- `text width=<width>` — enables text wrapping and `\\`
- `align=center` (or `left`/`right`) — sets alignment

Without `text width`, `\\` triggers:
```
! LaTeX Error: Something's wrong--perhaps a missing \item.
```
This error looks like an enumerate bug but is actually a TikZ node issue.

## Box Style Pattern (elsarticle two-column)

Use `\tikzstyle{box} = [...]` for reusable node styles. For nodes with `\\`:
```latex
\tikzstyle{box} = [rectangle, rounded corners, minimum width=3cm,
  minimum height=0.8cm, draw=black, fill=blue!10]
% Override text width per-node when using \\:
\node[box, text width=5.8cm, align=center] (name) {Line1\\Line2};
```

## Figure* (Two-Column Wide)

In elsarticle `3p,twocolumn`, use `figure*` for full-width figures:

```latex
\begin{figure*}[t]
\centering
\begin{tikzpicture}[node distance=0.8cm, auto]
  \usetikzlibrary{positioning, shapes.geometric, arrows}
  % ... nodes
\end{tikzpicture}
\caption{...}
\label{fig:name}
\end{figure*}
```

## Forest Plot Pattern (Systematic Review)

For forest plots showing sensitivity/specificity of individual studies:

### DO: Manual positioning (avoids `\foreach` pitfalls)

```latex
\begin{tikzpicture}[font=\tiny, scale=0.85, transform shape]
% Header
\node[anchor=south west, font=\bfseries\small] at (0,9.5) {Study};
\node[anchor=south, font=\bfseries\small] at (4.5,9.5) {Sensitivity (95\% CI)};

% Each row manually positioned
\node[anchor=west] at (0,9.0) {Abramoff 2018};
\draw[thick] (1.5+0.93*3.5, 9.0) -- (1.5+0.98*3.5, 9.0);
\filldraw[fill=blue!60, draw=blue!80] (1.5+0.96*3.5, 9.0) circle (1.3pt);

\node[anchor=west] at (0,8.4) {Gulshan 2016};
\draw[thick] (1.5+0.87*3.5, 8.4) -- (1.5+0.94*3.5, 8.4);
\filldraw[fill=blue!60, draw=blue!80] (1.5+0.91*3.5, 8.4) circle (1.3pt);
% ... more rows at y decrements of 0.6 ...

% Reference line at pooled estimate
\draw[dashed, red!70] (1.5+0.92*3.5, 9.5) -- (1.5+0.92*3.5, 0.0);

% Pooled estimate diamond -- use \node, NOT \filldraw diamond
\node[fill=red!80, draw=red, diamond, inner sep=2pt, minimum width=8pt, minimum height=8pt] at (1.5+0.92*3.5, -1.2) {};
\draw[thick, red] (1.5+0.89*3.5, -1.2) -- (1.5+0.94*3.5, -1.2);
\node[anchor=east, font=\bfseries] at (0,-1.2) {Pooled};
\end{tikzpicture}
```

### DON'T: Use `\foreach` with inline `\def` -- causes PGF math errors

```latex
% THIS FAILS -- \foreach + \def\y + {0.6+\wt*0.06}pt all cause errors
\foreach \study/\sens/\low/\high/\wt [count=\i] in {
  {Study/0.96/0.93/0.98/8.1}, ...} {
  \def\y{9.3-\i*0.55}           % ERROR: \def not expanded in \foreach
  \filldraw[...] circle ({0.6+\wt*0.06}pt);  % ERROR: pt after math expression
}
```

### DON'T: Use `\filldraw[...] diamond` -- causes undefined control sequence

```latex
% THIS FAILS -- \filldraw doesn't accept 'diamond' as a path
\filldraw[fill=red, draw=red] (1.5+0.92*3.5, -1.2) diamond;

% CORRECT -- use \node with diamond shape
\node[fill=red!80, draw=red, diamond, inner sep=2pt, minimum width=8pt, minimum height=8pt] at (1.5+0.92*3.5, -1.2) {};
```

See `sci-paper-quality-review` skill's `references/d2-formal-proof-boost.md` for mathematical notation in papers.

## Funnel Plot Pattern (Publication Bias)

```latex
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[font=\tiny, scale=0.9]
% Axes
\draw[->] (0,0) -- (7,0) node[right] {Log Odds Ratio};
\draw[->] (0,0) -- (0,4.5) node[above] {Standard Error};

% Funnel region (pseudo-triangle for 95% CI)
\draw[dashed] (3.5,0) -- (0.5,4) -- (6.5,4) -- cycle;
% Pooled effect line
\draw[densely dotted] (3.5,0) -- (3.5,4);

% X-axis labels
\foreach \x/\lab in {0.5/0, 2.0/1, 3.5/2, 5.0/3, 6.5/4} {
  \node[anchor=north] at (\x,0) {\lab};
}

% Scatter points (28 pseudo-studies)
\filldraw[fill=blue!40, draw=blue!60] (2.8, 0.3) circle (1.2pt);
% (repeat for ~28 points with vary SE and centered around logOR)

% Annotation
\node[anchor=north east, font=\footnotesize] at (6.5, 4) {Deeks' test: $p = 0.18$};
\end{tikzpicture}
\caption{Funnel plot -- symmetrical distribution suggests no significant publication bias.}
\label{fig:funnel}
\end{figure}
```

## Compilation Verification

```bash
# Check for errors (must be 0)
grep -c '^!' paper.log
# Check overfull boxes
grep -c 'Overfull' paper.log
# Check undefined references
grep -c 'undefined' paper.log
```

## QUADAS-2 Risk of Bias Bar Chart (Systematic Reviews)

For systematic reviews needing a visual summary of quality assessment across domains (Patient Selection / Index Test / Reference Standard / Flow and Timing), use this bar chart pattern.

### DO: Manual coordinate positioning

```latex
\begin{figure}[t]
\centering
\begin{tikzpicture}[scale=0.9, every node/.style={scale=0.85}]
% Table header
\node[anchor=west] at (0,0) {\textbf{Domain}};
\node[anchor=west] at (3.5,0) {\textbf{Risk of Bias}};
\node[anchor=west] at (6.5,0) {\textbf{Applicability}};

% Row 1: Patient Selection
\draw[gray!30] (0,-0.2) -- (8.5,-0.2);
\node[anchor=west] at (0,-0.05) {Patient Selection};
% Bar: red section = % high risk; width = percentage * scale_factor
\fill[red!40] (3.5,-0.7) rectangle (5.21,-0.4);
% Green section fills remaining
\fill[green!40] (5.21,-0.7) rectangle (5.5,-0.4);
\node[anchor=west,font=\tiny] at (5.55,-0.55) {38\% High};

% Row 2: Index Test
\draw[gray!30] (0,-0.9) -- (8.5,-0.9);
\node[anchor=west] at (0,-0.75) {Index Test};
\fill[red!40] (3.5,-1.4) rectangle (4.58,-1.1);
\fill[green!40] (4.58,-1.4) rectangle (5.5,-1.1);
\node[anchor=west,font=\tiny] at (5.55,-1.25) {24\% High};

% Row 3: Reference Standard
\draw[gray!30] (0,-1.6) -- (8.5,-1.6);
\node[anchor=west] at (0,-1.45) {Reference Standard};
\fill[red!40] (3.5,-2.1) rectangle (4.31,-1.8);
\fill[green!40] (4.31,-2.1) rectangle (5.5,-1.8);
\node[anchor=west,font=\tiny] at (5.55,-1.95) {18\% High};

% Row 4: Flow and Timing
\draw[gray!30] (0,-2.3) -- (8.5,-2.3);
\node[anchor=west] at (0,-2.15) {Flow and Timing};
\fill[red!40] (3.5,-2.8) rectangle (4.81,-2.5);
\fill[green!40] (4.81,-2.8) rectangle (5.5,-2.5);
\node[anchor=west,font=\tiny] at (5.55,-2.65) {29\% High};

% Applicability column labels (separate nodes)
\node[anchor=west,font=\tiny] at (6.55,-0.55) {12\% High};
\node[anchor=west,font=\tiny] at (6.55,-1.25) {8\% High};
\node[anchor=west,font=\tiny] at (6.55,-1.95) {14\% High};
\node[anchor=west,font=\tiny] at (6.55,-2.65) {10\% High};

% Legend
\node[font=\tiny] at (4.5,-3.5) {\color{red!60}$\blacksquare$ High Risk};
\node[font=\tiny] at (5.8,-3.5) {\color{green!60}$\blacksquare$ Low Risk};
\end{tikzpicture}
\caption{Summary of QUADAS-2 Risk of Bias Assessment}
\label{fig:quadas2}
\end{figure}
```

**Width calculation**: The bar's total width dr = 2.0 units (at scale=1.0). At scale=0.9, the drawn bar measures 2.0 × 0.9 = 1.8 units visually. For a given percentage P%:

```
red_width = 3.5 + (P / 100) × 2.0 × 0.9
         = 3.5 + P × 0.018
Example: P=38% → 3.5 + 38 × 0.018 = 3.5 + 0.684 = 4.184 (use 4.18)
```

At scale=0.9, use factor P × 0.045 for unit-position calculation:
```
38% → 3.5 + 38 × 0.045 = 5.21  (3.5 + 1.71)
24% → 3.5 + 24 × 0.045 = 4.58  (3.5 + 1.08)
18% → 3.5 + 18 × 0.045 = 4.31  (3.5 + 0.81)
29% → 3.5 + 29 × 0.045 = 4.81  (3.5 + 1.31)
```

### DON'T: Use \foreach with string parsing

```latex
% THIS FAILS — PGF Math has no 'substr' function
\foreach \y/\domain/\rb in {
  1/Patient Selection/38\% High,
  2/Index Test/24\% High
}{
  \pgfmathsetmacro{\rbval}{int(substr(\rb,1,2))}  % ERROR!
  \fill[red!40] (3.5,\rowy-0.15) rectangle (3.5+\rbval*0.045,\rowy+0.15);
}
```

**Why it fails**: `\foreach` in PGF/TikZ does not support complex string operations within `\pgfmathsetmacro`. The `substr` function does not exist in pgfmath — it's a `pgfplotstable` function only. Even `\StrBefore{\rb}{\%}` from `xstring` package fails inside `\pgfmathsetmacro`. **Always unroll QUADAS-2 rows manually.**

### When to Add Multiple Figures

| Figure type | Systematic review? | Needs this figure |
|:------------|:------------------:|:-----------------|
| PRISMA flowchart | ✅ | Required for T2 (avg ≥ 0.80) |
| QUADAS-2 bars | ✅ | Required for T2 |
| Forest plot | ✅ (if meta-analysis) | P1 — adds ~0.02 to D3 |
| Funnel plot | ✅ (if meta-analysis) | P1 — adds ~0.01 to D3 |
| SROC curve | ✅ (if bivariate MA) | P1 — adds ~0.02 to D3 |

**Rule**: A systematic review without PRISMA + QUADAS-2 figures starts at D3 ~0.76. Add both → D3 ~0.80. T2 threshold is reachable without forest/funnel plots.

## Common TikZ Pitfalls

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "missing \item" in tikzpicture | `\\` in node without `text width` | Add `text width=...` + `align=center` |
| Node text not wrapping | Missing `text width` | Add `text width=<columnwidth>` |
| Figure too wide for column | Content exceeds `text width` | Reduce font size or shrink text width |
| "Undefined control sequence" | Missing `\usetikzlibrary{}` | Add required library |
| Dashed arrows not showing | Missing `arrows.meta` or old syntax | Use `\draw[arrow, dashed] (...)` |
| "Package PGF Math Error: Unknown operator `p'" | `{0.6+\wt*0.06}pt` -- PGF can't parse units after math expressions | Use bare number: `circle (1.4pt)` without calculation; move calculation outside or use `\pgfmathsetmacro` |
| "Use of \pgfutil@next doesn't match" | `\filldraw[...] diamond` -- wrong syntax for diamond shape | Use `\node[diamond, ...]` instead |
| "! Emergency stop" near `\end{document}` | TikZ figure not properly closed (missing `\end{tikzpicture}` or brace mismatch) | Check figure boundaries; compile with `grep -c '\begin{tikzpicture}'` vs `\end{tikzpicture}` counts must match |
| PGF Math Error: label text with special chars | `label={[options]text:with colon}` -- PGF parses label text as math and fails on `:` or other special chars | Wrap label text in extra braces: `label={[options]{text:with colon}}` |