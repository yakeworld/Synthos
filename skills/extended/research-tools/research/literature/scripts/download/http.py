#!/usr/bin/env python3
"""
HTTP 下载工具 — HTTP/HTTPS 下载、Tor 代理、子进程下载。
"""
import subprocess
from typing import Dict, Optional, Any


def download_http(url: str, headers: dict = None, timeout: int = 30, use_cffi: bool = False) -> Optional[bytes]:
    """Download URL content with optional curl_cffi fallback."""
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/pdf,*/*",
        }

    try:
        if use_cffi:
            from curl_cffi import requests as cffi_req
            r = cffi_req.get(url, headers=headers, impersonate="chrome",
                            timeout=timeout, allow_redirects=True)
        else:
            import requests as req
            r = req.get(url, headers=headers, timeout=timeout, allow_redirects=True)

        if r.status_code == 200:
            return r.content
        return None
    except Exception:
        return None


def download_http_tor(url: str, timeout: int = 30) -> Optional[bytes]:
    """Download via Tor SOCKS5 proxy using curl --socks5-hostname."""
    try:
        cmd = [
            "curl", "-s", "-o", "-",
            "--socks5-hostname", "127.0.0.1:9050",
            "--max-time", str(timeout),
            "-L",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=False, timeout=timeout + 5)
        if result.returncode == 0 and result.stdout:
            return result.stdout
        return None
    except Exception:
        return None


def download_via_subprocess(cmd: list, timeout: int = 30) -> Optional[bytes]:
    """Download via subprocess (curl) — safest for cron environment."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=False, timeout=timeout)
        if result.returncode == 0 and result.stdout:
            return result.stdout
        return None
    except Exception:
        return None


def smart_download(url: str, headers: dict = None, timeout: int = 30, **kwargs) -> Optional[bytes]:
    """
    Smart download: requests first → Cloudflare detected → curl_cffi fallback.
    Returns PDF bytes or None.
    """
    from . import config
    content = download_http(url, headers, timeout, use_cffi=False)
    if content and content[:4] == config.PDF_MAGIC:
        return content

    # Check for Cloudflare block on first attempt
    cf_blocked = False
    if content:
        for sig in config._CLOUDFLARE_SIGNATURES:
            if sig in content[:10000]:
                cf_blocked = True
                break
        try:
            import requests as req
            r = req.head(url, headers=headers or {}, timeout=5)
            if r.status_code == 403 and 'cloudflare' in r.headers.get('Server', '').lower():
                cf_blocked = True
        except Exception:
            pass

    if cf_blocked or (content and content[:4] != config.PDF_MAGIC):
        return download_http(url, headers, timeout, use_cffi=True)

    return content