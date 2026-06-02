---
name: academic-diagram
description: >-
  Submission-grade Nature/CNS journal figure creation for architecture diagrams,
  pipeline flowcharts, system schematics, and evolution/growth trajectory plots.
  Uses TikZ with Nature-style white background, high-contrast palette, and
  publication-standard dimensions. Covers: figure contract → archetype →
  layout → color → render → verify. Not for data plots (bar, heatmap, trend)
  — use nature-figure skill for those.
version: 1.3.0
author: Absorbed from nature-figure (Yuan Yizhe, SJTU) + architecture-diagram (Cocoon AI) + SynthOS experience
license: MIT
dependencies: [pdflatex, xcolor, tikz]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [academic, diagram, Nature, TikZ, figure, schematic, pipeline, architecture]
    related_skills: [nature-figure, architecture-diagram, excalidraw]
---

# Academic Diagram Skill

⚠️ **LOAD THIS SKILL BEFORE ANY FIGURE OPERATION**
Including iteration, modification, or resizing of existing figures. The user
will explicitly correct: *"作图应该调用技能去完成的"* if you skip this step.
Run `skill_view("academic-diagram")` before touching any `.tex` figure code.

Create high-quality, publication-ready system architecture diagrams and pipeline
flowcharts for Nature/CNS/SCI journal papers. Uses TikZ with Nature-style
white-background, high-contrast, color-blind-safe aesthetic.

**Design philosophy:** Every figure starts from a claim, not from a template.
Establish the figure contract before writing a single line of TikZ code.

## Scope

**Best suited for:**
- System architecture diagrams (CNS-style, 3-layer stacked or horizontal)
- Pipeline/flowchart diagrams (horizontal gates, sequence flows)
- Evolution trajectory plots (score vs. cycle, with annotation markers)
- Any white-background, box+arrow schematic for academic papers
- Multi-layer composite figures with consistent horizontal styling

**Look elsewhere first for:**
- Statistical data plots (bar, heatmap, trend) → use `nature-figure` (matplotlib/ggplot2)
- Dark-themed cloud/infra diagrams → use `architecture-diagram`
- Hand-drawn whiteboard sketches → use `excalidraw`
- Video/animated explainers → use `manim-video`

## Workflow

### Step 0: Figure Contract (MANDATORY — do not skip)

Before plotting, establish the contract. Write this in your response:

```text
Core conclusion:
Figure archetype: [architecture | pipeline | trajectory | mixed]
Target journal/output:
Final size (width × height): [89mm single | 183mm double | custom]
Panel map:
  - [panel A description]
  - [panel B description]
Evidence hierarchy:
  - hero panel:
  - supporting panels:
Reviewer risk:
```

### Step 1: Archetype Selection

| Archetype | Description | Layout Strategy |
|-----------|-------------|-----------------|
| `architecture` | Multi-layer system design | Vertical stack, 3-4 layers, ≤4 elements per row |
| `pipeline` | Horizontal flow/sequence gates | Single row, ≤8 elements, outcome text below |
| `trajectory` | Growth/progress over time | XY plot with markers and annotations |
| `mixed` | Schematic-led composite | Schematic 45-60% height + supporting panels |

**For architecture archetype:** Use `references/tikz-templates.md` → `ARCH` base.
**For pipeline archetype:** Use `references/tikz-templates.md` → `PIPE` base.
**For trajectory archetype:** Use `references/tikz-templates.md` → `TRAJ` base.

### Step 2: Layout Planning

#### Multi-Layer Spacing Algorithm (for stacked architecture)

1. **Compute each layer's Y-extent**: Find min and max y of all visible elements
2. **Add padding**: 0.5-0.8 units above and below elements within each layer
3. **Check layer-to-layer gaps**: 
   - `L1_element_top - L2_element_bottom ≥ 1.0`
   - `L1_bg_top - L2_bg_bottom ≥ 0.5` (for background rectangles)
