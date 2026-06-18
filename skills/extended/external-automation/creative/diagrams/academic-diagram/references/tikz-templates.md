# TikZ Templates

Three base templates for the three archetypes. Copy-paste into a `.tex` file,
compile with `pdflatex`, then `\includegraphics` into the main paper.

---

## ARCH: Architecture Diagram (3-Layer Stacked)

For system architecture with 3-4 layers stacked vertically.

```latex
\documentclass[tikz,border=1pt]{standalone}
\usepackage{xcolor,tikz}
\usetikzlibrary{shapes,arrows,positioning}

% Choose palette: Nature 6-color or NMI pastel
\definecolor{c1}{HTML}{0072B2}  % Layer 3 (top)
\definecolor{c2}{HTML}{009E73}  % Layer 2 (middle)
\definecolor{c3}{HTML}{0072B2}  % Layer 1 (bottom)

\begin{document}
\begin{tikzpicture}[
    every node/.style={font=\sffamily},
    box/.style={draw=#1, fill=#1!10, text=#1!90!black, minimum width=16mm,
                minimum height=5mm, rounded corners=1mm, font=\sffamily\footnotesize\bfseries,
                align=center, inner sep=2pt, line width=0.8pt},
    layer/.style={draw=black!25, rounded corners=2.5mm, fill=black!2, line width=0.7pt},
    lbl/.style={text=black!55, font=\sffamily\small\bfseries, align=center},
    cap/.style={text=black!40, font=\sffamily\tiny, align=center},
]

%%% CONFIGURE: Layer positions %%%
% Layer 3 (top):   y_center = Y3,  bg from Y3_start to Y3_end
% Layer 2 (middle): y_center = Y2,  bg from Y2_start to Y2_end  
% Layer 1 (bottom): y_center = Y1,  bg from Y1_start to Y1_end
% Inter-layer: gap between bg_end(L_N) and bg_start(L_{N-1}) ≥ 0.5
%
% Example coordinate plan (for 3 layers, ~10 total height):
%   Layer 3 bg: (-4.5, 7.5) to (4.5, 11.0)  → top
%   Layer 2 bg: (-4.5, 3.2) to (4.5, 6.8)    → middle  
%   Layer 1 bg: (-4.5, -1.2) to (4.5, 2.5)   → bottom
%   Gaps: L3bg_bottom(6.8) - L2bg_top(7.5) = 0.7 ✓
%         L2bg_bottom(2.5) - L1bg_top(3.2) = 0.7 ✓

%%% Layer 3 (top) %%%
\draw[layer] (-4.5,Y3_start) rectangle (4.5,Y3_end);
\node[lbl] at (0,Y3_end-0.4) {Layer 3 Title};
% Boxes (horizontal, ≤ 4 per row)
\node[box=c1] (a) at (-2.0,Y3_center) {Box A};
\node[box=c1] (b) at (0,Y3_center) {Box B};
\node[box=c1] (c) at (2.0,Y3_center) {Box C};
\draw[->, c1!50, >=stealth, line width=0.6pt, shorten >=2pt] (a) -- (b);
\draw[->, c1!50, >=stealth, line width=0.6pt, shorten >=2pt] (b) -- (c);
\node[cap] at (0,Y3_start+0.3) {Caption text};

%%% Layer 2 (middle) %%%
\draw[layer] (-4.5,Y2_start) rectangle (4.5,Y2_end);
\node[lbl] at (0,Y2_end-0.4) {Layer 2 Title};
% Two rows of boxes
\node[box=c2] at (-2.0,Y2_center+0.5) {Row1 A};
\node[box=c2] at (0,Y2_center+0.5) {Row1 B};
\node[box=c2] at (2.0,Y2_center+0.5) {Row1 C};
\node[box=c2] at (-1.0,Y2_center-0.5) {Row2 X};
\node[box=c2] at (1.0,Y2_center-0.5) {Row2 Y};
\draw[->, c2!50, >=stealth, line width=0.5pt, shorten >=2pt] (...) -- (...);
\node[cap] at (0,Y2_start+0.3) {Caption text};

%%% Layer 1 (bottom) %%%
\draw[layer] (-4.5,Y1_start) rectangle (4.5,Y1_end);
\node[lbl] at (0,Y1_end-0.4) {Layer 1 Title};
% Two rows with horizontal bus
\node[box=c3] at (-2.0,Y1_center+0.5) {Atom 1};
\node[box=c3] at (0,Y1_center+0.5) {Atom 2};
\node[box=c3] at (2.0,Y1_center+0.5) {Atom 3};
\node[box=c3] at (-1.0,Y1_center-0.5) {Atom 4};
\node[box=c3] at (1.0,Y1_center-0.5) {Atom 5};
\draw[c3!50, line width=0.5pt] (-3.5,Y1_center) -- (3.5,Y1_center);
\node[cap] at (0,Y1_start+0.3) {Caption text};

%%% Inter-layer arrows %%%
\draw[->, black!30, >=stealth, line width=0.7pt] (0,Y1_end) -- (0,Y2_start);
\draw[->, black!30, >=stealth, line width=0.7pt] (0,Y2_end) -- (0,Y3_start);

%%% Title (above top layer) %%%
\node[text=black, font=\sffamily\bfseries\large] at (0,Y3_end+0.7) {Figure Title};

\end{tikzpicture}
\end{document}
```

