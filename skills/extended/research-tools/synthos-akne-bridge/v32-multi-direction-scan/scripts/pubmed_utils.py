#!/usr/bin/env python3
"""
PubMed and OpenAlex utility functions with resilience against NCBI API instability.
Used by v32-multi-direction-scan and paper-pipeline cron jobs.

Usage:
    # PubMed queries
    from pubmed_utils import pubmed_count, pubmed_titles, pubmed_titles_safe
    count, titles = pubmed_count("intraocular pressure AND ODE AND glaucoma")
    count, titles = pubmed_titles("accommodation reflex AND ODE", retmax=5)

    # Single-title lookup
    from pubmed_utils import fetch_title_via_esummary
    title = fetch_title_via_esummary("33105416")

    # OpenAlex queries (already available in this module)
    from pubmed_utils import openalex_search
    count, titles = openalex_search("periodic alternating nystagmus PINN")
    # Returns: (count_int, [title_str, ...])
    
    # For title-only checks, use esummary (more reliable than eFetch):
    from pubmed_utils import fetch_title_via_esummary
    title = fetch_title_via_esummary("33105416")
"""
import urllib.request
import urllib.error
import urllib.parse
import json
import time
import ssl

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

USER_AGENT = "Synthos/1.0 (academic research; synthos@research)"
MAX_RETRIES = 5
RETRY_DELAY = 3  # seconds


def _parse_json_raw(raw_bytes):
    """Parse JSON with resilience against NCBI's extra preamble/BOM."""
    raw = raw_bytes.decode('utf-8').lstrip('\ufeff')
    # Strip anything before first {
    brace = raw.find('{')
    if brace > 0:
        raw = raw[brace:]
    # Handle multiple JSON objects — parse only up to the last }
    end = raw.rfind('}')
    if end > 0:
        raw = raw[:end+1]
    return json.loads(raw)


def pubmed_count(query, retmax=50, retries=MAX_RETRIES):
    """
    Get PubMed search count for a query.
    
    Returns: (count, [titles])
    Titles are from top retmax results.
    """
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = urllib.parse.urlencode({
        'db': 'pubmed',
        'term': query,
        'retmax': str(retmax),
        'retmode': 'json'
    })
    
    err = None
    for attempt in range(retries):
        try:
            url = f"{base}?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
                data = _parse_json_raw(r.read())
                count = int(data.get("esearchresult", {}).get("count", 0))
                ids = data.get("esearchresult", {}).get("idlist", [])
                
                # Try to get titles via esummary (more reliable than eFetch)
                titles = []
                if ids:
                    titles = _fetch_titles_via_esummary(ids[:5])
                
                return count, titles
                
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504, 429):
                time.sleep(RETRY_DELAY)
                err = f"HTTP {e.code}"
                continue
            err = str(e)
            break
        except Exception as e:
            time.sleep(RETRY_DELAY)
            err = str(e)
    
    return -1, [f"FAILED after {retries} retries: {err}"]


def _fetch_titles_via_esummary(pm_ids, retries=MAX_RETRIES):
    """Fetch titles via esummary endpoint (more reliable than eFetch)."""
    ids_str = ','.join(pm_ids)
    params = urllib.parse.urlencode({
        'db': 'pubmed',
        'id': ids_str,
        'version': '2.0',
        'retmode': 'json'
    })
    
    err = None
    for attempt in range(retries):
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
                fd = _parse_json_raw(r.read())
                
                titles = []
                result = fd.get("result", {})
                for pmid in pm_ids:
                    item = result.get(str(pmid), {})
                    title = item.get("title", item.get("Title", ""))
                    if title:
                        titles.append(title)
                return titles if titles else ["NO_TITLES"]
                
        except Exception as e:
            err = str(e)
            time.sleep(RETRY_DELAY)
    
    return [f"ESUMMARY_FAILED: {err}"]


def fetch_title_via_esummary(pm_id):
    """Get a single PubMed title via esummary."""
    params = urllib.parse.urlencode({
        'db': 'pubmed',
        'id': pm_id,
        'version': '2.0',
        'retmode': 'json'
    })
    err = None
    for attempt in range(MAX_RETRIES):
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
                fd = _parse_json_raw(r.read())
                result = fd.get("result", {})
                item = result.get(str(pm_id), {})
                return item.get("title", "NO_TITLE")
        except Exception as e:
            err = str(e)
            time.sleep(RETRY_DELAY)
    return f"ERROR: {err}"


def openalex_search(query, retmax=5):
    """
    Search OpenAlex works.
    
    Returns: (count, [titles])
    """
    encoded = urllib.parse.quote(query)
    url = f"https://api.openalex.org/works?search={encoded}&per_page={retmax}&select=id,title,abstract_inverted_index"
    
    err = None
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
                results = data.get("results", [])
                titles = [r.get("title", "") for r in results[:retmax]]
                return len(results), titles
        except Exception as e:
            err = str(e)
            time.sleep(RETRY_DELAY)
    
    return -1, [f"FAILED: {err}"]
