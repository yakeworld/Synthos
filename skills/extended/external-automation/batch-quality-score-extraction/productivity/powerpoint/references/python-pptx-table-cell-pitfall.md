# python-pptx Table Cell Access — Critical Pitfall

**Date discovered:** 2026-06-07  
**Class of tasks:** python-pptx presentations, table cells, text formatting

## Problem

`table.cell(r, c)` returns a `_Cell` object that does **NOT** have a `.paragraphs` attribute directly.

```python
# ❌ FAILS — AttributeError: '_Cell' object has no attribute 'paragraphs'
cell = table.cell(r, c)
cell.text = val
for p in cell.paragraphs:  # CRASH
    for r in p.runs:
        r.font.size = Pt(12)
```

## Correct Pattern

**Must use `cell.text_frame.paragraphs`:**

```python
cell = table.cell(r, c)
cell.text = val
for p in cell.text_frame.paragraphs:  # ✅ Correct
    for run in p.runs:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x00,0x00,0x00)
        run.font.bold = True
```

## Other Cell Operations

```python
# Set text (auto-creates text_frame.paragraphs if needed)
cell.text = "header text"

# Access text_frame directly
tf = cell.text_frame
tf.word_wrap = True

# Multiple paragraphs
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
run = p.add_run()
run.text = "First paragraph"
run.font.size = Pt(14)
```

## Full Table Style Example

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[6])

table = slide.shapes.add_table(rows=4, cols=3,
    Inches(1), Inches(1), Inches(9), Inches(3)).table

# Header row
headers = ["Name", "Value", "Status"]
for i, h in enumerate(headers):
    cell = table.cell(0, i)
    cell.text = h
    for p in cell.text_frame.paragraphs:       # ✅ text_frame
        p.alignment = PP_ALIGN.CENTER
        for run in p.runs:
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0x00,0x5B,0xA6)

# Data rows
data = [["Alice", "42", "Active"], ["Bob", "35", "Inactive"]]
for r, row in enumerate(data):
    bg = RGBColor(0xF0,0xF2,0xF5) if r % 2 == 0 else RGBColor(0xFF,0xFF,0xFF)
    for c, val in enumerate(row):
        cell = table.cell(r + 1, c)
        cell.text = val
        for p in cell.text_frame.paragraphs:     # ✅ text_frame
            for run in p.runs:
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(0x1A,0x27,0x44)
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg

prs.save("/tmp/example.pptx")
```

## Key Takeaways

| Do | Don't |
|----|-------|
| `cell.text_frame.paragraphs` | `cell.paragraphs` |
| `cell.text_frame.word_wrap = True` | assume it's on by default |
| `cell.text = "value"` auto-creates paragraphs | manually create paragraphs for simple text |
| `PP_ALIGN.CENTER` for alignment | assume left-aligned |
| `Pt()` for font sizes | use pixel/point values directly |
