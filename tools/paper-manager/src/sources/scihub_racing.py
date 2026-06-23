"""Sci-Hub download with domain rotation, health probing, curl_cffi bypass, and Tor fallback."""
import logging, time, os, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Primary Sci-Hub domains (HTTPS)
SCI_HUB_DOMAINS = [
    "https://sci-hub.ru", "https://sci-hub.ee", "https://sci-hub.shop",
    "https://sci-hub.ren", "https://sci-hub.red", "https://sci-hub.al",
    "https://sci-hub.vg", "https://sci-hub.wf", "https://sci-hub.es",
    "https://sci-hub.box", "https://sci-hub.yt",
]

TOR_PROXY = "socks5h://127.0.0.1:9050"

_PROBE_TTL = 3600 * 4  # 4 hours between probes
_PROBE_WORKERS = 8
_lock = threading.Lock()


def _extract_pdf_url(html: str, base_domain: str) -> str | None:
    """Extract PDF download URL from Sci-Hub HTML page."""
    soup = BeautifulSoup(html, 'html.parser')

    # Method 1: Download link
    for a in soup.find_all('a'):
        href = a.get('href', '')
        text = (a.text or '').lower()
        if 'download' in text or ('.pdf' in href and 'storage' in href):
            return href if href.startswith('http') else f"{base_domain}{href}"

    # Method 2: iframe#pdf
    iframe = soup.find('iframe', id='pdf')
    if iframe and iframe.get('src'):
        src = iframe['src']
        return src if src.startswith('http') else f"{base_domain}{src}"

    # Method 3: embed
    embed = soup.find('embed', type='application/pdf')
    if embed and embed.get('src'):
        return embed['src']

    return None


def _probe_domains():
    """Probe all domains for reachability, update stats."""
    from domain_db import update_probe, get_probe_timestamp, set_probe_timestamp

    last_probe = get_probe_timestamp()
    if time.time() - last_probe < _PROBE_TTL:
        return

    def probe(domain):
        t0 = time.time()
        try:
            r = cffi_requests.get(f"{domain}/", impersonate="chrome", timeout=10, allow_redirects=True)
            ok = r.status_code == 200
            latency = (time.time() - t0) * 1000
            return domain, ok, latency
        except Exception:
            return domain, False, 99999.0

    with ThreadPoolExecutor(max_workers=_PROBE_WORKERS) as pool:
        futures = {pool.submit(probe, d): d for d in SCI_HUB_DOMAINS}
        for future in as_completed(futures, timeout=20):
            domain, ok, latency = future.result()
            update_probe(domain, ok, latency)

    set_probe_timestamp()
    logger.info(f"Sci-Hub domain probe complete ({len(SCI_HUB_DOMAINS)} domains)")


def _try_scihub_on_domains(domains: list, doi: str, output_path: str,
                           proxy: str | None = None) -> dict | None:
    """Try downloading from SciHub on given domains, optionally via proxy."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    proxy_kw = {"proxy": proxy} if proxy else {}

    for domain in domains:
        try:
            url = f"{domain}/{doi}"
            label = f"{domain} (Tor)" if proxy else domain
            logger.info(f"  Sci-Hub: {label}")

            resp = cffi_requests.get(url, headers=headers, impersonate="chrome",
                                     timeout=30, allow_redirects=True, **proxy_kw)

            if resp.status_code != 200:
                logger.debug(f"  HTTP {resp.status_code}")
                continue

            pdf_url = _extract_pdf_url(resp.text, domain)
            if not pdf_url:
                title = BeautifulSoup(resp.text, 'html.parser').title
                title_text = title.string.lower() if title else ''
                if 'отсутствует' in title_text or 'not found' in title_text:
                    logger.info(f"  Article not in database ({label})")
                    continue
                logger.debug(f"  No PDF URL found")
                continue

            r2 = cffi_requests.get(pdf_url, headers=headers, impersonate="chrome",
                                   timeout=60, allow_redirects=True, **proxy_kw)

            if r2.content[:4] == b'%PDF' and len(r2.content) > 1000:
                os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(r2.content)
                src = f'SciHub-{domain}-Tor' if proxy else f'SciHub-{domain}'
                logger.info(f"  ✅ PDF ({len(r2.content)} bytes)")
                return {'success': True, 'file': output_path, 'source': src, 'size': len(r2.content)}
            else:
                logger.debug(f"  Not a valid PDF ({r2.content[:20]})")

        except Exception as e:
            logger.debug(f"  {label}: {e}")
            continue

    return None


def try_scihub_curl(doi: str, output_path: str, **kwargs) -> dict | None:
    """
    Download from Sci-Hub using curl_cffi (TLS fingerprint bypass).

    Two-pass strategy:
    1. Direct connection via curl_cffi (fast, works for reachable domains)
    2. If all direct fail, retry via Tor SOCKS5 proxy (bypasses IP blocks)

    Returns {'success': True, 'file': output_path} or None.
    """
    from domain_db import get_best_domains, record_download_result, get_cooldown_domains

    _probe_domains()

    best = get_best_domains()
    cooldown = set(get_cooldown_domains())

    if best:
        domains = [b['domain'] for b in best]
    else:
        domains = SCI_HUB_DOMAINS

    domains = [d for d in domains if d not in cooldown]

    # Pass 1: Direct
    result = _try_scihub_on_domains(domains, doi, output_path)
    if result:
        return result

    # Pass 2: Tor fallback (if Tor is available)
    try:
        import socket
        s = socket.create_connection(("127.0.0.1", 9050), timeout=3)
        s.close()
        logger.info("  Tor SOCKS proxy available, retrying via Tor...")
        result = _try_scihub_on_domains(domains, doi, output_path, proxy=TOR_PROXY)
        if result:
            return result
    except Exception:
        logger.debug("  Tor SOCKS proxy not available, skipping Tor fallback")

    return None
