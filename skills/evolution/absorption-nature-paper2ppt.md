# Absorption Record: nature-paper2ppt

## Source
- **GitHub**: https://github.com/GARCH-QUANT/garch-nature-paper2ppt
- **Author**: GARCH-QUANT
- **License**: MIT
- **Stars**: 1

## 5-Dimension Score

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Architectural Alignment | 4.5 | python-pptx + PyMuPDF + Pillow stack aligns with Synthos's Terminal-native philosophy |
| Philosophical Alignment | 5.0 | "Figure-first, asymmetric layout, evidence hierarchy" — directly extendable to Synthos paper-workflow's figure generation |
| Gap Fill | 4.5 | Synthos paper-workflow doesn't produce PPTX decks; this fills the "paper → presentation" gap |
| Code Quality | 4.0 | Well-structured SKILL.md, cross-platform policy, clean fallback rules |
| Actionability | 5.0 | Directly absorbable as a new Synthos skill; layout rules (70/30, full-width, etc.) reusable across Synthos |

**Overall Score: 4.6/5.0 (P0)**

## Key Capabilities Absorbed

| # | Capability | Synthos Integration | Priority |
|:-:|:-----------|:--------------------|:--------:|
| 1 | **Figure-first layout** — asymmetric/70-30/full-width | Central to nature-paper2ppt skill | P0 |
| 2 | **Paper type classification → presentation logic** | 7-type classification + 7 presentation logics | P0 |
| 3 | **Evidence hierarchy on slides** | Hero figure + narrow annotation rail | P0 |
| 4 | **Conclusion-style titles** | Direct labeling rule for Synthos ARG output | P1 |
| 5 | **Cross-platform Python stack** | PyMuPDF/Pillow/python-pptx (no GUI, no LibreOffice) | P1 |

## What Synthos Should NOT Absorb

| Feature | Reason to Skip |
|:--------|:---------------|
| Separate README (Chinese) | Synthos aggregates in SKILL.md only |
| Figure-plan/outline as separate files | Synthos produces as optional outputs when complexity demands |
| LibreOffice/soffice rendering | Depends on desktop environment, not portable |

## Integration Plan

**P0 (immediate):**
1. Create `nature-paper2ppt` skill under Synthos/skills/
2. Add 原理层·文言: `转化之道` — 图为首，文为佐
3. Include full figure-first layout system with asymmetric rules
4. Register in Synthos/SKILL.md extended skills list

**P1 (next cycle):**
5. Bridge with ARG (argument-expression) — figure layout suggestions from argument type
6. Bridge with figure-generation — reuse Nature/Okabe-Ito color palettes for PPT-native charts

## References
- GARCH-QUANT. *garch-nature-paper2ppt*. GitHub: https://github.com/GARCH-QUANT/garch-nature-paper2ppt
