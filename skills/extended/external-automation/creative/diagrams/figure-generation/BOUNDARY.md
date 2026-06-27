# Boundary: figure-generation

## Scope

Figure generation — create publication-ready scientific charts for SCI papers, PPT, and reports.

## In-Scope

- Scientific data figures (bar charts, scatter plots, ROC curves, confusion matrices, etc.)
- Architecture/flow diagrams (boxes + arrows)
- Quality report visualization (report -> image)
- Multi-panel composite figures
- Statistical plots with significance annotation

## Out-of-Scope

| Item | Instead Use |
|:-----|:------------|
| 3D/GIS visualization | `figure-generation/3d-curve-fitting-figures/` |
| AI illustrations / concept art | `image_generate` or `comfyui` |
| Animated diagrams / video | `manim-video` |
| Interactive charts (Plotly/Altair) | Not in scope |
| Hand-drawn flowcharts | `excalidraw` |
| Promotional covers / posters | `pil-image-generation` |
| Paper to PPT conversion | `nature-paper2ppt` |
| PDF reverse engineering | Standalone `pdf-reverse-engineering` skill |

## Decision Tree

1. Is this a scientific figure?
   - Yes -> figure-generation
   - No -> skip
2. What kind of scientific figure?
   - Data chart (bar, scatter, ROC, etc.) -> figure-generation (standard path)
   - Architecture/flow diagram -> figure-generation (hybrid workflow)
   - Quality report visualization -> figure-generation (HTML+Firefox or Pillow)
3. Any special requirements?
   - 3D -> route to `3d-curve-fitting-figures/`
   - Animation -> route to `manim-video`
   - Interactive -> out-of-scope