4. **Aspect ratio check**:
   - Calculate: `scaled_h = fig_h * (target_w / fig_w)`
   - Target: `scaled_h ≤ 0.5\textheight` (~340pt for letter, 0.75in margins)
   - If too tall: widen layout or split into two figures
5. **Consistency rule**: All layers must use the same visual style (same box shape, same font, same spacing rhythm)

#### Pipeline Spacing Algorithm (for horizontal flow)

1. **Element count**: N gates
2. **Gate width**: 18-21mm each
3. **Gap between gates**: 2-5mm
4. **Total width**: `N × gate_W + (N-1) × gap`
5. **Fit in column**: Single column = max 89mm width. If total > 89mm, use double column (183mm) or reduce gate width

### Step 3: Color Palette

Use **one neutral family + one signal family + one accent family** per figure.

#### Nature-Approved 6-Color Palette (Color-Blind Safe)

| Name | Hex | Use | Fill/Text Rule |
|------|-----|-----|----------------|
| Blue | `#0072B2` | Primary/hero method | `fill=#0072B2!10, text=#0072B2!95!black` |
| Orange | `#E69F00` | Secondary method | `fill=#E69F00!10, text=#E69F00!95!black` |
| Green | `#009E73` | Positive/improvement | `fill=#009E73!10, text=#009E73!95!black` |
| Pink | `#CC79A7` | Highlight/accent | `fill=#CC79A7!10, text=#CC79A7!95!black` |
| Brown | `#D55E00` | Baseline/reference | `fill=#D55E00!10, text=#D55E00!95!black` |
| Gray | `#999999` | Neutral/background | `fill=#999999!10, text=#999999!95!black` |

**Critical rule:** Always use `fill=COLOR!10` to `COLOR!15` + `text=COLOR!90!black` to `COLOR!95!black` for maximum contrast. Never use white text on dark fills for academic figures — that's for presentation slides. Light fill + dark text is Nature/CNS standard.

#### NMI Pastel Family (for dense multi-panel)

| Name | Hex | Use |
|------|-----|-----|
| Blue main | `#0F4D92` | Hero method |
| Blue sec. | `#3775BA` | Second method |
| Teal | `#42949E` | Accent |
| Violet | `#9A4D8E` | Accent |
| Neutral | `#767676` | Background |

#### TikZ Color Definitions

```latex
% Nature 6-color palette (color-blind safe)
\definecolor{nat_blue}{HTML}{0072B2}
\definecolor{nat_orange}{HTML}{E69F00}
\definecolor{nat_green}{HTML}{009E73}
\definecolor{nat_pink}{HTML}{CC79A7}
\definecolor{nat_brown}{HTML}{D55E00}
\definecolor{nat_gray}{HTML}{999999}

% Box style: light fill + dark text = maximum contrast
% draw=nat_blue, fill=nat_blue!10, text=nat_blue!90!black
```

### Step 4: Render

### CJK / Chinese Text Support

When rendering diagrams with Chinese/CJK text (e.g. for Chinese SCI journals, NSFC applications, or bilingual figures):

**Compiler requirement:** Use **xelatex**, not pdflatex. pdflatex does not handle Unicode CJK characters.

**Preamble for CJK support:**
```latex
\documentclass[tikz,border=1pt]{standalone}
\usepackage{xcolor,tikz,amsmath}
\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont{Noto Sans CJK SC}
\setCJKsansfont{Noto Sans CJK SC}
\usetikzlibrary{shapes,arrows,positioning}
```

**Font selection:**
- `Noto Sans CJK SC` — preferred sans-serif CJK font; available via `apt install fonts-noto-cjk`
- `AR PL UMing` / `AR PL UKai` — fallback alternatives
- Always test with `fc-list :lang=zh` to verify CJK font availability before compiling

