#!/usr/bin/env python3
"""
下载模块配置 — 全局变量、常量、辅助函数。
所有下载模块共享的配置。
"""
import os
import re
import time

# Environment variables
MEDDATA_API_KEY = os.environ.get("MEDDATA_API_KEY", "")
TOR_PROXY_URL = os.environ.get("TOR_PROXY", "socks5://127.0.0.1:9050")
SS_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
DEFAULT_OUTPUT_DIR = os.environ.get("PDF_OUTPUT_DIR", "./outputs/papers/pdfs")

# S2 rate limiter
_s2_request_count = 0
_s2_last_request_time = 0

def _s2_rate_limit():
    """Ensure Semantic Scholar API requests are spaced at least 1 second apart."""
    global _s2_request_count, _s2_last_request_time
    _s2_request_count += 1
    if _s2_request_count > 1:
        elapsed = time.time() - _s2_last_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
    _s2_last_request_time = time.time()


def _find_pdf_links(html):
    """Find .pdf URLs in HTML, handling both single and double quotes safely."""
    pattern = r'href=[\x22\x27][^\x22\x27]*\.pdf[^\x22\x27]*[\x22\x27]'
    return re.findall(pattern, html)


# Sci-Hub domains (sorted by reliability based on Synthos history)
SCIHUB_DOMAINS = [
    "https://sci-hub.ru",
    "https://sci-hub.ee",
    "https://sci-hub.wf",
    "https://sci-hub.vg",       # Tor-verified working (2026-06-19)
    "https://sci-hub.ren",
    "https://sci-hub.se",
]

# Tor-verified working domain (2026-06-19)
SCIHUB_TOR_DOMAIN = "https://sci-hub.vg"

# Frontiers journal mapping (DOI prefix → journal slug)
FRONTIERS_PREFIXES = {
    "10.3389/f": "f",          # fneur, fimmu, fncom, etc.
    "10.3389/fsymp": "fsymp",
}

# Cloudflare detection
_CLOUDFLARE_SIGNATURES = [
    b'cf-browser-verification',
    b'Checking your browser',
    b'DDoS protection',
    b'Just a moment',
    b'Attention Required',
]

# PDF magic header
PDF_MAGIC = b'%PDF'

# Validate PDF fingerprint (avoid known pseudopdf)
KNOWN_PSEUDOPDF_MD5 = {
    "fd469bd7cd29446f2800f099e3b71457",  # MedData pseudopdf
}