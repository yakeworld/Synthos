---
name: python-docx
description: "Create, read, edit .docx files using python-docx. Covers reading templates, filling tables and paragraphs, setting Chinese fonts (East Asia rFonts), page setup, table manipulation, preserving structure, and converting between formats. Related to powerpoint (pptx) and ocr-and-documents (PDF extraction)."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [DOCX, Word, Documents, python-docx, Office, Templates, Tables, Fonts]
    related_skills: [powerpoint, ocr-and-documents]
---

# python-docx: DOCX Creation, Reading, Editing

For PDFs: see `ocr-and-documents`. For PPTX: see `powerpoint`.
This skill covers **.docx files** with `python-docx` (also known as `python-docx` or `docx` on PyPI).

## When to use

Use this skill any time a `.docx` file is involved — creating, reading, editing, filling templates, or converting from/to DOCX. This includes: filling form fields, modifying tables, adding content, setting fonts, page layout, headers/footers, and extracting text.

## Installation

```bash
pip install python-docx
```

**⚠️ Sandbox vs Terminal**: `python-docx` may not be available in the sandbox. If `ModuleNotFoundError: No module named 'docx'`, run via terminal instead:

```bash
python3 -c "import docx; print('OK')"  # Test availability
```

If terminal also lacks it, install with: `pip3 install python-docx --break-system-packages`

## Core API Quick Reference

### Opening & Saving

```python
from docx import Document

# Open existing
doc = Document("template.docx")

# Create new
doc = Document()

# Save
doc.save("output.docx")
```

### Adding Paragraphs

```python
p = doc.add_paragraph()
run = p.add_run("Hello world")
run.font.size = Pt(12)
run.font.bold = True
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.style = doc.styles['Heading 1']  # Use existing styles
```

### Adding Tables

```python
table = doc.add_table(rows=3, cols=4, style='Table Grid')
table.alignment = WD_TABLE_ALIGNMENT.CENTER

# Set column widths
for row in table.rows:
    for i, w in enumerate([Cm(2), Cm(5), Cm(3), Cm(3)]):
        row.cells[i].width = w

# Set cell content
table.rows[0].cells[0].text = "Header"
table.rows[1].cells[0].text = "Data"

# Clear and set content in existing cells
p = table.rows[1].cells[0].paragraphs[0]
p.clear()
run = p.add_run("New content")
```

### Setting Chinese Fonts (East Asia rFonts)

**CRITICAL**: The `w:rPr` element may not exist on new runs, and `rFonts` may lack the `w:eastAsia` attribute. Always handle both:

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def ensure_rPr(run):
    """Ensure run has rPr element"""
    if run._element.rPr is None:
        run._element.insert(0, OxmlElement('w:rPr'))

def set_chinese_font(run, font_name="宋体"):
    """Set Chinese font for a run"""
    ensure_rPr(run)
    rPr = run._element.rPr
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:eastAsia'), font_name)

# Usage:
run = p.add_run("中文文本")
set_chinese_font(run, "黑体")
run.font.size = Pt(12)
```

**Common Chinese fonts** (check with `fc-list :lang=zh`):
- `黑体` — Bold/heading style
- `宋体` — Body text (default)
- `仿宋` — Formal/document style
- `楷体` — Calligraphic/emphasis
- `微软雅黑` — Modern UI style

### Modifying Existing Templates

When working with pre-existing DOCX templates (most common case):

```python
doc = Document("template.docx")
table = doc.tables[0]

# Fill existing table cells (DO NOT replace the table)
for cell_idx in [1, 2, 3]:
    cell = table.rows[1].cells[cell_idx]
    p = cell.paragraphs[0]
    p.clear()  # Clear old content
    run = p.add_run(content_text)
    set_chinese_font(run, "宋体")
    run.font.size = Pt(10.5)

# For paragraph-level template fields
p = doc.paragraphs[0]
p.clear()
run = p.add_run("New title")
```

**Key patterns**:
- **DO** modify existing cells/paragraphs in templates
- **DO NOT** clear `doc.paragraphs` and rebuild — this breaks the template's hidden structure
- **DO** use `p.clear()` to remove old content before writing new
- **DO** preserve existing cell formatting if present
- **DON'T** recreate the table — templates often have specific column widths and merged cells

### Page Setup

```python
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
```

### Reading DOCX Content

```python
doc = Document("document.docx")

