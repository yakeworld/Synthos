# PDF Extraction Tricks for Chinese Competitions

## pdftotext Common Issues

### Garbled Chinese Text
```bash
# Try different encoding
pdftotext -enc GB2312 input.pdf -
pdftotext -enc BIG5 input.pdf -
pdftotext -enc UTF-8 input.pdf -
```

### Tables Become Messy
- `pdftotext` does not preserve table structure
- Solution: Use `pdfplumber` or `tabula-py` for table extraction
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
```

### Multi-Column Layouts
```bash
# Force single column
pdftotext -layout input.pdf -
# Or use -noloc to remove layout info
```

### Scanned/OCR PDFs
```bash
# Check if PDF is scanned
pdfinfo input.pdf | grep -i "scan\|image"
# Use ocrmypdf
ocrmypdf input.pdf output.pdf
```

## pdfminer.six Fallback
```python
from pdfminer.high_level import extract_text
text = extract_text("file.pdf")
# More reliable for complex layouts but slower
```

## Quick Checklist
1. Always test `pdftotext` first (fastest)
2. If garbled, try `-enc GB2312` for Simplified Chinese
3. If still broken, try `pdfminer.six`
4. For scanned PDFs, run `ocrmypdf` first
5. Check table content separately with `pdfplumber`
6. Verify extracted text contains key sections (评分标准, 材料要求, 截止时间)
