---
name: architecture-diagram
description: "Dark-themed SVG architecture/cloud/infra diagrams as HTML."
version: 1.0.0
author: Cocoon AI (hello@cocoon-ai.com), ported by Hermes Agent
license: MIT
dependencies: []
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [architecture, diagrams, SVG, HTML, visualization, infrastructure, cloud]
    related_skills: [concept-diagrams, excalidraw, academic-diagram]
---

# Architecture Diagram Skill

Generate professional, dark-themed technical architecture diagrams as standalone HTML files with inline SVG graphics. No external tools, no API keys, no rendering libraries — just write the HTML file and open it in a browser.

## Scope

**Best suited for:**
- Software system architecture (frontend / backend / database layers)
- Cloud infrastructure (VPC, regions, subnets, managed services)
- Microservice / service-mesh topology
- Database + API map, deployment diagrams
- Anything with a tech-infra subject that fits a dark, grid-backed aesthetic

**⚠️ CRITICAL: Do NOT use this skill for academic paper figures.**
This skill produces **dark-themed SVG/HTML diagrams** with teal-on-navy color schemes and semi-transparent fills. These are visually striking on screen but **unsuitable for print journals, SCI papers, or Nature/CNS manuscripts** which require:
- White/light backgrounds (not dark)
- High-contrast text on light fills (dark text on light color, not white text on dark color)
- Print-safe, color-blind-accessible palettes
- TikZ vector format for LaTeX compilation

**Always redirect academic paper figures to `academic-diagram`** — that skill provides Nature-approved white-background TikZ templates with verified contrast and journal-compliant sizing.

**Look elsewhere first for:**
- **Academic paper figures (Nature/CNS style, white background, TikZ)** — use `academic-diagram` (class-level, all-three archetypes: architecture/pipeline/trajectory)
- Physics, chemistry, math, biology, or other scientific subjects
- Physical objects (vehicles, hardware, anatomy, cross-sections)
- Floor plans, narrative journeys, educational / textbook-style visuals
- Hand-drawn whiteboard sketches (consider `excalidraw`)
- Animated explainers (consider an animation skill)

If a more specialized skill is available for the subject, prefer that. If none fits, this skill can also serve as a general SVG diagram fallback — the output will just carry the dark tech aesthetic described below.

