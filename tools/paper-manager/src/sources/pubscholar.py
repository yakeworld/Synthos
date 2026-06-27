"""PubScholar download source — Chinese academic paper search + CDN download.

Uses the PubScholar API (RSSHub-discovered auth mechanism):
- salt = '6m6pingbinwaktg227gngifoocrfbo95'
- signature = sha1(sorted([salt, timestamp, nonce]).join(''))
- x-finger = 4× hex32(8) tokens

Tier priority:
  1. local_links CDN (is_free=True papers) → direct PDF download
  2. local_links preview (is_free=False papers) → try preview URL
  3. External OA links → try OA URL
"""
import hashlib, time, json, random, string, uuid, logging, os
from typing import Optional

logger = logging.getLogger(__name__)

SALT = '6m6pingbinwaktg227gngifoocrfbo95'
BASE_URL = 'https://pubscholar.cn'
API_URL = f'{BASE_URL}/hky/open/resources/api/v1/articles'

# ── Auth helpers ──────────────────────────────────────────────────────────

def _gen_nonce(length: int = 6) -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def _hex32(length: int = 8) -> str:
    return format(random.randint(0, 2**32-1), '08x')

def _get_signed_headers() -> dict:
    nonce = _gen_nonce(6)
    timestamp = str(int(time.time() * 1000))
    # Use string sort (lexicographic, same as JS .toSorted())
    signature = hashlib.sha1(''.join(sorted([SALT, timestamp, nonce])).encode()).hexdigest()
    x_finger = f"{_hex32(8)}{_hex32(8)}{_hex32(8)}{_hex32(8)}"
    uid = str(uuid.uuid4())
    return {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "nonce": nonce,
        "timestamp": timestamp,
        "signature": signature,
        "x-finger": x_finger,
        "x-xsrf-token": uid,
        "Cookie": f"XSRF-TOKEN={uid}",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

# ── Search ────────────────────────────────────────────────────────────────

def _search_pubscholar(keyword: str, max_results: int = 3) -> list[dict]:
    """Search PubScholar by keyword. Returns list of paper dicts."""
    import urllib.request
    
    headers = _get_signed_headers()
    body = {
        "page": 1,
        "size": max_results,
        "order_field": "date",
        "order_direction": "desc",
        "user_id": hashlib.md5(str(int(time.time())).encode()).hexdigest(),
        "lang": "zh",
        "query": keyword,
        "strategy": None,
        "orderField": "default",
    }
    
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body, ensure_ascii=False).encode('utf-8'),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result.get('content', [])
    except urllib.request.HTTPError as e:
        if e.code in (429, 403):
            logger.warning(f"PubScholar rate limited ({e.code}), retrying in 15s")
            time.sleep(15)
            try:
                with urllib.request.urlopen(req, timeout=15) as retry:
                    result = json.loads(retry.read().decode())
                    return result.get('content', [])
            except:
                pass
        logger.debug(f"PubScholar search HTTP {e.code}: {e.reason}")
    except Exception as e:
        logger.debug(f"PubScholar search error: {e}")
    return []

def _search_by_doi(doi: str) -> list[dict]:
    """Search PubScholar by DOI."""
    return _search_pubscholar(doi, max_results=3)

# ── Download ──────────────────────────────────────────────────────────────

def _download_from_url(url: str, output_path: str, referer: str = "https://pubscholar.cn/") -> bool:
    """Download a PDF from a URL. Returns True on success."""
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Referer": referer,
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if data[:4] == b'%PDF' and len(data) > 10000:  # >10KB = real PDF
                os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(data)
                logger.info(f"✅ PubScholar CDN: {len(data)} bytes")
                return True
    except Exception as e:
        logger.debug(f"PubScholar download error from {url}: {e}")
    return False

def try_pubscholar(doi: str, output_path: str, extra: Optional[dict] = None) -> dict:
    """Try to download a paper via PubScholar.
    
    Strategy:
      1. Search by DOI (exact match)
      2. If found → check local_links CDN
      3. If free → download from CDN
      4. If not free → try OA links
    
    Args:
        doi: The DOI to search for
        output_path: Where to save the PDF
        extra: Optional dict with 'title' for fallback search
    
    Returns:
        dict with 'success' (bool) and optional metadata
    """
    papers = _search_by_doi(doi)
    
    # Also try searching by title if DOI search fails
    if not papers and extra and extra.get('title'):
        papers = _search_pubscholar(extra['title'], max_results=5)
    
    # Also try a broader search with just the DOI prefix (short enough to match)
    if not papers:
        # Try searching with just the last meaningful part of the DOI
        short_doi = doi.split('/')[-1] if '/' in doi else doi
        if len(short_doi) > 8:
            papers = _search_pubscholar(short_doi[:30], max_results=5)
    
    if not papers:
        return {"success": False, "error": "No papers found on PubScholar"}
    
    for paper in papers:
        title = paper.get('title', '')[:80]
        is_free = paper.get('is_free', False)
        local_links = paper.get('local_links', [])
        links = paper.get('links', [])
        
        # Strategy 1: local CDN (free papers)
        if is_free and local_links:
            for link in local_links:
                # Prefer full-file link over preview
                if 'files' in link and 'fastdfspath' in link:
                    if _download_from_url(link, output_path):
                        return {"success": True, "source": "pubscholar_cdn", "title": title}
            # Fallback: first local link
            if _download_from_url(local_links[0], output_path):
                return {"success": True, "source": "pubscholar_cdn", "title": title}
        
        # Strategy 2: preview link for non-free papers
        if local_links:
            for link in local_links:
                if 'preview2' in link:
                    if _download_from_url(link, output_path):
                        return {"success": True, "source": "pubscholar_preview", "title": title}
        
        # Strategy 3: external OA links
        for link in links:
            url = link.get('url', '')
            is_oa = link.get('is_open_access', False)
            if is_oa and url:
                if _download_from_url(url, output_path):
                    return {"success": True, "source": "pubscholar_oa", "title": title}
    
    return {"success": False, "error": "No downloadable PDF found on PubScholar"}
