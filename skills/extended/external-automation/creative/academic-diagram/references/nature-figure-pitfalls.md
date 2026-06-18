# Nature/CNS Journal Figure Guidelines (Practical)

These guidelines are distilled from actual Nature/Cell/PNAS/NEJM published figures and from 3 iteration cycles of feedback in one session.

## General Rules

1. **White background, always.** Dark backgrounds are for presentation slides or infographics, not journal figures.
2. **Color-blind friendly palette.** The 7-color palette in SKILL.md (blue/green/purple/orange/red/brown/grey) is adapted from the Wong Nature Methods palette (2011) — it works for all common color-blind types.
3. **Text in black, not white** on colored boxes. Use `color!12` fill + `color!95!black` text for maximum contrast.
4. **No emoji or icons.** Use simple geometric shapes.
5. **No 3D effects.** Flat, 2D boxes with rounded corners.

## Figure Sizing for Twocolumn Papers

Paper layout (letter, 0.75in margins): textwidth = 504pt, textheight = 684pt.

| Target | Width | Use Case |
|:---|---:|:---|
| Single column | ~252pt (89mm) | Small figs that fit in one column |
| Double column (full) | ~504pt (178mm) | Wide figs spanning both columns |
| Double column (scaled) | 0.7-0.85\textwidth | Portrait-oriented figs with height constraint |

**Critical sizing formula:**
```python
scaled_height = fig_height_pts * (target_width / fig_width_pts)
# If scaled_height > 400pt (0.6 textheight): figure is too tall
# Fix: reduce width scaling, or re-layout figure horizontally
```

## Layer Stacking Arithmetic (from SynthOS architecture figure iterations)

### Iteration 1 (FAILED — background overlap)
- Layer 1 bg: y=-7.5 to -0.8 → Layer 2 bg: y=-0.5 to 4.2 → overlap 0.3 units
- Root cause: guessed positions instead of computing extents

### Iteration 2 (FAILED — still crowded)
- Layer 1 bg: y=-7.0 to -0.5 → Layer 2 bg: y=0.0 to 4.5 → no overlap but element elements nearly touched

### Iteration 3 (SUCCESS — Nature-style white bg)
- Layer 1 bg: y=-1.2 to 1.8 (atoms at y=-1.2..1.2 from bus at y=-0.2±1.1)
- Layer 2 bg: y=2.5 to 5.0 (text at y=2.9..4.7)
- Layer 3 bg: y=5.8 to 8.8 (elements at y=6.0..8.5)
- Gap: Layer 1→2: 0.7 units. Layer 2→3: 0.8 units
- Total: 10 units vertical → 285pt → fits at 0.7\textwidth

### Lesson: Always compute exact y-extents before drawing backgrounds

## TikZ Compilation Checklist

Before pushing any figure:
```
□ pdflatex figure.tex → exits 0
□ pdfinfo figure.pdf → dimensions reasonable
□ pdftotext figure.pdf → all expected labels present, no cut-off text
□ Full paper pdflatex ×2 + bibtex + pdflatex ×2 → no errors
□ grep "fig_name" paper.log → verified figure was embedded
□ grep -i "overfull\|emergency" paper.log → zero figure-related warnings
```
