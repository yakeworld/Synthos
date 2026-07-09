#!/usr/bin/env python3
"""
Tier 4: 出版社直链 — DOI2PDF, CORE, OpenURL, ScienceDirect, Springer, Wiley, IEEE, ACM, S2, BioRxiv.
"""
import json
import os
import re
import urllib.request
from typing import Optional

from .utils import verify_pdf
from .http import download_http
from . import config

SS_API_KEY=os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")


def normalize_doi(doi: str) -> str:
    """Normalize DOI to standard form (10.xxxx/...)."""
    doi = doi.strip()
    # Strip URL prefix
    for prefix in ["https://doi.org/", "http://doi.org/", "doi:"]:
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    # Strip leading 10. if not present
    if not doi.startswith("10."):
        doi = "10." + doi
    # Remove trailing slashes
    doi = doi.rstrip("/")
    return doi


def extract_doi_from_text(text: str) -> Optional[str]:
    """Extract DOI from any text."""
    m = re.search(r'(10\.\d{4,}(?:\.\d+|[a-zA-Z]+)[/\-][^\s\)]+)', text)
    return m.group(1) if m else None


def extract_arxiv_id(text: str) -> Optional[str]:
    """Extract arXiv ID from text."""
    m = re.search(r'(?:arxiv\.org/abs/|archive\.org/pdf/)(\d{4}\.\d{4,5}(?:v\d+)?)', text)
    if m:
        return m.group(1)
    m = re.search(r'(\d{4}\.\d{4,5})', text)
    return m.group(1) if m else None


def extract_pmcs_id(text: str) -> Optional[str]:
    """Extract PMC full-text ID."""
    m = re.search(r'(PMC?\d{7,8})', text)
    return m.group(1).replace('PMC', 'PMC') if m else None


def extract_pmid(text: str) -> Optional[str]:
    """Extract PMID from text."""
    m = re.search(r'(?:pmid[:\s]*|NCBI:?PMID:?\s*)(\d{6,8})', text)
    if m:
        return m.group(1)
    # Try plain 7-9 digit number in context
    m = re.search(r'\b(\d{7,9})\b', text)
    if m and int(m.group(1)) > 1000000:
        return m.group(1)
    return None


# ─── Racing Engine ───────────────────────────────────────────────────────────


# === Tier 0: Semantic Scholar PDF URL ===
def download_s2_pdf(doi=None, external_ids=None):
    """Download PDF from Semantic Scholar openAccessPdf URL. Uses API key with rate limiting."""
    pdf_url = None
    if external_ids and isinstance(external_ids, dict):
        for key in ["openAccessPdf", "open_access_pdf"]:
            val = external_ids.get(key)
            if isinstance(val, dict) and val.get("url"):
                pdf_url = val["url"]
                break
    if not pdf_url and doi:
        from .config import _s2_rate_limit
        _s2_rate_limit()
        url = "https://api.semanticscholar.org/graph/v1/paper/DOI:" + normalize_doi(doi) + "?fields=title,year,openAccessPdf,externalIds,citedByUrl"
        try:
            import requests as _s2_req
            headers = {"Accept": "application/json", "User-Agent": "Synthos/2.0"}
            if SS_API_KEY:
                headers["x-api-key"] = SS_API_KEY
            resp = _s2_req.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                pdf = data.get("openAccessPdf")
                if pdf and isinstance(pdf, dict) and pdf.get("url"):
                    pdf_url = pdf["url"]
        except Exception:
            pass
    if not pdf_url:
        return None
    try:
        content = download_http(pdf_url, timeout=60, headers={"User-Agent": "Synthos/2.0"})
        if content and verify_pdf(content):
            return content
    except Exception:
        pass
    return None


