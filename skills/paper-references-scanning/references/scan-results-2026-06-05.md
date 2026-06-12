# Scan Results Reference

These are actual scan results from the paper library. Useful for comparing against future runs.

## Summary

- 11 papers scanned
- All 11 show D10a = 100.0%
- 8 papers with compiled .bbl artifacts
- 2 papers with inline `thebibliography` (no .bib file): `crispdm-heart`, `data-leakage-breast-cancer-critical-audit`
- 1 paper with `thebibliography` in .bib (3wd-framework): `3wd-framework-trustworthy-clinical-ai`

## Key Findings

- `pima-crispdm`: 33 D8, 33 cites, 100% — hyphenated bib keys (`Norgeot2020MI-CLAIM`) handled correctly
- `dual-ellipse-pupil-localization`: 42 D8, 42 cites, 100% — largest reference set
- `membranous-scc-reconstruction`: 33 D8, 33 cites, 100% — cleanest with .bbl

## Script Usage

Run via: `python3 scripts/d8d10a-scan.py` from skill directory with papers_dir updated to your target.
