# Cross-Repo Code Recovery for Figure Scripts

## Problem
Figure generation scripts live in multiple locations across the Synthos workspace:
- `/media/yakeworld/sda2/Synthos/outputs/papers/<paper>/03-code/experiments/` — active development
- `/media/yakeworld/sda2/Synthos/outputs/papers/<paper>/05-figures/` — output (figures only)
- `/media/yakeworld/sda2/Synthos/outputs/papers/<paper>/figures/` — third output copy
- `/media/yakeworld/sda2/academic_writer/article<id>_<name>/` — original master copy (before Synthos migration)

When a figure script in `03-code/` is modified/lost/broken, the **only** reliable source is the `academic_writer/` directory where it was originally generated.

## Recovery Steps

1. **Check `academic_writer/` first** — look for `generate_figures.py` or `generate_figures_v2.py`
   ```bash
   find /media/yakeworld/sda2/academic_writer/ -name "generate_fig*" -o -name "fig1*"
   ```

2. **Extract the specific function** — use `sed` or `head`/`tail` to extract the function from the master script:
   ```bash
   grep -n "def generate_system_architecture\|def generate_roc" path/to/generate_figures_v2.py
   # Then extract lines: head -n <end_line> file.py | tail -n +<start_line>
   ```

3. **Fix paths before using** — the original uses absolute paths like:
   ```python
   OUTPUT_DIR = "/media/yakeworld/sda2/academic_writer/article10_breast/figures"
   results_file = "/media/yakeworld/sda2/academic_writer/article10_breast/generalization_results.json"
   ```
   Replace with relative paths:
   ```python
   OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '05-figures')
   results_file = '../generalization_results.json'
   ```

4. **Add missing boilerplate** — the original may be missing:
   - `if __name__ == '__main__': generate_system_architecture()`
   - `plt.close(fig)` (prevents memory leaks)
   - `print()` statements for debugging

5. **Verify size match** — compare generated PNG size:
   - Original: 703228 bytes (from May 8 generation)
   - If significantly different (<500K), there's content missing

6. **Sync to all locations**:
   ```bash
   cp fig.png 05-figures/
   cp fig.png 03-code/05-figures/
   cp fig.png figures/
   ```

## Key Differences Between Scripts

| Aspect | academic_writer version | Synthos version |
|--------|----------------------|-----------------|
| figsize | `(14, 9.5)` inches | Often different |
| rcParams | seaborn-styled, serif fonts | Minimal matplotlib defaults |
| DPI | figure=150, savefig=300 | Usually just savefig dpi |
| Color palette | C_EXPERT_A/B/C defined at top | Hardcoded hex values |
| Structure | Single file, multiple figures | Split per figure, separate scripts |
| Data loading | loads from JSON at runtime | Hardcoded or no data |

## Lesson (2026-06-26)

When a user says "这张图完全不同了" (this figure is completely different), it means:
1. The code was reconstructed from memory, not from the original source
2. Missing rcParams, color definitions, or text elements changed the output
3. **Always** check `academic_writer/` first before trying to reconstruct