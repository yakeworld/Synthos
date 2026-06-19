#!/usr/bin/env python3
"""
PDF Download Engine — Multi-Source Racing Download
===================================================
Synthos Knowledge Acquisition — PDF Download Execution Script

Downloads PDFs from multiple sources with a tiered racing strategy:
  Tier 1: OA Direct (arXiv → Crossref/Unpaywall → PMC/Frontiers/PLOS)
  Tier 2: Sci-Hub direct (curl_cffi impersonate) + Sci-Hub via Tor
  Tier 3: LibGen (5 mirrors)
  Tier 4: MedData (Foreign literature DB, Chinese institutional access)

Usage:
    python3 pdf_download_engine.py 10.1016/j.neuron.2020.01.015 /tmp/paper.pdf
    python3 pdf_download_engine.py 2502.02508 /tmp/paper.pdf --type arxiv_id
    python3 pdf_download_engine.py 42296359 /tmp/paper.pdf --type pmid
    python3 pdf_download_engine.py "query" --type search --max 5 --output-dir /tmp/pdfs
    python3 pdf_download_engine.py --test  # Run full connectivity test

Environment Variables:
    MEDDATA_API_KEY         - MedData API key (optional)
    TOR_PROXY               - Tor SOCKS5 proxy (default: socks5://127.0.0.1:9050)
    PDF_OUTPUT_DIR          - Default output directory (default: ./outputs/papers/pdfs)

Exit Codes:
    0 - Success (at least one PDF downloaded)
    1 - All sources failed or invalid input
"""
import sys
import os
import json
import hashlib
import argparse
import subprocess
import re
import time
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional, Any, List

# ─── Configuration ───────────────────────────────────────────────────────────



def _find_pdf_links(html):
    """Find .pdf URLs in HTML, handling both single and double quotes safely."""
    import re as _re_mod2
    # Match href="...pdf..." or href='...pdf...'
    pattern = r"href=[\x22\x27]([^\x22\x27]*\.pdf[^\x22\x27]*)[\x22\x27]"
    return _re_mod2.findall(pattern, html)


MEDDATA_API_KEY = os.environ.get("MEDDATA_API_KEY", "")
TOR_PROXY_URL = os.environ.get("TOR_PROXY", "socks5://127.0.0.1:9050")
# Semantic Scholar API key
SS_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

# Rate limiter for Semantic Scholar API (1 request per second)
_s2_request_count = 0
_s2_last_request_time = 0

def _s2_rate_limit():
    """Ensure Semantic Scholar API requests are spaced at least 1 second apart."""
    global _s2_request_count, _s2_last_request_time
    _s2_request_count += 1
    if _s2_request_count > 1:
        elapsed = time.time() - _s2_last_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
    _s2_last_request_time = time.time()
DEFAULT_OUTPUT_DIR = os.environ.get("PDF_OUTPUT_DIR", "./outputs/papers/pdfs")
OUTPUT_FILE = os.path.join(DEFAULT_OUTPUT_DIR, "{title_safe}.pdf")

# Sci-Hub domains (sorted by reliability based on Synthos history)
SCIHUB_DOMAINS = [
    "https://sci-hub.ru",
    "https://sci-hub.ee",
    "https://sci-hub.wf",
    "https://sci-hub.vg",       # Tor-verified working (2026-06-19)
    "https://sci-hub.ren",
    "https://sci-hub.se",
]

# Tor-verified working domain (2026-06-19)
SCIHUB_TOR_DOMAIN = "https://sci-hub.vg"

# Frontiers journal mapping (DOI prefix → journal slug)
FRONTIERS_PREFIXES = {
    "10.3389/f": "f",          # fneur, fimmu, fncom, etc.
    "10.3389/fsymp": "fsymp",
}

# Cloudflare detection
_CLOUDFLARE_SIGNATURES = [
    b'cf-browser-verification',
    b'Checking your browser',
    b'DDoS protection',
    b'Just a moment',
    b'Attention Required',
]

# PDF magic header
PDF_MAGIC = b'%PDF'

# Validate PDF fingerprint (avoid known pseudopdf)
KNOWN_PSEUDOPDF_MD5 = {
    "fd469bd7cd29446f2800f099e3b71457",  # MedData pseudopdf
}


# ─── Utilities ───────────────────────────────────────────────────────────────

def safe_filename(title: str, max_len: int = 80) -> str:
    """Create safe filename from title."""
    s = title.strip().replace("/", "_").replace("\\", "_")
    s = re.sub(r'[^\w\s\.\-]', '', s)
    s = re.sub(r'\s+', '_', s).strip('_')
    return s[:max_len] if len(s) > max_len else s


def save_pdf(content: bytes, path: str) -> str:
    """Save PDF content to file, create directories if needed."""
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'wb') as f:
        f.write(content)
    return path



