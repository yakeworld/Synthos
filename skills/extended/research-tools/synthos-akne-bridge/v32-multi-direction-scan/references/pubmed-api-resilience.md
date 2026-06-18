# PubMed API Resilience Patterns

## Pattern: NCBI API Instability (v137)

**Problem:** NCBI eUtils endpoints (eSearch, eFetch, esummary) exhibit intermittent failures across sessions:
- **eFetch JSON parsing errors:** `json.decoder.JSONDecodeError: Extra data: line 2 column 1 (char 9)` — NCBI sometimes sends extra preamble before the JSON `{` object (BOM, comments, or HTML error pages).
- **HTTP 502/503/504:** Intermittent gateway errors, especially during peak usage.
- **esummary structure variance:** Different response structures (`docs` vs `documents` vs `result.uids` → `result.{pmid}`) across calls.
- **Multiple JSON objects:** Sometimes the response contains more than one JSON object, causing `json.loads()` to fail.

**Working pattern (v137):**
1. **Use esummary for titles** (more reliable than eFetch):
   ```python
   url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&version=2.0&retmode=json"
   # Response: {"header":..., "result":{"uids":["{pmid}"],"{pmid}":{"title":"...","pubdate":"...","source":"..."}}}
   ```
2. **Strip BOM and preamble:**
   ```python
   raw = r.read().decode('utf-8').lstrip('\ufeff')
   brace = raw.find('{')
   if brace > 0: raw = raw[brace:]
   fd = json.loads(raw)
   ```
3. **Handle multiple JSON objects:** If `json.loads()` fails, try finding the last `}` and parsing up to it.
4. **Use eSearch first to get IDs**, then eSummary for titles (not eFetch).
5. **Retry 4-5 times** with 2-3 second delays between retries.
6. **Set `User-Agent` header** — NCBI may block requests without one.

**Fallback chain:**
```
eSearch (count) → eSummary (title) → eFetch (detailed) → direct curl with retry
```

## Pattern: esummary response structure

**Structure:**
```json
{
  "header": {"type": "esummary", "version": "0.3"},
  "result": {
    "uids": ["33105416"],
    "33105416": {
      "uid": "33105416",
      "title": "Optic Disc Edema and Posterior Globe Flattening...",
      "pubdate": "2021 Jun 1",
      "source": "J Neuroophthalmol",
      "authors": [{"name": "Albano de Guimarães J"}],
      "lastauthor": "Moura FC"
    }
  }
}
```

**Key:** `result.{pmid}.title` — NOT `result.{pmid}.*title` or `docs.{pmid}.title`.

## Pattern: curl-based title fetch (bypasses Python JSON issues)

When Python `json.loads()` consistently fails, use curl directly:
```bash
# eSummary via curl
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=33105416&version=2.0&retmode=json"

# For text-based extraction, use Python to parse JSON safely
```

The curl command succeeded where Python's urllib failed in one session, indicating the issue may be in how Python handles the HTTP response encoding.

## Pattern: eFetch vs esummary tradeoffs

| Endpoint | Reliability | Use case |
|----------|-------------|----------|
| eSearch | HIGH | Getting PMIDs for queries (always works) |
| esummary | MEDIUM | Getting titles and metadata |
| eFetch | LOW | Getting full abstracts (frequently fails) |

**Rule of thumb:** Only use eFetch when you need abstract text. For title checks, esummary is sufficient and more reliable.