**CJK text inside TikZ nodes:**
- Use `\\` for line breaks within Chinese labels (same as English): `{知识引导四维\\眼动观测}`
- `\sffamily` applies correctly to CJK fonts when xeCJK is configured
- `\itshape` (italic) is NOT available for most CJK fonts — it silently falls back to regular. Avoid italic for Chinese text; use `\textit{}` only for English/Latin terms.

**Compile command:**
```bash
xelatex -interaction=nonstopmode fig_NAME.tex
```

**Verification after compilation:**
```bash
grep -c "Missing character" fig_NAME.log
```
If count > 0, the CJK font is not configured correctly — characters will show as blanks in PDF.

**Known CJK pitfalls:**
| Issue | Fix |
|-------|-----|
| `Missing character: There is no 路 in font [lmsans10-bold]` | CJK font not set. Add `\setCJKmainfont{...}` with a real CJK font name |
| `LaTeX Font Warning: Font shape .../m/it' undefined` | CJK fonts have no italic variant. Use regular for all Chinese text |
| `! LaTeX Error: Unicode character 个 (U+4E2A) not set up` | pdflatex can't handle CJK. Switch to xelatex |
| Chinese text appears as blanks/boxes in PDF | Font missing or `\setCJKmainfont` points to nonexistent font. Run `fc-list :lang=zh` to find available fonts |

#### TikZ Infrastructure

```latex
\documentclass[tikz,border=1pt]{standalone}
\usepackage{xcolor,tikz}
\usetikzlibrary{shapes,arrows,positioning}

% Nature-style color definitions here...

\begin{document}
\begin{tikzpicture}[
    every node/.style={font=\sffamily},
    box/.style={draw=#1, fill=#1!10, text=#1!90!black, minimum width=16mm,
                minimum height=5mm, rounded corners=1mm, font=\sffamily\footnotesize\bfseries,
                align=center, inner sep=2pt, line width=0.8pt},
    layer/.style={draw=black!25, rounded corners=2.5mm, fill=black!2, line width=0.7pt},
    lbl/.style={text=black!55, font=\sffamily\small\bfseries, align=center},
]

% CONTENT HERE

\end{tikzpicture}
\end{document}
```

#### Text Width Verification Before Pushing

When a user reports "text outside box" or after resizing boxes, use the
`references/text-width-measurement.md` technique to verify numerically:

1. Create a `\showwidth` test file with the exact font settings
2. Compile + `pdftotext` to extract numerical widths (in pt)
3. Compare against box size: `box_minW - 2*inner_sep` vs `text_width`
4. If margin < 10% of box width → widen box
5. Verify that ONLY the intended dimensions changed (font, inner_sep remain same)

#### Standard Dimensions

| Context | Width | Font Size | Line Width |
|---------|-------|-----------|------------|
| Single column (Nature) | 89mm / 253pt | 7-8pt | 0.6-0.8pt |
| Double column (Nature) | 183mm / 520pt | 9pt | 0.8-1.0pt |
| Full page (Nature) | 214mm / 607pt | 9-10pt | 1.0pt |

#### Font Settings

- **Family**: `\sffamily` (Arial/Helvetica for Nature)
- **Box text**: `\footnotesize\bfseries`
- **Layer labels**: `\small\bfseries`
- **Annotations**: `\tiny`
- **Caption text**: `\tiny` in gray (`black!40`)
- **Title**: `\large\bfseries` or `\Large\bfseries`

### Step 5: Verification Workflow (MANDATORY)

Before sharing or presenting a figure, run this checklist **in order**:

