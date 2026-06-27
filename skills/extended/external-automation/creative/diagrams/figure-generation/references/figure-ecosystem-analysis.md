# Figure-Ecosystem Analysis

Cross-project figure capability audit. 2026-06-27.

Core Figure Skills (6):
1. figure-generation - Scientific data figures, matplotlib/Pillow/HTML, P2/v1.7, 6-item QA
2. figure-qa-check - Standalone QA, regex source extraction, self-contained
3. excalidraw - Hand-drawn flowcharts, JSON/excalidraw.com, P2 complete
4. pil-image-generation - Promotional covers, Pillow pure Python, P2 complete
5. nature-paper2ppt - Paper to PPT, PyMuPDF/Pillow/python-pptx, P2 QA report
6. pdf-reverse-engineering - PDF reverse engineering -> reproducible Python code, P2

Deleted skills (absorbed into figure-generation):
- academic-diagram (merged into figure-generation as diagram workflow mode)
- architecture-diagram (merged into figure-generation as architecture workflow mode)

Key Gaps (RESOLVED):
- figure-selector created for unified entry point
- global-palette.md created for unified color source
- pillow-primitives.md created for unified Pillow primitives
- BOUNDARY/IO_CONTRACT/EVIDENCE_SCHEMA all filled with useful content
- PDF reverse engineering extracted as standalone skill

Decision Tree:
- Scientific data chart -> figure-generation
- Academic diagram -> academic-diagram (TikZ)
- Engineering diagram -> architecture-diagram or excalidraw
- Promotional cover -> pil-image-generation
- Paper to PPT -> nature-paper2ppt
- 3D spiral/centerline -> 3d-curve-fitting-figures
- AI illustration -> image_generate or comfyui
- Math animation -> manim-video