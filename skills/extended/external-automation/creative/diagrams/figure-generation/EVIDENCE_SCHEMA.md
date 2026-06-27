# Evidence Schema: figure-generation

## Evidence Types

| Type | Format | Example |
|:-----|:--------|:--------|
| Source code | `.py` | `generate_fig2_roc.py` in `03-code/experiments/` |
| Output image | `.svg/.pdf/.png` | `05-figures/fig2_roc_curves.svg` |
| QA report | `.md` | `07-quality/qa-fig2.md` |
| Data source | `.csv/.json` | `01-data/experiment_results.json` |

## Evidence Storage

```
paper/
├── 03-code/experiments/generate_figX.py    # Source code
├── 05-figures/figX.svg                     # Editable vector
├── 05-figures/figX.pdf                     # Publication-ready PDF
├── 05-figures/figX.png                     # High-res raster
└── 07-quality/qa-figX.md                   # QA report
```

## Validation Method

1. **Source code**: `python generate_figX.py` must produce identical output every run
2. **Output files**: `md5sum` across all copies must match
3. **QA report**: All 6 checks must pass (no errors, no warnings)

## Evidence Retrieval

- When user says "show the figure" -> `ls 05-figures/figX.*`
- When user says "show the code" -> `ls 03-code/experiments/generate_figX.py`
- When user says "show QA" -> `cat 07-quality/qa-figX.md`

## Retention

- Source code: Retain for entire project lifecycle
- Output images: Retain until paper submission
- QA reports: Retain for 1 year after submission
