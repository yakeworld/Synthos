# PubMed E-utilities XML Parsing — Common Traps

## Trap: `int()` on XML fragments fails with control characters

```python
# BROKEN — int() on raw XML fragment fails silently
data = req.read().decode()
count = int(data.split('<Count>')[1].split('>')[1].split('<')[0])
# Returns: invalid literal for int() with base 10: ''
# When XML has no results, <Count>0</Count> returns empty string
```

## Fix: Use `re.search` with safe fallback

```python
import re

data = req.read().decode()
m = re.search(r'<Count>(\d+)', data)
count = int(m.group(1)) if m else 0
# Returns 0 if no results, never raises ValueError
```

## Trap: PubMed E-utilities response format varies by endpoint

- `esearch.fcgi` returns XML with `<Count>`, `<IdList>`, `<WebEnv>`, `<QueryKey>`
- `efetch.fcgi` returns plain text or XML depending on `retmode`
- Always check for empty responses before parsing

## Safe Pattern for All PubMed Endpoints

```python
import re, urllib.request

def safe_pubmed_count(xml_text):
    """Extract count from PubMed XML, safe for empty results."""
    m = re.search(r'<Count>(\d+)', xml_text)
    return int(m.group(1)) if m else 0

def safe_pubmed_ids(xml_text):
    """Extract all IDs from PubMed XML, safe for empty results."""
    return [m.group(1) for m in re.finditer(r'<Id>(\d+)', xml_text)]
```

## Session Notes (2026-06-07)

This session failed with `int()` parsing on 5/5 PubMed queries, all returning `invalid literal for int()`. The issue was that the previous session's code (used in v61-v75 logs) had been using `split()`-based parsing which silently failed when responses contained unexpected whitespace or empty fields. Switching to `re.search()` fixed all queries.
