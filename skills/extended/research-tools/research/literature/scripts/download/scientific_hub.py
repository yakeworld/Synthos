#!/usr/bin/env python3
"""
Sci-Hub 下载管线 — 分层架构。

架构:
    直连层 (direct)   — 无需代理，速度快
    代理层 (proxy)    — 通过 TOR_PROXY 访问
    总入口 (download) — 直连优先，失败自动切换代理

环境变量:
    TOR_PROXY=www.3deyes.top:9050   （SOCKS5 代理，可选）

用法:
    from download.scientific_hub import download
    
    # 自动模式（推荐）
    pdf = download("10.3389/fnmol.2020.00001")
    
    # 指定模式
    pdf = download("10.3389/fnmol.2020.00001", mode="direct")
    pdf = download("10.3389/fnmol.2020.00001", mode="proxy")
    
    # 指定域名
    pdf = download("10.3389/fnmol.2020.00001", domain="https://sci-hub.vg")
"""
import os
import re
import subprocess
from typing import Optional, List, Dict, Any

# ─── 直连域名（经全面测试，目前唯一可用） ───
DIRECT_DOMAINS = [
    "https://sci-hub.vg",
]

# ─── 代理域名（经全面测试，目前均不可用，保留备用） ───
PROXY_DOMAINS = [
    "https://sci-hub.do",
    "https://sci-hub.st",
]

# ─── PDF 链接模式 ───
PDF_PATTERNS = [
    r'iframe[^>]+src=["\']([^"\']*\.pdf[^"\']*)["\']',     # iframe src
    r'embed[^>]+src=["\']([^"\']*\.pdf[^"\']*)["\']',     # embed src
    r'href=["\']([^"\']*\.pdf[^"\']*)["\']',                # href
    r'location\.href=["\']([^"\']*\?id=[^"\']*\.pdf[^"\']*)["\']',  # JS redirect
]

# ─── 代理 ───

def get_proxy() -> str:
    """获取 SOCKS5 代理地址（去除协议前缀）。"""
    proxy = os.environ.get("TOR_PROXY", "")
    for prefix in ["socks5://", "socks5h://", "socks://"]:
        if proxy.startswith(prefix):
            proxy = proxy[len(prefix):]
            break
    return proxy if proxy else ""


# ─── 核心 curl ───

def _curl(
    url: str,
    timeout: int = 30,
    proxy: str = None,
    referer: str = None,
) -> Optional[bytes]:
    """
    通过 curl 下载 URL 原始内容。
    
    参数:
        url: 目标 URL
        timeout: 超时秒数
        proxy: SOCKS5 代理地址（host:port），None 为直连
        referer: Referer header
    
    返回:
        bytes: 原始字节内容，失败返回 None
    """
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
        r = subprocess.run(cmd, capture_output=True, text=False, timeout=timeout + 5)
        if r.returncode != 0 or len(r.stdout) < 50:
            return None
        return r.stdout
    except Exception:
        return None


# ─── 直连层 ───

def download_direct(doi: str, domain: str = None, timeout: int = 15) -> Optional[bytes]:
    """
    直连下载 Sci-Hub 全文。
    
    流程: 直连获取 HTML → 提取 PDF 链接 → 直连下载 PDF
    """
    domains = [domain] if domain else DIRECT_DOMAINS
    
    for domain in domains:
        html = _curl(f"{domain}/{doi}", timeout=timeout)
        if not html:
            continue
        
        # 直接响应就是 PDF
        if html[:4] == b"%PDF":
            return html
        
        # 提取 PDF 链接
        pdf_url = _extract_pdf_url(html)
        if not pdf_url:
            continue
        
        # 直连下载 PDF
        pdf = _curl(pdf_url, timeout=30, referer=f"{domain}/{doi}")
        if pdf and pdf[:4] == b"%PDF":
            return pdf
    
    return None


# ─── 代理层 ───

def download_proxy(doi: str, domain: str = None, timeout: int = 15) -> Optional[bytes]:
    """
    通过代理下载 Sci-Hub 全文。
    
    流程: 代理获取 HTML → 提取 PDF 链接 → 代理下载 PDF
    """
    proxy = get_proxy()
    if not proxy:
        return None
    
    domains = [domain] if domain else PROXY_DOMAINS
    
    for domain in domains:
        html = _curl(f"{domain}/{doi}", timeout=timeout, proxy=proxy)
        if not html:
            continue
        
        # 直接响应就是 PDF
        if html[:4] == b"%PDF":
            return html
        
        # 提取 PDF 链接
        pdf_url = _extract_pdf_url(html)
        if not pdf_url:
            continue
        
        # 代理下载 PDF
        pdf = _curl(pdf_url, timeout=30, proxy=proxy, referer=f"{domain}/{doi}")
        if pdf and pdf[:4] == b"%PDF":
            return pdf
    
    return None


# ─── 总入口 ───

def download(
    doi: str,
    mode: str = "auto",
    domain: str = None,
    timeout: int = 15,
) -> Optional[bytes]:
    """
    统一下载入口。
    
    参数:
        doi: 论文 DOI
        mode: "auto"（自动）/ "direct"（直连）/ "proxy"（代理）
        domain: 指定域名（可选）
        timeout: 超时秒数
    
    返回:
        bytes: PDF 字节内容，失败返回 None
    
    示例:
        >>> download("10.3389/fnmol.2020.00001")
        <PDF bytes>
        >>> download("10.3389/fnmol.2020.00001", mode="direct")
        <PDF bytes>
    """
    if mode == "auto":
        # 直连优先，失败再代理
        result = download_direct(doi, domain=domain, timeout=timeout)
        if result:
            return result
        
        # 直连失败，尝试代理
        if get_proxy():
            return download_proxy(doi, domain=domain, timeout=timeout)
        return None
    
    elif mode == "direct":
        return download_direct(doi, domain=domain, timeout=timeout)
    
    elif mode == "proxy":
        return download_proxy(doi, domain=domain, timeout=timeout)
    
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'auto', 'direct', or 'proxy'.")


# ─── 辅助函数 ───

def _extract_pdf_url(html: bytes) -> Optional[str]:
    """从 HTML 页面提取 PDF 链接。"""
    html_text = html.decode('utf-8', errors='replace')
    
    for pattern in PDF_PATTERNS:
        m = re.search(pattern, html_text)
        if m:
            url = m.group(1)
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                # 相对路径，返回 None（调用者补全）
                return url
            return url
    
    return None


# ─── CLI ───

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 scientific_hub.py <doi> [output.pdf] [--mode direct|proxy|auto]")
        sys.exit(1)
    
    doi = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else f"{doi}.pdf"
    
    mode = "auto"
    for arg in sys.argv[3:]:
        if arg.startswith("--mode="):
            mode = arg.split("=", 1)[1].lower()
    
    print(f"Downloading: {doi} (mode={mode})")
    result = download(doi, mode=mode)
    
    if result:
        with open(output, 'wb') as f:
            f.write(result)
        print(f"✅ Saved: {output} ({len(result):,} bytes)")
    else:
        print("❌ Download failed")
        sys.exit(1)