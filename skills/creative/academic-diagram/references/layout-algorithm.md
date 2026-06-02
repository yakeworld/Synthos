# Multi-Layer Layout Algorithm

Derived from 3 iteration cycles of Figure 1 placement debugging in SynthOS paper.
Use this arithmetic BEFORE writing TikZ code to prevent overlap bugs.

## Step 1: Compute Text Widths → Set Box Dimensions (REQUIRED)

**Before choosing box widths, measure the longest label in each layer.**

```python
# Reference: Arial/Helvetica bold at common academic font sizes
# \tiny (5pt):  avg char ~3.0pt → longest word: chars × 3.0pt = width_pt
# \footnotesize (7pt): avg char ~4.0pt → width_pt = chars × 4.0pt
# \small (9pt): avg char ~5.0pt

# Conversion: 1pt = 0.353mm
# Box_min_mm = text_width_mm + 2×padding_mm
# padding_mm: 1.5mm minimum, 2.5mm comfortable

# Empirical measurements for common labels:
# \tiny\bfseries: "Philosophy"(10ch) ≈ 9.1mm → box ≥ 11mm
# \tiny\bfseries: "Hypothesis"(10ch) ≈ 9.3mm → box ≥ 12mm
# \footnotesize\bfseries: "ROUTE"(5ch) ≈ 7.5mm → box ≥ 10mm
```

**Example — SynthOS architecture figure:**
| Layer | Font | Longest Label | Width | Box Width | Margin |
|-------|------|---------------|-------|-----------|--------|
| Absorption | \tiny\bfseries | "Philosophy" (10ch) | 9.1mm | 12mm | +2.9mm ✓ |
| Evolution | \tiny\bfseries | "Hypothesis" (10ch) | 9.3mm | 12mm | +2.7mm ✓ |
| Atom Layer | \footnotesize\bfseries | "ROUTE" (5ch) | 7.5mm | 11mm | +3.5mm ✓ |

**Rule:** After setting box widths, verify ALL labels fit with ≥ 1.5mm margin. If any label is tight (< 1.0mm), increase that box width

**After setting box widths, determine horizontal layout:**
```text
total_width = N_boxes × box_width + (N-1) × gap
half_width = total_width / 2
background_x = -(half_width + margin_x) to +(half_width + margin_x)
```

## Step 2: Define Coordinate System

TikZ default: 1 unit = 1cm = 28.45pt.
Center the figure at x=0. Y increases upward.

## Step 3: Per-Layer Bounding

For each layer L_i, compute:

```
element_y_min = min(y of all visible nodes in L_i)
element_y_max = max(y of all visible nodes in L_i)
bg_y_min = element_y_min - padding_bottom
bg_y_max = element_y_max + padding_top
```

**Padding defaults:**
- `padding_bottom = 0.8` (below lowest element)
- `padding_top = 0.3` (above highest element)

## Step 4: Gap Verification (with Rounded Corner Correction)

**CRITICAL: `rounded corners` extends visual bounds.** A layer with
`rounded corners=2.5mm` visually extends 2.5mm beyond its rectangle
coordinates on all four sides. The `bg_gap` must account for this.

For adjacent layers L_i and L_{i+1} with `rounded corners=R mm`:

```
# 1. Element gap (visual crowding check)
element_gap = L_{i+1}_element_y_min - L_i_element_y_max
REQUIRE: element_gap ≥ 1.0

# 2. Background gap — CORRECTED for rounding
bg_gap = L_i_bg_y_min - L_{i+1}_bg_y_max  # positive = gap, negative = overlap
visual_gap = bg_gap - 2*R/10               # subtract double rounding radius in cm
REQUIRE: visual_gap ≥ 0.3                  # minimum visual clearance

# Example: R=2.5mm, bg_gap=0.3cm
# visual_gap = 0.3 - 2*0.25 = 0.3 - 0.5 = -0.2cm → OVERLAP by 2mm!
# Solution: increase bg_gap to ≥ 0.5+R*2 = 1.0cm for 2.5mm rounding
```

**Rule of thumb for common rounding radii:**
| Rounded corners | Minimum bg_gap for 0.3cm visual clearance |
|----------------|-------------------------------------------|
| 1.5mm | ≥ 0.6cm |
| 2.0mm | ≥ 0.7cm |
| 2.5mm | ≥ 0.8cm |
| 3.0mm | ≥ 0.9cm |

If visual_gap < 0.3, increase spacing by shifting the upper layer up by `delta = 0.5 + R*2/10` (minimum).

## Step 5: Aspect Ratio Budget

Calculate if the figure fits the target column width:

```
target_width_pt = 504 (for 0.75in margin, full textwidth)
               or 253 (single column Nature, 89mm)
               or 520 (double column Nature, 183mm)

fig_width_pt = actual TikZ width (max_x - min_x in tikz units * 28.45)
fig_height_pt = actual TikZ height (max_y - min_y in tikz units * 28.45)
scaled_height = fig_height_pt * (target_width_pt / fig_width_pt)

REQUIRE: scaled_height ≤ 0.5 * textheight
         where textheight_pt ≈ 684 (letter, 0.75in margin)
         or textheight_pt ≈ 660 (A4, 2.54cm margin)
```

If scaled_height exceeds limit:
- **Option A**: Reduce fig_width by 10%, recheck
- **Option B**: Split into two figures
- **Option C**: Re-layout horizontally instead of vertical stacking
- **Option D**: Use height-constrained `\includegraphics[height=0.45\textheight, keepaspectratio]`

## Step 6: Consistency Check

```
VISUAL CONSISTENCY:
□ All layers use same box.size, font.size, rounding radius
□ All layers use same arrow style
□ All layers have same padding rhythm
□ Inter-layer arrows are vertically aligned (same x-position)
□ Title font consistent with layer label font
```

## Quick Reference: 3-Layer Architecture

| Layer | Y_center | Element Range | Padding | BG Range |
|-------|----------|---------------|---------|----------|
| 3 (top) | +8.5 | +5.8 to +10.8 | 0.8/0.3 | +5.0 to +11.1 |
| 2 (mid) | +5.0 | +2.5 to +5.0 | 0.5/0.3 | +2.0 to +5.3 |
| 1 (bot) | 0 | -2.0 to +1.5 | 1.0/0.3 | -3.0 to +1.8 |

Gaps: L1→L2 = 2.5-1.5=1.0, L2→L3 = 5.0-5.0=0 → ADJUST: shift L3 up.

## Quick Reference: Pipeline (6-8 Gates)

| Parameter | 6 Gates | 7 Gates | 8 Gates |
|-----------|---------|---------|---------|
| Gate width | 20mm | 19mm | 18mm |
| Gap | 3mm | 3mm | 2mm |
| Total width | 138mm | 151mm | 158mm |
| Dbl col? | ✓ fits 183mm | ✓ fits 183mm | ✓ fits 183mm |
| Sgl col? | ✗ too wide | ✗ too wide | ✗ too wide |
