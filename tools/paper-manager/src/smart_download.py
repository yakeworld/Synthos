"""Smart download: try regular requests first, fall back to curl_cffi on Cloudflare."""
import logging

logger = logging.getLogger(__name__)

# Cloudflare detection signatures
_CF_INDICATORS = [
    b'cf-browser-verification',
    b'Checking your browser',
    b'DDoS protection',
    b'Just a moment',
    b'Attention Required',
    b'cf-ray',
]


def _is_cloudflare(response) -> bool:
    """Detect if response is a Cloudflare challenge page."""
    if response.status_code in (403, 503, 429):
        # Check headers
        server = response.headers.get('Server', '')
        if 'cloudflare' in server.lower():
            return True
        # Check body
        body = response.content[:10000]
        for indicator in _CF_INDICATORS:
            if indicator in body:
                return True
    return False


def smart_download(url: str, *, headers: dict | None = None,
                   timeout: int = 30, allow_redirects: bool = True,
                   **kwargs) -> dict:
    """
    Download a URL with automatic Cloudflare bypass.

    Strategy:
    1. Try regular `requests.get()` first.
    2. If response looks like Cloudflare block → retry with curl_cffi.
    3. Return dict with {ok, status, content, headers, source}.

    Returns {'ok': True, 'response': response_obj} or equivalent with ok=False.
    """
    import requests as _req

    if headers is None:
        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36")
        }

    attempt = 0
    max_attempts = 2  # regular → fallback

    while attempt < max_attempts:
        attempt += 1
        use_cffi = (attempt == 2)

        try:
            if use_cffi:
                from curl_cffi import requests as cffi_req
                logger.debug(f"  smart_download: curl_cffi → {url[:80]}...")
                r = cffi_req.get(url, headers=headers, impersonate="chrome",
                                 timeout=timeout, allow_redirects=allow_redirects,
                                 **kwargs)
            else:
                logger.debug(f"  smart_download: requests → {url[:80]}...")
                r = _req.get(url, headers=headers, timeout=timeout,
                             allow_redirects=allow_redirects, **kwargs)

            # Check for Cloudflare on first attempt
            if attempt == 1 and _is_cloudflare(r):
                logger.info(f"  Cloudflare detected, retrying with curl_cffi...")
                continue

            return {
                'ok': True,
                'status': r.status_code,
                'content': r.content,
                'headers': dict(r.headers),
                'source': 'curl_cffi' if use_cffi else 'requests',
            }

        except Exception as e:
            if use_cffi:
                logger.debug(f"  smart_download failed (both attempts): {e}")
                return {'ok': False, 'error': str(e)}
            logger.debug(f"  smart_download: requests failed ({e}), trying curl_cffi...")
            continue

    return {'ok': False, 'error': 'all attempts failed'}
