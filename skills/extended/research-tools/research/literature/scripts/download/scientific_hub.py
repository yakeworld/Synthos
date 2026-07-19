#!/usr/bin/env python3
"""
Sci-Hub 下载管线 — CDN 直连优先，frontend 页面解析备胎。

流程:
  优先: https://sci.bban.top/pdf/{doi}.pdf (直连 CDN，无 captcha)
  备胎: frontend HTML 页面 → 解析 iframe#pdf → CDN URL → 下载

原理:
  Sci-Hub 架构: N 个 frontend 域名 → 统一 CDN sci.bban.top (实际 PDF 源)
  CDN 直连不需要 captcha，比走 frontend 更可靠。
  Frontend 页面现在有 captcha (altcha)，仅作 CDN URL 格式变更时的备胎。

环境变量:
    SCIHUB_FRONTEND — 指定 frontend 域名，如 "sci-hub.ru" (可选)
"""
import subprocess
import os
import re
from typing import Optional

# Sci-Hub CDN 唯一入口
SCIHUB_CDN_BASE = "https://sci.bban.top/pdf/%s.pdf"

# Sci-Hub frontend 域名池（CDN 备胎）
FRONTEND_DOMAINS = [
    "sci-hub.ru",
    "sci-hub.st",
    "sci-hub.ee",
    "sci-hub.se",
    "sci-net.xyz",
]


def _download_from_url(url: str, timeout: int = 30) -> Optional[bytes]:
    """从 URL 下载并验证 PDF。"""
    cmd = [
        "curl", "-s", "-o", "-",
        "--connect-timeout", "10",
        "--max-time", str(timeout),
        "-L",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        url,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=False, timeout=timeout + 5)
        if r.returncode != 0:
            return None
        if len(r.stdout) < 100:
            return None
        if r.stdout[:4] != b"%PDF":
            return None
        return r.stdout
    except Exception:
        return None


def _ping_frontend(domain: str, timeout: int = 3) -> bool:
    """检查 frontend 域名是否可达。"""
    url = f"https://{domain}"
    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "--connect-timeout", str(timeout),
        "--max-time", str(timeout),
        url,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
        return r.stdout.strip() in ("200", "301", "302")
    except Exception:
        return False


def _get_html(domain: str, doi: str, timeout: int = 15) -> Optional[str]:
    """获取 Sci-Hub 页面 HTML。"""
    url = f"https://{domain}/{doi}"
    cmd = [
        "curl", "-s",
        "--connect-timeout", "10",
        "--max-time", str(timeout),
        "-L",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        url,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode == 0 and len(r.stdout) > 200 and "iframe" in r.stdout:
            return r.stdout
        return None
    except Exception:
        return None


def _extract_pdf_url(html: str) -> Optional[str]:
    """从 HTML 中提取 PDF URL。"""
    # iframe#pdf → src
    m = re.search(r'<iframe[^>]*id=["\']pdf["\'][^>]*src=["\']([^"\']+)["\']', html)
    if m:
        src = m.group(1)
        return f"https:{src}" if src.startswith("//") else src

    # plain iframe → src
    m = re.search(r'<iframe[^>]+src=["\']([^"\']+\.pdf[^"\']*)["\']', html)
    if m:
        src = m.group(1)
        return f"https:{src}" if src.startswith("//") else src

    # embed → src
    m = re.search(r'<embed[^>]+src=["\']([^"\']+)["\']', html)
    if m:
        src = m.group(1)
        return f"https:{src}" if src.startswith("//") else src

    return None


def download(doi: str, output: str = None, timeout: int = 60) -> Optional[bytes]:
    """
    通过 Sci-Hub 下载 PDF。

    策略: CDN 直连优先 → frontend 页面解析备胎

    参数:
        doi: 论文 DOI
        output: 输出文件路径，None 则返回 bytes
        timeout: 超时秒数

    返回:
        bytes: PDF 字节内容，失败返回 None
    """
    # ── 策略 1: CDN 直连 ──
    cdn_url = SCIHUB_CDN_BASE % doi
    result = _download_from_url(cdn_url, timeout=timeout // 2)
    if result:
        if output:
            with open(output, "wb") as f:
                f.write(result)
        return result

    # ── 策略 2: frontend 页面 → iframe 解析 → CDN 下载 ──
    frontend = os.environ.get("SCIHUB_FRONTEND", "").strip()
    domains = [frontend] if frontend else FRONTEND_DOMAINS

    for d in domains:
        if not _ping_frontend(d):
            continue

        html = _get_html(d, doi, timeout=timeout // 2)
        if not html:
            continue

        pdf_url = _extract_pdf_url(html)
        if not pdf_url:
            continue

        result = _download_from_url(pdf_url, timeout=timeout // 2)
        if result:
            if output:
                with open(output, "wb") as f:
                    f.write(result)
            return result

    return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 scientific_hub.py <doi> [output.pdf]")
        sys.exit(1)

    doi = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else f"{doi.replace('/', '_')}.pdf"

    result = download(doi, output=output)
    if result:
        print(f"Saved: {output} ({len(result):,} bytes)")
    else:
        print("Failed")
        sys.exit(1)
