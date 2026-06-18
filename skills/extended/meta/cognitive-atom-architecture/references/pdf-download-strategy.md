# PDF Download Strategy (Atom 1)

Knowledge Acquisition (Atom 1) MUST download full-text PDFs, not just metadata. Default `download_pdfs=True`.

## 6-Stage Download Chain

```
① OA URL (S2 openAccessPdf) → ② arXiv PDF → ③ PMC (PMID→PMCID NCBI Converter)
→ ④ Unpaywall → ⑤ DOI content negotiation → ⑥ Sci-Hub (last resort)
```

## Field Schema

Each paper dict gets: `pdf_path`, `pdf_status`, `pdf_note`, `open_access_url`, `arxiv_id`, `pmid`

pdf_status values: open_access | arxiv | pmc | unpaywall_oa | doi_redirect | scihub | cached | unavailable

## Key Implementation Details

1. **PMID→PMCID conversion**: NCBI ID Converter API: `https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={pmid}&format=json`
2. **S2 openAccessPdf**: Extract from API response: `(item.get("openAccessPdf") or {}).get("url", "")`
3. **arXiv ID**: Parse from `<id>` element: `re.search(r'arxiv.org/abs/([^/]+)', id_text)`
4. **Sci-Hub mirrors**: sci-hub.se, .st, .ru, .ee, .ren — try in order, parse PDF URL from page
5. **Force close**: Use `aiohttp.TCPConnector(force_close=True)` to avoid unclosed session warnings

## Performance Notes

- Never disable Sci-Hub — user explicitly requires it for paywalled papers
- S2 returns 403 when API key expires → set `_S2_DISABLED = True` at module level to skip 8s of retries
- arXiv returns 429 when rate-limited → set `_ARXIV_DISABLED = True` after first 429
- PMC downloads often return HTML stubs instead of PDFs → try PMID→PMCID conversion
- Cache: 24h search cache by query hash saves repeat searches
