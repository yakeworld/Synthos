# Static QA vs Runtime QA — Validation & Pitfalls

**Date**: 2026-06-26
**Context**: figure-qa-check.py static extraction was producing false positives for HCS-3WT Figure 1.
After 3+ iterations, 3 root causes were found and fixed.

## Problem

Static QA script reported 11 errors, but runtime `get_window_extent` showed most were false positives.

## Root Causes & Fixes

### 1. AABB Format Mismatch (Critical)

`parse_fancy_box_patches` returns `(x, y, w, h)` which is converted to AABB `(x, y, x+w, y+h)`.
But `determine_text_box()` received AABB and unpacked as `(bx, by, bw, bh)`, then computed
`bx + bw` = `x_max + width` instead of `x_max`. This made ALL boxes twice as large, causing
every text to match the first box.

**Fix**: Use `(bx, by, bx2, by2)` consistently everywhere. Compare with `bx <= x <= bx2`.

### 2. Multiline Text `\n` Handling

Source code: `"Uncertain\\nCases"` (16 chars including literal backslash-n)
Matplotlib renders: `"Uncertain\nCases"` (actual newline → two lines)

Static estimate: `16 * 8 * 0.55/72 = 0.92in` width → triggers false overflow.
Actual rendered: `max(len("Uncertain"), len("Cases")) * 8 * 0.55/72 = 0.55in` width → no overflow.

**Fix**: `parse_ax_text_calls()` now does `text.replace('\\n', '\n')` to convert literal escapes
to actual newlines before any width estimation.

### 3. Fontsize Multi-line Extraction

Source has:
```python
ax.text(7, 7.5, "PowerTransformer...", ha="center", va="center",
        fontsize=7.5, color="#777777")
```

Single-line regex `fontsize=(\d+)` after the text fails because `fontsize=` is on the next line.
Backs off to default fontsize=8, causing height estimation error.

**Fix**: Line-based search — find line containing text, then search next 3 lines for `fontsize=`.

### 4. Text Overlap False Positives

Old: `tw = len(text) * fontsize * 0.55 / 72` then check `abs(x1-x2) < (tw1+tw2)/2`
This triggered overlaps for texts that are far apart (x gap 1.8in but static estimate each ~2in).

**Fix**: 
- Only check overlap within same box (`bname1 == bname2`)
- Use `get_text_extent` for actual width
- Check actual bounding box overlap, not just anchor distance
- Cross-box texts are free layout — no overlap check

## Verification

After all fixes, figure-qa-check.py on HCS-3WT Figure 1:
- **0 errors** (was 11)
- **0 warnings** (was 2 false positives)
- Only remaining error: real Input Box subtitle overflow (0.1025in) — fixed by moving box bottom
  from 7.55→7.50, height 0.6→0.66, subtitle y 7.5→7.55

## Key Principle

Static regex extraction is inherently lossy for multi-line Python code. Always validate static
results with runtime `get_window_extent` on the actual rendered figure before fixing code.
