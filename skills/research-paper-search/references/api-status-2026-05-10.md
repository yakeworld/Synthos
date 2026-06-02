# API Status Report (Updated 2026-05-22)

## Current Status

| Source | Status | Notes |
|--------|--------|-------|
| PubMed (NCBI E-utilities) | OPERATIONAL | 3 req/s without key, 10 req/s with key |
| arXiv | UNRELIABLE | PDF serving (arxiv.org/pdf/{id}) works with -L for redirects; API endpoint (export.arxiv.org) frequently down (connection opens but 0 bytes returned, timeout). **Try direct PDF URL first, skip API.**
| OpenAlex | OPERATIONAL | Free, no rate limit. Best fallback when others fail. |
| Semantic Scholar | RATE-LIMITED (429) | Parallel requests trigger IP-level 429 ban. Must use serial requests with ≥2s delay. Free API key (100 req/s) available at semanticscholar.org/product/api. |
| Crossref | OPERATIONAL | Returns metadata, not PDFs |
| Unpaywall | NEEDS API KEY | Requires valid email in URL parameter. Without proper registration, returns errors. |

## Workarounds

- **For preprint coverage**: Use OpenAlex (includes bioRxiv/medRxiv preprints)
- **For citation analysis**: Use OpenAlex citation endpoints
- **For BibTeX**: Generate from OpenAlex or Crossref metadata

## Re-registration Links

- Semantic Scholar: https://www.semanticscholar.org/product/api#api-key-form
- NCBI API Key (recommended): https://www.ncbi.nlm.nih.gov/account/ (3 req/s → 10 req/s)