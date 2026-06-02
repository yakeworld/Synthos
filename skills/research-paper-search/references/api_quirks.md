# API Quirks and Compatibility Notes

This file documents the specific API quirks discovered during implementation of the multi-database search system. Keep this updated as APIs change.

## Crossref

### Invalid `select` fields
These fields are NOT valid in the `select` parameter and will cause the API to return error objects instead of results:
- `publication-date` → use `issued` instead
- `citation-count` → use `is-referenced-by-count` instead

### Error response format
When `select` contains invalid fields, the response is:
```json
{
  "message": [
    {
      "type": "select-not-available",
      "value": "publication-date",
      "message": "Select 'publication-date' specified but there is no such select for this route..."
    }
  ]
}
```
Always check `isinstance(message, list)` before trying to iterate `message['items']`.

### Field format changes
- `issued`: `{date-parts: [[YYYY, MM, DD]]}` — modern standard, check first
- `published-print`: `{date-parts: [[YYYY, MM, DD]]}` — may be absent
- `published-online`: `{date-parts: [[YYYY, MM, DD]]}` — may be absent
- `link`: may be a single-item list `[...]` or a dict `{}` — handle both
- `abstract`: may be absent, empty string, or present with text

## PubMed eUtils

### esummary format
Single PMID response:
```json
{
  "result": {
    "uid": "42095638",
    "title": "...",
    "pubdate": "...",
    "authors": [...]
  }
}
```
Multiple PMID response:
```json
{
  "result": {
    "uids": ["42095638", "42095637"],
    "42095638": { ... },
    "42095637": { ... }
  }
}
```
For single PMID, the data is at `result['uid']` which is the PMID STRING, not a dict. For multiple, it's at `result['42095638']` which IS a dict.

### articleids format
Always a list of dicts:
```json
"articleids": [
  {"idtype": "pubmed", "idtypen": 1, "value": "42095638"},
  {"idtype": "doi", "idtypen": 3, "value": "10.1177/10870547261448262"},
  {"idtype": "pmc", "idtypen": 5, "value": "PMC1234567"}
]
```
NOT a dict like `{"doi": "10.1234/test"}`. Must iterate and match `idtype`.

### PMCID format
- May be absent: not in the dict at all
- May be string "N/A" when no PMC ID exists
- May be string like "PMC1234567" with prefix
- Strip "PMC" prefix before using as URL component: `str(pmcid).replace('PMC', '')`

## OpenAlex

### abstract_inverted_index
Abstract stored as position-based word index:
```json
"abstract_inverted_index": {
  "0": "Behavioral",
  "1": "inhibition",
  "2": "sustained",
  ...
}
```
Must sort by numeric key and join words with spaces. Keys can be non-numeric for bold/italic markers.

### ids vs external_ids
OpenAlex uses `ids` not `external_ids`:
```json
"ids": {
  "openalex": "https://openalex.org/W2106131177",
  "doi": "https://doi.org/10.1037/0033-2909.121.1.65",
  "pmid": "https://pubmed.ncbi.nlm.nih.gov/9000892",
  "mag": "2106131177"
}
```
The DOI includes the `https://doi.org/` prefix — must strip it.

## PDFminer.six

### Version 20221105 on Ubuntu 22.04 → LATER VERSION
- **`extract_text()` uses `file_path=`** — NOT `pdf_file=` (that was an intermediate version) or `pdf_path=`
- `extract_pages()` uses `file_path=`
- `extract_table()` uses `file_path=`
- `out_type` parameter was removed — do not pass it
- `PDFDocument` has NO `get_info()`, `initialize()`, or `catalog` attributes
- Use pikepdf for metadata extraction instead

### pikepdf for metadata
```python
import pikepdf
doc = pikepdf.open(pdf_path)
docinfo = doc.docinfo  # {'/Title': '', '/Author': '', ...}
doc.pages  # page count
doc.pdf_version  # "1.5"
doc.close()
```

## Semantic Scholar

### Rate limits
Free tier has rate limits visible in `X-RateLimit` headers. Use rate limiter pattern:
- Track request timestamps in a sliding window
- Wait if limit exceeded before next request

### Endpoints
- `/paper/search/bulk` — bulk search, works for large queries
- `/paper/search` — single query search
- `/paper/{id}` — get paper details
- `/paper/{id}/references` — get references
- `/paper/{id}/citations` — get citations
- `/papers/forpaper/{id}` — get recommendations

## BASE (Bielefeld Academic Search Engine)
- Mainly provides HTML, not JSON
- JSON endpoint unreliable — most queries return HTML
- Consider skipping BASE in production or using a different approach
