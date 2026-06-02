# Precise Text Width Measurement for TikZ Boxes

> A technique for verifying text fits inside TikZ boxes — **before** pushing to the user.
> Developed from SynthOS Figure 1 iteration (L3 absorption boxes, 5 texts in 20-22mm boxes).

## Why

When a user says "text is outside the box", you need to **prove** whether it fits or not —
not guess. Visual inspection of a PDF is unreliable (font rendering varies).
Numerical measurement is definitive.

## Technique: `\showwidth` + `pdftotext`

### Step 1: Create a measurement test file

```latex
\documentclass{standalone}
\usepackage{xcolor,tikz}

\newlength{\tw}
\newcommand{\showwidth}[1]{%
    \settowidth{\tw}{#1}%
    #1 (\the\tw)%
}

\begin{document}
\begin{tikzpicture}
    \node[font=\sffamily\tiny\bfseries, draw] at (0,0) {\showwidth{Philosophy}};
    \node[font=\sffamily\tiny\bfseries, draw, below=5mm] at (0,0) {\showwidth{Capability}};
    % ... more text items ...
    
    % Reference box
    \draw[red, dashed] (-10mm, -5mm) rectangle (10mm, 5mm);
    \node[red, font=\tiny] at (10.5mm, 0) {20mm box};
\end{tikzpicture}
\end{document}
```

### Step 2: Compile and extract widths

```bash
pdflatex measure.tex
pdftotext measure.pdf -
```

Output will show each text with its width in points:
```
Philosophy (24.59448pt)
Capability (22.57642pt)
Standard (20.45145pt)
Task (10.59448pt)
Pattern (17.25005pt)
```

### Step 3: Calculate available space

```
Available width = box_minimum_width - 2 × inner_sep

Example:
  box_minimum_width = 20mm = 56.9pt
  inner_sep = 2pt
  available = 56.9pt - 4pt = 52.9pt
  margin_per_side = (52.9 - 24.6) / 2 = 14.15pt (= 5mm)
  → text has 60% whitespace margin → definitely fits
```

### Step 4: Determine if box is appropriate

| Margin ratio | Assessment |
|-------------|------------|
| > 40% of box width | Text fits with generous padding — **good** |
| 20-40% | Adequate — OK for dense figures |
| 10-20% | Tight — consider widening box by 2-4mm |
| < 10% | Overflow risk — **must widen box** |

### Step 5: Before/after comparison

When making size changes, always document what changed and what stayed:

| Property | Before | After | Δ |
|----------|--------|-------|---|
| Box width | 18mm (51.2pt) | 22mm (62.6pt) | +4mm |
| Font size | `\tiny` (~6pt) | `\tiny` (~6pt) | **unchanged** |
| Text max width | 24.6pt | 24.6pt | unchanged |
| Margin per side | 13.3pt | 18.9pt | +5.6pt |

This table proves to both yourself and the user that the fix was targeted.

## Real Session Example

Session from 2026-05-18, SynthOS paper Figure 1 L3:
- User: "L3 text is outside the boxes"
- Initial fix: Increased boxes 18→20mm, 6.5→7mm
- User follow-up: "Did the font increase too?"
- **We proved: font stayed `\tiny`, text measured 24.6pt in 56.9pt box = 57% margin**
- Final fix: Increased boxes further to 22×7.5mm, kept font unchanged

## When to Use

- Any time a user reports "text outside box" or "text overflow"
- After making box size changes — verify only the intended dimension changed
- Before pushing a figure update — confirm all text still fits
- When debugging layout issues between different font sizes (`\tiny` vs `\footnotesize` vs `\small`)
