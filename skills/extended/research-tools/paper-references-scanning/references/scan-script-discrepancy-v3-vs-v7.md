# Scan Script Discrepancy: v3 vs v7 (2026-06-20)

**Problem**: Two scan scripts exist with fundamentally different D8/D10a algorithms. Running both and comparing raw numbers produces misleading results.

## Algorithm Comparison

| Aspect | v3 (paper-d8-d10a-scan/scripts/scan.py) | v7 (paper-references-scanning/scripts/d8d10a-scan.py) |
|--------|------------------------------------------|-------------------------------------------------------|
| D8 | `1 - orphans/cites` → match rate | Raw bib entry count |
| D10a | `1 - zombies/bib` → consistency | `matched_cites / total_cites` |
| No cites + has bib | Separate status (THEBIB/SKIP) | Auto=100% (self-referenced rule) |
| Bib file search | Only `references.bib` | Broader: `{name}.bib`, parent `references.bib`, `enhanced_refs/enhanced.bib` |
| Comment filtering | None | Line-by-line comment detection |
| Output | Markdown report | JSON to stdout |

## Impact

With 93 papers in library:
- **v3**: 12 PASS, 13 FAIL, 67 THEBIB, 1 WARN, 1 SKIP
- **v7**: 91/93 at D10a=100% (because no-cites auto=100%), D8 shows raw counts (0-75)

These are **completely incompatible** for comparison.

## Rule

G1-G7 pipeline gates use **v3 metrics** (paper-d8-d10a-scan). v7 is for raw inventory and structural audit only. When reporting scan results, always state which script was used.