```
□ 1. Compile standalone: pdflatex fig_NAME.tex
□ 2. Text position check: pdftotext -bbox fig_NAME.pdf - | extract y-positions
     → Verify text layers are properly separated (no interleaving between layers)
     → Check that content occupies ≤90% of page height (should not hit top/bottom edges)
□ 3. Check dimensions: pdfinfo fig_NAME.pdf | grep "Page size"
     → Verify width and height are reasonable (not excessively tall/narrow)
□ 4. Vision check: if model supports vision_analyze, convert PDF to PNG (pdftoppm -png -r 300)
     and inspect visually for overlap, contrast, and alignment issues
□ 5. Include in paper: update paper.tex with \includegraphics
□ 6. Full compile: pdflatex + bibtex + pdflatex + pdflatex
□ 7. Check paper.log: grep for figure errors, overfull boxes
□ 8. VISUALLY INSPECT the generated PDF before pushing to user
```

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Iterating on figure without loading this skill first | User corrects: *\"作图应该调用技能去完成的\"* — trust lost in approach | **Always** `skill_view(\"academic-diagram\")` before touching any figure `.tex` code, even for \"small\" dimension/position tweaks. The skill's verification (Step 5) and consistency rules apply to every edit cycle. |\n| Layer backgrounds overlap from rounded corners | Rounded corners (e.g. 2.5mm) extend visually beyond rectangle bounds. L3 and L2 appear to overlap despite `bg_gap = 0.3cm`. | Calculate: `visual_gap = bg_gap - 2*R/10` (R in mm). For 2.5mm rounding: `0.3 - 0.5 = -0.2cm` overlap! Increase gap to ≥0.8cm for 2.5mm rounding. Edge-to-edge arrows: `\draw[arr] (0,L2_top) -- (0,L3_bottom);` |
| Figure too tall for page | Figure extends past page bottom | Use height-constrained scaling (`height=0.45\textheight, keepaspectratio`) or re-layout horizontally |
| Inconsistent visual style per layer | Figure looks messy | Force same box shape, font, and spacing rhythm across ALL layers |
| Three different layout patterns in one figure | Reader cannot parse | Use one pattern (all horizontal rows) everywhere |
| Text too small after scaling | Labels unreadable in print | Start with 7-8pt; after \includegraphics scaling, verify minimum 6pt at final size |
| Box width set before measuring text | Text overflows box or is too small with wasted space | Measure longest label text width FIRST (`chars × avg_char_width + padding`), then set box minimum width with ≥1.5mm margin |
| Cross-layer size inconsistency after partial modification | User says \"first box changed but second/third didn't\" — visual mismatch across layers | When modifying ANY layer's container or box dimensions (width, height, spacing), expand ALL layers to the same new dimensions. A 11cm L3 with 10cm L2/L1 is visually inconsistent. Check: are all `\draw[layer]` rectangles the same width? |
| `cap` TikZ style name conflicts with built-in `/tikz/cap` line-end key | `\\node[cap]` silently fails or misapplies style; TeX logs show `pgfkeys Error: The key '/tikz/cap' requires a value` | **Always use `cpt`, `annot`, or `captionstyle`** instead of `cap` as a TikZ style name. TikZ reserves `cap`, `butt`, `round`, and `rect` for line-end configuration. |
| `\def` variable name conflicts with LaTeX built-in commands | `! Undefined control sequence. \@@clr` — cryptic errors at the line where the `\def` variable is used. For example, `\def\hbar{2.2}` fails because `\hbar` is the reduced Planck constant (`ℏ`). Also affects `\angle`, `\grad`, `\div`, `\curl`, `\real`, `\Re`, `\Im`, `\mod`, `\ker`, `\hom`, `\lim`, `\sup`, `\inf`, `\max`, `\min`, `\det`, `\Pr`, `\arg`, `\deg`, `\log`, `\ln`, `\lg`, `\sin`, `\cos`, `\tan`, `\sec`, `\csc`, `\cot`, `\sinh`, `\cosh`, `\tanh`, `\coth`, `\arcsin`, `\arccos`, `\arctan`, `\exp`, `\gcd`, `\bmod`, `\pmod`, and many others. | **Name all `\def` variables with descriptive multi-word names to avoid any collision with LaTeX primitives.** Good: `\def\subrowA{2.2}`, `\def\boxHeight{3.0cm}`, `\def\gateSpacing{42mm}`. Bad: `\def\hbar`, `\def\const`, `\def\angle`. If you need to reuse a variable name, check `texdef -t latex <name>` or grep the LaTeX kernel for it. The safest approach is to prefix all diagram variables: `\def\fig@rowA`, or just use long descriptive names. |
| Color contrast too low | Light fills with white text | **Always use: fill=COLOR!10 + text=COLOR!90!black** (light fill + dark text = maximum contrast) |
| Arrows visible behind translucent box fills | Lines protrude through boxes | Draw arrows BEFORE background rectangles (z-order: arrows early, bgs late) |
| Color palette not unified | Each panel uses a different color scheme | Pick ONE palette family at Step 0; reuse across all panels |
| Chinese/CJK characters render as missing boxes | `pdflatex` with `CJKutf8` fails on Unicode chars. `xelatex` with CJK chars uses Latin Modern Sans (no CJK glyphs) unless CJK font is specified. | For Chinese text: use `xelatex` (not `pdflatex`), add `\usepackage{xeCJK}`, and set `\setCJKmainfont{Noto Sans CJK SC}` (or any installed CJK font — check with `fc-list :lang=zh`). Add compile instruction: `% Compile with: xelatex fig_NAME.tex`. |
| Figure pushed without local verification | Overlaps or cut-off detected by user | Follow Step 5 verification workflow — NEVER skip |
| Size change without self-consistency check | User asks "did font increase too?" | When changing box dimensions, verify font + inner_sep remained unchanged by checking the actual code. Provide a before/after table (Property / Before / After / Δ) to prove the fix was targeted. |
| Vision inspection skipped when available | Layout issues not caught until user feedback | Convert PDF to PNG (`pdftoppm -png -r 300`) and use vision_analyze to check overlap, contrast, spacing |

