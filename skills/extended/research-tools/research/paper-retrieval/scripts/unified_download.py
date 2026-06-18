#!/usr/bin/env python3
"""
Unified Paper Download Orchestrator - Paper download racing engine v2.0
Strategy: OA direct -> Sci-Hub direct -> Sci-Hub via Tor -> MedData
P0 evidence, P1 atomicity, P2 structure.
"""
import logging
import os
import sys
import time
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

PLACEHOLDER_MD5 = "fd469bd7cd29446f2800f099e3b71457"
SCI_HUB_DOMAINS = [
    "https://sci-hub.ru", "https://sci-hub.ee", "https://sci-hub.shop",
    "https://ci-hub.ren", "https://sci-hub.red", "https://sci-hub.al",
    "https://sci-hub.wf", "https://sci-hub.box",
]

def md5sum(filepath):
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def download_arxiv(doi_or_id, output):
    arxiv_id = doi_or_id
    if doi_or_id.startswith("10.48550/"):
        arxiv_id = doi_or_id.split("/")[-1].split("arxiv.")[1].split(",")[0]
    elif doi_or_id.startswith("10.3842/"):
        arxiv_id = doi_or_id.split("/")[-1].split("abs/")[1].split("/")[0]
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "SynthosAgent/2.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
        if content[:4] == b"%PDF" and len(content) > 1000:
            Path(output).parent.mkdir(parents=True, exist_ok=True)
            with open(output, "wb") as f:
                f.write(content)
            return {"success": True, "source": "arxiv", "size": len(content), "url": url}
    except Exception as e:
        logger.debug(f"arXiv failed: {e}")
    return None

