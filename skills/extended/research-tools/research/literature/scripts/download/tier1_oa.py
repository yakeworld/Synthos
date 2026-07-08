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
    from .http import download_http
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
        from .http import download_http
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
    from .http import download_http
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
                from .http import download_http
                content = download_http(link_url, timeout=30)
                if content and content[:4] == b'%PDF' and len(content) > 100:
                    return content
    oa = result.get("best_oa_location", {})
    if oa:
        pdf_url = oa.get("pdf_url") or oa.get("url")
        if pdf_url:
            from .http import download_http
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
            from .http import download_http
            return download_http(pdf_url, timeout=30)
    return None


def download_pubmed_central(pmcs_id: str) -> Optional[bytes]:
    """Download PDF from PubMed Central."""
    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcs_id}/pdf/"
    from .http import download_http
    return download_http(url, timeout=30)


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