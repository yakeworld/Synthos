# PDF-to-Markdown Workflow (pymupdf)

Quick reference for converting academic PDFs to readable Markdown,
confirmed working with Frontiers, Nature/Springer, and JMIR PDFs.

## Preferred Method: pymupdf

```python
import pymupdf
doc = pymupdf.open("paper.pdf")
text = ""
for page in doc:
    text += page.get_text() + "\n\n---\n\n"
with open("paper.md", "w") as f:
    f.write(f"# {paper_title}\n\n{text}")
doc.close()
```

- Produces clean text with paragraph breaks preserved
- Handles complex layouts (multi-column, tables partially)
- Journal compatibility: Frontiers ✅, Nature/Springer ✅, JMIR ✅
- Typical output: 10-15KB per page (12-page PDF → ~57KB markdown)

## Fallback: pdftotext

```bash
pdftotext input.pdf output.md
```

- Faster, less formatting preservation
- Best for text-heavy PDFs without complex layouts

## Fallback 2: pdfminer.six

```python
from pdfminer.high_level import extract_text
text = extract_text(file_path="paper.pdf")
```

- Most portable (no system deps)
- Can struggle with non-standard encodings

## When Each Works Best

| PDF Type | Best Tool | Reason |
|----------|-----------|--------|
| Typeset academic (Frontiers, Nature) | pymupdf | Handles multi-column |
| Simple text | pdftotext | Fastest |
| Scanned/image PDF | Needs OCR (marker-pdf / surya) | None of the above work |
