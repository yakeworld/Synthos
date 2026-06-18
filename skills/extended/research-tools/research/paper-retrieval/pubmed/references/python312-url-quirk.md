# PubMed urllib Python 3.12 URL Encoding Fix

## Problem (v106 — 2026-06-08)

Python 3.12's `urllib.request.urlopen()` rejects bare spaces in URL path components:

```python
# FAILS — http.client.InvalidURL: "URL can't contain control characters"
urllib.request.urlopen("https://eutils.ncbi.nlm.nih.gov/...&term=eye head coordination&retmode=json")
```

## Fix

Use `urllib.parse.quote_plus(query, safe='')` to encode the query term:

```python
from urllib.parse import quote_plus
safe_term = quote_plus(query, safe='')
url = f"{BASE}esearch.fcgi?db=pubmed&term={safe_term}&retmax={retmax}&retmode=json"
```

## Applied

This fix was applied to `scripts/pubmed-urllib.py`:
- Added `from urllib.parse import quote_plus` import
- Changed `f"...&term={query}..."` to `f"...&term={safe_term}..."` with `quote_plus(query, safe='')`

## Notes

- `quote_plus` encodes spaces as `+`, which PubMed accepts
- `safe=''` ensures all special characters are encoded (conservative)
- This is consistent with the OpenAlex Python 3.12 urllib fix documented in `research-paper-search` skill
