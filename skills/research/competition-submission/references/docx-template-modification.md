# Python-docx Template Modification — Verified Patterns

Patterns for reliably modifying .docx templates (e.g., 附件3-大赛申报书.docx, 附件4-建设说明书.docx) used in competition submission workflows.

## Pattern 1: Inspect Before Modify

```python
from docx import Document
doc = Document("template.docx")
# Print table structure first
for t_idx, table in enumerate(doc.tables):
    for r_idx, row in enumerate(table.rows):
        print(f"  Table {t_idx}, Row {r_idx}: {[c.text[:30] for c in row.cells]}")
# Then modify based on actual structure
```

## Pattern 2: Chinese Font Setting

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def ensure_rPr(run):
    """Ensure run has rPr element"""
    if run._element.rPr is None:
        run._element.insert(0, OxmlElement('w:rPr'))

def set_chinese_font(run, font_name="宋体"):
    """Set Chinese font by directly manipulating XML"""
    ensure_rPr(run)
    rPr = run._element.rPr
    
    # Check for existing rFonts (may already exist with different attrs)
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    
    # Set eastAsia attribute (don't replace — just set/add)
    rFonts.set(qn('w:eastAsia'), font_name)
```

**Why this works**: The template's existing runs may have `rPr` and `rFonts` already, but `rFonts` might only have `w:hint` attribute (not `w:eastAsia`). Don't try to replace — just add the `w:eastAsia` attribute.

## Pattern 3: Clearing Cell Content

```python
p = cell.paragraphs[0]
p.clear()  # Remove all runs from this paragraph
run = p.add_run("新内容")
set_chinese_font(run, "宋体")
run.font.size = Pt(10.5)
```

**Important**: Only clear and modify the first paragraph of a cell. The template structure usually has one paragraph per cell with content. Don't iterate over all paragraphs — modify the first one.

## Pattern 4: Table Cell Targeting

When filling a table, identify cells by their position:
- Header row (row 0): labels like "智能体名称", "简介", "应用成效"
- Data rows: row 1 = 简介 content, row 2 = 应用成效 content, etc.
- Special cells: row 3 col 1 = 测试链接, row 3 col 3 = 测试账号

**Always verify** by reading the cell text before and after modification.

## Pattern 5: Word Count Verification

```python
# Chinese character count (not bytes!)
text = "..."  # Your content
char_count = len(text)  # Python counts characters, not bytes
print(f"字数: {char_count} (限2000)")
```

## Common Pitfalls

1. **Don't use glob patterns in ffmpeg**: `ffmpeg -i "scene_*.png"` doesn't work. Use concat list or explicit file list.
2. **Don't assume cell positions are what they look like**: The template may have empty cells or merged cells that shift the layout. Always read all cells first.
3. **Don't clear all paragraphs**: Only clear the first paragraph of a cell. Other paragraphs may be formatting artifacts.
4. **Don't use CSS rgba()**: Pillow uses `(R, G, B)` or `(R, G, B, A)` tuples, not CSS color strings.
5. **Don't forget `-loop 1`**: FFmpeg needs `-loop 1` to repeat a single image for video duration. Without it, each image is treated as one frame.
6. **Don't skip verification**: After modifying a docx, always re-read and print the cell contents to verify the changes took effect.
