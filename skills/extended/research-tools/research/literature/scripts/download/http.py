#!/usr/bin/env python3
"""HTTP 下载工具 — HTTP and HTTPS 下载、Tor 代理、子进程下载。

职责: 提供安全的 HTTP 下载函数，支持 Tor 代理和子进程下载。

设计决策:
- smart_download() 是统一入口，接受 URL → 返回 bytes 或 None
- 优先使用 Python urllib（std），失败时回退到 curl subprocess
- Tor 代理配置通过 TOR_PROXY 环境变量（socks5://127.0.0.1:9050）
- PDF 验证通过 verify_pdf() 检查 %PDF-1.x 魔术字节
- 超时保护: 连接超时 5s，读取超时 30s

函数:
  smart_download(url, timeout=None, tor=False) → bytes | None
    - 下载 URL，返回 PDF 字节
    - 失败返回 None（不抛异常）

  verify_pdf(content) → bool
    - 验证 content 是有效的 PDF
    - 检查魔术字节 %PDF-1.x

  download_via_curl(url, timeout=30, tor=False) → bytes | None
    - 通过 curl subprocess 下载
    - 用于需要特定 curl_cffi 能力的场景

  download_via_urllib(url, timeout=30) → bytes | None
    - 通过 Python urllib 下载
    - 简单 HTTP GET，无额外功能

  safe_filename(title, max_length=60) → str
    - 将标题安全转为文件名
    - 去除/替换非法字符: /\:*?"<>|
    - 截断到 max_length

  generate_bibkey(authors, year, title_short=None) → str
    - 生成 BibTeX key
    - 格式: AuthorYear 或 AuthorYearFirstWord
    - 示例: "Yang2024", "Yang2024Vestibular"
"""
import os
import subprocess
import re
import urllib.request
import urllib.error
from .config import (
    CONNECT_TIMEOUT, READ_TIMEOUT, TOTAL_TIMEOUT, MAX_SIZE,
    USER_AGENT, TOR_PROXY
)


def smart_download(url, timeout=None, tor=False):
    """安全下载 URL，返回 PDF 字节或 None。

    参数:
        url: 要下载的 URL
        timeout: 超时秒数（默认 30）
        tor: 是否通过 Tor 代理下载
    返回:
        bytes: PDF 字节内容
        None: 下载失败（网络错误、非 PDF、超时）
    原理:
        1. 如果 TOR_PROXY 非空且 tor=True，使用 curl subprocess（支持 socks5 代理）
        2. 否则使用 Python urllib（简单 HTTP GET）
        3. 下载后验证 %PDF-1.x 魔术字节
        4. 超过 MAX_SIZE 返回 None
    限制:
        - urllib 不支持 socks5 代理，需要 Tor 时自动回退到 curl
        - curl 需要安装在系统 PATH 中
    """
    if timeout is None:
        timeout = 30

    # 尝试通过 curl 下载（支持 Tor）
    if tor or TOR_PROXY:
        result = download_via_curl(url, timeout=timeout, tor=tor)
        if result:
            return result

    # 回退到 urllib
    return download_via_urllib(url, timeout=timeout)


def verify_pdf(content):
    """验证 PDF 内容。

    参数:
        content: 下载的字节内容
    返回:
        bool: True 如果是有效 PDF
    原理:
        - 所有 PDF 文件必须以 %PDF-1.x 开头（x=0-7）
        - 这是 PDF 规范的魔术字节
        - 如果返回 HTML 错误页面（如 403、404），此检查会失败
    示例:
        >>> verify_pdf(b"%PDF-1.4...")
        True
        >>> verify_pdf(b"<!DOCTYPE html>...")
        False
    """
    if not content or len(content) < 8:
        return False
    return content[:8].startswith(b"%PDF-1.")


def download_via_curl(url, timeout=30, tor=False):
    """通过 curl subprocess 下载。

    参数:
        url: 目标 URL
        timeout: 超时秒数
        tor: 是否通过代理
    返回:
        bytes | None
    原理:
        curl -s --connect-timeout N --max-time N -X GET URL
        如果 tor=True 且 TOR_PROXY 已设置，使用 --socks5-hostname（SOCKS5）
    限制:
        - 依赖 curl 在 PATH 中
        - shell=True 有注入风险（但 URL 来自可信源）
    """
    cmd = (
        "curl -s --connect-timeout %d --max-time %d "
        "-X GET '%s' -H 'User-Agent: %s'"
    ) % (CONNECT_TIMEOUT, timeout, url, USER_AGENT)
    if tor and TOR_PROXY:
        # SOCKS5 proxy: use --socks5-hostname for domain names
        # Format: host:port
        cmd += f" --socks5-hostname {TOR_PROXY}"

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=False, timeout=timeout
        )
        if result.returncode != 0:
            return None
        content = result.stdout
        if len(content) > MAX_SIZE:
            return None
        if verify_pdf(content):
            return content
        return None
    except Exception:
        return None


def download_via_urllib(url, timeout=30):
    """通过 Python urllib 下载。

    参数:
        url: 目标 URL
        timeout: 超时秒数
    返回:
        bytes | None
    原理:
        - urllib.request.urlopen 是同步阻塞的
        - 不支持 socks5 代理（需 curl 回退）
        - timeout 包括连接和读取的总时间
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read()
            if len(content) > MAX_SIZE:
                return None
            if verify_pdf(content):
                return content
            return None
    except Exception:
        return None


def safe_filename(title, max_length=60):
    """Convert title to safe filename."""
    """Convert title to safe filename."""
    name = str(title)
    import string
    illegal = set(string.punctuation) - set("_")
    name = "".join(c if c not in illegal else "_" for c in name)
    import re
    name = re.sub(r"\s+", "_", name)
    name = name.strip("_")
    if len(name) > max_length:
        name = name[:max_length]
    return name


def normalize_doi(doi: str) -> str:
    """Normalize DOI string: remove https://doi.org/ prefix and lowercase."""
    if not doi:
        return ""
    if doi.startswith("https://doi.org/"):
        doi = doi[len("https://doi.org/"):]
    return doi.strip().lower()



# Alias for backward compatibility
download_http = smart_download
