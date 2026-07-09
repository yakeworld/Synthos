#!/usr/bin/env python3
"""
Sci-Hub 全文下载 — 简洁调用（DEPRECATED）。

⚠️ 已合并入 scientific_hub.py，请使用:
    from download.scientific_hub import download

保留此文件仅作为兼容层。
"""
import sys
import os
import re
import subprocess
from typing import Optional

SCIHUB_DOMAIN = "https://sci-hub.vg"


def get_proxy() -> str:
    """获取 SOCKS5 代理地址。"""
    proxy = os.environ.get("TOR_PROXY", "")
    for prefix in ["socks5://", "socks5h://", "socks://"]:
        if proxy.startswith(prefix):
            proxy = proxy[len(prefix):]
            break
    return proxy if proxy else ""


def _curl(url: str, timeout: int = 30, proxy: str = None, referer: str = None) -> Optional[bytes]:
    """curl 下载，返回原始字节（不验证 PDF）。"""
    cmd = [
        "curl", "-s", "-o", "-",
        "--connect-timeout", "5",
        "--max-time", str(timeout),
        "-X", "GET",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        url,
    ]
    if proxy:
        cmd.extend(["--socks5-hostname", proxy])
    if referer:
        cmd.extend(["-H", f"Referer: {referer}"])

    try:
        r = subprocess.run(cmd, capture_output=True, text=False, timeout=timeout + 5)
        if r.returncode != 0:
            return None
        if len(r.stdout) < 50:
            return None
        return r.stdout
    except Exception:
        return None


def download(doi: str) -> Optional[bytes]:
    """
    下载 Sci-Hub 全文。

    流程:
        1. 直连 sci-hub.vg 获取 HTML
        2. 从 HTML 提取 PDF 链接
        3. 直连下载 PDF → 失败则代理
    """
    proxy = get_proxy()
    url = f"{SCIHUB_DOMAIN}/{doi}"

    # Step 1: 获取 HTML 页面
    html = _curl(url, timeout=15)
    if not html:
        return None

    # 直接响应就是 PDF
    if html[:4] == b"%PDF":
        return html

    # Step 2: 提取 PDF 链接
    html_text = html.decode('utf-8', errors='replace')
    m = re.search(r'iframe[^>]+src=["\']([^"\']*\.pdf[^"\']*)["\']', html_text)
    if not m:
        m = re.search(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', html_text)
    if not m:
        return None

    pdf_url = m.group(1)
    if pdf_url.startswith('//'):
        pdf_url = 'https:' + pdf_url
    elif pdf_url.startswith('/'):
        pdf_url = SCIHUB_DOMAIN + pdf_url

    # Step 3: 先直连下载
    pdf = _curl(pdf_url, timeout=30, referer=url)
    if pdf and pdf[:4] == b"%PDF":
        return pdf

    # 直连失败，尝试代理
    if proxy:
        pdf = _curl(pdf_url, timeout=30, proxy=proxy, referer=url)
        if pdf and pdf[:4] == b"%PDF":
            return pdf

    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 sci_hud_download.py <doi> [output.pdf]")
        sys.exit(1)

    doi = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else f"{doi}.pdf"

    print(f"Downloading: {doi}")
    result = download(doi)

    if result:
        with open(output, 'wb') as f:
            f.write(result)
        print(f"✅ Saved: {output} ({len(result):,} bytes)")
    else:
        print("❌ Download failed")
        sys.exit(1)