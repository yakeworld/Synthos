"""LibGen PDF download with multi-mirror failover."""
import logging, os, re, urllib.parse
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

LIBGEN_MIRRORS = [
    "https://libgen.li", "https://libgen.bz", "https://libgen.gs",
    "https://libgen.rs", "https://libgen.st",
]

def try_libgen(doi: str, output_path: str, **kwargs) -> dict | None:
    """
    Download from Library Genesis.
    Returns {'success': True, 'file': output_path} or None.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    q = urllib.parse.quote(doi, safe='')
    
    for mirror in LIBGEN_MIRRORS:
        try:
            url = f"{mirror}/ads.php?doi={q}"
            logger.info(f"  LibGen: {mirror}")
            
            resp = cffi_requests.get(url, headers=headers, impersonate="chrome", timeout=20, allow_redirects=True)
            
            if resp.status_code != 200:
                continue
            
            # Find download link in HTML
            soup = BeautifulSoup(resp.text, 'html.parser')
            dl_link = None
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'get.php' in href:
                    dl_link = urllib.parse.urljoin(url, href)
                    break
            
            if not dl_link:
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.endswith('.pdf'):
                        dl_link = urllib.parse.urljoin(url, href)
                        break
            
            if dl_link:
                logger.info(f"  Found: {dl_link[:80]}")
                r2 = cffi_requests.get(dl_link, headers=headers, impersonate="chrome", timeout=60, allow_redirects=True)
                
                if r2.content[:4] == b'%PDF' and len(r2.content) > 1000:
                    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(r2.content)
                    logger.info(f"  ✅ PDF ({len(r2.content)} bytes)")
                    return {'success': True, 'file': output_path, 'source': f'LibGen-{mirror}', 'size': len(r2.content)}
            
        except Exception as e:
            logger.debug(f"  {mirror}: {e}")
            continue
    
    return None
