# Figure Verification Checklist

**MANDATORY.** Run in order before presenting any figure to the user.

## Phase 1: Standalone Compile

```
□ Compile: pdflatex fig_NAME.tex
   Expected: "Output written on fig_NAME.pdf (1 page, NNN bytes)"
□ On failure: check fig_NAME.log for the FIRST error line, fix, retry
```

## Phase 2: Visual Content Check

```
□ Text position analysis: pdftotext -bbox fig_NAME.pdf - | extract y-positions
   Group words by Y-coordinate. Verify layers are correctly ordered (top→bottom)
   and that inter-layer gaps ≥ 10pt. Check that content uses ≤90% of page height
   (title should not be within 10pt of page top edge).
□ Text width check: for boxed text, use references/text-width-measurement.md to
   numerically verify text fits inside boxes with ≥10% margin
□ Extract text: pdftotext fig_NAME.pdf -
   Verify ALL expected labels appear (no text was lost/cut off)
□ Check no text from different layers is interleaved (overlap)
□ Check dimensions: pdfinfo fig_NAME.pdf | grep "Page size"
   Width should be reasonable (not > 600pt for single figure)
   Height should be reasonable (not > 500pt before scaling)
□ Vision inspection (if available): pdftoppm -png -r 300 fig_NAME.pdf output.png
   Use vision_analyze to visually inspect for overlap, contrast, alignment,
   and text-clipping issues the text-based check might miss.
```

## Phase 3: Full Paper Integration

```
□ Update paper.tex: check \includegraphics path is correct
□ Compile: pdflatex paper.tex
□ Run bibtex: bibtex paper
□ Double compile: pdflatex + pdflatex (2x for refs and TOC)
□ Final compile: pdflatex paper.tex (3rd pass for stability)
```

## Phase 4: Log Verification

```
□ Check for figure errors: grep -i "overfull.*figure" paper.log
□ Check for missing files: grep -i "can't find\|! error" paper.log
□ Verify figure placement: grep "used on.*fig_" paper.log
   Each figure should appear exactly once with "used on line NN"
□ Verify all 3+ figures are present
```

## Phase 5: Final PDF Check

```
□ Page count: pdfinfo paper.pdf | grep Pages
   Reasonable for content (shouldn't be 1 page more/less than expected)
□ File size: ls -lh paper.pdf
   Reasonable for content (e.g., 300-500KB for 10-page paper)
□ VISUALLY INSPECT by opening paper.pdf and scrolling through
□ Push to user ONLY after all checks pass
```

## Anti-Overlap Checklist

```
□ Layer backgrounds don't cross each other: 
   For each adjacent pair L_i, L_{i+1}: L_i_bg_y_max < L_{i+1}_bg_y_min
   (Lower bg top < Upper bg bottom)
□ Elements don't cross layer boundaries:
   For each layer L_i: all element y coordinates are within L_i's background
□ Inter-layer arrows connect from bg boundary to bg boundary, not through elements
□ Text is not clipped at page edges
□ After \includegraphics scaling, no text is smaller than 6pt equivalent
```

## Common Fixes

| Problem | Fix |
|---------|-----|
| Figures missing from PDF | Re-run: pdflatex → bibtex → pdflatex → pdflatex |
| Figure overlaps text | Reduce scaling or add `[t]` placement |
| Figure appears at wrong page | Use `figure*[t]` for twocolumn |
| Colors wrong in PDF | Check color definitions; recompile |
| Font not found for TikZ | Use `\sffamily` only (avoids missing font errors) |
