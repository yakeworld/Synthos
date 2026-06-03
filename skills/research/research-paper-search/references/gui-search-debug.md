# GUI Search Error Debugging — 2026-05-08 Session

## Timeline of failures

### Failure 1: 403 Forbidden on search
```
All 3 attempts failed for _async_get: 403, message='Forbidden', url=URL('https://api.semanticscholar.org/graph/v1/paper/search?query=bppv&fields=...&limit=1000')
```

### Failure 2: 500 Internal Server Error
```
HTTP 500: {"message": "Internal Server Error"}
```
Occurs when `limit=1000` is passed to the S2 `/search` endpoint.

### Root Cause Investigation

1. **Searched for "Attention Is All You Need"** → worked initially, then started returning "A Guide to Teaching Elementary Science" (wrong paper).
2. **Traced to endpoint**: Code used `/paper/search/bulk` but the correct endpoint is `/paper/search`. The `/bulk` endpoint doesn't sort by relevance.
3. **Fixed endpoint**: Changed `/paper/search/bulk` → `/paper/search`.
4. **Still getting 500 on GUI**: Traced to `limit=1000` parameter.
5. **Discovered limit=100 cap**: Tested `limit=100, 500, 1000, 2000` via curl:
   - `limit=100`: OK, 100 results
   - `limit=500`: HTTP 500
   - `limit=1000`: HTTP 500
   - `limit=2000`: HTTP 500

### Fix Applied

**File**: `src/api/semantic_scholar.py` line 25
```python
# Before:
params = {'query': query, 'fields': self.fields, 'limit': min(limit, 5000)}
# After:
params = {'query': query, 'fields': self.fields, 'limit': min(limit, 100)}
```

**File**: `src/manager/paper_manager.py` line 58
```python
# Before:
papers_data = await self.paper_provider.search_papers(query)
# After:
papers_data = await self.paper_provider.search_papers(query, limit=100)
```

### Additional Findings

- `Paper.authors` is `List[Dict]`, not `List[Author]` — access via `p.authors[i]['name']`
- `Paper` has no `doi` field — use `p.external_ids.get('DOI', '')`
- `Paper` has no `source` field
- `create_bibtex_entry()` returns `(key, bibtex_string)` tuple, not a dict

### Verification

After fix, search "ADHD" returns 100 papers correctly:
- Paper 1: "Behavioral inhibition, sustained attention, and executive functions" (1997, 7712 citations)
- Paper 2: "The worldwide prevalence of ADHD: a systematic review" (2007, 5459 citations)
- CSV written to `results.csv` with 1704 lines (32 fields)
- BibTeX written to `references.bib` with 13418 lines
