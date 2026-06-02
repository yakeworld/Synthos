# Medical Proposal Technical Roadmap — Academic Diagram Adaptation

> 2026-05-21: PD Aspiration Risk Prediction Project (温州市科技局)
> These patterns extend the base `ARCH` and `PIPE` templates for Chinese medical proposals.

## Common Layout Pattern: 3-Phase Vertical Stack with Side Panels

Medical prediction model proposals typically have 3 phases:
1. **指标体系构建** — Indicator system construction (literature, framework, Delphi, pilot)
2. **预测模型构建与验证** — Model building & validation (cohort → data → LASSO → Logistic → validation)
3. **护理预警与临床转化** — Nursing warning & translation (interaction → stratification → intervention → closed loop)

Each phase needs:
- Main flow boxes (center-left)
- Side panels: validation/output (right)
- Sub-labels for methods/details (below boxes)

## Key Layout Parameters

```latex
% Phase Y-coordinates (cm) for ~15cm tall figure
\def\pOneTop{10.2}   \def\pOneBot{6.5}    % Phase 1
\def\pTwoTop{5.6}    \def\pTwoBot{1.5}    % Phase 2
\def\pThreeTop{0.8}  \def\pThreeBot{-3.0}  % Phase 3
% Column X-coordinates
\def\colA{-3.2}     % Main flow left
\def\colB{0}         % Main flow center
\def\colC{3.2}       % Main flow right
\def\colVal{5.2}     % Validation/output side panel
\def\colInt{1.8}     % Intervention column (Phase 3)
% Inter-phase gaps
\def\gapAB{0.9}      % Phase 1 bottom - Phase 2 top
\def\gapBC{0.7}      % Phase 2 bottom - Phase 3 top
```

## Color-Phase Mapping

| Phase | Box Color | Sub-box Color | Zone BG |
|:------|:----------|:--------------|:--------|
| 1. 指标体系构建 | `nat_blue` (#0072B2) | `nat_cyan` (#56B4E9) | `nat_blue!1` |
| 2. 预测模型构建与验证 | `nat_green` (#009E73) | — | `nat_green!1` |
| 3. 护理预警与临床转化 | `nat_orange` (#E69F00) | — | `nat_orange!1` |
| Output/validation | `nat_pink` (#CC79A7) | — | — |
| Intervention | `nat_brown` (#D55E00) | — | — |
| Special highlight | `nat_green` (#009E73) as solid fill | — | — |

## CJK Compilation

```bash
xelatex -interaction=nonstopmode fig_roadmap.tex
```

Verify CJK rendering:
```bash
grep -c "Missing character" fig_roadmap.log
# Must be 0 — if >0, CJK font is not configured
```

## Common Pitfalls (Medical Proposals)

1. **`cap` name conflict**: TikZ reserves `cap` for line caps. Use `annot` instead.
2. **CJK font not found**: Run `fc-list :lang=zh` before compiling. Install with `apt install fonts-noto-cjk`.
3. **Figure too tall**: For single-column (89mm wide), compress text and reduce phase gaps to 0.5cm.
4. **Overfull hbox**: If `\node[...]` text exceeds box width, reduce font or widen `minimum width`.
5. **Intervention column overlaps**: For 3 rows of interventions, space them 0.9-1.0cm apart vertically.