def download_crossref_oa(doi, output):
    try:
        import urllib.request, json
        url = f"https://api.unpaywall.org/v2/{doi}?email=agent@synthos-research.local"
        req = urllib.request.Request(url, headers={"User-Agent": "SynthosAgent/2.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        best_oa = data.get("best_oa_location", {})
        if best_oa and best_oa.get("url_for_pdf"):
            pdf_url = best_oa["url_for_pdf"]
            try:
                import urllib.request
                req2 = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req2, timeout=30) as resp2:
                    content = resp2.read()
                if content[:4] == b"%PDF" and len(content) > 1000:
                    Path(output).parent.mkdir(parents=True, exist_ok=True)
                    with open(output, "wb") as f:
                        f.write(content)
                    return {"success": True, "source": "unpaywall", "size": len(content)}
            except Exception:
                pass
    except Exception as e:
        logger.debug(f"Unpaywall failed: {e}")
    return None

def download_scihub_direct(doi, output, timeout=30):
    try:
        from curl_cffi import requests as cffi_req
    except ImportError:
        logger.warning("curl_cffi not installed, skipping Sci-Hub")
        return None
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    from bs4 import BeautifulSoup
    for domain in SCI_HUB_DOMAINS:
        try:
            url = f"{domain}/{doi}"
            resp = cffi_req.get(url, headers=headers, impersonate="chrome120", timeout=timeout, allow_redirects=True)
            if resp.status_code != 200:
                continue
            if resp.content[:4] == b"%PDF" and len(resp.content) > 1000:
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                with open(output, "wb") as f:
                    f.write(resp.content)
                return {"success": True, "source": f"scihub-{domain}", "size": len(resp.content)}
            soup = BeautifulSoup(resp.text, "html.parser")
            pdf_url = None
            iframe = soup.find("iframe", id="pdf")
            if iframe and iframe.get("src"):
                pdf_url = iframe["src"]
                if not pdf_url.startswith("http"):
                    pdf_url = domain + pdf_url
            if not pdf_url:
                for a in soup.find_all("a"):
                    href = a.get("href", "")
                    text = (a.text or "").lower()
                    if "download" in text or (".pdf" in href and "storage" in href):
                        pdf_url = href if href.startswith("http") else domain + href
                        break
            if pdf_url:
                pdf_resp = cffi_req.get(pdf_url, headers=headers, impersonate="chrome120", timeout=60, allow_redirects=True)
                if pdf_resp.content[:4] == b"%PDF" and len(pdf_resp.content) > 1000:
                    Path(output).parent.mkdir(parents=True, exist_ok=True)
                    with open(output, "wb") as f:
                        f.write(pdf_resp.content)
                    return {"success": True, "source": f"scihub-{domain}", "size": len(pdf_resp.content)}
        except Exception as e:
            logger.debug(f"Sci-Hub {domain} failed: {e}")
            continue
    return None

def download_scihub_tor(doi, output, timeout=60):
    try:
        from curl_cffi import requests as cffi_req
    except ImportError:
        return None
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
    from bs4 import BeautifulSoup
    for domain in SCI_HUB_DOMAINS:
        try:
            url = f"{domain}/{doi}"
            resp = cffi_req.get(url, headers=headers, proxies=proxies, timeout=timeout)
            if resp.status_code != 200:
                continue
            if resp.content[:4] == b"%PDF" and len(resp.content) > 1000:
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                with open(output, "wb") as f:
                    f.write(resp.content)
                return {"success": True, "source": f"scihub-tor-{domain}", "size": len(resp.content)}
            soup = BeautifulSoup(resp.text, "html.parser")
            pdf_url = None
            iframe = soup.find("iframe", id="pdf")
            if iframe and iframe.get("src"):
                pdf_url = iframe["src"]
                if not pdf_url.startswith("http"):
                    pdf_url = domain + pdf_url
            if pdf_url:
                pdf_resp = cffi_req.get(pdf_url, headers=headers, proxies=proxies, timeout=timeout)
                if pdf_resp.content[:4] == b"%PDF" and len(pdf_resp.content) > 1000:
                    Path(output).parent.mkdir(parents=True, exist_ok=True)
                    with open(output, "wb") as f:
                        f.write(pdf_resp.content)
                    return {"success": True, "source": f"scihub-tor-{domain}", "size": len(pdf_resp.content)}
        except Exception as e:
            logger.debug(f"Tor Sci-Hub {domain} failed: {e}")
            continue
    return None

def download_paper(identifier, output, identifier_type="doi", max_concurrent=3, enable_tor=True):
    sources = []
    if identifier_type == "arxiv_id" or identifier.startswith("10.48550/"):
        sources.append((lambda d, o, **kw: download_arxiv(d, o), "arXiv", 10))
    if identifier_type == "pmid":
        sources.append((lambda d, o, **kw: download_pmc(d, o), "PMC", 15))
    sources.append((lambda d, o, **kw: download_crossref_oa(d, o), "Crossref/OA", 10))
    sources.append((lambda d, o, **kw: download_scihub_direct(d, o, timeout=30), "Sci-Hub-direct", 30))
    if os.environ.get("MEDDATA_API_KEY"):
        sources.append((lambda d, o, **kw: download_meddata(d, o), "MedData", 15))
    if enable_tor:
        sources.append((lambda d, o, **kw: download_scihub_tor(d, o, timeout=60), "Sci-Hub-Tor", 60))
    
    best = None
    start = time.time()
    with ThreadPoolExecutor(max_workers=min(max_concurrent, len(sources))) as pool:
        futures = {pool.submit(fn, identifier, output): label for fn, label, _ in sources}
        try:
            for future in as_completed(futures, timeout=120):
                label = futures[future]
                try:
                    result = future.result(timeout=5)
                    if result and result.get("success"):
                        elapsed = time.time() - start
                        logger.info(f"{label} won ({elapsed:.1f}s)")
                        best = result
                        for f in futures:
                            if not f.done():
                                f.cancel()
                        return result
                except Exception as e:
                    logger.warning(f"{label}: {e}")
        except TimeoutError:
            logger.warning("Download race timeout")
    logger.error(f"All sources failed for {identifier}")
    return None

def record_download(doi, result, output_path):
    record = {
        "doi": doi,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "success": result is not None,
        "source": result.get("source", "none") if result else "none",
        "size": result.get("size", 0) if result else 0,
        "file": output_path,
    }
    if result:
        record["md5"] = md5sum(output_path) if os.path.exists(output_path) else ""
    log_path = Path(output_path).parent / "download_record.json"
    if log_path.exists():
        try:
            with open(log_path) as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []
    else:
        history = []
    history.append(record)
    with open(log_path, "w") as f:
        json.dump(history, f, indent=2)
    return record

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Unified Paper Download Orchestrator")
    parser.add_argument("identifier", help="DOI, arXiv ID, or PMID")
    parser.add_argument("output", help="Output PDF path")
    parser.add_argument("--type", default="doi", choices=["doi", "arxiv_id", "pmid"])
    parser.add_argument("--tor", action="store_true", default=True)
    parser.add_argument("--no-tor", dest="tor", action="store_false")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    result = download_paper(args.identifier, args.output, identifier_type=args.type, enable_tor=args.tor)
    print(json.dumps(record_download(args.identifier, result, args.output), indent=2))
    sys.exit(0 if result else 1)