# Read all paragraphs
for p in doc.paragraphs:
    print(f"[{p.style.name}] {p.text}")

# Read tables
for i, table in enumerate(doc.tables):
    for row in table.rows:
        print([cell.text for cell in row.cells])

# Read tables as structured data
import csv
with open("output.csv", "w") as f:
    writer = csv.writer(f)
    for table in doc.tables:
        for row in table.rows:
            writer.writerow([cell.text for cell in row.cells])
```

### Clearing Existing Content

```python
# Clear paragraphs (be careful — removes all paragraphs)
for p in doc.paragraphs[:]:
    p._element.getparent().remove(p._element)

# Clear table
for t in list(doc.tables):
    t._element.getparent().remove(t._element)

# Clear single cell content
p = cell.paragraphs[0]
p.clear()
```

## Filling Forms: Common Patterns

### Pattern 1: Simple Table-Based Form (Most Common for Competitions/Forms)

Many Chinese competition/government forms use a 4-column table structure:

| Column 0 | Column 1 (content) | Column 2 (same content) | Column 3 (same content) |
|----------|-------------------|------------------------|------------------------|
| Label    | User input        | User input             | User input             |

```python
table = doc.tables[0]

# Row 0: Name
p = table.rows[0].cells[1].paragraphs[0]
p.clear()
run = p.add_run("Project Name")
set_chinese_font(run, "黑体")
run.font.size = Pt(14)
run.font.bold = True

# Row 1: Long-form content (split across cols 1-3)
p = table.rows[1].cells[1].paragraphs[0]
p.clear()
run = p.add_run("Long content here...")
set_chinese_font(run, "宋体")
run.font.size = Pt(10.5)
```

### Pattern 2: Paragraph-Based Labels

Template has text like `[name]`, `[description]` etc. that you replace:

```python
for p in doc.paragraphs:
    if "[name]" in p.text:
        p.clear()
        run = p.add_run("Actual Name")
        set_chinese_font(run, "黑体")
        run.font.size = Pt(12)
```

### Pattern 3: Checkbox Selection

```python
# Replace placeholder checkboxes with checked ones
p = table.rows[4].cells[1].paragraphs[0]
p.clear()
run = p.add_run("☑ Option 1    ☐ Option 2")
set_chinese_font(run, "宋体")
```

## Pitfalls

- **`rPr` can be None**: New runs created via `add_run()` may not have `rPr`. Always call `ensure_rPr(run)` before setting font attributes.
- **`rFonts` may lack `w:eastAsia`**: The existing element may only have `w:hint`. Use `.set(qn('w:eastAsia'), ...)` to add the attribute, not `.set()` to replace.
- **`p.clear()` clears the paragraph structure**: Only clear the first paragraph in a cell, not all. Other cells' content in the same row may share the same underlying paragraph.
- **Sandbox has no `python-docx`**: If `ModuleNotFoundError: No module named 'docx'`, switch to terminal execution. The sandbox environment is isolated.
- **Don't replace whole tables in templates**: Template tables have specific column widths, merged cells, and sometimes hidden structural elements. Modify cell content in place.
- **Chinese font availability**: Not all systems have Chinese fonts installed. Check with `fc-list :lang=zh` first. Common paths: `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` or `/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc`.
- **Line breaks**: `\n` in `add_run()` creates a single run with line breaks. For separate paragraphs, add a new `add_paragraph()` instead.
- **Table content sharing**: In Word, cells[1], cells[2], cells[3] of the same row may share the same underlying content. Writing to cells[1] is often sufficient — it spills to the others.
- **Old `.doc` format NOT supported**: `python-docx` only handles `.docx` (Office Open XML). Legacy `.doc` (OLE2/Word 97-2003) files raise `ValueError` or `PackageNotFoundError`. **Fix**: Convert with LibreOffice:
  ```bash
  libreoffice --headless --convert-to docx input.doc --outdir /tmp/
  ```
  Then open the converted file with `Document()`. LibreOffice may warn about Java (`failed to launch javaldx`), but the conversion still succeeds. Check availability: `which libreoffice`.

## Templates

See `templates/fill_form.py` — generic function for filling DOCX form tables.

## Scripts

See `scripts/fill_template.py` — reusable helper for filling pre-existing DOCX templates with structured content.
