# PDF → Markdown Conversion Workflow

> Prerequisite for knowledge extraction when full-text PDFs are available.

## Why

Raw PDF text extraction (pdfminer.six) produces scrambled output for multi-column academic papers — text reads column-by-column, not logically. `pymupdf4llm` uses layout detection to produce clean Markdown with proper headings, paragraph order, and table structure.

## Installation

```bash
pip install pymupdf pymupdf4llm
```

(~30MB total, no heavy model downloads)

## Conversion

```python
import pymupdf4llm
md_text = pymupdf4llm.to_markdown("paper.pdf")
with open("paper.md", "w", encoding="utf-8") as f:
    f.write(md_text)
```

## Integration with knowledge-acquisition

After PDF download step, immediately convert to Markdown:

```
outputs/runs/<run_id>/
├── pdfs/
│   ├── paper1.pdf
│   └── paper2.pdf
└── markdown/
    ├── paper1.md    ← converted from PDF
    └── paper2.md
```

## What it handles well

| Feature | pymupdf4llm | pdfminer.six |
|---------|-------------|--------------|
| Multi-column layout | ✅ Correct reading order | ❌ Column-by-column |
| Headings | ✅ ## sections | ❌ Plain text |
| Paragraph structure | ✅ Preserved | ❌ Fragmented |
| Tables | ✅ Basic | ❌ Raw text |
| Header/footer | ✅ Stripped | ❌ Mixed in body |

## What it doesn't handle

- Scanned PDFs (needs OCR → marker-pdf, ~5GB)
- Complex equations
- Some heavily formatted tables

In those cases, fall back to reading the abstract from the acquisition output.
