# OpenAlex Python 3.12 URL Encoding Quirk

> **Critical**: Python 3.12's `urllib.request.urlopen()` rejects `%20` (URL-encoded space) in URLs with error: "URL can't contain control characters."

## Symptom

```python
import urllib.request
import urllib.parse

query = "PINN fluid dynamics"
encoded = urllib.parse.quote(query, safe='')  # "PINN%20fluid%20dynamics"
url = f"https://api.openalex.org/works?search={encoded}&per_page=3"

# Python 3.12: urllib.request.urlopen(url) → HTTPError: URL can't contain control characters.
```

## Root Cause

Python 3.12's `urllib.request` became stricter about URL encoding. The `%20` encoded space is treated as a "control character" by the URL parser, even though `%20` is a valid URL encoding per RFC 3986.

## Working Solutions

### Option 1: Use `urllib.parse.quote_plus()` with `safe=' '` (RECOMMENDED)

```python
import urllib.parse
query = "PINN fluid dynamics"
encoded = urllib.parse.quote_plus(query, safe=' ')  # "PINN+fluid+dynamics" — + is accepted
url = f"https://api.openalex.org/works?search={encoded}&per_page=3"
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=15) as r:
    d = json.loads(r.read())
```

**Confirmed working 2026-06-06**: OpenAlex server accepts `+` as space separator. This is the most reliable bare-metal approach (no external dependencies, no subprocess overhead).

### Option 3: Use `requests` library (bypasses urllib entirely)

```python
import requests
params = {"search": "PINN fluid dynamics", "per_page": 3}
r = requests.get("https://api.openalex.org/works", params=params)
```

## Pitfall in Cron Sessions

In cron sessions where `requests` may not be installed, `quote_plus(query, safe=' ')` is the safest bare-metal pattern:

```python
# SAFE — encode spaces as '+', which urllib 3.12 accepts and OpenAlex handles
import urllib.parse
query = "benign paroxysmal positional vertigo"
encoded = urllib.parse.quote_plus(query, safe=' ')
url = f"https://api.openalex.org/works?search={encoded}&per_page=3"
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=15) as r:
    d = json.loads(r.read())
```

**CRITICAL**: Do NOT use bare spaces in the URL string — Python 3.12's `urllib.request` rejects bare spaces as "control characters" (`URL can't contain control characters`).

**Tested 2026-06-06**: All 10 OpenAlex queries in v23 scan used `quote_plus(query, safe=' ')` and succeeded.

## Test Cases

| Approach | Works in Python 3.12? | Notes |
|----------|----------------------|-------|
| Bare space in URL string | ❌ NO | "URL can't contain control characters" (confirmed 2026-06-06) |
| `urllib.parse.quote()` with `%20` | ❌ NO | Same control chars error |
| `urllib.parse.quote_plus()` with `+` | ✅ YES | Most reliable bare-metal approach |
| `quote_plus(query, safe=' ')` | ✅ YES | Same result, explicitly preserves other chars |
| `requests` library with params dict | ✅ YES | But `requests` may not be installed |

## Session Origin

Discovered 2026-06-05 during `bppv-pinn-canalolithiasis` ref_check. 15 reference verification scripts failed with "URL can't contain control characters" before the `quote_plus` approach was tested and found working.

**Updated 2026-06-06**: v23 scan (12 PubMed + 10 OpenAlex queries) confirmed that bare spaces FAIL in Python 3.12. All 10 OpenAlex queries must use `quote_plus(query, safe=' ')`.

## Related: PubMed URL Encoding

PubMed works differently — `urllib.parse.quote()` produces `%20` which PubMed's e-utilities accept without issue. The urllib 400 error is specific to how urllib.request handles the URL internally, not the target server. PubMed e-utilities are lenient; OpenAlex server is also lenient (accepts `+` or bare spaces), but Python's urllib.request is the bottleneck.