**Key parameters to configure:**
- `Y1_start, Y1_center, Y1_end` — bottom layer Y-coordinates
- `Y2_start, Y2_center, Y2_end` — middle layer Y-coordinates
- `Y3_start, Y3_center, Y3_end` — top layer Y-coordinates
- `c1, c2, c3` — color per layer (Nature palette)
- Box names, labels, captions
- Inter-layer arrow paths

---

## PIPE: Pipeline/Flow Diagram (Horizontal)

For horizontal pipeline/sequence flow with ≤8 elements.

```latex
\documentclass[tikz,border=1pt]{standalone}
\usepackage{xcolor,tikz}
\usetikzlibrary{shapes,arrows}

\definecolor{c1}{HTML}{0072B2}
\definecolor{c2}{HTML}{009E73}
\definecolor{c3}{HTML}{CC79A7}
\definecolor{c4}{HTML}{E69F00}
\definecolor{c5}{HTML}{D55E00}
\definecolor{c6}{HTML}{999999}

\begin{document}
\begin{tikzpicture}[
    every node/.style={font=\sffamily},
    gate/.style={draw=#1, fill=#1!12, text=#1!95!black, minimum width=19mm,
                 minimum height=8mm, rounded corners=1.5mm, font=\sffamily,
                 align=center, inner sep=1.5pt, line width=1.2pt},
]

%%% Compute gate positions %%%
% Total width: N * gate_W + (N-1) * gap
% N=6, gate_W=21mm (center spacing), total=126mm = ~358pt
%
% Values in cm: gate 1 at 0, gate 2 at 2.1, gate 3 at 4.2, etc.
% For N gates: centers at x = 0, spacing, 2*spacing, ..., (N-1)*spacing

%%% Draw arrows FIRST (z-order: behind gates) %%%
\foreach \i in {1,...,5} {
    \draw[->, black!40, >=stealth, line width=0.8pt, shorten >=1.5pt, shorten <=1.5pt]
        ({(\i-1)*spacing + gate_half + 0.1}, 0) -- ({(\i)*spacing - gate_half - 0.1}, 0);
}

%%% Gates %%%
\node[gate=c1] (g1) at (0,0) {\textbf{G1}\\[-2pt]\footnotesize Name};
\node[text=black!80, font=\sffamily\bfseries\tiny, align=center] at (0,-0.85) {Outcome 1};

\node[gate=c2] (g2) at (spacing,0) {\textbf{G2}\\[-2pt]\footnotesize Name};
\node[text=black!80, font=\sffamily\bfseries\tiny, align=center] at (spacing,-0.85) {Outcome 2};

% ... repeat for remaining gates ...

%%% Title %%%
\node[text=black, font=\sffamily\bfseries\small] at (total_center,0.95) {Figure Title};

%%% Critical gate highlight (if needed) %%%
% For critical gates, use a ★ marker and red color
% \node[text=c5, font=\sffamily\tiny\bfseries] at (critical_x,-1.2) {★ Critical};

\end{tikzpicture}
\end{document}
```

**Key parameters to configure:**
- `spacing` — center-to-center distance between gates (e.g., 2.1cm)
- `gate_half` — half gate width for arrow offset (e.g., 1.0cm for 2cm gates)
- `N` — number of gates
- `c1...cN` — colors per gate (from Nature palette)
- Gate names, outcomes
- Title text

---

## PIPEx: Pipeline with Sub-Boxes (Complex Pipeline)

For research methodology pipelines where each stage has sub-components (methods, sub-tasks, data flows). Each stage has a main gate at y=0, sub-boxes in rows below, method labels, and top-annotation labels for data flow. Supports a feedback loop/iteration path.

