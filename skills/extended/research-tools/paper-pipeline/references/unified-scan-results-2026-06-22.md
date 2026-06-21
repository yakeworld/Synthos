# Unified Paper Scan — Results Reference 2026-06-22

## Key Statistics

- **93 papers scanned**, all D8=1.0000, no placeholder keys
- **Reference format distribution:**
  - bibitem_inline: 67 (references stored in thebibliography of .tex)
  - separate_bib: 9 (dedicated .bib files only)
  - separate_bib+bibitem_inline: 14 (both formats)
  - separate_bib+numbered: 2 (bib + numbered markdown)
  - bibitem_inline+numbered: 1

## Bib Integrity

- **125 .bib files**, 2,842 entries, 2,082 DOIs (73.3% coverage)
- **239 suspicious entries** (mostly @misc without proper fields)
- **201 cross-file duplicates** (mostly consistent)

## Notable Finding: .bib Files Can Contain Markdown

Several `.bib` files (e.g. `102-vestibular-efferent-PINN/07-ref_check/references.bib`) contain numbered markdown references `[1] Author, Title, Journal...` instead of BibTeX format. The unified-scan-v2 script correctly handles this by looking at thebibliography in the `.tex` file for cite key matching.

## Entry Type Case Inconsistency

Mixed case: `@article`, `@Article`, `@ARTICLE` should be normalized to lowercase.
