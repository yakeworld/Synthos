# Figure Audit Runbook — Refined Pattern (2026-06-27)

## When to Run
- User says "检查论文配图" / "review figures"
- Paper delivery before submission
- After any figure modification cycle

## Step 1: 文件完整性 (File Integrity)

```bash
base="/path/to/paper"
find "$base/05-figures" -name "fig*" \( -name "*.pdf" -o -name "*.png" \) | sort
```

## Step 2: 脚本覆盖 (Script Coverage)

```bash
find "$base/03-code" -name "generate_*.py" | sort
```

**Rule**: Every fig*.* in 05-figures/ must have a generate_figname.py in 03-code/ or 03-code/experiments/.

## Step 3: Script Quality Check

For each script, verify:
1. `matplotlib.use('Agg')` — headless
2. `fig.savefig()` — at least one (PDF or PNG)
3. `os.makedirs('05-figures', exist_ok=True)` — creates output dir
4. `PAPER_ROOT` variable — resolves to paper root, not cwd-relative

## Step 4: LaTeX 引用检查 (Reference Check)

```python
import re
with open('01-manuscript/improved.tex') as f:
    tex = f.read()
fig_refs = set(re.findall(r'\\ref\{fig:(\w+)\}', tex))
fig_labels = set(re.findall(r'\\label\{fig:(\w+)\}', tex))
includes = set(re.findall(r'\\includegraphics[^{]*\{[^}]+\}', tex))
```

**Key insight**: `includegraphics` count may differ from `\\ref{}` count. A figure can be in captions without text reference — both valid.

## Step 5: 视觉质量检查 (Visual Quality)

Run `vision_analyze()` on each figure:
1. All labels readable?
2. No text overlap?
3. No elements outside figure boundary?
4. Legend items all visible?

## Session-Specific Lessons (HCS-3WT, 2026-06-27)

1. **fig3 metrics truncation**: Bottom metrics cut off with 5 subplots. Fix: use `ax.text()` with negative y offset + `bbox` for consistent placement.
2. **fig6 sample size error**: n=899 instead of n=699. Verify dataset metadata before plotting.
3. **fig6 legend overlap**: Shared legend at bottom obscures footer. Fix: per-panel legends (lower-right / lower-left) instead of shared.
4. **includegraphics path**: `figures/figX` but real dir is `05-figures/figX`. Use actual relative paths from .tex location.
5. **CSV path in scripts**: Script's OUTPUT_DIR via `os.path.dirname(os.path.abspath(script_path))` resolves to script's dir, NOT cd'd cwd. Always use absolute paths.
