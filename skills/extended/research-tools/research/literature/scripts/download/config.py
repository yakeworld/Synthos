#!/usr/bin/env python3
"""
下载模块配置 — 全局变量、常量、辅助函数。
所有下载模块共享的配置。
"""
import os
import re
import time

# ===== 网络超时配置 =====
CONNECT_TIMEOUT = int(os.environ.get("LIT_CONNECT_TIMEOUT", "5"))
READ_TIMEOUT = int(os.environ.get("LIT_READ_TIMEOUT", "30"))
TOTAL_TIMEOUT = int(os.environ.get("LIT_TOTAL_TIMEOUT", "60"))

# ===== 文件限制 =====
MAX_SIZE = 30 * 1024 * 1024  # ~30MB

# ===== PDF 验证 =====
VERIFY_PDF_HEADER = b"%PDF-1."
VERIFY_PDF_HEADER_BYTES = len(VERIFY_PDF_HEADER)

# ===== 重试配置 =====
MAX_RETRIES = int(os.environ.get("LIT_MAX_RETRIES", "2"))
RETRY_DELAY = int(os.environ.get("LIT_RETRY_DELAY", "2"))

# ===== User-Agent =====
USER_AGENT = "Synthos-Literature/1.0"

# ===== 代理配置 =====
TOR_PROXY_URL = os.environ.get("TOR_PROXY", "socks5://127.0.0.1:9050")
TOR_PROXY = TOR_PROXY_URL  # alias for backward compatibility

# ===== 输出配置 =====
MAX_FILENAME_LENGTH = 60
DEFAULT_OUTPUT_DIR = os.environ.get("PDF_OUTPUT_DIR", "./outputs/papers/pdfs")

# ===== API Keys =====
MEDDATA_API_KEY = os.environ.get("MEDDATA_API_KEY", "")
SS_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

# ===== S2 Rate Limiter =====
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


# ===== Sci-Hub domains (sorted by reliability) =====
SCIHUB_DOMAINS = [
    "https://sci-hub.ru",
    "https://sci-hub.ee",
    "https://sci-hub.wf",
    "https://sci-hub.se",
]

SCIHUB_TOR_DOMAIN = "https://sci-hub.do"

# ===== Frontiers journal mapping (DOI prefix → journal slug) =====
FRONTIERS_PREFIXES = {
    "10.3389/f": "f",  # fneur, fimmu, fncom, etc.
    "10.3389/fsymp": "fsymp",
}

# ===== Cloudflare detection =====
_CLOUDFLARE_SIGNATURES = [
    b'cf-browser-verification',
    b'Checking your browser',
    b'DDoS protection',
    b'Just a moment',
    b'Attention Required',
]

# ===== PDF magic header =====
PDF_MAGIC = b'%PDF'

# ===== Known pseudopdf MD5s (avoid false positives) =====
KNOWN_PSEUDOPDF_MD5 = {
    "fd469bd7cd29446f2800f099e3b71457",  # MedData pseudopdf
}