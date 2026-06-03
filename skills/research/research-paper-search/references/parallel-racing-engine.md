# Parallel Racing Engine — Multi-Source PDF Download

> Integrated from scansci-pdf (https://pypi.org/project/scansci-pdf/)

## Architecture

```
Tier 1 (15s): Sci-Hub via curl_cffi  → TLS fingerprint bypass → Download ✅
  ├── Domain health probing (SQLite, 4h TTL)
  ├── curl_cffi impersonate="chrome120" (handles DDoS-Guard)
  └── Auto cooldown for failing domains (fail_streak >= 3)
  
Tier 2 (20s): LibGen multi-mirror   → 5 mirrors → Download ✅
  └── libgen.li, bz, gs, rs, st
```

Each tier runs sources in PARALLEL via ThreadPoolExecutor. First success wins. Remaining futures are cancelled.

## Source Code

Location: `/media/yakeworld/sda2/Synthos/outputs/code/src/`

| File | Purpose |
|:-----|:--------|
| `racing_engine.py` | ThreadPoolExecutor parallel racing, tier builder |
| `domain_db.py` | SQLite domain health tracking, cooldown management |
| `sources/scihub_racing.py` | Sci-Hub download via curl_cffi + domain probing |
| `sources/libgen.py` | LibGen download with 5-mirror rotation |
| `downloader/pdf_downloader.py` | Integrates racing engine via `_download_racing()` |

## Key Techniques

### curl_cffi TLS Fingerprint Bypass
```python
from curl_cffi import requests
r = requests.get(url, impersonate="chrome120", timeout=30, allow_redirects=True)
# Bypasses DDoS-Guard/Cloudflare at TLS level — no browser needed
```

### Domain Health Probing
- SQLite DB at `.domain_cache/domain_stats.db`
- Probes all 11 Sci-Hub mirrors every 4 hours via ThreadPoolExecutor (8 workers)
- Tracks: success count, fail count, fail_streak, avg latency, reachable
- Cooldown: domains with fail_streak >= 3 are skipped until they succeed again

### Sci-Hub PDF URL Extraction
```python
# Three methods tried in order:
# 1. <a> tag with "download" text or .pdf + "storage" in href
# 2. <iframe id="pdf"> src attribute
# 3. <embed type="application/pdf"> src attribute
```

### LibGen Download
- Searches 5 mirrors via `{mirror}/ads.php?doi={doi}`
- Extracts `get.php` download link from HTML
- Falls back to `.pdf` direct links
