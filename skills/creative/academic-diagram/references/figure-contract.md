# Figure Contract

Adopted from nature-figure (Yuan Yizhe, SJTU). Use before writing any TikZ code.

## Required Contract

```text
Core conclusion: [One sentence with a verb — the claim the figure must defend]
Figure archetype: [architecture | pipeline | trajectory | mixed]
Target journal/output: [Nature, Cell, NeurIPS, SCI journal, etc.]
Final size: [89mm single col | 183mm double col | custom]
Panel map:
  - A: [Panel A — hero or first panel]
  - B: [Panel B]
  - C: [Panel C]
Evidence hierarchy:
  - hero evidence: [Primary evidence, largest panel]
  - validation evidence: [Supporting quantitative panels]
  - controls/robustness: [Robustness checks]
Layout constraints:
  - max layers:
  - max elements per row:
  - color palette:
Reviewer risk: [What could a reviewer criticize? Address proactively]
```

## Core Rules

1. Every panel must answer a unique question
2. The hero panel gets 45-60% of figure area
3. One neutral family + one signal family + one accent family per figure
4. Keep the same color for the same concept across all panels
5. Prefer direct labels over separate legends when categories are spatially fixed

## Archetype Checklist

### architecture
- [ ] 3-4 layers stacked vertically
- [ ] Each layer uses same visual style (same box shape, same font)
- [ ] Layer spacing gap ≥ 1.0
- [ ] ≤ 4 elements per horizontal row
- [ ] Nature-style white background
- [ ] Layer background rectangles clearly separated

### pipeline
- [ ] Horizontal flow, ≤ 8 elements
- [ ] Arrow direction consistent (left→right)
- [ ] Outcome text below each gate
- [ ] Critical gates visually distinguished (e.g., red, ★ marker)

### trajectory
- [ ] XY plot with labeled axes
- [ ] Key milestones annotated
- [ ] Scale appropriate for data range
- [ ] Legend for multiple series

### mixed
- [ ] Schematic component takes 45-60% height
- [ ] Quantitative panels are smaller and less saturated
- [ ] Same material palette used in schematic and plots
