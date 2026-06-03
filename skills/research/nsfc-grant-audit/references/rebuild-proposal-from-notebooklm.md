# Rebuild Grant Proposal .docx from NotebookLM Sources

## When to Use

The user wants a complete grant application document (.docx) but the original file was uploaded to NotebookLM (not saved to disk), or the only copy is in a NotebookLM notebook.

## Workflow

### Step 1: Confirm the Source Exists in NotebookLM

```bash
notebooklm use "<partial_notebook_id>"
notebooklm source list
```

Look for the original document (e.g., `01_原始标书_PD...docx`) and any analysis/review sources.

### Step 2: Retrieve Full Content via Sequential Short Prompts

Do NOT ask for the whole document in one `notebooklm ask` call — it will time out (60s limit). Instead:

```bash
# Per section — each is short enough to complete in <30s
notebooklm ask "请输出01_原始标书中立项背景部分的完整内容"
notebooklm ask "请输出01_原始标书中研究目标与内容部分的完整内容"
notebooklm ask "请输出01_原始标书中研究方法与技术路线部分的完整内容"
notebooklm ask "请输出01_原始标书中可行性分析部分的完整内容"
notebooklm ask "请输出01_原始标书中预期成果部分的完整内容"
```

Multi-turn conversations auto-continue — no need to re-select the notebook.

### Step 3: Build the .docx with python-docx

Key structure template:

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()

# Set default font (Song Ti for Chinese)
style = doc.styles['Normal']
font = style.font
font.name = '宋体'
font.size = Pt(12)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# Helper: bold + normal mixed text in one paragraph
def add_bold_text(para, text):
    para.add_run(text).bold = True

def add_normal_text(para, text):
    para.add_run(text)

# Title
title = doc.add_heading('项目名称', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Info table
info_table = doc.add_table(rows=N, cols=2, style='Table Grid')
# ... populate key-value pairs

# Sections with headings
doc.add_heading('一、立项的背景和意义', level=1)

# Budget table
budget_table = doc.add_table(rows=M, cols=4, style='Table Grid')
# headers: 序号, 用途, 金额, 说明

doc.save('output.docx')
```

### Step 4: Upload the .docx Back to NotebookLM

```bash
notebooklm source add /path/to/output.docx
notebooklm source rename "<uuid_prefix>" "01_重构申请书_版本号"
```

### Step 5: Send to User

Use `MEDIA:/absolute/path/to/file` in the Feishu response to attach the .docx inline.

## Pitfalls

- **60s timeout on long queries**: Never ask for more than 1-2 sections at a time. Break the document into 4-6 sequential queries.
- **Retrieved text may need deduplication or stitching**: NotebookLM's answer may not be verbatim from the source. Compare across queries and reconcile inconsistencies manually.
- **NotebookLM source titles are truncated in `source list`**: Use UUID prefixes (8+ chars) for `source get` and `source rename` operations.
- **Source content exists even if file not on disk**: The user may have uploaded via another session, Feishu attachment handler, or web UI. Don't assume file was lost.
- **Chinese font rendering**: python-docx needs explicit `w:eastAsia` font setting for Chinese characters. Set it on the Normal style and verify before generating the full document.
