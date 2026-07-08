#!/usr/bin/env python3
"""
Tier 3: 备份下载 — LibGen（图书）+ MedData（机构库）。
"""
import json
import os
import re
import subprocess
import time
import urllib.parse
from typing import Optional
from . import config


def download_libgen(doi: str = None, title: str = None) -> Optional[bytes]:
    """Download from LibGen mirrors by title."""
    if not title:
        return None

    libgen_hosts = [
        "https://libgen.is",
        "https://libgen.rs",
        "https://b-ok.cc",
        "https://libgen.li",
        "https://gen.lib.rus.ec",
    ]

    for host in libgen_hosts:
        try:
            query = urllib.parse.quote(title[:100])
            url = f"{host}/sql.php?req={query}&column=title&view=simple&res=25&phrase=1"
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode('utf-8', errors='replace')

            # Find PDF links
            import re as _re_mod
            pdf_links = _re_mod.findall(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', html)
            for link in pdf_links:
                if link.startswith('http'):
                    from .http import download_http
                    content = download_http(link, timeout=30)
                    if content and content[:4] == b'%PDF' and len(content) > 100:
                        return content
        except Exception:
            continue
    return None


def _get_meddata_token() -> Optional[str]:
    """Get MedData API token."""
    import urllib.request
    if not config.MEDDATA_API_KEY:
        return None
    url = "https://api.meddata.com.cn/v1/auth/token"
    try:
        req = urllib.request.Request(url, method="POST",
            data=json.dumps({"api_key": config.MEDDATA_API_KEY}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("token") or data.get("access_token")
    except Exception:
        return None


def download_meddata(doi: str = None, filename: str = None, pmid: str = None) -> Optional[bytes]:
    """Download from MedData (Chinese institutional DB)."""
    import urllib.request
    import urllib.parse
    token = _get_meddata_token()
    if not token:
        return None

    url = "https://api.meddata.com.cn/v1/download"
    params = {"token": token}
    if doi:
        params["doi"] = doi
    if pmid:
        params["pmid"] = pmid
    if filename:
        params["filename"] = filename

    try:
        req = urllib.request.Request(f"{url}?{urllib.parse.urlencode(params)}",
            headers={"User-Agent": "Synthos/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read()
            if content and content[:4] == b'%PDF' and len(content) > 100:
                return content
    except Exception:
        return None
    return None