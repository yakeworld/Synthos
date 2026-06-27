# PDF Reverse-Engineering → Reproducible Code

## Problem Pattern

A paper contains a figure (architecture diagram, flowchart, schematic) in the PDF with **no source code** in the `03-code/` directory. The figure was manually created (draw.io, Illustrator, PPT, etc.) and exported to PDF without keeping the source.

## Session Example

**HCS-3WT paper Figure 1** — had 6 figures total (fig1–fig6). fig2–fig6 had Python generation scripts; fig1 had **zero** source code. Verified via:
- `git log --diff-filter=AM -- "*/hcs3wt-breast-cancer/05-figures/*"` → empty
- `grep -rn "savefig\|fig1\|system_arch"` across all `03-code/experiments/*.py` → no matches
- `strings *.pdf` for embedded source references → no results
- `find *.drawio *.svg *.excalidraw *.ai *.eps` → none found

## Solution: pdftotext -bbox-layout Extraction

### Step 1: Extract exact coordinates

```bash
pdftotext -bbox-layout /path/to/figure.pdf - | python3 -c "import sys; print(sys.stdin.read())"
```

Output: HTML with `<block>`, `<line>`, `<word>` elements containing exact `xMin`, `xMax`, `yMin`, `yMax` coordinates in points.

### Step 2: Parse and structure

```python
import re, json

html = open('/tmp/fig1_bbox.txt').read()
# Parse blocks with their text content and coordinates
# Group by <flow> sections (visual zones)
# Extract each block: {xMin, xMax, yMin, yMax, text}
```

The HTML structure:
- `<doc>` → `<page width="..." height="...">` → `<flow>` → `<block>` → `<line>` → `<word>`
- Each `<word>` has `xMin`, `yMin`, `xMax`, `yMax` (point coordinates)
- Words group into `<line>` (same Y range), lines into `<block>` (contiguous region)

### Step 3: Reconstruct layout in matplotlib

Use parsed coordinates as ground truth for:
- Text placement positions (exact Y baselines from the original PDF)
- Box/container sizes and positions
- Section groupings (which text belongs to which visual block)
- Column structure (left/middle/right)

### Key Coordinates to Extract

From the original PDF:
```
Page dimensions: 998.64 × 674.64 pts

Title: HCS-3WT System Architecture — centered, top
Subtitle: Hybrid Cascade-Stacking... — below title

Key Design Principles (left sidebar) — block at x~56-203, y~68-119

Center title: Hybrid Cascade-Stacking Three-Way Triage — x~297-702, y~55-75

Expert B (Catcher) — x~116-248, y~212-297
Expert A (Refiner) — x~118-281, y~386-458  
Expert C (Arbiter) — x~119-268, y~556-641

Clear Negative — x~444-541, y~226-247
Clear Positive — x~441-544, y~400-421
Gray Zone — x~457-528, y~575-597

Performance Metrics (right) — multiple blocks at x~675-815, y~350-562
```

### Step 4: Write generation script

```python
# generate_fig1_system_architecture.py
# Must include:
# - All design system variables (colors, fonts, sizes)
# - All coordinate constants (X, Y, W, H)
# - QA overlap checking class
# - Save to PNG (300 DPI) + PDF (vector)
# - Save to 05-figures/ and manuscript figures/
```

## QA Checklist for Reconstructed Figures

1. **Text overlap check** — bounding boxes of all text elements must not intersect with box borders
2. **Title spacing** — title-to-first-content gap ≥ 55pts (≈8pt at 72dpi)
3. **Box boundaries** — all text must fit within parent box (word xMax < box xMax)
4. **Consistency** — box styles, colors, fonts must match paper style
5. **Reproducibility** — `python script.py` must produce identical output each run

## Pitfalls

- **Not all PDFs are from matplotlib** — check the PDF metadata first: `pdftotext -bbox-layout` gives HTML with `<meta name="Creator">` and `<meta name="Producer">`. If Producer=matplotlib, the figure was from matplotlib but source code may be lost. If Producer=GIMP or Adobe, it's a different source format.
- **Page coordinate origin** — `pdftotext -bbox-layout` uses bottom-left origin with Y going UP (typographic convention). matplotlib uses bottom-left with Y going UP too. So coordinates are directly usable.
- **Multi-page PDFs** — extract only the page with the figure. Skip title pages, tables, etc.
- **Embedded images** — some PDFs contain raster images (screenshots) instead of vector text. `pdftotext` will find no text in those. Use `pdfimages` to extract embedded images.
- **Non-ASCII text** — CJK characters may not appear in `-bbox-layout` output if the PDF lacks proper encoding. Fall back to `pdftotext -layout` (non-bbox) to extract what text exists.
- **Coordinate precision** — bbox coordinates are in PDF points (1/72 inch). matplotlib `figsize` in inches too, so coordinates transfer directly without conversion factor.
- **Cross-repo recovery first** — Before doing any PDF reverse-engineering or memory reconstruction, ALWAYS check if the original script exists in `/media/yakeworld/sda2/academic_writer/`. Memory reconstruction produces incomplete code (missing rcParams, color definitions, etc.) that generates visually different output (356K vs 703K PNG). The `academic_writer/` directory is the authoritative source for all pre-Synthos-migration figure scripts. See `references/cross-repo-code-recovery.md` for detailed recovery steps.