def generate_bibkey(title: str, authors: List[str] = None, year: int = None) -> str:
    """Generate a BibTeX-style citation key from paper metadata.
    Standard format: AuthorLastNameYearTitleAbbreviation (e.g., Vaswani2017Attention).
    Compatible with Crossref, Semantic Scholar, and Google Scholar conventions.
    """
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
    if content[:4] != PDF_MAGIC:
        return False
    # Check for pseudopdf
    md5 = hashlib.md5(content).hexdigest()
    if md5 in KNOWN_PSEUDOPDF_MD5:
        return False
    # Check for typical PDF markers
    if b'%EOF' in content or b'endobj' in content:
        return True
    # Even without %EOF, if magic header is valid and size > 10KB, likely OK
    return len(content) > 10240


def download_http(url: str, headers: dict = None, timeout: int = 30, use_cffi: bool = False) -> Optional[bytes]:
    """Download URL content with optional curl_cffi fallback."""
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/pdf,*/*",
        }

    try:
        if use_cffi:
            from curl_cffi import requests as cffi_req
            r = cffi_req.get(url, headers=headers, impersonate="chrome",
                            timeout=timeout, allow_redirects=True)
        else:
            import requests as req
            r = req.get(url, headers=headers, timeout=timeout, allow_redirects=True)

        if r.status_code == 200:
            return r.content
        return None
    except Exception:
        return None


def download_http_tor(url: str, timeout: int = 30) -> Optional[bytes]:
    """Download via Tor SOCKS5 proxy using curl --socks5-hostname.
    DNS resolution also goes through Tor to prevent leaks.
    """
    try:
        cmd = [
            "curl", "-s", "-o", "-",
            "--socks5-hostname", "127.0.0.1:9050",
            "--max-time", str(timeout),
            "-L",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=False, timeout=timeout + 5)
        if result.returncode == 0 and result.stdout:
            return result.stdout
        return None
    except Exception:
        return None



def download_via_subprocess(cmd: list, timeout: int = 30) -> Optional[bytes]:
    """Download via subprocess (curl) — safest for cron environment."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=False, timeout=timeout)
        if result.returncode == 0 and result.stdout:
            return result.stdout
        return None
    except Exception:
        return None


def smart_download(url: str, headers: dict = None, timeout: int = 30, **kwargs) -> Optional[bytes]:
    """
    Smart download: requests first → Cloudflare detected → curl_cffi fallback.
    Returns PDF bytes or None.
    """
    content = download_http(url, headers, timeout, use_cffi=False)
    if content and content[:4] == PDF_MAGIC:
        return content

    # Check for Cloudflare block on first attempt
    cf_blocked = False
    if content:
        for sig in _CLOUDFLARE_SIGNATURES:
            if sig in content[:10000]:
                cf_blocked = True
                break
        # Also check by status
        import requests as req
        try:
            r = req.head(url, headers=headers or {}, timeout=5)
            if r.status_code == 403 and 'cloudflare' in r.headers.get('Server', '').lower():
                cf_blocked = True
        except Exception:
            pass

    if cf_blocked or (content and content[:4] != PDF_MAGIC):
        return download_http(url, headers, timeout, use_cffi=True)

    return content


# ─── Tier 1: OA Direct Download ─────────────────────────────────────────────

def download_arxiv_pdf(arxiv_id: str) -> Optional[bytes]:
    """Download PDF from arXiv directly."""
    # arXiv PDF URL
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    content = download_http(url, timeout=30)
    if verify_pdf(content):
        return content
    # Fallback: abstract page
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
    # Frontiers DOI format: 10.3389/f{journal}.{year}.{article}
    m = re.match(r'10\.3389/(f\w+)\.\d+\.\d+', doi)
    if m:
        journal = m.group(1)
        # Strip leading f if present in journal name
        doi_no_slash = doi.replace('/', '_')
        url = f"https://www.frontiersin.org/journals/{journal}/articles/{doi}/pdf"
        content = download_http(url, timeout=30)
        if verify_pdf(content):
            return content
        # Try with DOI slash replaced
        doi_replaced = doi.replace('/', '-')
        url2 = f"https://www.frontiersin.org/journals/{journal}/articles/{doi_replaced}/pdf"
        return download_http(url2, timeout=30)
    return None


def download_plos_pdf(doi: str) -> Optional[bytes]:
    """Download PDF from PLOS journals."""
    doi_no_slash = doi.replace('/', '')
    url = f"https://journals.plos.org/plosone/article/file?id={doi_no_slash}&type=pdf"
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
    # Check link field for PDF
    for link in result.get("link", []):
        if link.get("intended-application") == "text-mining" or link.get("content-type") == "unspecified":
            url = link.get("url", "")
            if url and ("pdf" in url.lower() or url.endswith(".pdf")):
                return download_http(url, timeout=30)
    # Check best_oa_location
    oa = result.get("best_oa_location", {})
    if oa:
        pdf_url = oa.get("pdf_url") or oa.get("url")
        if pdf_url:
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
            return download_http(pdf_url, timeout=30)
    return None


def download_pubmed_central(pmcs_id: str) -> Optional[bytes]:
    """Download PDF from PubMed Central."""
    # PMC ID can be PMC{number} or PMC{number}
    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcs_id}/pdf/"
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
        return link_ids[0].get("LinkID", "")  # PMC ID
    return None


# ─── Tier 2: Sci-Hub ────────────────────────────────────────────────────────

def download_scihub_direct(doi: str) -> Optional[bytes]:
    """
    Download from Sci-Hub via curl_cffi (impersonate chrome).
    Tries all domains sequentially.
    """
    import curl_cffi.requests as cffi_req

    for domain in SCIHUB_DOMAINS:
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
            if resp.content[:4] == PDF_MAGIC:
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
                # Try generic /storage/ pattern
                m = re.search(r'href=["\'](/storage/[^"\']+)["\']', html)
                if m:
                    pdf_url = m.group(1)
                    if pdf_url.startswith('/'):
                        pdf_url = domain + pdf_url

            if not pdf_url:
                continue

            # Normalize URL
            if pdf_url.startswith('//'):
                pdf_url = 'https:' + pdf_url
            elif pdf_url.startswith('/'):
                pdf_url = domain + pdf_url

            # Download PDF with Referer
            pdf_resp = s.get(
                pdf_url, timeout=60,
                headers={'Referer': url}
            )
            if pdf_resp.status_code == 200 and pdf_resp.content[:4] == PDF_MAGIC:
                return pdf_resp.content

        except Exception:
            continue

    return None


def download_scihub_via_tor(doi: str) -> Optional[bytes]:
    """Download from Sci-Hub via Tor using curl --socks5-hostname.
    Strategy:
    1. curl to Sci-Hub via Tor -> get HTML with iframe/embed PDF URL
    2. Extract PDF URL from HTML
    3. curl to PDF URL via Tor -> get actual PDF content
    Tries multiple Tor-verified domains sequentially.
    """
    import subprocess as _sub
    import time as _time_mod
    
    # Try multiple domains sequentially
    domains = ["https://sci-hub.ren", "https://sci-hub.vg", "https://sci-hub.ru", "https://sci-hub.ee"]
    
    for domain in domains:
        try:
            url = f"{domain}/{doi}"
            
            # Step 1: Get HTML page via Tor using curl
            _time_mod.sleep(0.5)  # Rate limit between domains
            cmd = [
                "curl", "-s", "-o", "/tmp/synthos_scihub_tmp.html",
                "--socks5-hostname", "127.0.0.1:9050",
                "--max-time", "25",
                "-L",
                "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                url,
            ]
            result = _sub.run(cmd, capture_output=True, text=False, timeout=30)
            
            if not os.path.exists("/tmp/synthos_scihub_tmp.html") or os.path.getsize("/tmp/synthos_scihub_tmp.html") < 100:
                continue
            
            try:
                with open("/tmp/synthos_scihub_tmp.html", "r", errors="replace") as f:
                    html = f.read()
            except:
                continue
            
            if len(html) < 200:
                continue
            
            # Step 2: Extract PDF URL from HTML using multiple patterns
            pdf_url = None
            
            # Extract PDF URL from Sci-Hub HTML — must match actual .pdf URLs only
            # Pattern A: href/src containing a real URL ending in .pdf
            m = re.search(r'(?:href|src)=["\']([^"\']*(?:https?://)?[^"\']*(?:/|\\)\.pdf[^"\']*)["\']', html)
            if m:
                candidate = m.group(1)
                if '/pdf/' in candidate or candidate.endswith('.pdf') or 'sci.bban' in candidate or 'storage' in candidate:
                    pdf_url = candidate
            
            # Pattern B: Find URLs ending in .pdf anywhere in HTML (more general)
            if not pdf_url:
                m = re.search(r'(?:https?://[^"\'\s>]+/[^"\'\s>]*\.pdf(?:\?[^"\'\s>]*)?)', html)
                if m:
                    candidate = m.group(0)
                    # Must look like a real PDF URL
                    if '/pdf/' in candidate or 'sci.' in candidate or 'storage' in candidate or 'bban' in candidate:
                        pdf_url = candidate
            
            # Pattern C: /storage/ pattern (Sci-Hub internal)
            if not pdf_url:
                m = re.search(r'href=["\'](/storage/[^"\']+)["\']', html)
                if m:
                    pdf_url = domain + m.group(1)
            
            # Pattern D: JavaScript location.href with .pdf
            if not pdf_url:
                m = re.search(r'location\.href=[\'\"]([^"\'\"]*\.pdf[^"\'\"]*)', html)
                if m:
                    pdf_url = m.group(1)
                pdf_url = domain + pdf_url
            elif not pdf_url.startswith('http'):
                pdf_url = domain + '/' + pdf_url
            
            # Step 3: Download PDF via Tor
            pdf_cmd = [
                "curl", "-s", "-o", "-",
                "--socks5-hostname", "127.0.0.1:9050",
                "--max-time", "60",
                "-L",
                "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "-e", url,
                pdf_url,
            ]
            pdf_result = _sub.run(pdf_cmd, capture_output=True, text=False, timeout=65)
            
            if pdf_result.returncode == 0 and pdf_result.stdout:
                content = pdf_result.stdout
                if verify_pdf(content):
                    try:
                        os.remove("/tmp/synthos_scihub_tmp.html")
                    except:
                        pass
                    return content
                    
        except Exception:
            continue
        finally:
            try:
                if os.path.exists("/tmp/synthos_scihub_tmp.html"):
                    os.remove("/tmp/synthos_scihub_tmp.html")
            except:
                pass
    
    return None

# ─── Tier 3: LibGen ─────────────────────────────────────────────────────────

def download_libgen(doi: str = None, title: str = None) -> Optional[bytes]:
    """
    Download from LibGen mirrors.
    Searches by title (DOI not directly supported by LibGen API).
    """
    if not title:
        return None

    libgen_hosts = [
        "https://libgen.is",
        "https://libgen.rs",
        "https://b-ok.cc",
        "https://libgen.li",
        "https://gen.lib.rus.ec",
    ]

    for host in libgen_hosts:
        try:
            query = urllib.parse.quote(title[:100])
            url = f"{host}/sql.php?req={query}&column=title&view=simple&res=25&phrase=1"
            content = download_http(url, timeout=20)
            if content:
                # Look for PDF links in results
                pdf_links = re.findall(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', content.decode('utf-8', errors='replace'))
                for link in pdf_links[:3]:
                    if link.startswith('//'):
                        link = 'https:' + link
                    pdf_content = download_http(link, timeout=30)
                    if verify_pdf(pdf_content):
                        return pdf_content
        except Exception:
            continue

    return None


# ─── Tier 4: MedData ─────────────────────────────────────────────────────────

def _get_meddata_token() -> Optional[str]:
    """Get a valid MedData token via 2-step SSO flow.
    Priority: MEDDATA_TOKEN env → MEDDATA_USERNAME+MEDDATA_PASSWORD.
    """
    # Direct token first
    token = os.environ.get("MEDDATA_TOKEN", "")
    if token:
        return token

    username = os.environ.get("MEDDATA_USERNAME", "")
    password = os.environ.get("MEDDATA_PASSWORD", "")
    if not username or not password:
        return None

    try:
        import requests as req
        # Step 1: SSO login → bucToken
        sso_url = "https://uuct.medbooks.com.cn:9443/sso/login"
        r = req.post(sso_url, json={
            "username": username, "password": password, "type": "0"
        }, timeout=15, verify=False)
        if r.status_code != 200:
            return None
        data = r.json()
        if data.get("code") != "200":
            return None
        buc_token = None
        url_field = data.get("data", {}).get("url", "")
        if url_field and "bucToken=" in url_field:
            buc_token = url_field.split("bucToken=")[1].split("&")[0] if "bucToken=" in url_field else None
        if not buc_token:
            return None

        # Step 2: Exchange bucToken → meddata token
        app_url = "http://app.meddata.com.cn:8878"
        r2 = req.get(f"{app_url}/api/sso/user/login", params={"bucToken": buc_token}, timeout=10)
        if r2.status_code != 200:
            return None
        token = r2.json().get("responseData", "")
        return token if token else None
    except Exception:
        return None


def download_meddata(doi: str = None, filename: str = None, pmid: str = None) -> Optional[bytes]:
    """Download from MedData (foreign literature full-text database, Chinese institutional access).
    Correct workflow: SSO login -> token -> full_look -> viewtext (app.meddata.com.cn:8878).
    Covers foreign journal papers (Elsevier/Springer/BMJ/Frontiers etc.) via Chinese institutional subscription.
    ->
    abstractId: use PMID (unique, clean) when available, fallback to DOI_no_slash.
    pmid parameter: any number is accepted by the API.
    doi parameter: the actual DOI of the target paper.
    """
    token = _get_meddata_token()
    if not token:
        return None

    if not doi:
        return None

    doi_no_slash = doi.replace("/", "")

    # Determine abstractId: PMID is preferred (unique, clean numeric ID)
    abstract_id = None
    if pmid:
        abstract_id = pmid
    else:
        abstract_id = doi_no_slash

    # Always pass the DOI as the third parameter
    target_doi = doi

    try:
        import requests as req
        base_url = "http://www.meddata.com.cn"
        app_url = "http://app.meddata.com.cn:8878"

        # full_look -> get fileName for viewtext
        fl_url = f"{base_url}/api/abstract/full_look?token={token}&abstractId={abstract_id}&pmid={pmid or '1'}&doi={target_doi}"
        r = req.get(fl_url, timeout=15)
        if r.status_code != 200:
            return None
        fl_data = r.json()
        rd = fl_data.get("responseData", {})
        fname = rd.get("fileName", "")
        status = rd.get("status")
        file_url = rd.get("fileUrl")

        # Download from fileUrl if available (status=0: has full text with fileUrl)
        if file_url:
            try:
                r3 = req.get(file_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
                if r3.status_code == 200 and r3.content[:4] == PDF_MAGIC:
                    if hashlib.md5(r3.content).hexdigest() not in KNOWN_PSEUDOPDF_MD5:
                        return r3.content
            except Exception:
                pass

        # viewtext: download actual PDF via fileName
        # status=2 (indexed without fileUrl) STILL returns real PDF via viewtext
        # Only status=3 (not found) or no fileName means truly unavailable
        if fname and status != 3:
            time.sleep(1)
            vt_url = f"{app_url}/api/abstract/viewtext?fileName={fname}&token={token}"
            r2 = req.get(vt_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            if r2.status_code == 200 and r2.content[:4] == PDF_MAGIC:
                if hashlib.md5(r2.content).hexdigest() not in KNOWN_PSEUDOPDF_MD5:
                    return r2.content

    except Exception:
        pass

    return None




# ─── DOI Normalization ───────────────────────────────────────────────────────

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


def race_downloads(doi: str = None, title: str = None, arxiv_id: str = None,
                   pmid: str = None, pmcs_id: str = None, external_ids: Dict = None,
                   timeout: int = 60) -> Dict[str, Any]:
    """
    Race multiple download sources concurrently.
    Returns dict with download results.
    """
    results = []
    start_time = time.time()

    source_fns = []

    # ═══ Tier 0: Semantic Scholar (instant OA URL) ═══
    if doi:
        ext_ids = {}
        if external_ids and isinstance(external_ids, dict):
            ext_ids = external_ids
        source_fns.append(("s2_pdf", lambda: download_s2_pdf(doi=doi, external_ids=ext_ids), "Semantic Scholar OA"))

    # ═══ Tier 1: OA Direct (instant) ═══
    if arxiv_id:
        source_fns.append(("arxiv_direct", lambda: download_arxiv_pdf(arxiv_id), "arXiv Direct"))
    if doi:
        if doi.startswith("10.1101/"):
            source_fns.append(("biorxiv", lambda: download_biorxiv_pdf(doi), "BioRxiv/MedRxiv"))
        if doi.startswith("10.3389/"):
            source_fns.append(("frontiers", lambda: download_frontiers_pdf(doi), "Frontiers OA"))
        if doi.startswith("10.1371/"):
            source_fns.append(("plos", lambda: download_plos_pdf(doi), "PLOS OA"))

        source_fns.append(("crossref", lambda: download_crossref_link(doi), "Crossref OA"))
        source_fns.append(("unpaywall", lambda: download_unpaywall(doi), "Unpaywall"))
        source_fns.append(("doi2pdf", lambda: download_doi2pdf(doi), "DOI2PDF"))
        source_fns.append(("core", lambda: download_core(doi), "CORE OA"))
        source_fns.append(("openurl", lambda: download_via_openurl(doi=doi, title=title), "OpenURL/SFX"))

        # Publisher-specific OA
        if doi.startswith("10.1016/"):
            source_fns.append(("sciencedirect", lambda: download_sciencedirect(doi), "ScienceDirect OA"))
        if doi.startswith("10.1007/") or doi.startswith("10.1186/") or doi.startswith("10.1515/"):
            source_fns.append(("springer", lambda: download_springer(doi=doi, title=title), "SpringerLink OA"))
        if doi.startswith("10.1002/") or doi.startswith("10.1111/"):
            source_fns.append(("wiley", lambda: download_wiley(doi), "Wiley OA"))
        if doi.startswith("10.1109/"):
            source_fns.append(("ieee", lambda: download_ieee(doi), "IEEE Xplore OA"))
        if doi.startswith("10.1145/"):
            source_fns.append(("acm", lambda: download_acm(doi), "ACM DL OA"))

    # ═══ Tier 2: Sci-Hub (grey literature) ═══
    if doi:
        source_fns.append(("scihub_direct", lambda: download_scihub_direct(doi), "Sci-Hub Direct"))
        source_fns.append(("scihub_tor", lambda: download_scihub_via_tor(doi), "Sci-Hub via Tor"))

    # ═══ Tier 3: LibGen (book/mass-download) ═══
    if title:
        source_fns.append(("libgen", lambda: download_libgen(doi=doi, title=title), "LibGen"))

    # ═══ Tier 4: MedData (Foreign literature DB, Chinese institutional access) ═══
    if doi:
        source_fns.append(("meddata", lambda: download_meddata(doi=doi, pmid=pmid), "MedData"))

    # ═══ Tier 5: PubMed Central (by PMID) ═══
    if pmid:
        pmcs = search_pmc_for_pubmed(pmid)
        if pmcs:
            source_fns.append(("pubmed_central", lambda: download_pubmed_central(pmcs), "PMC Full Text"))

    if not source_fns:
        return {"error": "No viable download sources for given input", "papers": []}

    # Run concurrent downloads
    with ThreadPoolExecutor(max_workers=min(4, len(source_fns))) as pool:
        futures = {}
        for label, fn, name in source_fns:
            futures[pool.submit(fn)] = {"label": label, "name": name, "start": time.time()}

        try:
            for future in as_completed(futures, timeout=min(timeout, 30)):
                elapsed = time.time() - (futures[future]["start"])
                try:
                    content = future.result(timeout=15)
                except Exception as e:
                    results.append({
                        "source": futures[future]["name"],
                        "label": futures[future]["label"],
                        "status": "failed",
                        "error": str(e),
                        "elapsed": round(elapsed, 2),
                    })
                    continue

                if content and verify_pdf(content):
                    results.append({
                        "source": futures[future]["name"],
                        "label": futures[future]["label"],
                        "status": "success",
                        "size": len(content),
                        "md5": hashlib.md5(content).hexdigest(),
                        "elapsed": round(elapsed, 2),
                    })
                    return {"papers": results, "status": "success", "elapsed": round(time.time() - start_time, 2),
                            "total_raw": time.time() - start_time, "content": content,
                            "winning_source": futures[future]["name"],
                            "winning_label": futures[future]["label"],
                            "size": len(content), "md5": hashlib.md5(content).hexdigest()}
                else:
                    results.append({
                        "source": futures[future]["name"],
                        "label": futures[future]["label"],
                        "status": "failed",
                        "error": "Invalid PDF content",
                        "elapsed": round(elapsed, 2),
                    })
        except TimeoutError:
            for fut in futures:
                try:
                    fut.cancel()
                except Exception:
                    pass
        except Exception as outer_e:
            results.append({
                "source": "engine",
                "label": "race_downloads",
                "status": "failed",
                "error": str(outer_e),
                "elapsed": round(time.time() - start_time, 2),
            })

    elapsed = time.time() - start_time
    return {"papers": results, "status": "failed", "elapsed": round(elapsed, 2)}


# ─── Multi-Paper Batch Download ──────────────────────────────────────────────

def batch_download(candidates: List[Dict], output_dir: str = None) -> Dict[str, Any]:
    """
    Batch download from a list of paper candidates (from multi_source_search).
    Saves each PDF with bibkey filename format: {FirstAuthorYearTitle}.pdf
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    results = []
    for p in candidates:
        if not p.get("title"):
            continue

        doi = None
        if p.get("external_ids"):
            if isinstance(p["external_ids"], dict):
                for key in ["DOI", "doi"]:
                    if p["external_ids"].get(key) and p["external_ids"][key] != "N/A":
                        doi = p["external_ids"][key]
                        break

        arxiv_id = None
        if p.get("external_ids"):
            arxiv_id = p["external_ids"].get("arXiv", p["external_ids"].get("arxiv"))

        pmid = None
        if p.get("external_ids"):
            pmid = p["external_ids"].get("PMID")

        if not doi and not arxiv_id and not pmid:
            results.append({"title": p["title"], "status": "skipped", "reason": "no identifier"})
            continue

        bibkey = generate_bibkey(
            title=p.get("title", ""),
            authors=p.get("authors"),
            year=p.get("year"),
        )
        output_path = os.path.join(output_dir, f"{bibkey}.pdf")

        result = race_downloads(
            doi=doi, title=p.get("title"), arxiv_id=arxiv_id,
            pmid=pmid, pmcs_id=p.get("external_ids", {}).get("PMC"),
            external_ids=p.get("external_ids")
        )

        if result.get("status") == "success" and result.get("content"):
            pdf_content = result["content"]
            winning_source = result["winning_source"]
            winning_label = result["winning_label"]
            size = result["size"]
            elapsed = result["elapsed"]

            if pdf_content and verify_pdf(pdf_content):
                path = save_pdf(pdf_content, output_path)
                results.append({
                    "title": p["title"],
                    "bibkey": bibkey,
                    "status": "downloaded",
                    "source": f"{winning_source} ({winning_label})",
                    "path": path,
                    "size": size,
                    "elapsed": round(elapsed, 2),
                })
            else:
                results.append({
                    "title": p["title"],
                    "bibkey": bibkey,
                    "status": "failed",
                    "reason": "invalid PDF content",
                    "path": output_path,
                })
        else:
            results.append({
                "title": p["title"],
                "bibkey": bibkey,
                "status": "failed",
                "sources": [r.get("source", "") for r in result.get("papers", [])],
                "path": output_path,
            })

    return {"papers": results, "total": len(candidates),
            "downloaded": sum(1 for r in results if r["status"] == "downloaded"),
            "failed": sum(1 for r in results if r["status"] == "failed")}



def run_test() -> Dict[str, Any]:
    """Full connectivity test for all download paths."""
    test_results = {}

    print("=" * 60)
    print("PDF Download Engine — Connectivity Test")
    print("=" * 60)

    # 1. Semantic Scholar
    print("\n[1/8] Semantic Scholar API...")
    try:
        req = urllib.request.Request(
            "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1",
            headers={"x-api-key": os.environ.get("SEMANTIC_SCHOLAR_API_KEY", ""),
                     "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        ok = "data" in data
        test_results["semantic_scholar"] = "ok" if ok else "error"
        print(f"  {'✅' if ok else '❌'} {test_results['semantic_scholar']}")
    except Exception as e:
        test_results["semantic_scholar"] = f"error: {e}"
        print(f"  ❌ {e}")

    # 2. PubMed
    print("\n[2/8] PubMed eSearch...")
    try:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=test&retmode=json"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        ok = "esearchresult" in data
        test_results["pubmed"] = "ok" if ok else "error"
        print(f"  {'✅' if ok else '❌'} {test_results['pubmed']}")
    except Exception as e:
        test_results["pubmed"] = f"error: {e}"
        print(f"  ❌ {e}")

    # 3. OpenAlex
    print("\n[3/8] OpenAlex API...")
    try:
        url = "https://api.openalex.org/works?search=test&per_page=1"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        ok = "results" in data and len(data["results"]) > 0
        test_results["openalex"] = "ok" if ok else "error"
        print(f"  {'✅' if ok else '❌'} {test_results['openalex']}")
    except Exception as e:
        test_results["openalex"] = f"error: {e}"
        print(f"  ❌ {e}")

    # 4. arXiv Direct
    print("\n[4/8] arXiv Direct...")
    content = download_arxiv_pdf("2502.02508")
    ok = content and verify_pdf(content)
    test_results["arxiv_direct"] = "ok" if ok else "failed"
    print(f"  {'✅' if ok else '❌'} {test_results['arxiv_direct']}" +
          (f" ({len(content)} bytes)" if ok else ""))

    # 5. arXiv Tor
    print("\n[5/8] arXiv via Tor...")
    tor_ok = False
    try:
        proxy = urllib.request.ProxyHandler({"https": TOR_PROXY_URL})
        opener = urllib.request.build_opener(proxy)
        req = urllib.request.Request(
            "https://export.arxiv.org/api/query?search_query=all:test&max_results=1",
            headers={"User-Agent": "Test"}
        )
        with opener.open(req, timeout=15) as resp:
            data = resp.read()
        tor_ok = b'<feed' in data
    except Exception:
        pass
    test_results["arxiv_tor"] = "ok" if tor_ok else "failed"
    print(f"  {'✅' if tor_ok else '❌'} {test_results['arxiv_tor']}")

    # 6. Tor SOCKS5
    print("\n[6/8] Tor SOCKS5 Proxy...")
    tor_socks_ok = False
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(("127.0.0.1", 9050))
        s.close()
        tor_socks_ok = True
    except Exception:
        pass
    test_results["tor_socks5"] = "ok" if tor_socks_ok else "failed"
    print(f"  {'✅' if tor_socks_ok else '❌'} {test_results['tor_socks5']}")

    # 7. Sci-Hub Direct
    print("\n[7/8] Sci-Hub Direct (curl_cffi)...")
    sh = download_scihub_direct("10.1136/bmj.m2689")  # Known working DOI from test
    ok = sh and verify_pdf(sh)
    test_results["scihub_direct"] = "ok" if ok else "failed"
    print(f"  {'✅' if ok else '❌'} {test_results['scihub_direct']}")

    # 8. Crossref OA
    print("\n[8/8] Crossref OA...")
    cr = download_crossref_link("10.1136/bmj.m2689")
    ok = cr and verify_pdf(cr)
    test_results["crossref_oa"] = "ok" if ok else "failed"
    print(f"  {'✅' if ok else '❌'} {test_results['crossref_oa']}")

    print(f"\n{'=' * 60}")
    ok_count = sum(1 for v in test_results.values() if v == "ok")
    print(f"Results: {ok_count}/{len(test_results)} passed")
    print(f"{'=' * 60}")

    return test_results


# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="PDF Download Engine — Multi-Source Racing Download",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download single paper by DOI
  %(prog)s 10.1016/j.neuron.2020.01.015

  # Download by arXiv ID
  %(prog)s 2502.02508 --type arxiv_id

  # Download by PMID
  %(prog)s 42296359 --type pmid

  # Batch download from JSON candidates
  %(prog)s --batch results.json

  # Run connectivity test
  %(prog)s --test

        """,
    )

    parser.add_argument("identifier", nargs="?", default=None,
                        help="DOI, arXiv ID, PMID, or paper title")
    parser.add_argument("--output", "-o", default=None,
                        help="Output PDF file path")
    parser.add_argument("--type", "-t", default="doi",
                        choices=["doi", "arxiv_id", "pmid", "search"],
                        help="Identifier type (default: doi)")
    parser.add_argument("--output-dir", "-d", default=None,
                        help="Output directory (default: ./outputs/papers/pdfs)")
    parser.add_argument("--max", "-m", type=int, default=5,
                        help="Max results per source (default: 5)")
    parser.add_argument("--batch", "-b", default=None,
                        help="Batch mode: read paper candidates from JSON file")
    parser.add_argument("--timeout", "-T", type=int, default=60,
                        help="Total timeout in seconds (default: 60)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    parser.add_argument("--test", action="store_true",
                        help="Run connectivity test")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.test:
        result = run_test()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if args.batch:
        with open(args.batch) as f:
            data = json.load(f)
        # Support: list of paper dicts, or {papers: [...], total_found: N}
        if isinstance(data, list):
            papers = data
        elif isinstance(data, dict):
            papers = data.get("papers", [])
        else:
            print("Error: invalid batch file format")
            sys.exit(1)
        output_dir = args.output_dir or DEFAULT_OUTPUT_DIR
        result = batch_download(papers, output_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if not args.identifier:
        print("Error: identifier required (or --batch / --test)")
        sys.exit(1)

    # Parse input
    identifier = args.identifier.strip()
    doi = None
    arxiv_id = None
    pmid = None
    pmcs_id = None
    title = None

    if args.type == "arxiv_id":
        arxiv_id = identifier
    elif args.type == "pmid":
        pmid = identifier
    elif args.type == "doi":
        doi = normalize_doi(identifier)
    else:
        # Search mode: extract any identifier
        doi = normalize_doi(identifier) if identifier.startswith("10.") else extract_doi_from_text(identifier)
        arxiv_id = extract_arxiv_id(identifier)
        pmid = extract_pmid(identifier)
        pmcs_id = extract_pmcs_id(identifier)

    output_dir = args.output_dir or DEFAULT_OUTPUT_DIR
    # Derive output filename from identifier
    if args.output:
        output_path = args.output
    elif doi:
        # DOI-based: remove '10.' prefix and slashes for clean name
        clean = doi.strip().replace('10.', '').replace('/', '_')
        output_path = os.path.join(output_dir, f"{clean}.pdf")
    elif arxiv_id:
        output_path = os.path.join(output_dir, f"{arxiv_id}.pdf")
    elif pmid:
        output_path = os.path.join(output_dir, f"pmid_{pmid}.pdf")
    else:
        output_path = os.path.join(output_dir, f"downloaded_{time.strftime('%Y%m%d_%H%M%S')}.pdf")

    print(f"\n{'=' * 60}")
    print("PDF Download Engine — Synthos")
    print(f"{'=' * 60}")
    print(f"DOI:        {doi or 'N/A'}")
    print(f"arXiv ID:   {arxiv_id or 'N/A'}")
    print(f"PMID:       {pmid or 'N/A'}")
    print(f"Output:     {output_path}")
    print(f"Timeout:    {args.timeout}s")
    print(f"{'=' * 60}")

    # Run racing download
    result = race_downloads(
        doi=doi, title=title, arxiv_id=arxiv_id,
        pmid=pmid, pmcs_id=pmcs_id,
        timeout=args.timeout
    )

    if result.get("status") == "success":
        # Use PDF bytes directly from race result (no re-download needed)
        pdf_content = result.get("content")
        winning_source = result.get("winning_source", "unknown")
        winning_label = result.get("winning_label", "unknown")
        size = result.get("size", 0)
        md5 = result.get("md5", "")
        elapsed = result.get("elapsed", 0)

        print(f"\n✅ Downloaded via {winning_source} ({winning_label})")
        print(f"   Size: {size} bytes")
        print(f"   MD5:  {md5}")

        if pdf_content and verify_pdf(pdf_content):
            path = save_pdf(pdf_content, output_path)
            print(f"   Saved: {path}")
        else:
            print(f"   ⚠️ Content not available — saving metadata only")

        print(f"\n{'=' * 60}")
        sys.exit(0)
    else:
        print(f"\n❌ All sources failed ({result.get('elapsed', 0):.1f}s)")
        for r in result.get("papers", []):
            if r.get("status") == "failed":
                print(f"   {r.get('source', '')}: {r.get('error', 'unknown')}")
        print(f"{'=' * 60}")
        sys.exit(1)


if __name__ == "__main__":
    main()