Based on [Cocoon AI's architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) (MIT).

## Workflow

1. User describes their system architecture (components, connections, technologies)
2. Generate the HTML file following the design system below
3. Save with `write_file` to a `.html` file (e.g. `~/architecture-diagram.html`)
4. User opens in any browser — works offline, no dependencies

### Output Location

Save diagrams to a user-specified path, or default to the current working directory:
```
./[project-name]-architecture.html
```

### Preview

After saving, suggest the user open it:
```bash
# macOS
open ./my-architecture.html
# Linux
xdg-open ./my-architecture.html
```

## Design System & Visual Language

### Color Palette (Semantic Mapping)

Use specific `rgba` fills and hex strokes to categorize components:

| Component Type | Fill (rgba) | Stroke (Hex) |
| :--- | :--- | :--- |
| **Frontend** | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (cyan-400) |
| **Backend** | `rgba(6, 78, 59, 0.4)` | `#34d399` (emerald-400) |
| **Database** | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (violet-400) |
| **AWS/Cloud** | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (amber-400) |
| **Security** | `rgba(136, 19, 55, 0.4)` | `#fb7185` (rose-400) |
| **Message Bus** | `rgba(251, 146, 60, 0.3)` | `#fb923c` (orange-400) |
| **External** | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (slate-400) |

### Typography & Background
- **Font:** JetBrains Mono (Monospace), loaded from Google Fonts
- **Sizes:** 12px (Names), 9px (Sublabels), 8px (Annotations), 7px (Tiny labels)
- **Background:** Slate-950 (`#020617`) with a subtle 40px grid pattern

```svg
<!-- Background Grid Pattern -->
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
</pattern>
```

## Technical Implementation Details

### Component Rendering
Components are rounded rectangles (`rx="6"`) with 1.5px strokes. To prevent arrows from showing through semi-transparent fills, use a **double-rect masking technique**:
1. Draw an opaque background rect (`#0f172a`)
2. Draw the semi-transparent styled rect on top

### Connection Rules
- **Z-Order:** Draw arrows *early* in the SVG (after the grid) so they render behind component boxes
- **Arrowheads:** Defined via SVG markers
- **Security Flows:** Use dashed lines in rose color (`#fb7185`)
- **Boundaries:**
  - *Security Groups:* Dashed (`4,4`), rose color
  - *Regions:* Large dashed (`8,4`), amber color, `rx="12"`

### Spacing & Layout Logic
- **Standard Height:** 60px (Services); 80-120px (Large components)
- **Vertical Gap:** Minimum 40px between components
- **Message Buses:** Must be placed *in the gap* between services, not overlapping them
- **Legend Placement:** **CRITICAL.** Must be placed outside all boundary boxes. Calculate the lowest Y-coordinate of all boundaries and place the legend at least 20px below it.

## For LaTeX/TikZ Output (Academic Paper Use)

When producing diagrams for LaTeX papers (common in academic writing), follow these adjustments:

### Output Format
- Use **TikZ** (`\documentclass[tikz,border=2pt]{standalone}`) instead of HTML/SVG for LaTeX-toolchain compatibility
- Compile standalone with `pdflatex`, then `\includegraphics` in the main paper
- TikZ renders with the same font/color fidelity as the paper

### Multi-Layer Layout: Spacing Rules
Multi-layer diagrams (stacked architecture, pipeline flow) are the most common source of overlap bugs. Follow this arithmetic:

1. **Compute element extent per layer**: For each layer, find the min and max y-coordinate of all visible elements (nodes, labels, bounding rectangles)
2. **Pad each layer's background**: Add at least 0.5 units of padding above and below the extreme elements
3. **Check background-to-background gaps**: After padding, verify adjacent backgrounds do NOT overlap: `gap = L1_bg_top - L2_bg_bottom`. Require `gap ≥ 0.3`
4. **Check element-to-element gaps**: `gap = L1_max_element_y - L2_min_element_y`. Require `gap ≥ 0.5` to prevent visual crowding
5. **Aspect ratio budget**: For a twocolumn paper with 0.75in margins, the figure's height after `\includegraphics` scaling must not exceed ~400pt (0.6\textheight). Calculate: `scaled_h = fig_h * (target_w / fig_w)`. If >400pt, re-layout horizontally rather than vertically

### Verification Workflow (MANDATORY — do not skip)
Before sharing or presenting a figure:
1. Compile the standalone figure: `pdflatex fig_*.tex`
2. Visually inspect the PDF for overlapping text or cut-off edges
3. Compile the FULL paper with the figure included (at least 2 passes of pdflatex + bibtex)
4. Check `paper.log` for figure-related errors (overfull boxes, missing files, figure placement issues)
5. **Only then push the result to the user**

### Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Layer backgrounds overlap | Elements from different layers visually blend | Increase vertical spacing between layer centers by 1.0–1.5 units; recalculate bg rectangles |
| Figure too tall for page | Figure + caption extends below page bottom | Reduce width scaling, or split into two figures, or re-layout horizontally |
| Aspect ratio mismatch | Figure looks tiny or distorted in the paper | Compute scaled height before setting width; if height > 0.6\textheight, constrain with `height=` instead of `width=` |
| Arrows visible behind opaque fills | Arrow paths protrude through background rectangles | Draw arrows BEFORE background rectangles (z-order: arrows early, bgs late) |
| Delegated subagent produces broken TikZ | Compile errors or malformed output | Always compile locally after subagent returns; never forward unverified output to user |
| **Using dark diagrams for paper figures** | User rejects dark-background figures in an academic context | **Redirect to `academic-diagram`**. This skill produces presentation slides, not journal figures. |
| **Three different layer styles in one figure** | Figure looks inconsistent (radial + text + boxes mixed) | Force identical visual style (same box shape, same font, same spacing) across ALL layers |

## Document Structure

The generated HTML file follows a four-part layout:
1. **Header:** Title with a pulsing dot indicator and subtitle
2. **Main SVG:** The diagram contained within a rounded border card
3. **Summary Cards:** A grid of three cards below the diagram for high-level details
4. **Footer:** Minimal metadata

### Info Card Pattern
```html
<div class="card">
  <div class="card-header">
    <div class="card-dot cyan"></div>
    <h3>Title</h3>
  </div>
  <ul>
    <li>• Item one</li>
    <li>• Item two</li>
  </ul>
</div>
```

## Output Requirements
- **Single File:** One self-contained `.html` file
- **No External Dependencies:** All CSS and SVG must be inline (except Google Fonts)
- **No JavaScript:** Use pure CSS for any animations (like pulsing dots)
- **Compatibility:** Must render correctly in any modern web browser

## Template Reference

Load the full HTML template for the exact structure, CSS, and SVG component examples:

```
skill_view(name="architecture-diagram", file_path="templates/template.html")
```

The template contains working examples of every component type (frontend, backend, database, cloud, security), arrow styles (standard, dashed, curved), security groups, region boundaries, and the legend — use it as your structural reference when generating diagrams.
