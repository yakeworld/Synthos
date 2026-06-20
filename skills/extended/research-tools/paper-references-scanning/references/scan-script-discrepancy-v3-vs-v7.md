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

## Metric Cross-Mapping (2026-06-21 confirmation)

| V3 metric | V7 equivalent | Notes |
|-----------|---------------|-------|
| D8 (`1 - orphans/cites`) | `d10a` (= `matched/total_cites`) | V7's `d10a` is actually the same formula as V3's D8. Despite different names, they measure the same thing: citation existence (1 - orphan rate). |
| D10a (`1 - zombies/bib`) | **No direct equivalent** | V7 lists zombies per paper but does not compute `matched/bib` as a ratio. V7 has no zombie-consistency metric. |
| THEBIB status | `bib_source=inline` | 70/93 papers (2026-06-21 scan) |
| No bib source | `bib_source=none` | 4/93 papers; if `total_cites > 0`, it's a structural gap (e.g., orthokeratology: 17 cites, 17 orphans) |
| Auto 100% (no cites) | V7 sets D10a=100% for 0-cite papers | V3 leaves these as THEBIB/SKIP status |

**Critical**: V7's `d10a` field name is misleading — it corresponds to V3's D8, not V3's D10a. When reading v7 output, treat `d10a` as "citation existence rate" and note that v7 does not provide a "citation consistency rate" (v3's D10a).

## Rule

G1-G7 pipeline gates use **v3 metrics** (paper-d8-d8a-scan). v7 is for raw inventory and structural audit only. When reporting scan results, always state which script was used. Always use the cross-mapping table above to relate v7 output to v3 concepts.
