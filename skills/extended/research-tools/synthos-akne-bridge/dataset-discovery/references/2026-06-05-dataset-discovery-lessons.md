# Dataset Discovery — Platform Capabilities (2026-06-05)

## Platform Access Matrix

| Platform | REST API | Scraping | Auth Required | Notes |
|----------|----------|----------|---------------|-------|
| **Kaggle** | ❌ SPA only | ❌ No HTML body | OAuth/token | All endpoints return HTML SPA shell. `kaggle` CLI requires login. |
| **UCI Repo** | ❌ SPA only | ❌ No HTML body | No | Archive moved to SPA at `archive.ics.uci.edu`. No JSON/API endpoint reachable. |
| **OpenML** | ✅ JSON API | N/A | No | `/api/v1/json/data/list/limit/N` — **LIMIT 50-100 only**. Larger returns truncated/invalid JSON. Use `offset` for pagination. |
| **Semantic Scholar** | ✅ JSON API | N/A | x-api-key | Rate limited (429 after ~5 calls). Good for paper search. |
| **Crossref** | ✅ JSON API | N/A | No | Reliable for paper metadata. Valid selects: title, author, DOI, container-title, published-print. NOT `citation-count`. |
| **PubMed** | ✅ JSON API | N/A | Optional | E-utilities work well. |

## OpenML Pitfalls

1. **Pagination limit**: `limit > 200` often produces truncated JSON. Use `limit=50` with `offset` pagination.
2. **Value types**: All quality metric values are **strings** (e.g., `"684.0"`), not numbers. Must use `float()` not `int()` conversion.
3. **Tag search**: `/api/v1/json/data/tag/{tag}` returns `{"error": "Function not valid"}` — tag queries use different endpoint.
4. **Name search**: `/api/v1/json/data/name/{name}` also returns error — search uses `/api/v1/json/data/list/` with filtering.
5. **ID mapping**: OpenML IDs for UCI datasets are NOT sequential or predictable — must search by name filtering, not guess IDs.