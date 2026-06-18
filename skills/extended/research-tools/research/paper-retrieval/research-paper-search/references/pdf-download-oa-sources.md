# PDF Download — OA Source Reliability Testing Results

Tested 2026-05-08 via curl and Python requests against BPPV search results (38 GOLD OA papers from Semantic Scholar).

## Working Sources

| Publisher | URL Pattern | Status | Notes |
|-----------|-------------|--------|-------|
| **Frontiersin** | `frontiersin.org/journals/*/articles/*/pdf` | ✅ Works | Downloads valid PDF via curl and requests. Fast, no redirect issues. |
| **BMC Med Info** | `bmcmedinformdecismak.biomedcentral.com/counter/pdf/` | ✅ Some | Works for some papers, may timeout for others. |
| **Springer Open** | `ejo.springeropen.com/counter/pdf/` | ✅ Some | Works for some papers. |

## Blocked Sources (HTTP 403 / Anti-Bot)

| Publisher | URL Pattern | HTTP Code | Notes |
|-----------|-------------|-----------|-------|
| **MDPI** | `mdpi.com/*/pdf?version=...` | 403 | Removing `version=` parameter doesn't help. |
| **BMJ Open** | `bmjopen.bmj.com/content/*/full.pdf` | 403 | Direct PDF URL blocked. |
| **Cureus** | `assets.cureus.com/uploads/review_article/pdf/` | 404 | Link may be stale, or link structure changed. |

## Other Failure Modes

| Source | Status | Notes |
|--------|--------|-------|
| **Sci-Hub** (sci-hub.se, sci-hub.ru, etc.) | ❌ Connection refused | DNS not found from this environment. Not accessible. |
| **arXiv** | ⚠️ Limited | Works for CS/math papers but most medical papers aren't on arXiv. |
| **DOI redirects** (doi.org) | ⚠️ Mixed | Works via `curl -L` and `requests`, but **fails with aiohttp** (403). Use `requests` for DOI downloads. |

## Key Takeaway

**Frontiersin is the most reliable OA source.** Of the 38 GOLD OA papers found for BPPV:
- Frontiersin URLs: 100% download success
- BMC/Springer: ~50% success (may timeout)
- MDPI/BMJ/Cureus: 0% success (anti-bot protection)

## Workaround for Blocked OA Sites

1. Try the DOI landing page (HTML) and parse the PDF link from it.
2. Try alternative mirrors: Semantic Scholar → Unpaywall → CORE.
3. For Python downloads: use `requests` (synchronous) instead of `aiohttp` for DOI/OA URL downloads, as aiohttp returns 403 on many sites.
4. Accept that some OA sites will not work through automated download — document which sources worked.