**Use with xelatex when Chinese text is needed.**

```latex
\documentclass[tikz,border=1pt]{standalone}
\usepackage{xcolor,tikz,amsmath}
\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont{Noto Sans CJK SC}
\setCJKsansfont{Noto Sans CJK SC}
\usetikzlibrary{shapes,arrows,positioning}

% Nature 6-color palette (color-blind safe)
\definecolor{nat_blue}{HTML}{0072B2}
\definecolor{nat_green}{HTML}{009E73}
\definecolor{nat_orange}{HTML}{E69F00}
\definecolor{nat_pink}{HTML}{CC79A7}
\definecolor{nat_brown}{HTML}{D55E00}
\definecolor{nat_gray}{HTML}{999999}

\begin{document}
\begin{tikzpicture}[
    every node/.style={font=\sffamily},
    stage/.style={draw=#1, fill=#1!10, text=#1!95!black, minimum width=34mm,
                  minimum height=9mm, rounded corners=1.5mm, font=\sffamily\bfseries\small,
                  align=center, inner sep=2pt, line width=1.0pt},
    subbox/.style={draw=#1!60!black, fill=#1!6, text=#1!95!black, minimum width=30mm,
                   minimum height=6mm, rounded corners=0.8mm, font=\sffamily\tiny,
                   align=center, inner sep=1.5pt, line width=0.5pt},
    method/.style={draw=none, text=#1!75!black, font=\sffamily\scriptsize\itshape,
                   align=center},
    arr/.style={->, black!35, >=stealth, line width=0.8pt, shorten >=2pt, shorten <=2pt},
    lbl/.style={text=black!50, font=\sffamily\fontsize{6}{7}\selectfont\bfseries, align=center},
    tag/.style={text=black!40, font=\sffamily\fontsize{5}{6}\selectfont, align=center},
]

% ========== Stage positions ==========
\def\figSpacing{42mm}         % Center-to-center between stages
\def\figSubRowA{2.2}          % Sub-box Y (row 1)
\def\figSubRowB{3.7}          % Sub-box Y (row 2)
\def\figMethodRow{5.0}        % Method label Y
\def\figLblRow{6.5}           % Bottom label Y

% ========== Draw connecting arrows FIRST (z-order: behind) ==========
\foreach \i in {1,...,3} {
    \draw[arr, black!25, line width=0.7pt]
        ({\i*\figSpacing - 17mm - 0.1cm}, 0) -- ({\i*\figSpacing - 17mm + 0.1cm}, 0);
}

% ========== Stage 1 (Blue) ==========
\node[stage=nat_blue] at (0,0) {Stage 1\\Title};
\node[subbox=nat_blue] at (0,-\figSubRowA) {Sub A\\detail};
\node[subbox=nat_blue] at (0,-\figSubRowB) {Sub B\\detail};
\node[method=nat_blue] at (0,-\figMethodRow) {Method label};
\node[lbl] at (0,-\figLblRow) {Category\\label};

% ========== Stage 2 (Green) ==========
\node[stage=nat_green] at (\figSpacing,0) {Stage 2\\Title};
\node[subbox=nat_green] at (\figSpacing,-\figSubRowA) {Sub A\\detail};
\node[subbox=nat_green] at (\figSpacing,-\figSubRowB) {Sub B\\detail};
\node[method=nat_green] at (\figSpacing,-\figMethodRow) {Method label};
\node[lbl] at (\figSpacing,-\figLblRow) {Category\\label};

% ========== Stage 3 (Orange) ==========
\node[stage=nat_orange] at ({2*\figSpacing},0) {Stage 3\\Title};
\node[subbox=nat_orange] at ({2*\figSpacing},-\figSubRowA) {Sub A\\detail};
\node[subbox=nat_orange] at ({2*\figSpacing},-\figSubRowB) {Sub B\\detail};
\node[method=nat_orange] at ({2*\figSpacing},-\figMethodRow) {Method label};
\node[lbl] at ({2*\figSpacing},-\figLblRow) {Category\\label};

% ========== Stage 4 (Pink) ==========
\node[stage=nat_pink] at ({3*\figSpacing},0) {Stage 4\\Title};
\node[subbox=nat_pink] at ({3*\figSpacing},-\figSubRowA) {Sub A\\detail};
\node[subbox=nat_pink] at ({3*\figSpacing},-\figSubRowB) {Sub B\\detail};
\node[method=nat_pink] at ({3*\figSpacing},-\figMethodRow) {Method label};
\node[lbl] at ({3*\figSpacing},-\figLblRow) {Category\\label};

% ========== Top annotations: data flow labels ==========
\node[tag, text=nat_blue!60] at (0,{0+0.95}) {Data In A};
\node[tag, text=nat_green!60] at (\figSpacing,{0+0.95}) {Data In B};
\node[tag, text=nat_orange!60] at ({2*\figSpacing},0.95) {Data In C};
\node[tag, text=nat_pink!60] at ({3*\figSpacing},0.95) {Data Out};

% ========== Feedback loop (dashed back-arrow) ==========
\draw[->, nat_brown!40, dashed, >=stealth, line width=0.5pt, rounded corners=3pt]
    ({3*\figSpacing + 17mm + 0.2cm}, -1.2) -- 
    ({3*\figSpacing + 17mm + 0.6cm}, -1.2) --
    ({3*\figSpacing + 17mm + 0.6cm}, 1.2) --
    ({0 - 17mm - 0.6cm}, 1.2) --
    ({0 - 17mm - 0.2cm}, 1.2);
\node[nat_brown!50, font=\sffamily\fontsize{5}{6}\selectfont, align=center] 
    at ({1.5*\figSpacing + 17mm + 0.4cm}, 1.5) {Iteration\\Loop};

% ========== Figure title ==========
\node[text=black, font=\sffamily\bfseries\normalsize] at ({1.5*\figSpacing}, 2.8) 
    {Figure Title};

% ========== Subtitle ==========
\node[text=black!50, font=\sffamily\small\itshape] at ({1.5*\figSpacing}, 2.2) 
    {Context $\cdot$ Keywords $\cdot$ Notes};

\end{tikzpicture}
\end{document}
```

