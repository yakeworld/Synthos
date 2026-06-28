# SearXNG Google Scholar Engine Limitation

## Status

**PERSISTENTLY BLOCKED.** The `google_scholar` engine in SearXNG reliably returns `access denied`.

## 2026-06-26 Session Confirmation

- **Environment**: Host `scholar.google.com` → HTTP 200 in 2.85s (Tailscale exit node working)
- **SearXNG google_scholar engine**: 0 results (specified `engines=google%20scholar` explicitly)
- **SearXNG google engine**: ~20 results, some pointing to scholar.google.com
- **Conclusion**: The block is permanent and not solvable by network changes. The `google` engine remains the best SearXNG-based path for academic search.

- Engine responds with `unresponsive_engines: [['google scholar', 'access denied']]`
- SearXNG logs show no specific error — the engine simply returns 0 results
- Host machine can access `https://scholar.google.com/` directly (HTTP 200)

## Root Cause

Google Scholar uses aggressive anti-scraping that goes beyond standard Google CAPTCHA:
- Request fingerprinting (User-Agent, connection pattern)
- Cookie/session validation that SearXNG's simplified request model can't satisfy
- Rate limiting specifically targeting automated search queries

## Workarounds (in order of preference)

### 1. Use SearXNG's regular `google` engine
The standard google engine can return links pointing to scholar.google.com. Not as focused as a dedicated scholar search, but works reliably.

### 2. User browser direct access
Since the host has Tailscale exit node enabled, `scholar.google.com` is directly accessible from the user's terminal or browser. SearXNG doesn't need to be the intermediary for scholar searches.

### 3. Alternative academic sources
- PubMed (has its own SearXNG engine)
- Semantic Scholar (if configured in settings.yml)
- Crossref (if configured)
- Direct DOI lookups

## Diagnosis

```bash
# 1. Verify host can reach scholar.google.com (via current network egress)
curl -s --max-time 10 -o /dev/null -w "HTTP %{http_code} in %{time_total}s" "https://scholar.google.com/"

# 2. Check SearXNG engine status
curl -s --max-time 30 "http://127.0.0.1:8080/search?q=test&format=json&engines=google%20scholar" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('unresponsive_engines', 'no data'))"

# 3. Confirm settings.yml has the engine (it loads, just gets blocked)
docker exec searxng cat /etc/searxng/settings.yml | grep -A2 scholar
```

## Do NOT

- Attempt to configure proxy rotation or CAPTCHA solving for Google Scholar — the effort/benefit ratio is not worth it
- Add multiple google_scholar engine instances — this makes rate limiting worse
- Assume the engine will "start working" with network changes — the block is on Google's side, not the local network
