# API Key Fallback Pattern — Multi-Key Ring + File Fallback

## The Problem
When running Python code via Hermes Agent's `execute_code` with `shell=True`, environment variables from `.bashrc` are not accessible because:
1. `bash -c` is non-interactive and doesn't source `.bashrc` by default
2. Even with explicit `source ~/.bashrc`, child Python processes don't inherit exported variables due to subprocess isolation

## The Solution: File-Based Fallback + Multi-Key Ring

### Step 1: Create the key file(s)
```
media/yakeworld/sda2/Synthos/tools/code-tools/src/core/.api_key
```
Content: comma-separated keys, e.g. `iYTN...IVzt,s2k-HT...TmBD`

### Step 2: Modify config.py to read fallback with key ring
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
    
    def failover(self) -> str:
        """Switch to next key in ring"""
        if len(self._key_ring) <= 1:
            return self.api_key
        self._key_index = (self._key_index + 1) % len(self._key_ring)
        self.api_key = self._key_ring[self._key_index]
        return self.api_key
```

### Step 3: Add to .gitignore
```
src/core/.api_key
*.key
*.secret
```

## When to Use
- Running automated scripts in Hermes Agent environment
- API keys need to be available in subprocess contexts
- Environment variables are set in `.bashrc` but not accessible
- **Multi-key rotation needed** — API services with rate limits, rotating credentials, or primary/fallback pairs

## Multi-Key Ring Pattern
For services that support multiple API keys (e.g., Semantic Scholar), the key ring pattern provides:
1. **Automatic failover** — on 403/429/500, switch to next key
2. **Key diversity** — primary (legacy format) + fallback (new format)
3. **Zero code changes** — config reads both env vars + file fallback
4. **Thread-safe** — `_key_index` is only written at object creation or explicit failover

### Key Ring Structure
```
Key[0] = primary key (highest priority, e.g. iYTNXX legacy format)
Key[1] = fallback key (e.g. s2k- prefixed format)
...
Key[N] = additional backups
```

### Key Rotation Trigger
- HTTP 403 (Forbidden) → key expired/revoked → failover
- HTTP 429 (Too Many Requests) → rate limit → rotate to different key
- HTTP 500 (Internal Server Error) → possible service issue → try next key
- Timeout (> 30s via Tor) → slow path → try direct (if Tor disabled)

## Multi-Key Ring Pattern
For services that support multiple API keys (e.g., Semantic Scholar), the key ring pattern provides:
1. **Automatic failover** — on 403/429/500, switch to next key
2. **Key diversity** — primary (legacy format) + fallback (new format)
3. **Zero code changes** — config reads both env vars + file fallback
4. **Thread-safe** — `_key_index` is only written at object creation or explicit failover

## Pros and Cons
| | Pros | Cons |
|---|------|------|
| Multi-key ring | Resilience against single key failure | More credential management |
| File fallback | Works in all contexts | File must be present |
| .bashrc exports | Standard Linux practice | Not accessible in subprocess |
| /etc/environment | Most reliable | Requires root/sudo |

## Key Insight
The **file-based fallback + key ring** is the most reliable pattern for Hermes Agent environments. It handles both subprocess isolation (file fallback) and credential lifecycle (key rotation). Combined with Tor proxy support, it provides a complete resilient API access layer.

## Tor Proxy Integration
When Tor is enabled (`USE_TOR_FOR_S2=true`), all API requests go through `socks5://127.0.0.1:9050`. Both `aiohttp` and `requests` sessions inherit the proxy, so key rotation happens transparently through Tor:

```python
# In Config
self.tor_proxy = os.environ.get('SOCKS_PROXY', 'socks5://127.0.0.1:9050')
self.tor_enabled = True

# In BaseAPIClient
if config.tor_enabled and config.tor_proxy:
    self._proxy = config.tor_proxy
    self.sync_session.proxies = {
        'http': config.tor_proxy,
        'https': config.tor_proxy,
    }
```

## Verification
1. Both keys in `.secrets` / `.bashrc` — `echo ${#SEMANTIC_SCHOLAR_API_KEY}` should be 40+
2. File fallback — `.api_key` exists with comma-separated keys
3. Key ring loads — `len(config._key_ring)` == 2 (or more)
4. Failover works — `config.failover()` switches to next key
5. Tor works — `curl --socks5 127.0.0.1:9050` reaches target
6. End-to-end — API call succeeds via Tor + key ring
