# SS Dual-Key Failover — Complete Reference

## Context
Semantic Scholar API (SS) supports multiple API keys simultaneously. The user has two active keys:
- **Primary**: `iYTNXXDH278PVXl2FJ2YU1TyZ5joLAZr3WA9IVzt` (40 chars, no prefix, legacy format)
- **Fallback**: `s2k-HTuOQt7IYWcPOmxnJPvfLjISRjJg8tZK9aKGTmBD` (44 chars, `s2k-` prefix, new format)

Both keys are valid and functional. SS does not distinguish between key formats — both grant equal API access.

## Why Two Keys?
1. **Format diversity** — Legacy (no prefix) + new (`s2k-` prefix)
2. **Rotational resilience** — if one key is revoked or rate-limited, the other continues working
3. **No API distinction** — SS treats all keys the same; key rotation is application-level

## Implementation

### config.py — Key Ring
```python
class Config:
    def __init__(self):
        self._primary_key = os.environ.get('SEMANTIC_SCHOLAR_API_KEY', '')
        self._fallback_key = os.environ.get('S2_FALLBACK_KEY', '')
        self._key_ring = []
        if self._primary_key:
            self._key_ring.append(self._primary_key)
        if self._fallback_key:
            self._key_ring.append(self._fallback_key)
        if not self._key_ring:
            import pathlib
            _key_file = pathlib.Path(__file__).parent / '.api_key'
            if _key_file.is_file():
                raw = _key_file.read_text().strip()
                for k in raw.split(','):
                    k = k.strip()
                    if k:
                        self._key_ring.append(k)
        self.api_key = self._key_ring[0] if self._key_ring else ''
        self._key_index = 0
        self.tor_proxy = os.environ.get('SOCKS_PROXY', 'socks5://127.0.0.1:9050')
        self.tor_enabled = os.environ.get('USE_TOR_FOR_S2', 'true').lower() in ('true', '1', 'yes')
    
    def failover(self) -> str:
        if len(self._key_ring) <= 1:
            return self.api_key
        self._key_index = (self._key_index + 1) % len(self._key_ring)
        self.api_key = self._key_ring[self._key_index]
        return self.api_key
```

### base_client.py — Tor Proxy
```python
class BaseAPIClient(BaseAPIClient):
    def __init__(self, config):
        self._proxy = None
        if config.tor_enabled and config.tor_proxy:
            self._proxy = config.tor_proxy
            self.sync_session.proxies = {
                'http': config.tor_proxy,
                'https': config.tor_proxy,
            }
    
    async def create_session(self):
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.download_timeout + 5)
            kwargs = {'timeout': timeout}
            if self._proxy:
                kwargs['proxy'] = self._proxy
            self.session = aiohttp.ClientSession(**kwargs)
```

### .secrets
```bash
export SEMANTIC_SCHOLAR_API_KEY="iYTN...IVzt"
export S2_FALLBACK_KEY="s2k-HT...TmBD"
```

### .api_key (file fallback)
```
iYTNXXDH278PVXl2FJ2YU1TyZ5joLAZr3WA9IVzt,s2k-HTuOQt7IYWcPOmxnJPvfLjISRjJg8tZK9aKGTmBD
```

## Rate Limits
- Free tier: 1 request/second max
- Never parallelize SS calls
- Use `sleep(1)` between sequential calls
- Rate limit is per IP, not per key (rotating keys does NOT bypass rate limits)
- Tor adds latency (~3-5s per request)

## Verification Commands

### Test Key Validity
```bash
# Key 1 (legacy)
curl -s -H "x-api-key: iYTNXXDH278PVXl2FJ2YU1TyZ5joLAZr3WA9IVzt" \
    "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1&fields=title" \
    -w "HTTP: %{http_code}" --max-time 15

# Key 2 (s2k-)
curl -s -H "x-api-key: s2k-HTuOQt7IYWcPOmxnJPvfLjISRjJg8tZK9aKGTmBD" \
    "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1&fields=title" \
    -w "HTTP: %{http_code}" --max-time 15
```

### Test Tor Connectivity
```bash
curl -s --socks5 127.0.0.1:9050 \
    "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1&fields=title" \
    -H "x-api-key: iYTNXXDH278PVXl2FJ2YU1TyZ5joLAZr3WA9IVzt" \
    -w "HTTP: %{http_code}" --max-time 30
```

### Test Python Config
```python
from src.core.config import Config
c = Config()
assert len(c._key_ring) == 2
assert c.tor_enabled == True
assert c._proxy == 'socks5://127.0.0.1:9050'
c.failover()
assert c._key_index == 1  # switched to fallback
```

## Key Facts
- SS API has NO rate limit per key — it's per IP address
- Both key formats (legacy + s2k-) are equally valid
- Key rotation is for **resilience against revocation**, not for bypassing rate limits
- Tor adds ~3-5s latency but provides better IP diversity for distributed requests
- File-based fallback (`.api_key`) is the most reliable path for subprocess contexts
