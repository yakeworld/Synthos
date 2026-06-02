# Convergence Framework Architecture Diagram (TikZ)

> Phase 3 D4 enhancement for systematic review papers — reusable 3-layer architecture diagram.
> Replaces the need for a separate narrative-only convergence section with a visual architecture.

## Pattern Overview

A 3-layer TikZ diagram showing how multiple domain streams converge through shared blind spots into a unified resolution framework. Each layer is a dashed rectangle (`lbox` style) with labeled nodes inside. Arrows flow downward from domains → blind spots → resolution.

Verified in: vor-bppv-diagnosis v6 (D4 0.75→0.80, +0.05)

## Structure

```
Layer 3 (top):    Domain Streams    — 3-4 independent research domains
                      ↓ (arrows)
Layer 2 (middle): Shared Blind Spots — 3 shared limitations/gaps
                      ↓ (arrows)
Layer 1 (bottom): Convergence Resolution — standardized protocol/framework
```

## TikZ Styles

| Style name | Purpose | Visual |
|:-----------|:--------|:-------|
| `dbox` | Domain nodes | blue!10 fill, rounded corners |
| `bspot` | Blind spot nodes | yellow!15 fill, rounded corners |
| `rbox` | Resolution node | green!15 fill, rounded corners |
| `lbox` | Layer bounding box | dashed, gray!5 fill, min width 14cm |
| `myarr` | Downward arrows | thick, single-headed |
| `biarr` | Cross-blindspot arrows | dashed, red!50, double-headed |

**⚠️ CRITICAL: Do NOT use 'domain' as a TikZ style name.** `domain` conflicts with pgfplots' built-in key `domain` (used in axis plots). Use `dbox` instead. Same for `layer` → use `lbox`, `arr` → use `myarr`.

**⚠️ Global style registration**: If the document has multiple TikZ pictures using `myarr`, register it globally in the preamble:
```latex
\tikzset{myarr/.style={->, >=stealth, thick}}
```

## Template

```latex
\begin{figure}[htbp]
\centering
\resizebox{\textwidth}{!}{%
\begin{tikzpicture}[
  dbox/.style={rectangle, draw, rounded corners=2mm, minimum width=3.0cm, minimum height=0.8cm, align=center, font=\small, fill=blue!10},
  bspot/.style={rectangle, draw, rounded corners=2mm, minimum width=3.8cm, minimum height=0.7cm, align=center, font=\small, fill=yellow!15},
  rbox/.style={rectangle, draw, rounded corners=2mm, minimum width=4.5cm, minimum height=0.8cm, align=center, font=\small, fill=green!15},
  lbox/.style={rectangle, draw, dashed, rounded corners=3mm, inner sep=3mm, minimum width=14cm},
  myarr/.style={->, >=stealth, thick},
  biarr/.style={<->, >=stealth, thick, dashed, red!50},
  node distance=1.2cm and 0.5cm
]
% Layer 3: Domains (top)
\node[lbox, label={[above, font=\bfseries]Domain Streams}] (L3) at (0,0) {};
\node[dbox] (D1) at (-4.5,0) {Domain A\\Subtitle};
\node[dbox] (D2) at (0,0) {Domain B\\Subtitle};
\node[dbox] (D3) at (4.5,0) {Domain C\\Subtitle};

% Arrows downward
\draw[myarr] (D1.south) -- ++(0,-0.4) -| (-2.0,-1.2);
\draw[myarr] (D2.south) -- ++(0,-0.4) -| (0,-1.2);
\draw[myarr] (D3.south) -- ++(0,-0.4) -| (2.0,-1.2);

% Layer 2: Blind spots (middle)
\node[lbox, label={[above, font=\bfseries]Shared Blind Spots}] (L2) at (0,-2.2) {};
\node[bspot] (B1) at (-3.5,-2.2) {Blind Spot 1\\Description};
\node[bspot] (B2) at (0,-2.2) {Blind Spot 2\\Description};
\node[bspot] (B3) at (3.5,-2.2) {Blind Spot 3\\Description};

% Convergence arrows
\draw[myarr] (B1.south) -- ++(0,-0.4) -- (0,-3.8);
\draw[myarr] (B2.south) -- ++(0,-0.4) -- (0,-3.8);
\draw[myarr] (B3.south) -- ++(0,-0.4) -- (0,-3.8);

% Layer 1: Convergence Resolution (bottom)
\node[lbox, label={[above, font=\bfseries]Convergence Resolution}] (L1) at (0,-4.5) {};
\node[rbox] (R) at (0,-4.5) {Standardized Protocol\\Stage 1: A---Stage 2: B---Stage 3: C};

% Cross-links between blind spots
\draw[biarr] (B1.east) -- (B2.west);
\draw[biarr] (B2.east) -- (B3.west);

\end{tikzpicture}%
}
\caption{Convergence framework architecture. [N domain streams] converge through [N shared blind spots] into a unified [resolution framework]. The bidirectional arrows between blind spots indicate their interdependence.}
\label{fig:convergence_framework}
\end{figure}
```

## Content Customization Per Paper Type

| Paper type | Domains (Layer 3) | Blind Spots (Layer 2) | Resolution (Layer 1) |
|:-----------|:-------------------|:----------------------|:---------------------|
| Clinical diagnosis review | Physiology, Methodology, Clinical practice | Threshold heterogeneity, Temporal confounding, Validation gaps | Standardized protocol (3+ stages) |
| Technology calibration survey | Sensing hardware, Algorithms, Application | Hardware diversity, Algorithm opacity, Ground truth | Tiered calibration protocol |
| Biomarker systematic review | Mechanism, Detection, Clinical validation | Signal specificity, Cohort heterogeneity, Outcome standardization | Multi-biomarker integration pipeline |
| Cross-domain meta-analysis | Domain A, Domain B, Their intersection | Missing shared standards, Temporal/contextual confounds, Fragmented validation | Cross-domain convergence framework |

## Expected D4 Impact

| Before | After | Gain |
|:-------|:------|:-----|
| 0 Fig (review only) | +1 architecture fig | +0.04-0.06 |
| 1-2 Fig | +1 architecture fig | +0.03-0.05 |
| 3+ Fig | +1 architecture fig | +0.02-0.04 |

## Verification

After insertion, compile and verify:
```bash
pdflatex paper.tex && pdflatex paper.tex
grep 'Error' paper.log              # Should be 0 fatal errors
grep -c 'convergence_framework' paper.tex  # = 1 (label exists)
```

Common issues:
- **"Not in outer par mode"**: The figure is inside a `\paragraph{}` environment. Move figure outside the paragraph (after a blank line).
- **"domain" style conflict**: Replace `domain/.style=` with `dbox/.style=`. If the error persists, check all TikZ style names against pgfplots built-in keys.
- **Double `\end{figure}`**: `str.replace()` may have left a leftover `\end{figure}`. Verify `begin{figure}` count = `end{figure}` count.
