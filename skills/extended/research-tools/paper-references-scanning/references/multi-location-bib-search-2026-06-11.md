# Multi-Location Bib Search Pattern (2026-06-11)

## Discovery

During the 2026-06-11 D8/D10a scan of 151 papers, the canonical search path `06-references/references.bib` only found 24 papers. The remaining 127 papers had bib references in other locations.

## Actual Bib File Locations Found

| Location Pattern | Count | Notes |
|-----------------|-------|-------|
| `<paper>/references.bib` (root) | ~20 | Most common alternative |
| `<paper>/06-references/references.bib` | ~20 | Canonical path |
| `09-manuscript/<paper>/references.bib` | ~2 | Nested under 09-manuscript |
| `01-manuscript/<paper>/references.bib` | ~1 | Nested under 01-manuscript |
| `<paper>/paper.bib` | ~6 | Named after paper |
| `<paper>/enhanced_refs/enhanced.bib` | Rare | Enhanced variant |
| No bib file (inline thebibliography) | ~84 | Bibitem entries embedded in tex |

## Search Algorithm (Recommended)

```
For each paper directory P:
  1. Try P/06-references/references.bib
  2. Try P/references.bib
  3. Try P/<name>.bib (where <name> = basename(P))
  4. Try P/*/references.bib (first-level subdirs)
  5. Try P/*/01-manuscript/paper.tex (for inline thebibliography)
  6. If none found: treat as "inline references only" — count \bibitem{} in tex
```

## Key Finding: Inline thebibliography

84 papers have `\cite{}` calls in their tex body but NO `.bib` file. Their references are stored as raw `\bibitem{}` entries in the `thebibliography` environment at the end of the tex file.

These papers:
- Have D8 > 0 (from `\bibitem{}` counting)
- Have D10a ≥ 80% if their `\cite{}` keys match `\bibitem{}` keys
- Do NOT have a separate `.bib` file for maintenance
- Are harder to update (must edit tex directly to add/remove references)

Detection: `cited_count > 0 and bib_path is None and D8 > 0` → inline thebibliography.

## DOI Regex Fix

The original regex `[Dd][Oo][Ii]\s*=\s*"\{?([^}"\s]+)\}?"?` matched ZERO entries because it required the quote character `"` to match the brace style `{`/`}` inconsistently.

Working patterns:
- `r'(?:doi|DOI)\s*=\s*(?:["{]?([^}"\s]+?)["}]?)'` — general purpose
- `r'doi\s*=\s*\{([^}]+)\}'` — standard BibTeX only

## Cross-Scan Comparison

| Metric | 2026-06-07 | 2026-06-11 |
|--------|-----------|-----------|
| Total papers | 95 | 151 |
| With bib (canonical) | ~30 | 24 |
| With inline refs | ~35 | 84 |
| No refs at all | ~30 | 37 |
| Healthy | 6 (6%) | 3 (2%) |

The library grew by 56 papers since 2026-06-07, but the proportion of inline-thebibliography papers grew faster than the bib-file papers, reducing the overall healthy count.
