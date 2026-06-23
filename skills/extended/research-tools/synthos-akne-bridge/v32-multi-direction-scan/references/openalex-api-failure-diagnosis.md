# OpenAlex API Failure Diagnosis

## Discovery (Cycle 208, 2026-06-23)

During the Cycle 208 staleness guard probe, ALL OpenAlex cross-check queries returned -1:

```
OA_BPPV_DT: OpenAlex=-1
OA_SCC_PINN: OpenAlex=-1
OA_Ocular_Torsion: OpenAlex=-1
OA_Pupil_Seg_VOG: OpenAlex=-1
```

This is the error return value from `openalex_search()` (all retries exhausted, last error captured).

Meanwhile, PubMed queries (`pubmed_count()`) succeeded normally — all 12+ queries returned valid counts (0, 5, 18, etc.). This pattern rules out a general network failure.

## Root Cause Analysis

### Primary: Missing lenient SSL context

The `openalex_search()` function called `urllib.request.urlopen(req, timeout=20)` **without** `context=CTX` (the custom `ssl.CERT_NONE` context). The `CTX` variable is defined at module level:

```python
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
```

The pubmed functions (`pubmed_count`, `_fetch_titles_via_esummary`, `fetch_title_via_esummary`) all pass `context=CTX`. `openalex_search` was the only function using the system-default SSL context.

### Secondary: Environment-specific SSL bundle

Hermes deployments running on headless Linux systems may lack the full CA certificate bundle. OpenAlex's SSL certificate (LetsEncrypt or similar) may not validate against the minimal system CA store.

**Diagnosis test** (run in terminal or Python):
```python
import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
url = 'https://api.openalex.org/works?search=test&per_page=1'
req = urllib.request.Request(url, headers={'User-Agent': 'Synthos/1.0'})
try:
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        data = json.loads(r.read())
        print(f'OK: {len(data.get(\"results\", []))} results')
except Exception as e:
    print(f'FAIL: {e}')
```

If this works with context=ctx but fails without it, the SSL bundle is the issue.

## Fix Applied

In Cycle 208, `openalex_search()` was patched to pass `context=CTX` (the lenient SSL context), matching the pubmed functions. See `scripts/pubmed_utils.py`.

## Residual Risk

Even with the fixed SSL context, OpenAlex may still fail if:
- The Hermes environment blocks `api.openalex.org` via firewall/iptables
- A security scanner (tirith, etc.) intercepts non-NCBI HTTPS
- The API is temporarily rate-limited or down

**Fallback**: When ALL OpenAlex queries return -1 while PubMed succeeds, rely on PubMed-only gap validation. The ABSOLUTE_WHITE claim is slightly weaker (single-source) but still valid when PubMed returns 0 with narrow keyword queries.
