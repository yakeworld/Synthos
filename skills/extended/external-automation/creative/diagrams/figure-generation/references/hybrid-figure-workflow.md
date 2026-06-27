# Hybrid Figure Workflow — HCS-3WT Figure 1 Case Study

**Date**: 2026-06-26
**Author**: Synthos
**Type**: Session-specific detail — a complete working example of the hybrid figure workflow pattern

## Background

User feedback: matplotlib code for Figure 1 had ongoing layout issues — arrow endpoints outside target boxes, text overflow, overlapping boxes. Each fix required multiple code iterations (8+ rounds).

Key insight: **架构流程图 (architecture/flow diagrams) are inherently visual** — box positions, colors, arrow connections are design decisions best made visually (draw.io), not in code. The data (accuracy, AUC, method names) is what changes frequently and is best handled by code.

**Solution**: Separate structure from data.

## Architecture

```
Structure (draw.io template)     Data (experiment results)
┌──────────────────────────┐     ┌─────────────────────────┐
│ Box positions            │     │ accuracy: 96.88%        │
│ Arrow connections        │  +  │ f1: 97.55%              │
│ Color scheme             │     │ auc: 98.6%              │
│ Layout (3 columns)       │     │ ...                     │
│ Fixed text labels        │     └─────────────────────────┘
└──────────────────────────┘              │
          │                                 │
          ▼                                 ▼
    generate_figure.py ───────────────────→ SVG → PDF
```

## Workflow

1. **Draw the complete architecture in draw.io** → save as `.drawio` template file
2. **Each data cell** marked with a placeholder (e.g. `{{accuracy}}`) or fixed in SVG
3. **Python script** reads experiment JSON → injects data → outputs SVG + PDF
4. **Layout changes**: drag boxes/arrows in draw.io, code unchanged
5. **Data updates**: re-run Python script, 5 seconds

## Two Implementation Paths

### Path A: draw.io XML → Inject → Inkscape Export
- Template: `.drawio` file
- Inject: Python parses XML, modifies `value` attributes
- Export: `drawio --to pdf` or `inkscape` (Inkscape can't read `.drawio` directly)

### Path B: Generate SVG Directly → Inkscape to PDF (RECOMMENDED)
- Template: Python script with SVG structure hardcoded
- Inject: Directly modify SVG `value` attributes
- Export: `inkscape template.svg --export-type=pdf --export-filename=output.pdf`
- **Advantages**: No external draw.io dependency, SVG is plain-text version-controlable

## HCS-3WT Figure 1 Implementation

### Files Created

| File | Purpose |
|------|---------|
| `generate_figure1_svg.py` | Main generator — reads experiment JSON, produces SVG + PDF |
| `generate_fig1_system_architecture.py` | Legacy matplotlib version (kept for reference) |
| `architecture_template.drawio` | draw.io template (manual editing reference) |
| `figure_config.yaml` | Text content configuration for all boxes |
| `inject_figure_data.py` | Legacy: inject data into draw.io XML (not used anymore) |

### Data Elements

**Numeric (auto-injected from experiment_results.json):**
- Overall Accuracy: 96.88%
- Overall F1-Score: 97.55%
- Overall AUC: 98.6%
- Automation Rate: 61.6%
- Automation Accuracy: 99.42%
- Gray Zone Accuracy: 92.2%
- Clear Negative%: 4.0%
- Clear Positive%: 14.5%
- Gray Zone%: 11.5%

**Text (configurable via YAML or in code):**
- Method names (SVC, VotingClassifier, etc.)
- Parameter descriptions
- Principle descriptions
- Pipeline steps

### Key Design Decisions

1. **SVG as intermediate format** — Inkscape handles SVG→PDF conversion reliably, no matplotlib dependency
2. **SVG is version-controlable** — plain text, diffable, not binary like draw.io files
3. **draw.io template preserved** — for visual editing without touching code
4. **YAML config for text** — easy to change method names without touching SVG generation code
5. **All outputs copied** to all required locations (05-figures/, figures/, academic_writer/figures/)

### Inkscape Conversion

```bash
# Generate SVG with injected data
python3 generate_figure1_svg.py --data experiments/experiment_results.json

# Inkscape exports to PDF
inkscape fig1.svg --export-type=pdf --export-filename=fig1.pdf --export-background=white
```

Inkscape 1.4+ on this system works reliably for SVG→PDF conversion.

## When to Use This Pattern

| Scenario | Recommended Approach |
|----------|---------------------|
| Data changes frequently, layout stable | Hybrid workflow (Path B) |
| Layout changes frequently, data stable | draw.io manual + export PDF |
| One-time figure | matplotlib or draw.io either way |
| Quantitative data figures (bar charts, scatter plots) | matplotlib + QA (standard path) |

## Migration Notes

The old `generate_fig1_system_architecture.py` (matplotlib) has been replaced by `generate_figure1_svg.py`. Both produce identical layout; the SVG version:
- Is smaller (~17KB vs ~17KB for the Python source)
- Exports to PDF via Inkscape (no matplotlib PDF backend dependency)
- Is easier to manually edit in draw.io
- Has no coordinate math — purely visual layout

## Lessons Learned

1. **User feedback on layout issues was correct** — matplotlib code for architecture diagrams is hard to maintain because every change is a code diff
2. **draw.io is the right tool for structure** — drag-and-drop box layout, visual arrow connections
3. **Python is the right tool for data injection** — automatic, reproducible, version-controlled
4. **The hybrid approach eliminates the 8+ round iteration cycle** — change layout in draw.io (instant visual feedback), change data in JSON (5-second script run)
5. **SVG as intermediate format works** — no need to maintain draw.io XML manipulation code; just generate SVG directly
