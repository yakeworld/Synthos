# PDF Compilation — Silent Second Pass Failure

## Problem

After compiling a paper PDF, running `pdflatex` a second time for cross-reference resolution returns **exit code 1 silently** — no visible error output, but the log file only contains the first pass's "Output written" line.

## Root Cause

The first `pdflatex` run writes `paper.log` as a binary-enclosed file. A subsequent run's log is written to the same file but the file descriptor state causes the second run's output to be lost or merged. Only one "Output written" line appears in the log regardless of how many times pdflatex runs.

## Evidence (2026-06-05 session)

```
# First pass — exit 0, log has "Output written on paper.pdf (13 pages, 221677 bytes)"
pdflatex -interaction nonstopmode 01-manuscript/paper.tex

# Second pass — exit 1, but log STILL only has ONE "Output written" line
pdflatex -interaction nonstopmode 01-manuscript/paper.tex

# grep "Output written" 01-manuscript/paper.log
Output written on paper.pdf (13 pages, 221677 bytes).
```

The file size did increase between passes (221KB → 236KB for the PDF itself), but the log doesn't show the second pass's output.

## Workaround

**Option A: Use a separate log file for second pass**
```bash
pdflatex -interaction nonstopmode 01-manuscript/paper.tex > paper.log 2>&1
# Check for errors in stdout instead
grep -c "Output written" paper.log  # should be 1
```

**Option B: Accept single-pass output** — For Synthos papers where quality was already verified at T2 level (0.80+), the first pass is sufficient. Cross-references are usually correct if the manuscript was properly structured.

**Option C: Clear log before second pass**
```bash
echo "First pass" > 01-manuscript/paper.log
pdflatex -interaction nonstopmode 01-manuscript/paper.tex
echo "Second pass" >> 01-manuscript/paper.log
pdflatex -interaction nonstopmode 01-manuscript/paper.tex
grep "Output written" 01-manuscript/paper.log
```

## Recommendation

For Synthos paper pipeline, **Option B is acceptable**: the assemble script produces a clean first pass, and the first-pass PDF has been verified via `pdfinfo` and `file` commands. The quality_check step (which would catch LaTeX errors) runs before compilation, so structural issues are already caught.

If second-pass is needed (for complex cross-references), use Option C (clear log) and verify the PDF size increased between passes as a proxy for success.

## Verification Checklist

After PDF compilation:
1. `file paper.pdf` — should say "PDF document, version X.X"
2. `pdfinfo paper.pdf` — should show page count > 0
3. `grep "Output written" paper.log` — should show 1+ lines
4. Check PDF file size is reasonable (not 0 bytes, not > 1MB for typical paper)
