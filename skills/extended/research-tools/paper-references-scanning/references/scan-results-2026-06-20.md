# Scan Results — 2026-06-20

**Two-scan cross-validation**: v3 (markdown report) + v7 (JSON stdout).

## v3 Results (paper-d8-d9a-scan/scripts/scan.py)

| Status | Count |
|--------|-------|
| PASS (D8=100%, D10a=100%) | 12 |
| WARN | 1 |
| FAIL | 13 |
| SKIP | 1 |
| THEBIB | 67 |
| **Total** | **94** |

### Key observations
- 67 of 94 papers use inline thebibliography with no `.bib` file
- 5 papers have template placeholders (`<label>`, `lamport94`) that were never removed
- 7 papers have D8=0.0 (entire citation set unmatched against bib)
- `pima-crispdm`: 75 cites, 34 bib entries, 60+ missing — highest impact
- `hcs3wt-breast-cancer`: 73 cites, 32 bib entries, 15+ missing — high impact

## v7 Results (paper-references-scanning/scripts/d8d10a-scan.py)

- Papers scanned: 93 (94 dirs, 1 non-paper)
- D8=0 (no bib source): 4 papers
- D8=100: 0 papers (v7 D8 is raw bib entry count, not match rate)
- D10a=100%: 91/93 (v7 auto-100% for no-cites papers)
- bib_source=inline: 70 papers
- bib_source=file: 89 papers
- bib_source=none: 4 papers (1 with cites = structural gap)
- Total orphans: 20
- Total zombies: 209

## Cross-Score Note

v3 and v7 produce **completely different** scores because they define D8/D10a differently. See `references/scan-script-discrepancy-v3-vs-v7.md` for full analysis.
