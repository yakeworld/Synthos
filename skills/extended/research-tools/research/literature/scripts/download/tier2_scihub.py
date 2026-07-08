#!/usr/bin/env python3
"""
Tier 2: Sci-Hub 下载 — curl_cffi 直连 + Tor 代理。
"""
import json
import os
import re
import subprocess
import time
from typing import Optional
from . import config


def download_scihub_direct(doi: str) -> Optional[bytes]:
    """Download from Sci-Hub via curl_cffi (impersonate chrome). Tries all domains sequentially."""
    import curl_cffi.requests as cffi_req

    for domain in config.SCIHUB_DOMAINS:
        try:
            url = f"{domain}/{doi}"
            s = cffi_req.Session()
            s.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36",
            })
            resp = s.get(url, timeout=30, allow_redirects=True)

            # Case 1: Direct PDF response
            if resp.content[:4] == config.PDF_MAGIC:
                return resp.content

            # Case 2: HTML page → extract PDF URL
            html = resp.text
            pdf_url = None

            patterns = [
                r'iframe[^>]+src=["\']([^"\']*\.pdf[^"\']*)["\']',
                r'embed[^>]+src=["\']([^"\']*\.pdf[^"\']*)["\']',
                r'href=["\']([^"\']*\.pdf[^"\']*)["\']',
                r'(/storage/tail/[^"\']*\.pdf)',
            ]
            for p in patterns:
                m = re.search(p, html)
                if m:
                    pdf_url = m.group(1)
                    break

            if not pdf_url:
                m = re.search(r'href=["\'](/storage/[^"\']+)["\']', html)
                if m:
                    pdf_url = m.group(1)
                    if pdf_url.startswith('/'):
                        pdf_url = domain + pdf_url

            if not pdf_url:
                continue

            if pdf_url.startswith('//'):
                pdf_url = 'https:' + pdf_url
            elif pdf_url.startswith('/'):
                pdf_url = domain + pdf_url

            pdf_resp = s.get(pdf_url, timeout=60, headers={'Referer': url})
            if pdf_resp.status_code == 200 and pdf_resp.content[:4] == config.PDF_MAGIC:
                return pdf_resp.content

        except Exception:
            continue

    return None


def download_scihub_via_tor(doi: str) -> Optional[bytes]:
    """Download from Sci-Hub via Tor using curl --socks5-hostname."""
    domains = ["https://sci-hub.ren", "https://sci-hub.vg", "https://sci-hub.ru", "https://sci-hub.ee"]

    for domain in domains:
        try:
            url = f"{domain}/{doi}"

            time.sleep(0.5)
            cmd = [
                "curl", "-s", "-o", "/tmp/synthos_scihub_tmp.html",
                "--socks5-hostname", "127.0.0.1:9050",
                "--max-time", "25",
                "-L",
                "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                url,
            ]
            result = subprocess.run(cmd, capture_output=True, text=False, timeout=30)

            if not os.path.exists("/tmp/synthos_scihub_tmp.html") or os.path.getsize("/tmp/synthos_scihub_tmp.html") < 100:
                continue

            try:
                with open("/tmp/synthos_scihub_tmp.html", "r", errors="replace") as f:
                    html = f.read()
            except Exception:
                continue

            if len(html) < 200:
                continue

            pdf_url = None
            m = re.search(r'(?:href|src)=["\']([^"\']*(?:https?://)?[^"\']*(?:/|\\)\\.pdf[^"\']*)["\']', html)
            if m:
                candidate = m.group(1)
                if '/pdf/' in candidate or candidate.endswith('.pdf') or 'sci.bban' in candidate or 'storage' in candidate:
                    pdf_url = candidate

            if not pdf_url:
                m = re.search(r'(?:https?://[^"\'\s>]+/[^"\'\s>]*\.pdf(?:\?[^"\'\s>]*)?)', html)
                if m:
                    candidate = m.group(0)
                    if '/pdf/' in candidate or 'sci.' in candidate or 'storage' in candidate or 'bban' in candidate:
                        pdf_url = candidate

            if not pdf_url:
                m = re.search(r'href=["\'](/storage/[^"\']+)["\']', html)
                if m:
                    pdf_url = domain + m.group(1)

            if not pdf_url:
                m = re.search(r'location\.href=[\'\"]([^\"\'\"]*\.pdf[^\"\'\"]*)', html)
                if m:
                    pdf_url = m.group(1)
                    if not pdf_url.startswith('http'):
                        pdf_url = domain + '/' + pdf_url

            pdf_cmd = [
                "curl", "-s", "-o", "-",
                "--socks5-hostname", "127.0.0.1:9050",
                "--max-time", "60",
                "-L",
                "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "-e", url,
                pdf_url,
            ]
            pdf_result = subprocess.run(pdf_cmd, capture_output=True, text=False, timeout=65)

            if pdf_result.returncode == 0 and pdf_result.stdout:
                content = pdf_result.stdout
                from .utils import verify_pdf
                if verify_pdf(content):
                    try:
                        os.remove("/tmp/synthos_scihub_tmp.html")
                    except Exception:
                        pass
                    return content

        except Exception:
            continue
        finally:
            try:
                if os.path.exists("/tmp/synthos_scihub_tmp.html"):
                    os.remove("/tmp/synthos_scihub_tmp.html")
            except Exception:
                pass

    return None