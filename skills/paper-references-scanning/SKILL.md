---
name: paper-references-scanning
description: "Scan paper library for citation health: D8 (bib entry count), D10a (cite-to-bib match rate),   orphans, zombies. Class of tasks: LaTeX reference integrity auditing."
version: 1.0.0
metadata:
  synthos:
    priority: P1
    atom_type: pipeline
    description: "Scan paper library for citation health: D8 (bib entry count), D10a (cite-to-bib match rate), orphans, zombies."
    signature: |
      paper_dir: str -> scan_result: dict | scan_result: dict (d8, d10a, orphans, zombies, bib_health_report)
    related_skills: [knowledge-extraction, knowledge-acquisition, paper-cron-scan, paper-pipeline]


---




# Paper References Scanning (D8/D10a)

## Scope
Scanning LaTeX paper directories for reference integrity metrics.

## Pitfalls

### DOI regex is case-insensitive and handles multiple formats
Bib DOI fields appear as `doi = {value}`, `DOI = {value}`, or `doi="value"`.
- WRONG: `r'[Dd][Oo][Ii]\s*=\s*"\{?([^}"\s]+)\}?"?'` — the `"?` around `{` is too strict; it requires the quote to match the brace style, causing zero matches.
- CORRECT: `r'(?:doi|DOI)\s*=\s*(?:["{]?([^}"\s]+?)["}]?)'` — matches all common DOI formats regardless of quote/brace nesting.
- Even simpler: `r'doi\s*=\s*\{([^}]+)\}'` for standard BibTeX format.

### Bib files exist in multiple locations beyond the canonical search path
The canonical skill searches `06-references/references.bib → {name}.bib → references.bib → enhanced_refs/enhanced.bib`. In practice, bib files are also found:
- At paper root level (e.g., `<paper>/references.bib`)
- In `09-manuscript/<paper>/references.bib` subdirectories
- In any `.bib` file directly under the paper directory
- In deeply nested directories like `01-manuscript/<paper>/references.bib`

When scanning, expand to: first check `06-references/references.bib`, then `<paper>/references.bib`, then any `.bib` in `<paper>/`, then fall back to `01-manuscript/<paper>/` and `09-manuscript/<paper>/`.

### Papers with \bibitem{} in thebibliography but zero \cite{} calls
Some papers list references via raw `\bibitem{}` in the `thebibliography` environment but never call them with `\cite{}` in the body. This results in D8 counting the bibitems but D10a=0% (no citations to match). These are real papers with references — the `\cite{}` may be missing, or the references may be uncited. Detect this pattern: `cited_count == 0 and bibitem_count > 0`. These papers need a `\cite{}` fix, not a new bib file.

### `\\cite` regex uses single-escape in raw strings
`re.compile(r'\\\\cite')` — two backslashes in source, regex engine interprets as one literal backslash.
- `r'\\\\\\\\cite'` → matches double-backslash → WRONG for standard tex files
- `r'\\cite'` → `\c` is invalid regex escape → SyntaxError
- Correct: `r'\\\\cite'`

### Comment detection must distinguish `%` from `\%`
`%%` and `%` at line start = comment. But `$13.9\%$` or `~\%` are NOT comments.
Check `line.lstrip().startswith('%')` only.

### Bib keys can contain hyphens
Use `[^\s,;]+?` instead of `\w+` for bib key capture (`Norgeot2020MI-CLAIM` has `-`).

### Bib key prefix stripping
`bib_key_re` captures `@EntryType{key,` including the prefix. The script strips it by finding `{`, taking after it, then finding `,` and taking before it. Without this, `@Article{Ahmad2020,` won't match cite key `Ahmad2020`, causing false orphans and zombies.

### Commented `\\bibitem{}` must be excluded from D8
Only count uncommented `\bibitem{}` for D8.

### Directory count ≠ Paper count
The `/media/yakeworld/sda2/Synthos/outputs/papers/` directory contains **non-paper subdirectories** mixed with actual paper dirs — ML projects (kaggle-wdbc-classification, stroke-prediction, cleveland-heart-disease), old papers, script directories, reference directories, gap analysis subdirs, etc. The `get_main_tex()` function silently filters these out by looking for a valid `.tex` file. As of 2026-06-12: **187 total directories, only 153 are valid papers**. Always distinguish these numbers in audit reports. The scan script now appends `__metadata__` as the last entry with `total_directories`, `papers_scanned`, and `non_paper_directories` for traceability. **Consumers of the JSON must skip the `__metadata__` entry** and use `papers_scanned` for the true paper count, not `len(results) - 1`.

## Steps

1. Discover paper dirs with `01-manuscript/paper.tex` (excludes `_*` and `lit-reviews`)
2. Extract cite keys from uncommented lines: `\cite{}`, `\citep{}`, `\cite[opt]{}`
3. Find ONE best bib file: `06-references/references.bib` → `{name}.bib` → `references.bib` → `enhanced_refs/enhanced.bib`
4. Also extracts `\bibitem{}` from thebibliography in tex
5. Computes D8, D10a, orphans, zombies, bbl status

## Canonical Skill

This IS the canonical scan skill. The scan script `scripts/d8d10a-scan.py` handles all resolution: inline theinlinebibliography, external .bib files, single-bib-per-paper priority, comment filtering. Run it directly.

## Support Files
- `references/ocular-blood-flow-paper-116.md` — Paper 116 ocular blood flow 2-ODE reference (R2=0.993, Cc=0.45 bifurcation)
- `scripts/d8d10a-scan.py` — Primary scan script. Produces JSON to stdout. Scan logic:
  1. Discovers paper dirs with `01-manuscript/paper.tex` (excludes `_*` and `lit-reviews`)
  2. Extracts uncommented `\cite{}`, `\citep{}`, `\cite[opt]{}` keys
  3. Finds ONE best bib file: 06-references/references.bib → {name}.bib → references.bib → enhanced_refs/enhanced.bib
  4. Also extracts `\bibitem{}` from thebibliography in tex
  5. Computes D8, D10a, orphans, zombies, bbl status
  6. Appends `__metadata__` entry with directory/paper count discrepancy
- `references/scan-results-2026-06-11.md` — Latest full scan: 151 papers, 3 healthy, 148 problems
- `references/scan-results-2026-06-09-v3.md` — Earlier scan: 147 papers, 45 healthy
- `references/scan-results-2026-06-08.md` — Earlier scan
- `references/scan-results-2026-06-12.md` — Updated scan: 153 papers, non-paper dir detection added
- `references/non-paper-directory-taxonomy-2026-06-12.md` — Classification of 33 non-paper directories found in papers/ root