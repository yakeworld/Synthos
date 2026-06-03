---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, marker-pdf)."
signature: "document_path: str -> extracted_text: str"
related_skills: [airtable, chinese-form-automation, google-workspace, jupyter-live-kernel, linear]
allowed-tools: [terminal, read_file, write_file, search_files]
version: 2.3.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

### Scanned Page Replacement (pdftk + ImageMagick)

When you need to replace one page in a PDF with a **scanned/stamped image** (e.g., replacing the last page of competition proof materials with a stamped version):

1. Convert the scanned image to A4 PDF with ImageMagick: `convert scan.jpg -resize 2480x3508 -background white -gravity center -extent 2480x3508 stamp_fixed.png && convert stamp_fixed.png -page A4 stamp_page.pdf`
2. Merge with pdftk: `pdftk A=orig.pdf B=stamp_page.pdf cat A1-4 B1 output result.pdf`

Use pdftk instead of pymupdf when the replacement page is a scanned image — pymupdf may not embed scanned images at correct A4 scale. See `references/scanned-page-replacement.md` for full workflow, verification steps, and pitfalls.

---

## Chinese Scanned PDF OCR (tesseract route)

When `marker-pdf` is unavailable (disk space / install time) and `pymupdf` returns 0-50 chars (scanned/no text layer):

```bash
# 1. Check text layer
pdftotext document.pdf - | wc -c
# < 100 chars → scanned, need OCR

# 2. Convert to images
pdftoppm -png -r 300 document.pdf /tmp/page

# 3. OCR with Chinese
tesseract /tmp/page-1.png /tmp/output -l chi_sim
cat /tmp/output.txt

# 4. Batch all pages
for f in /tmp/page-*.png; do
  tesseract "$f" "${f%.png}" -l chi_sim 2>/dev/null
done
cat /tmp/page-*.txt > /tmp/full_text.txt
```

**Alternative: ocrmypdf** (creates a searchable PDF, then use pdftotext):
```bash
ocrmypdf --force-ocr input.pdf /tmp/ocr.pdf
pdftotext /tmp/ocr.pdf -
```

**When to use which:**
| Tool | Pros | Cons |
|:-----|:-----|:-----|
| `tesseract -l chi_sim` | Fast, no deps, direct text output | Per-page files need merging |
| `ocrmypdf --force-ocr` | Single output PDF, preserves layout | Slower, needs tesseract installed |

**Prerequisite check:**
```bash
tesseract --list-langs 2>&1 | grep chi    # Should show chi_sim
# If missing: sudo apt install tesseract-ocr-chi-sim
```

## Chinese Form-Filling (docx/xlsx)

See the `chinese-form-automation` skill for the full workflow: extracting requirements from scanned notifications → analyzing docx/xlsx template structure → filling cells with python-docx/openpyxl → handling merged cells → generating submission guides.

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: use `python-docx` (better than OCR — parses actual structure)
  - Creating/editing DOCX: see `python-docx` skill (templates, forms, Chinese fonts, tables)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)
