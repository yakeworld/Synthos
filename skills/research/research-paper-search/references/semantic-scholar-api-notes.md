# Semantic Scholar API Notes

## API Endpoint Changes

The Semantic Scholar API changed its search endpoint from:
- **Old**: `/graph/v1/paper/search/bulk` — returns wrong sorting order for some queries
- **New**: `/graph/v1/paper/search` — correct relevance sorting

## Field Availability

The new `/search` endpoint does NOT include `DOI` in the response, even when explicitly requested. Use `externalIds.DOI` or `externalIds.ARXIV` for paper identification instead.

### Supported Fields (new search endpoint)
- `title`, `year`, `externalIds`, `authors`
- `citationCount`, `referenceCount`
- `abstract`, `openAccessPdf`, `publicationVenue`
- `citationStyles` (includes bibtex)
- `venue`, `isOpenAccess`, `tldr`, `fieldsOfStudy`
- `paperId`

### Unsupported Fields
- `doi` (top-level)
- `keywords`

## Rate Limiting & Errors

- **500 Internal Server Error**: Occurs on certain short queries (e.g., `bpvv`, `bpv`, `bp`). This is an API-side issue, not a client bug.
- **400 Bad Request**: When query is empty or fields are invalid.
- **403/429 Forbidden/Too Many Requests**: Caused by one of three things:
  1. **Rate limiting**: Some keys limited to 1 req/sec — add `sleep(1)` between calls. Others allow ~3500 req/hour. Apply exponential backoff (1s, 2s, 4s) on 429.
  2. **Expired/revoked key**: Previously valid keys that have been rotated or deactivated
  3. **Corrupted environment variable**: Check for trailing whitespace, quotes, or newlines in `$SEMANTIC_SCHOLAR_API_KEY`
- **Diagnosis**: Use `curl -s -H "x-api-key: $KEY" "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1" -o /dev/null -w '%{http_code}'` to quickly test

## Key Format — CORRECTED 2026-05-12

**Both key formats work:**
- **Old style** (pre-2025ish): 40-char alphanumeric, e.g. `SEMANTIC_SCHOLAR_API_KEY_PLACEHOLDER`
- **New style** (s2k- prefixed): e.g. `s2k-HTuOQt7IYWcPOmxnJPvfLjISRjJg8tZK9aKGTmBD` — **these DO work at api.semanticscholar.org**. Earlier doc claiming they don't was incorrect. Tested working 2026-05-12.
- **Verification**: Always test before assuming a key works. A 403 on first call is likely rate limiting or expired key, not format mismatch (since both formats work).

## Common Code Patterns

Projects often use `_S2_DISABLED = True` flags for graceful degradation when the S2 key fails:
```python
_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
_S2_DISABLED = False  # Toggle to False once key is verified
```
Check for this flag in project code — it's commonly left as `True` after a key expiry incident and can silently disable S2 even when a working key is in the environment.

## Reference Transcript

This session discovered that `paper/search/bulk` returned incorrect results for "Attention Is All You Need", while `paper/search` returned the correct paper (Vaswani et al., 2017). The fix was changing the base URL endpoint from `/paper/search/bulk` to `/paper/search` in `src/api/semantic_scholar.py`.
