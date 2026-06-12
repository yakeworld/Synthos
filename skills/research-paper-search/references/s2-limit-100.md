# Semantic Scholar API `limit` Parameter Pitfall

## Discovery
**Date:** 2026-05-08
**Source:** Direct testing of `https://api.semanticscholar.org/graph/v1/paper/search`

## Problem
The `/search` endpoint returns HTTP 500 Internal Server Error when the `limit` parameter is greater than 100.

## Evidence

| `limit` value | Response |
|---------------|----------|
| 100 | OK, 100 results |
| 500 | HTTP 500 Internal Server Error |
| 1000 | HTTP 500 Internal Server Error |
| 2000 | HTTP 500 Internal Server Error |

## Root Cause
The S2 Graph API has a hard cap of 100 on the `limit` query parameter for the `/search` endpoint.

## Fix
Always cap `limit` at 100 in the initial request:

```python
params = {'query': query, 'fields': fields, 'limit': min(requested_limit, 100)}
```

To get more than 100 results, use the pagination `token` field from the response:

```python
total_results = []
params = {'query': query, 'fields': fields, 'limit': min(requested_limit, 100)}

while len(total_results) < requested_limit:
    data = await api_get(url, params=params)
    total_results.extend(data['data'])
    
    if 'token' not in data or data['token'] in seen_tokens:
        break
    seen_tokens.add(data['token'])
    params['token'] = data['token']
    await asyncio.sleep(1)  # Rate limit delay
```

## Notes
- The `/search/bulk` endpoint also appears to be affected (returned 500 during testing, though results were sometimes correct with short queries).
- This is different from the old API behavior where higher limits were accepted.
- The `limit` parameter in `search_papers()` default was 1000 — this caused silent failures (3 retries of 500 errors before giving up).
- A single query with `limit=10` works fine — the cap only triggers at > 100.