# === Tier 1: BioRxiv / MedRxiv ===
def download_biorxiv_pdf(doi=None):
    """Download PDF from bioRxiv/medRxiv. DOI prefix: 10.1101/"""
    if not doi or not doi.startswith("10.1101/"):
        return None
    normalized = normalize_doi(doi)
    search_url = "https://api.biorxiv.org/details/biorxiv/" + normalized + "/"
    try:
        req = urllib.request.Request(search_url, headers={"User-Agent": "Synthos/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        series = data.get("screened", [])
        if series:
            info = series[0].get("metadata", {})
            server = info.get("server", "bioRxiv")
            version = info.get("version", "1")
            url = "https://www." + server + ".org/content/" + server + "/" + version + "/full.pdf"
            content = download_http(url, timeout=60)
            if content and verify_pdf(content):
                return content
    except Exception:
        pass
    m = re.search(r'10\.1101/(\d+)', normalized)
    if m:
        for pattern in [
            "https://www.biorxiv.org/content/" + normalized + "v1.full.pdf",
            "https://www.medrxiv.org/content/" + normalized + "v1.full.pdf",
            "https://www.biorxiv.org/content/" + normalized + ".full.pdf",
        ]:
            try:
                content = download_http(pattern, timeout=60)
                if content and verify_pdf(content):
                    return content
            except Exception:
                continue
    return None


# === Tier 1: CORE OA Aggregator ===
def download_core(doi=None):
    """Download from CORE — world's largest OA aggregation (60M+ papers)."""
    if not doi:
        return None
    normalized = normalize_doi(doi)
    url = "https://api.core.ac.uk/v30/documents/" + normalized
    try:
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "Synthos/2.0 (pdf-download)"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        d = data.get("download", {})
        if isinstance(d, dict) and d.get("downloadUrl"):
            content = download_http(d["downloadUrl"], timeout=60, headers={"User-Agent": "Synthos/2.0"})
            if content and verify_pdf(content):
                return content
    except Exception:
        pass
    search_url = "https://api.core.ac.uk/v30/search/works?q=doi:" + normalized + "&limit=1"
    try:
        req = urllib.request.Request(search_url, headers={
            "Accept": "application/json",
            "User-Agent": "Synthos/2.0 (pdf-download)"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        items = data.get("value", [])
        if items:
            for item in items:
                links = item.get("downloadUrl") or item.get("links", [])
                if isinstance(links, list):
                    for link in links:
                        if isinstance(link, dict) and link.get("url"):
                            u = link["url"]
                            if u.endswith(".pdf") or "pdf" in u.lower():
                                content = download_http(u, timeout=60)
                                if content and verify_pdf(content):
                                    return content
    except Exception:
        pass
    return None


# === Tier 1: DOI2PDF API ===
def download_doi2pdf(doi=None):
    """Download via DOI2PDF API (https://doi2pdf.org) — free PDF resolver."""
    if not doi:
        return None
    url = "https://doi2pdf.org/api/v1/download/" + normalize_doi(doi)
    try:
        content = download_http(url, timeout=60)
        if content and verify_pdf(content):
            return content
    except Exception:
        pass
    # Fallback: use the web page
    html_url = "https://doi2pdf.org/" + normalize_doi(doi)
    try:
        content = download_http(html_url, timeout=10)
        if content:
            pdf_links = _find_pdf_links(content.decode('utf-8', errors='replace'))
            for link in pdf_links[:3]:
                if link.startswith('//'):
                    link = 'https:' + link
                content = download_http(link, timeout=60)
                if content and verify_pdf(content):
                    return content
    except Exception:
        pass
    return None


# === Tier 1: OpenURL / SFX DOI Resolver ===
def download_via_openurl(doi=None, title=None):
    """Resolve PDF via OpenURL/SFX — standard link resolver protocol."""
    if not doi:
        return None
    kev = "rft_val_fmt=info:ofi/fmt:kev:mtx:article&rft.genre=journal&rft_id=info:doi/" + normalize_doi(doi) + "&rft.au=unknown&rft.ti=unknown"
    try:
        query = "https://sfx.biblio.ugent.be/openurl?" + kev
        content = download_http(query, timeout=10, headers={"User-Agent": "Synthos/2.0"})
        if content:
            html = content.decode('utf-8', errors='replace')
            pdf_links = _find_pdf_links(html)
            for link in pdf_links[:5]:
                if link.startswith('//'):
                    link = 'https:' + link
                pdf_content = download_http(link, timeout=60)
                if pdf_content and verify_pdf(pdf_content):
                    return pdf_content
    except Exception:
        pass
    return None


def download_sciencedirect(doi=None):
    """Download from ScienceDirect. DOI prefix: 10.1016/"""
    if not doi or not doi.startswith("10.1016/"):
        return None
    html_url = "https://www.sciencedirect.com/science/article/pii/" + normalize_doi(doi).split('/')[-1]
    try:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        content = download_http(html_url, timeout=30, headers={"User-Agent": ua})
        if content:
            html = content.decode('utf-8', errors='replace')
            for link in _find_pdf_links(html):
                if not link.startswith("http"):
                    link = "https:" + link
                pdf_content = download_http(link, timeout=60, headers={"User-Agent": ua})
                if pdf_content and verify_pdf(pdf_content):
                    return pdf_content
    except Exception:
        pass
    return None


# === Tier 2: SpringerLink ===
def download_springer(doi=None, title=None):
    """Download from SpringerLink. DOI prefixes: 10.1007, 10.1186 (BMC), 10.1515."""
    if not doi:
        return None
    normalized = normalize_doi(doi)
    url = "https://link.springer.com/content/pdf/" + normalized + ".pdf"
    try:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        content = download_http(url, timeout=30, headers={"User-Agent": ua})
        if content and verify_pdf(content):
            return content
    except Exception:
        pass
    html_url = "https://link.springer.com/article/" + normalized
    try:
        content = download_http(html_url, timeout=30, headers={"User-Agent": ua})
        if content:
            html = content.decode('utf-8', errors='replace')
            for link in _find_pdf_links(html):
                if "/content/pdf/" in link:
                    if not link.startswith("http"):
                        link = "https:" + link
                    pdf_content = download_http(link, timeout=60)
                    if pdf_content and verify_pdf(pdf_content):
                        return pdf_content
    except Exception:
        pass
    return None


# === Tier 2: Wiley Online Library ===
def download_wiley(doi=None):
    """Download from Wiley. DOI prefixes: 10.1002, 10.1111."""
    if not doi:
        return None
    normalized = normalize_doi(doi)
    url = "https://api.wiley.com/onlinelibrary/exports/resolve/" + normalized
    try:
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "Synthos/2.0"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        for link in data.get("references", []):
            pdf_url = link.get("pdfUrl") or link.get("pdf_link")
            if pdf_url and str(pdf_url).endswith(".pdf"):
                content = download_http(pdf_url, timeout=60)
                if content and verify_pdf(content):
                    return content
    except Exception:
        pass
    html_url = "https://onlinelibrary.wiley.com/doi/" + normalized
    try:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        content = download_http(html_url, timeout=30, headers={"User-Agent": ua})
        if content:
            html = content.decode('utf-8', errors='replace')
            for link in _find_pdf_links(html):
                if not link.startswith("http"):
                    link = "https:" + link
                pdf_content = download_http(link, timeout=60, headers={"User-Agent": ua})
                if pdf_content and verify_pdf(pdf_content):
                    return pdf_content
    except Exception:
        pass
    return None


# === Tier 2: IEEE Xplore ===
def download_ieee(doi=None):
    """Download from IEEE Xplore. DOI prefix: 10.1109/"""
    if not doi or not doi.startswith("10.1109/"):
        return None
    arnum = doi.split('/')[-1]
    url = "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=" + arnum
    try:
        content = download_http(url, timeout=60)
        if content and verify_pdf(content):
            return content
    except Exception:
        pass
    html_url = "https://ieeexplore.ieee.org/document/" + arnum
    try:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        content = download_http(html_url, timeout=30, headers={"User-Agent": ua})
        if content:
            html = content.decode('utf-8', errors='replace')
            import re as _re2
            m = _re2.search(r'href=.*?/stamp/stamp\.jsp[^"\']*"', html)
            if m:
                pdf_url = "https://ieeexplore.ieee.org" + m.group(0).strip('"\' ')
                pdf_content = download_http(pdf_url, timeout=60)
                if pdf_content and verify_pdf(pdf_content):
                    return pdf_content
    except Exception:
        pass
    return None


# === Tier 2: ACM Digital Library ===
def download_acm(doi=None):
    """Download from ACM Digital Library. DOI prefix: 10.1145/"""
    if not doi or not doi.startswith("10.1145/"):
        return None
    normalized = normalize_doi(doi)
    url = "https://dl.acm.org/doi/pdf/" + normalized
    try:
        content = download_http(url, timeout=60)
        if content and verify_pdf(content):
            return content
    except Exception:
        pass
    html_url = "https://dl.acm.org/doi/" + normalized
    try:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        content = download_http(html_url, timeout=30, headers={"User-Agent": ua})
        if content:
            html = content.decode('utf-8', errors='replace')
            for link in _find_pdf_links(html):
                if not link.startswith("http"):
                    link = "https:" + link
                pdf_content = download_http(link, timeout=60, headers={"User-Agent": ua})
                if pdf_content and verify_pdf(pdf_content):
                    return pdf_content
    except Exception:
        pass
    return None

