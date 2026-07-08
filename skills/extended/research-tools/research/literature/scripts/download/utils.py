#!/usr/bin/env python3
"""
下载模块 — 工具函数和配置。
安全文件名、PDF验证、Bibkey生成。
"""
import re
from typing import List

# Re-export config for convenience
from . import config

def safe_filename(title: str, max_len: int = 80) -> str:
    """Create safe filename from title."""
    s = title.strip().replace("/", "_").replace("\\", "_")
    s = re.sub(r'[^\w\s\.\-]', '', s)
    s = re.sub(r'\s+', '_', s).strip('_')
    return s[:max_len] if len(s) > max_len else s


def save_pdf(content: bytes, path: str) -> str:
    """Save PDF content to file, create directories if needed."""
    import os
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'wb') as f:
        f.write(content)
    return path


def generate_bibkey(title: str, authors: List[str] = None, year: int = None) -> str:  # type: ignore[assignment]
    """Generate a BibTeX-style citation key from paper metadata."""
    if not title:
        return "unknown"

    def _extract_lastname(author: str) -> str:
        parts = author.split()
        if not parts:
            return ""
        for p in reversed(parts):
            clean = re.sub(r'[^a-zA-Z]', '', p)
            if len(clean) >= 2:
                return clean.capitalize()
        clean = re.sub(r'[^a-zA-Z]', '', parts[-1])
        return clean.capitalize()

    first_author_lastname = ""
    if authors and len(authors) > 0:
        first_author_lastname = _extract_lastname(authors[0])

    if not first_author_lastname:
        title_words = title.split()
        if title_words:
            first_author_lastname = re.sub(r'[^a-zA-Z]', '', title_words[0]).capitalize() or "?"

    yr = str(year) if year else ""

    skip_words = {"the", "a", "an", "and", "or", "for", "of", "in", "on", "to", "at", "by", "with", "from", "via", "based", "using", "towards"}
    title_words = [w.strip() for w in re.sub(r'[^\w\s-]', '', title).split() if w.strip()]
    significant = [w for w in title_words if w.lower() not in skip_words]
    title_parts = []
    for w in significant[:3]:
        clean = re.sub(r'[^a-zA-Z]', '', w)
        if clean:
            title_parts.append(clean)

    return f"{first_author_lastname}{yr}{''.join(title_parts)}"


def verify_pdf(content: bytes) -> bool:
    """Verify content is a valid PDF (magic header + reasonable size)."""
    if not content or len(content) < 100:
        return False
    if content[:4] != config.PDF_MAGIC:
        return False
    import hashlib
    md5 = hashlib.md5(content).hexdigest()
    if md5 in config.KNOWN_PSEUDOPDF_MD5:
        return False
    if b'%EOF' in content or b'endobj' in content:
        return True
    return len(content) > 10240