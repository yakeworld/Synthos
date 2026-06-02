# Scanned Page Replacement — pdftk + ImageMagick

Replace one page of a PDF (e.g., the last page) with a scanned/stamped image.

## Workflow

### 1. Convert scanned image to A4 PDF

```bash
# Resize to A4 at 300dpi (2480×3508), center on white background
convert scan.jpg -resize 2480x3508 -background white -gravity center -extent 2480x3508 stamp_fixed.png
convert stamp_fixed.png -page A4 stamp_page.pdf
```

**Why this approach:**
- `-resize` maintains aspect ratio (image won't stretch)
- `-extent` pads to exact A4 pixel dimensions
- `-page A4` sets the PDF page size (595×842 pts) — otherwise the PDF may be tiny (resource size)
- Verify with: `pdfinfo stamp_page.pdf` → look for `Page size: 595 x 842 pts`

### 2. Merge with pdftk

```bash
# Take pages 1-N from original, append the new scanned page
pdftk A=orig.pdf B=stamp_page.pdf cat A1-4 B1 output result.pdf
```

**Options:**
- `A1-4` = original pages 1-4 (to replace page 5)
- `B1` = page 1 from the stamped file
- For multi-page replacement: `cat A1-N B1-M A{N+1}-end`

### 3. Verify

```bash
pdfinfo result.pdf
# Check: Pages=N+1, Page size=A4
```

## When to use pymupdf instead

If both the original PDF AND the replacement page are text-based (not scanned), use pymupdf instead — no external dependencies:

```python
import pymupdf
orig = pymupdf.open("orig.pdf")
replacement = pymupdf.open("replacement.pdf")
result = pymupdf.open()
result.insert_pdf(orig, from_page=0, to_page=3)    # pages 1-4
result.insert_pdf(replacement, from_page=0, to_page=0)  # new page 5
result.save("result.pdf")
```

**Use pdftk when:** the replacement page is a scanned image (pymupdf may not embed the image correctly at A4 scale).

## Dependencies
- `pdftk-java` (check with `which pdftk` or `pdftk --version`)
- ImageMagick (`convert` — check with `which convert`)
- Poppler (`pdfinfo`, `pdftoppm`)

## Pitfalls
- ImageMagick's default PDF output may have wrong page size — always use `-page A4`
- pdftk sets its own producer metadata; this is fine for submission materials
- If the scanned image is very low resolution (< 150dpi), upscale with `-density 300` before resize
