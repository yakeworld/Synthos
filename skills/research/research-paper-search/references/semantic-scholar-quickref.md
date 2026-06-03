# Semantic Scholar API Quick Reference

## Endpoint Cheatsheet

| Action | Endpoint |
|--------|----------|
| Search papers | `GET /graph/v1/paper/search?query=QUERY&fields=FIELDS&limit=N` |
| Get paper by ID | `GET /graph/v1/paper/{ID}?fields=FIELDS` |
| Get references | `GET /graph/v1/paper/{ID}/references?limit=N` |
| Get citations | `GET /graph/v1/paper/{ID}/citations?limit=N` |
| Get recommendations | `GET /graph/v1/paper/{ID}/recommendations?limit=N` |

## Search

```bash
curl -s -H "x-api-key: $SEMANTIC_SCHOLAR_API_KEY" \
  "https://api.semanticscholar.org/graph/v1/paper/search?query=Attention+Is+All+You+Need&limit=5&fields=title,year,authors,citationCount,abstract,externalIds"
```

**Always use `/paper/search`** (NOT `/paper/search/bulk` — returns wrong sort order).

## Key Format (both work)
- `iYTNXXDH278...` 40-char alphanumeric (old style)
- `s2k-HTuOQt7...` (new style, confirmed working)

Test: `curl -s -H "x-api-key: $KEY" "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1" -o /dev/null -w '%{http_code}'`

## Supported Fields
`title`, `year`, `abstract`, `authors`, `citationCount`, `referenceCount`, `externalIds`, `publicationVenue`, `openAccessPdf`, `citationStyles` (bibtex), `paperId`, `venue`, `isOpenAccess`, `tldr`, `fieldsOfStudy`

## Gotchas
- **No DOI in search results** — use `externalIds.ARXIV` or `externalIds.CorpusId`
- **Short queries 500**: `bpvv`, `bpv`, `bp` trigger API-side 500. Retry once, then skip.
- **Rate limits**: ~3500 req/h with key. Some tiers limit to 1 req/s. Exponential backoff.
- **Abstract truncation**: May be truncated or empty. Check `len(abstract)`.
- **Pagination**: Token-based. Pass `token` param for next page. Stop on cycle.
- **Empty recommendations**: Normal for some papers.

## Get BibTeX
```bash
curl -s -H "x-api-key: $KEY" \
  "https://api.semanticscholar.org/graph/v1/paper/PAPER_ID?fields=citationStyles" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('citationStyles',{}).get('bibtex','N/A'))"
```

## Also See
- `research-paper-search/references/semantic-scholar-api-notes.md` — detailed API changes, rate limiting diagnosis, key format history
- `research-paper-search/references/bashrc-noninteractive-pitfall.md` — env var loading issues that affect S2 key availability
