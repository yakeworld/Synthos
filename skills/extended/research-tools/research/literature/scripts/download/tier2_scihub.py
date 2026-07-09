#!/usr/bin/env python3
"""
Tier 2: Sci-Hub 下载 — curl subprocess + SOCKS5 代理。

原理:
1. 尝试通过代理（TOR_PROXY）访问各域名
2. 从 HTML 页面提取 PDF 链接（iframe/src/href）
3. 通过同一代理下载 PDF 全文
4. 验证 %PDF 魔术字节

关键:
- 使用 curl --socks5-hostname 通过 SOCKS5 代理
- 不再依赖 curl_cffi（直接连接被封锁）
- 多域名轮询，找到可用的
- 本地 Tor（ExitPolicy reject）不可用，依赖远程代理
"""
import os
import re
import subprocess
from typing import Optional
from .config import MAX_SIZE
from .utils import verify_pdf

# Sci-Hub 域名列表（按可用性排序）
SCIHUB_DOMAINS = [
    "https://sci-hub.vg",     # Currently best working domain
    "https://sci-hub.ru",     # May trigger captcha
    "https://sci-hub.se",
    "https://sci-hub.ee",
    "https://sci-hub.wf",
]


def get_proxy():
    """Get SOCKS5 proxy address from environment."""
    proxy = os.environ.get("TOR_PROXY", "")
    # TOR_PROXY can be socks5://host:port or just host:port
    for prefix in ["socks5://", "socks5h://", "socks://", "socks4://"]:
        if proxy.startswith(prefix):
            proxy = proxy[len(prefix):]
            break
    return proxy if proxy else ""


def _curl_raw(url, timeout=30, proxy=None, referer=None):
    """Download via curl, return raw bytes regardless of content type."""
    cmd = [
        "curl", "-s", "-o", "-",
        "--connect-timeout", "5",
        "--max-time", str(timeout),
        "-X", "GET",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        url,
    ]
    if proxy:
        cmd.extend(["--socks5-hostname", proxy])
    if referer:
        cmd.extend(["-H", f"Referer: {referer}"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=False, timeout=timeout + 5)
        if result.returncode != 0:
            return None
        content = result.stdout
        if len(content) > MAX_SIZE or len(content) < 50:
            return None
        return content
    except Exception:
        return None


def _extract_pdf_url(html_bytes, base_domain):
    """Extract PDF URL from Sci-Hub HTML page."""
    try:
        html = html_bytes.decode('utf-8', errors='replace')
    except Exception:
        return None

    # Pattern 1: iframe src with PDF
    m = re.search(r'iframe[^>]+src=["\']([^"\']*\.pdf[^"\']*)["\']', html)
    if m:
        return m.group(1)

    # Pattern 2: href link to PDF
    m = re.search(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', html)
    if m:
        return m.group(1)

    # Pattern 3: /storage/ path
    m = re.search(r'href=["\'](/storage/[^"\']+)["\']', html)
    if m:
        path = m.group(1)
        return base_domain + path if path.startswith('/') else path

    # Pattern 4: /storage/tail/ path
    m = re.search(r'(/storage/tail/[^"\']*\.pdf)', html)
    if m:
        return base_domain + m.group(1)

    return None


def download_scihub_proxy(doi: str) -> Optional[bytes]:
    """Download from Sci-Hub via SOCKS5 proxy. Tries all domains sequentially."""
    proxy = get_proxy()
    if not proxy:
        return None

    for domain in SCIHUB_DOMAINS:
        try:
            url = f"{domain}/{doi}"

            # Step 1: Get HTML page (raw, no PDF validation)
            html = _curl_raw(url, timeout=15, proxy=proxy)
            if not html:
                continue

            # If HTML is actually a direct PDF response, return it
            if verify_pdf(html):
                return html

            # Step 2: Extract PDF URL from HTML
            pdf_url = _extract_pdf_url(html, domain)
            if not pdf_url:
                continue

            # Normalize URL
            if pdf_url.startswith('//'):
                pdf_url = 'https:' + pdf_url
            elif pdf_url.startswith('/'):
                pdf_url = domain + pdf_url

            # Step 3: Download PDF
            pdf_content = _curl_raw(pdf_url, timeout=30, proxy=proxy, referer=url)
            if pdf_content:
                return pdf_content

        except Exception:
            continue

    return None


# Legacy alias for backward compatibility
download_scihub_direct = download_scihub_proxy


# Tor function removed - local Tor has ExitPolicy reject *:*
# and remote Tor is accessed via proxy instead
def download_scihub_via_tor(doi: str) -> None:
    """No-op: Tor not available (ExitPolicy reject)."""
    return None