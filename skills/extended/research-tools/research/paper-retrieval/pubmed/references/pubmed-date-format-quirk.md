# PubMed E-utilities Date Range Format Quirk

## Discovery (Cycle 187 — 2026-06-22)

While running Autonomous Core Researcher's PLR-H1 validation scan, all date-filtered PubMed queries silently returned **0 hits** despite bare (unfiltered) queries returning dozens of results.

### Root Cause

The PubMed E-utilities `esearch.fcgi` API **does not support** the `..` (double-dot) date separator that was the standard in older PubMed web interface syntax.

| Syntax | Works? | Example |
|:-------|:------:|:--------|
| `..` double-dot with quotes | ❌ | `"2025/01/01..2026/06/22"[Date - Publication]` → **0 hits** |
| `:` colon, no quotes | ✅ | `2025/01/01:2026/06/22[Date - Publication]` → correct count |
| `:` colon, quoted, separate fields | ✅ | `"2025/01/01"[Date - Publication] : "2026/06/22"[Date - Publication]` → correct count |

### Why It's Dangerous

The `..` format **does not raise an error** — it returns HTTP 200 with `count: 0` and empty `idlist`. Every prior cron cycle that used date filtering was silently underreporting or zeroing out results.

### Fix Applied (Cycle 187)

In `scripts/pubmed-urllib.py`:

```python
# Auto-convert ".." to ":" for backward compatibility
fixed_range = date_range.replace('..', ':')
query += f' AND {fixed_range}[Date - Publication]'
```

Key points:
- `replace('..', ':')` handles both old `"2025/01/01..2026/06/22"` and new `"2025/01/01:2026/06/22"` formats
- **Do NOT** wrap the date range in extra parentheses — `({fixed_range}[Date - Publication])` also returns 0 hits
- **Do NOT** double-quote the range value inside the f-string — the date is already a bare string

### Verification

```bash
# Before fix: 0 hits (wrong separator or wrong wrapping)
python3 pubmed-urllib.py "pupillometry AND Alzheimer AND biomarker" "2025/01/01..2026/06/22"
# After fix: 6 hits
python3 pubmed-urllib.py "pupillometry AND Alzheimer AND biomarker" "2025/01/01..2026/06/22"
```

### Affected Cycles

All date-filtered queries in Cycles 176–186 (Autonomous Core Researcher) were affected. The PLR-H1 counts that showed dramatic jumps (4→5→5→11→33→24→51→6) across those cycles are unreliable — the variations were caused by different query refinements accidentally avoiding or triggering the bug, not actual changes in the literature landscape.

**ABSOLUTE_WHITE determinations** (PINN/DT queries without date filters) were **not affected** — those queries returned the correct 0 even without date filtering.

### Recommendations

1. Always verify a date-filtered query against its unfiltered counterpart before trusting results
2. Use the script wrapper (`pubmed-urllib.py`) — it now handles the conversion
3. When constructing raw queries outside the script, use colon format:
   - `2025/01/01:2026/06/22[Date - Publication]`
   - NOT: `"2025/01/01..2026/06/22"[Date - Publication]`
