# pima-crispdm Reference Directory Normalization Case Study (2026-06-18)

## Problem
`pima-crispdm/06-references/` had a completely disorganized structure:
- Root directory: 7 old PDFs from a different project (NOT matching current Bib)
- `pdfs/` subdirectory: 44 PDFs (mixed old + new, some not matching Bib)
- `pdfs_md/` subdirectory: 40 MD files (NotebookLM artifacts)
- Metadata files: `bibkey-map.json`, `notebooklm-sources.json`, `REFERENCE_MANIFEST.md`
- `references.bib`: 29 entries (only some matched the PDFs)

## Diagnosis
- The old PDFs were from a DIFFERENT project's NotebookLM import
- Bib entries like `Kapoor2024Leakage` were actually Rosenblatt2024 (wrong paper)
- The `REFERENCE_MANIFEST.md` recorded 43 references for the old project, not the current 29
- Crossref verification showed 13/29 DOIs failed (due to wrong data, not just missing PDFs)

## Resolution
1. Deleted 7 old PDFs from root directory
2. Deleted 3 metadata files (`bibkey-map.json`, `notebooklm-sources.json`, `REFERENCE_MANIFEST.md`)
3. Copied 8 matching PDFs from `pdfs/` to root directory
4. Created 2 symbolic links (`Collins2015TRIPOD.pdf → Collins2015.pdf`, `Lundberg2017SHAP.pdf → Lundberg2017.pdf`)
5. Result: 18 PDFs/links in root + `references.bib` (29 entries)

## Key Lesson
**Always normalize reference directories before running quality scans.** A messy directory structure produces unreliable D10a/D8 metrics because the PDF count doesn't match Bib count, making it impossible to determine if a Bib entry has a supporting PDF.

## MedData Coverage Gap
After normalization, only 1 of 13 missing PDFs (Kapoor2023Leakage) was found in MedData. The other 12 Western English papers (Elsevier, Springer, BMJ, etc.) were NOT in the MedData database. MedData only covers Chinese/domestic medical literature.