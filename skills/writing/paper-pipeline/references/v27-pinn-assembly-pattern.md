# Minimal paper.tex Assembly — v27 Session Case Study

## Purpose

Demonstrates that `paper.tex` can be assembled with a minimal `\documentclass[12pt]{article}` template and still compile cleanly with all cross-references resolved. This is simpler than the `elsarticle` approach.

## Template Used (saccade-adaptation-pinn, Paper 57)

```latex
\documentclass[12pt]{article}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{hyperref}
\title{Physics-Informed Neural Networks for Saccade Adaptation Dynamics: A Neural ODE Approach}
\author{Synthos Research Team}
\date{\today}
\begin{document}
\maketitle
```

That's it for the preamble. All content goes between `\maketitle` and `\end{document}`.

## Result

- paper.tex: 23,288 bytes
- Pass 1: 0 errors, 11 pages generated
- Pass 2: 0 errors, cross-references resolved, 11 pages, 191,261 bytes
- 0 undefined references
- 4 numbered equations with \label
- 6 tables with \caption
- 15 \bibitem entries in thebibliography environment

## Key Design Decisions

1. **No .bib file**: All references inline in thebibliography environment. Simpler than managing external .bib.
2. **No elsarticle**: The `elsarticle` class is only needed for journal submission. For internal compilation, `article` is sufficient.
3. **No figure includes**: No actual figure files needed — just place holder text if figures are required later.
4. **Chinese comments**: All inline comments use Chinese for consistency with other Synthos papers.
5. **Section numbering**: \section, \subsection only — no \subsubsection unless needed (not needed for saccade-adaptation).
6. **Table formatting**: \begin{table}[htbp] with \centering and \begin{tabular} — no special formatting packages needed.

## When to Use elsarticle

Use `\documentclass[review,3p,twocolumn]{elsarticle}` when:
- Targeting an Elsevier journal (Computers in Biology and Medicine, etc.)
- The journal requires specific formatting (margins, author blocks, running headers)
- Submitting the final version (not for internal verification)

For all internal paper compilation and verification, `\documentclass[12pt]{article}` works.
