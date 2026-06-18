# LaTeX Academic Figure Reference

## Multi-Layer TikZ Architecture Diagrams

### Layout Arithmetic (case study from SynthOS paper)
For a 3-layer stacked architecture figure, use this coordinate planning method:

1. **Fix the bottom layer first** (largest, with radial elements):
   - Bus center at y=-3.5, atoms at radius 1.6 → y range [-5.1, -1.9]
   - Background: y from -6.0 to -1.0 (adds 0.9/0.9 padding)
   - Label slightly below bg bottom: y=-5.5

2. **Place the middle layer with gap ≥ 0.5** from bottom layer elements:
   - Center at y=2.0 (jumps from -1.9 to -2.0 = 3.9 gap from bottom layer max)
   - Steps at radius 1.6 → y range [0.4, 3.6]
   - Background: y from 0.0 to 4.5 (padding 0.4/0.9)
   - Check: bottom bg bottom (0.0) → middle bg top in previous? No — prev bg top is -1.0, gap 1.0 ✓

3. **Top layer above middle layer:**
   - Compute middle layer bg top (4.5)
   - Place top layer bottom element at ≥ 5.0 (gap 0.5)
   - Stack: Task(6.0), Capability(7.2), Pattern(8.4), Standard(9.6), Philosophy(10.8)
   - Background: y from 5.0 to 12.4

4. **Total height**: max_y - min_y = 12.4 - (-6.0) = 18.4 tikz units

### TikZ to PDF Size

1 tikz unit ≈ 1cm ≈ 28.45pt. A diagram spanning 18.4 units vertically → ~524pt.

### \includegraphics Sizing for Twocolumn Papers

Paper layout: letterpaper, margins 0.75in → textwidth ≈ 504pt, textheight ≈ 684pt.

Safe figure sizing:
- `width=\textwidth` → max 504pt wide
- For a 275×525pt figure: scaled_height = 525 * (504/275) = 962pt → TOO TALL
- Need to constrain: `width=0.75\textwidth, keepaspectratio` → 504*0.75=378pt, h=525*(378/275)=721pt → still too tall
- Solution: use BOTH dimensions: `width=0.6\textwidth, height=0.4\textheight, keepaspectratio` or `width=0.45\textwidth`
- General rule: for portrait (tall) figures, favor `height` constraint; for landscape (wide), favor `width`

### Common Failure Patterns

1. **Background rectangles drawn in TikZ with fixed y-coordinates that don't account for rotated/peripheral nodes**
   - Fix: compute exact node extents before drawing bg, not estimated

2. **Caption/text overlaps because figure floats to unexpected page position**
   - Fix: use `figure*[t]` for twocolumn, compile with at least 2 pdflatex passes

3. **Delegated TikZ figure has wrong library imports or syntax that only fails when compiled**
   - Prevention: compile EVERY figure locally after delegation, before presenting to user

### Color Palette (teal accent, dark navy bg)

```latex
\definecolor{teal}{HTML}{00BCCD}
\definecolor{navy}{HTML}{0A192F}
\definecolor{darkcard}{HTML}{112240}
\definecolor{lightcard}{HTML}{1A365D}
```

Box styles: `draw=teal!60, fill=darkcard, text=white`
Backgrounds: `fill=navy, draw=teal!30, rounded corners=2mm, opacity=0.7`
Arrows: `->, teal!60, draw, thick, >=stealth`