## When to load this skill (MANDATORY — scan before any figure-related response)

**If ANY of these match your task, you MUST load this skill:**

- User asks for a system architecture diagram for a paper
- User asks for a pipeline/flowchart diagram
- User asks for a "Nature-style" or "SCI" figure
- **User is iterating on figure layout and contrast (most commonly missed)**
- User is modifying existing figure dimensions, positions, spacing, or colors
- User mentions "学术论文图", "Nature图", "架构图", "流程图", or any Chinese figure-related terms
- User reports a layout problem (text outside boxes, spacing too tight, inconsistent sizing)

**Rule of thumb:** If the response involves writing or editing any `\documentclass[tikz]` or
`\includegraphics{fig_...}` code, load this skill first. Even if the change
seems trivial (resize one box, shift one label), the skill's consistency rules
apply.

## When NOT to load

- Data plots (bar, heatmap, trend) → use `nature-figure`
- Dark-themed cloud diagrams → use `architecture-diagram`
- One-off HTML prototypes → use `sketch` or `excalidraw`
- Video/animation → use `manim-video`

## Related Files

| File | Open when |
|------|-----------|
| `references/figure-contract.md` | Before starting any figure — establish conclusion, archetype, panel map |
| `references/nature-palette.md` | Choosing colors — has full 6/9 color-blind-safe palettes + CMYK |
| `references/tikz-templates.md` | Need TikZ base code for architecture/pipeline/trajectory |
| `references/layout-algorithm.md` | Need detailed multi-layer spacing calculation |
| `references/verification.md` | Before pushing figure to user — full checklist |
| `references/text-width-measurement.md` | When user reports text overflow or after resizing boxes — numerically verify text fits inside box |
| `references/synthos-figure-iteration.md` | When debugging multi-layer figure overlap, contrast, naming conflicts, or consistency issues — real failure cases with root causes, fixes, and detection heuristics from SynthOS paper iteration |
| `references/medical-proposal-roadmap.md` | Creating 3-phase vertical flowcharts for Chinese medical project proposals (CJK + Nature palette + side panels for validation/intervention) |
