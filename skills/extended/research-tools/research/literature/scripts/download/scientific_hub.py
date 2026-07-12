#!/usr/bin/env python3
"""
Sci-Hub 下载管线 — bban.top CDN 直连。

原理: https://sci.bban.top/pdf/{DOI}.pdf → 直接返回 PDF 字节
无需 HTML 中转，无需域名解析，无需代理。

环境变量:
    TOR_PROXY — 已废弃，不再使用

用法:
    from download.scientific_hub import download
    
    # 通过 DOI 下载
    pdf = download("10.1016/j.jcrs.2019.04.024")
    # → b'%PDF-...'
"""
import subprocess
import os
from typing import Optional

# Sci-Hub CDN 唯一入口
SCIHUB_CDN_BASE = "https://sci.bban.top/pdf/%s.pdf"


def download(doi: str, output: str = None, timeout: int = 60) -> Optional[bytes]:
    """
    通过 bban.top CDN 下载 PDF。
    
    参数:
        doi: 论文 DOI
        output: 输出文件路径，None 则返回 bytes
        timeout: 超时秒数
    
    返回:
        bytes: PDF 字节内容，失败返回 None
    """
    url = SCIHUB_CDN_BASE % doi
    
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


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 scientific_hub.py <doi> [output.pdf]")
        sys.exit(1)
    
    doi = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else f"{doi}.pdf"
    
    result = download(doi, output=output)
    if result:
        with open(output, 'wb') as f:
            f.write(result)
        print(f"Saved: {output} ({len(result):,} bytes)")
    else:
        print("Failed")
        sys.exit(1)
