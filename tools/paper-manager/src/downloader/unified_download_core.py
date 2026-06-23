"""
unified_download_core.py — Unified download entry point.

Accepts any paper ID (DOI, arXiv, CorpusID, PMID, PMC),
resolves cross-source metadata, and downloads via tiered racing.

Usage:
    from src.downloader.unified_download_core import download_paper
    result = download_paper("CorpusID:12345678", "/tmp/paper.pdf")
"""

import os, re, logging, tempfile
from typing import Optional

from src.utils.paper_id import normalize_paper_id
from src.sources.meddata import try_meddata
from src.sources.scihub_racing import try_scihub_curl
from src.sources.libgen import try_libgen

logger = logging.getLogger(__name__)

# ── ID resolution ──────────────────────────────────────────────────────

def _resolve_metadata(paper_id: str) -> dict:
    """Resolve any paper ID to canonical metadata (doi, pmid, arxiv_id, title).
    
    Uses Semantic Scholar API when needed (CorpusID → DOI/PMID).
    Returns dict with at minimum the original ID plus any discovered fields.
    """
    norm = normalize_paper_id(paper_id)
    meta = {"norm_id": norm, "doi": None, "pmid": None, "arxiv_id": None,
            "open_access_url": None}
    
    # Parse from normalized ID
    m = re.match(r"DOI:(.+)", norm, re.IGNORECASE)
    if m: meta["doi"] = m.group(1)
    m = re.match(r"ARXIV:(.+)", norm, re.IGNORECASE)
    if m: meta["arxiv_id"] = m.group(1)
    m = re.match(r"PMID:(.+)", norm, re.IGNORECASE)
    if m: meta["pmid"] = m.group(1)
    m = re.match(r"CorpusID:(\d+)", norm, re.IGNORECASE)
    corpus_id = m.group(1) if m else None
    
    # If already have all we need, return early
    if meta["doi"] and meta["pmid"]:
        return meta
    if meta["doi"] and corpus_id is None:
        # Try to resolve DOI → PMID via Semantic Scholar before returning early
        try:
            import requests
            r = requests.get(
                f"https://api.semanticscholar.org/graph/v1/paper/DOI:{meta['doi']}?fields=externalIds,openAccessPdf",
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                ext = data.get("externalIds", {}) or {}
                meta["pmid"] = meta["pmid"] or ext.get("PubMed")
                meta["arxiv_id"] = meta["arxiv_id"] or ext.get("ArXiv")
                oa = data.get("openAccessPdf") or {}
                meta["open_access_url"] = oa.get("url")
        except Exception:
            pass
        return meta
    
    # Try Semantic Scholar API for cross-resolution
    try:
        import requests
        from src.api.multi_database_search import MultiDatabaseSearchClient
        from src.core.config import Config
        
        # For CorpusID: fetch paper details via SS
        if corpus_id and (not meta["doi"] or not meta["pmid"]):
            url = f"https://api.semanticscholar.org/graph/v1/paper/CorpusID:{corpus_id}?fields=title,externalIds,doi"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                ext = data.get("externalIds", {}) or {}
                meta["doi"] = meta["doi"] or data.get("doi") or ext.get("DOI")
                meta["pmid"] = meta["pmid"] or ext.get("PubMed")
                meta["arxiv_id"] = meta["arxiv_id"] or ext.get("ArXiv")
        
        # For DOI without PMID: try Crossref
        if meta["doi"] and not meta["pmid"]:
            r = requests.get(f"https://api.crossref.org/works/{meta['doi']}", timeout=10)
            if r.status_code == 200:
                data = r.json().get("message", {})
                meta["title"] = data.get("title", [None])[0]
        
        # For PMID without DOI: try NCBI
        if meta["pmid"] and not meta["doi"]:
            import urllib.parse
            url = (f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                   f"?db=pubmed&id={meta['pmid']}&retmode=json")
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json().get("result", {})
                pm_data = data.get(meta["pmid"], {})
                ids = pm_data.get("articleids", [])
                for iid in ids:
                    if iid.get("idtype") == "doi":
                        meta["doi"] = iid.get("value")
    
    except Exception as e:
        logger.debug(f"Metadata resolution error: {e}")
    
    return meta


def _download_arxiv(arxiv_id: str, output_path: str) -> bool:
    """Download from arXiv.org directly."""
    import requests
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200 and r.content[:4] == b'%PDF':
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(r.content)
            logger.info(f"✅ arXiv direct: {len(r.content)} bytes")
            return True
    except Exception as e:
        logger.debug(f"arXiv download error: {e}")
    return False


def _download_open_access(url: str, output_path: str) -> bool:
    """Download from Semantic Scholar openAccessPdf URL."""
    import requests
    try:
        r = requests.get(url, timeout=30, allow_redirects=True)
        if r.status_code == 200 and r.content[:4] == b'%PDF' and len(r.content) > 1000:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(r.content)
            logger.info(f"✅ OA direct: {len(r.content)} bytes")
            return True
    except Exception as e:
        logger.debug(f"OA download error: {e}")
    return False


def _download_via_racing(doi: str, pmid: Optional[str], output_path: str) -> bool:
    """Tiered racing download: SciHub → LibGen → MedData.
    
    MedData gets PMID if available for complex DOI prefixes (Bentham, etc.).
    """
    tiers = [
        # Tier 1: SciHub (curl_cffi TLS bypass)
        [("SciHub", lambda: try_scihub_curl(doi, output_path))],
        # Tier 2: LibGen
        [("LibGen", lambda: try_libgen(doi, output_path))],
        # Tier 3: MedData (with PMID if available)
        [("MedData", lambda: try_meddata(doi, output_path,
                                         extra={"pmid": pmid} if pmid else {}))],
    ]
    
    for tier in tiers:
        for label, fn in tier:
            logger.info(f"  Tier [{label}] trying...")
            try:
                result = fn()
                if result and result.get('success'):
                    return True
            except Exception as e:
                logger.debug(f"  {label} error: {e}")
    
    return False


# ── Public API ─────────────────────────────────────────────────────────

def download_paper(identifier: str, output_path: str) -> bool:
    """Download a paper's full-text PDF by any ID.
    
    Args:
        identifier: arXiv ID, DOI, CorpusID, PMID, PMC, or any recognized format
        output_path: Where to save the PDF
    
    Returns:
        True if successful, False otherwise.
    """
    # Step 1: Normalize and resolve
    meta = _resolve_metadata(identifier)
    logger.info(f"Resolved: {meta['norm_id']} → doi={meta['doi']}, "
                f"pmid={meta['pmid']}, arxiv={meta['arxiv_id']}")
    
    # Step 2: Try direct download (arXiv, PMC) — fastest path
    if meta["arxiv_id"]:
        if _download_arxiv(meta["arxiv_id"], output_path):
            return True

    # Step 3: Try Semantic Scholar openAccessPdf (free OA papers)
    if meta["open_access_url"]:
        if _download_open_access(meta["open_access_url"], output_path):
            return True

    # Step 4: Tiered racing (SciHub → LibGen → MedData)
    if meta["doi"]:
        if _download_via_racing(meta["doi"], meta["pmid"], output_path):
            return True
    
    # Step 4: Last resort — try MedData with whatever ID we have
    if not meta["doi"] and meta["pmid"]:
        # PMID alone as abstract_id
        result = try_meddata(meta["pmid"], output_path)
        if result and result.get('success'):
            return True
    
    logger.warning(f"All download paths failed for: {identifier}")
    return False
