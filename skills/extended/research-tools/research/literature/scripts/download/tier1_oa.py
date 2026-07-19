#!/usr/bin/env python3
"""
Tier 1: OA 直链下载 — arXiv, Frontiers, PLOS, CrossRef, Unpaywall, PMC。
"""
import json
import re
import urllib.request
import urllib.parse
from typing import Optional


def download_arxiv_pdf(arxiv_id: str) -> Optional[bytes]:
    """Download PDF from arXiv directly."""
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    from .http_download import download_http
    content = download_http(url, timeout=30)
    if content and content[:4] == b'%PDF' and len(content) > 100:
        return content
    abs_url = f"https://arxiv.org/abs/{arxiv_id}"
    content = download_http(abs_url, timeout=30)
    if content:
        m = re.search(r'href=["\']([^"\']*(?:\.pdf|pdf\.abs)[^"\']*)["\']', content.decode('utf-8', errors='replace'))
        if m:
            pdf_url = m.group(1)
            if pdf_url.startswith('//'):
                pdf_url = 'https:' + pdf_url
            return download_http(pdf_url, timeout=30)
    return None


def download_frontiers_pdf(doi: str) -> Optional[bytes]:
    """Download PDF from Frontiers journals."""
    m = re.match(r'10\.3389/(f\w+)\.\d+\.\d+', doi)
    if m:
        journal = m.group(1)
        url = f"https://www.frontiersin.org/journals/{journal}/articles/{doi}/pdf"
        from .http_download import download_http
        content = download_http(url, timeout=30)
        if content and content[:4] == b'%PDF' and len(content) > 100:
            return content
        doi_replaced = doi.replace('/', '-')
        url2 = f"https://www.frontiersin.org/journals/{journal}/articles/{doi_replaced}/pdf"
        return download_http(url2, timeout=30)
    return None


def download_plos_pdf(doi: str) -> Optional[bytes]:
    """Download PDF from PLOS journals."""
    doi_no_slash = doi.replace('/', '')
    url = f"https://journals.plos.org/plosone/article/file?id={doi_no_slash}&type=pdf"
    from .http_download import download_http
    return download_http(url, timeout=30)


def download_crossref_link(doi: str) -> Optional[bytes]:
    """Crossref: get open access PDF link for a DOI."""
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception:
        return None

    result = data.get("message", {})
    for link in result.get("link", []):
        if link.get("intended-application") == "text-mining" or link.get("content-type") == "unspecified":
            link_url = link.get("url", "")
            if link_url and ("pdf" in link_url.lower() or link_url.endswith(".pdf")):
                from .http_download import download_http
                content = download_http(link_url, timeout=30)
                if content and content[:4] == b'%PDF' and len(content) > 100:
                    return content
    oa = result.get("best_oa_location", {})
    if oa:
        pdf_url = oa.get("pdf_url") or oa.get("url")
        if pdf_url:
            from .http_download import download_http
            return download_http(pdf_url, timeout=30)
    return None


def download_unpaywall(doi: str) -> Optional[bytes]:
    """Unpaywall API: get OA location for a DOI."""
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email=test@synthos"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception:
        return None

    if not data.get("is_oa"):
        return None

    oa_location = data.get("best_oa_location", {})
    if oa_location:
        pdf_url = oa_location.get("pdf_url") or oa_location.get("url")
        if pdf_url:
            from .http_download import download_http
            return download_http(pdf_url, timeout=30)
    return None


def download_pubmed_central(pmcs_id: str) -> Optional[bytes]:
    """Download PDF from PubMed Central.

    策略：
    1. 通过 efetch 获取 JATS XML，尝试提取 self-uri（PDF 直链）
    2. NCBI 已不再通过 pdf/ 路径直接提供 PDF（返回 HTML），需回退
    3. XML → 提取标题/正文 → Markdown → pandoc → PDF
    """
    import xml.etree.ElementTree as ET

    # Step 1: 获取 JATS XML
    xml_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcs_id}&retmode=xml"
    try:
        req = urllib.request.Request(xml_url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_content = resp.read()
    except Exception:
        return None

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return None

    # Step 2: NCBI 已不再通过 pdf/ 路径提供 PDF（超时 30s），直接跳过
    # 仅当有已知有效自部署 PDF 服务时启用

    # Step 3: XML → Markdown → pandoc → PDF
    import subprocess
    import tempfile
    import os

    try:
        # 从 XML 提取文本构建 Markdown
        md_lines = []
        for article_title in root.iter('article-title'):
            t = article_title.text
            if t:
                md_lines.append(f"# {t.strip()}")
        for sec in root.iter('sec'):
            title = sec.find('title')
            if title is not None and title.text:
                md_lines.append(f"## {title.text}")
            for p in sec.iter('p'):
                text = ''.join(p.itertext()).strip()
                if text:
                    md_lines.append(text)

        # 写入临时 Markdown
        # 替换常见 Unicode 数学符号为 ASCII（pdflatex 不支持 Unicode）
        md_text = '\n\n'.join(md_lines)
        for uni, ascii_rep in [('≥', '>='), ('≤', '<='), ('≠', '!='), ('→', '->'),
                                ('∑', 'SUM'), ('∏', 'PROD'), ('μ', 'u'), ('α', 'a')]:
            md_text = md_text.replace(uni, ascii_rep)

        with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w', encoding='utf-8') as md_f:
            md_path = md_f.name
            md_f.write(md_text)

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_f:
            pdf_path = pdf_f.name

        try:
            result = subprocess.run(
                ['pandoc', '-f', 'markdown', '-o', pdf_path, md_path, '--pdf-engine=pdflatex'],
                capture_output=True, timeout=120, text=True
            )
            # pandoc 返回 exit 43（LuaLaTeX zlib 不匹配）但 PDF 可能已生成
            # 只要 PDF 文件存在且非空就接受
            if os.path.getsize(pdf_path) > 100 and open(pdf_path, 'rb').read().startswith(b"%PDF-"):
                with open(pdf_path, 'rb') as f:
                    return f.read()
        finally:
            for p in (md_path, pdf_path):
                try: os.unlink(p)
                except: pass
    except Exception:
        pass

    return None


def search_pmc_for_pubmed(pmid: str) -> Optional[str]:
    """Search for PMC full text linked to a PMID."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&id={pmid}&db=pmc&retmode=json"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception:
        return None

    links = data.get("eLinkResult", {}).get("LinkSet", [{}])[0]
    link_ids = links.get("LinkSetDbHistory", {}).get("Link", [])
    if link_ids:
        return link_ids[0].get("LinkID", "")
    return None