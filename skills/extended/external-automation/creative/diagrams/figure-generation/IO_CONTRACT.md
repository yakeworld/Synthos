# Input-Output Contract: figure-generation

## Input

| Field | Type | Required | Description |
|:-------|:-----|:---------|:------------|
| `claim` | str | Yes | Single-sentence falsifiable hypothesis (with verb) |
| `data_path` | str | Yes | CSV/JSON path with column names |
| `figure_type` | str | Yes | bar, scatter, roc, confusion_matrix, bar_h, heat, radar, architecture |
| `export_formats` | list | No | ['svg', 'pdf', 'png'] (default: all three) |
| `dpi` | int | No | 300 (default) |
| `output_dir` | str | No | Default: `./figures/` |
| `panel_config` | dict | No | Number of panels, layout arrangement |
| `journal_target` | str | No | 'nature', 'science', 'sci-2-3', 'conference' |

## Output

| Field | Type | Description |
|:-------|:-----|:------------|
| `image_paths` | list[str] | Generated file paths (SVG, PDF, PNG) |
| `fig_size` | tuple(int,int) | Figure dimensions in inches |
| `panel_count` | int | Number of panels |
| `qa_passed` | bool | All 6 QA checks passed |
| `qa_report` | str | Quality report content |

## Contract Validation

### Pre-conditions
1. Data file exists and is readable
2. `claim` is a single sentence with a verb
3. `figure_type` is one of the supported types
4. Required columns exist in data file
5. Sample size > 0

### Post-conditions
1. All output files exist and are non-empty
2. Text is within figure boundary
3. All boxes within FIG_W/FIG_H
4. Arrow endpoints inside target boxes
5. No text overlap
6. Color-blind safe (when >=3 colors)

### Failure Handling
- Pre-condition not met -> request missing info, do NOT proceed
- Post-condition not met -> enter revision loop, show diff