**Key parameters to configure:**
- `\figSpacing` — distance between stage centers (42mm for double column, 25mm for single)
- `\figSubRowA`, `\figSubRowB` — Y-offsets for sub-box rows below each stage
- `\figMethodRow`, `\figLblRow` — Y-offsets for method and category labels
- Stage count: 4 stages shown; extend with Stage 5+ by adding `{4*\figSpacing}`, etc.
- Colors: use Nature 6-color palette; assign one per stage
- N=stages - 1 arrows in \foreach; update if stages change
- Feedback loop coordinates assume 4 stages; adjust if more/fewer
- For CJK: requires xelatex + xeCJK + Noto Sans CJK SC (see academic-diagram CJK section)

---

## TRAJ: Trajectory/Evolution Plot (XY)

For score-vs-cycle, performance-vs-time plots with annotation markers.

Use **pgfplots** package. Requires TikZ + pgfplots.

```latex
\documentclass[tikz,border=2pt]{standalone}
\usepackage{xcolor,tikz,pgfplots}
\pgfplotsset{compat=1.18}

\definecolor{nat_blue}{HTML}{0072B2}
\definecolor{nat_orange}{HTML}{E69F00}

\begin{document}
\begin{tikzpicture}
\begin{axis}[
    width=12cm, height=6cm,
    xlabel={X-axis Label},
    ylabel={Y-axis Label},
    xmin=0, xmax=50,
    ymin=0.7, ymax=1.0,
    xtick={0,10,20,30,40,50},
    ytick={0.70,0.75,0.80,0.85,0.90,0.95,1.00},
    grid=major,
    grid style={black!10, line width=0.3pt},
    tick label style={font=\sffamily\footnotesize},
    label style={font=\sffamily\small},
    legend style={font=\sffamily\footnotesize, draw=none, fill=none},
    axis line style={black!60, line width=0.8pt},
]

%%% Main curve %%%
\addplot[nat_blue, line width=1.5pt, mark=*]
    coordinates {
        (0, 0.850)
        (5, 0.880)
        (10, 0.920)
        % ... add more points ...
        (42, 0.975)
    };
\addlegendentry{Legend Entry}

%%% Milestone annotations %%%
% \node[nat_blue, font=\sffamily\tiny] at (axis cs:10,0.920) {v3.0};
% \draw[dashed, black!30, line width=0.4pt] (axis cs:10,0.70) -- (axis cs:10,0.920);

%%% Absorption markers (optional) %%%
% \node[nat_orange, font=\sffamily\tiny] at (axis cs:12,0.93) {★ Absorption};

\end{axis}
\end{tikzpicture}
\end{document}
```
