#!/usr/bin/env python3
"""
调度器 — 并行竞速下载 + 批量下载 + 连通性测试。
管线层：编排各 tier 的下载函数，返回统一结果。
"""
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import config
from .utils import verify_pdf, save_pdf
from .tier1_oa import (
    download_arxiv_pdf, download_frontiers_pdf, download_plos_pdf,
    download_crossref_link, download_unpaywall, download_pubmed_central,
    search_pmc_for_pubmed,
)
from .tier2_scihub import download_scihub_direct, download_scihub_via_tor
from .tier3_backup import download_libgen, download_meddata
from .tier4_publishers import (
    normalize_doi, download_s2_pdf, download_biorxiv_pdf, download_core,
    download_doi2pdf, download_via_openurl, download_sciencedirect,
    download_springer, download_wiley, download_ieee, download_acm,
)


def race_downloads(  # type: ignore[no-redef]
    doi: str | None = None, title: str | None = None,
    arxiv_id: str | None = None, pmid: str | None = None,
    pmcs_id: str | None = None, external_ids: dict | None = None,
    timeout: int = 60
) -> Dict[str, Any]:
    """Race multiple download sources concurrently."""
    results: List[Any] = []
    start_time = time.time()

    source_fns = []

    # Tier 0: Semantic Scholar (instant OA URL)
    if doi:
        ext_ids = {}
        if external_ids and isinstance(external_ids, dict):
            ext_ids = external_ids
        source_fns.append(("s2_pdf", lambda: download_s2_pdf(doi=doi, external_ids=ext_ids), "Semantic Scholar OA"))

    # Tier 1: OA Direct (instant)
    if doi:
        ndoi = normalize_doi(doi)
        source_fns.append(("crossref", lambda: download_crossref_link(ndoi), "CrossRef OA"))
        source_fns.append(("unpaywall", lambda: download_unpaywall(ndoi), "Unpaywall"))
        source_fns.append(("frontiers", lambda: download_frontiers_pdf(ndoi), "Frontiers"))
        source_fns.append(("plos", lambda: download_plos_pdf(ndoi), "PLOS"))
        source_fns.append(("core", lambda: download_core(ndoi), "CORE"))
        source_fns.append(("doi2pdf", lambda: download_doi2pdf(ndoi), "DOI2PDF"))

    if pmid:
        source_fns.append(("pmc_elink", lambda: _try_pmc_via_pmid(pmid), "PMC via PMID"))

    if pmcs_id:
        source_fns.append(("pmc", lambda: download_pubmed_central(pmcs_id), "PMC"))

    # Tier 2: Sci-Hub
    if doi:
        source_fns.append(("scihub_direct", lambda: download_scihub_direct(doi), "Sci-Hub direct"))

    # Tier 3: Backup
    if doi:
        source_fns.append(("meddata", lambda: download_meddata(doi=doi) if doi else None, "MedData"))
        if title:
            source_fns.append(("libgen", lambda: download_libgen(title=title), "LibGen"))

    # Tier 4: Publishers
    if doi:
        ndoi = normalize_doi(doi)
        source_fns.append(("sciencedirect", lambda: download_sciencedirect(ndoi), "ScienceDirect"))
        source_fns.append(("springer", lambda: download_springer(ndoi, title or ""), "Springer"))
        source_fns.append(("wiley", lambda: download_wiley(ndoi), "Wiley"))
        source_fns.append(("ieee", lambda: download_ieee(ndoi), "IEEE"))
        source_fns.append(("acm", lambda: download_acm(ndoi), "ACM"))

    # Run racing
    winning_source = None
    content: Optional[bytes] = None

    with ThreadPoolExecutor(max_workers=min(12, max(1, len(source_fns)))) as pool:
        futures = {}
        for name, fn, desc in source_fns:
            if fn is not None:
                futures[pool.submit(fn)] = (name, desc)

        for future in as_completed(futures, timeout=timeout):
            name, desc = futures[future]
            try:
                result = future.result(timeout=timeout)
                if result and verify_pdf(result):
                    winning_source = desc
                    content = result
                    for f in futures:
                        f.cancel()
                    break
            except Exception:
                continue

    elapsed = time.time() - start_time

    return {
        "status": "success" if content else "failed",
        "content": content,
        "winning_source": winning_source or "none",
        "elapsed": round(elapsed, 2),
        "size": len(content) if content else 0,
        "md5": hashlib.md5(content).hexdigest() if content else "",
    }


def _try_pmc_via_pmid(pmid: str) -> Optional[bytes]:
    """Search PMC via PMID, then download."""
    pmcs = search_pmc_for_pubmed(pmid)
    if pmcs:
        return download_pubmed_central(pmcs)
    return None


def batch_download(candidates: List[Dict], output_dir: str | None = None) -> Dict[str, Any]:
    """Batch download papers from search results."""
    if output_dir is None:
        output_dir = config.DEFAULT_OUTPUT_DIR
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    results: List[Dict[str, Any]] = []
    max_workers = min(8, len(candidates))

    start = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures: Dict[Any, Dict] = {}
        for p in candidates:
            if not p.get("title"):
                results.append({"title": "?", "status": "skipped", "reason": "no title"})
                continue
            title_safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in p.get("title", "?")[:60])
            doi = p.get("doi", "") or ""
            if doi:
                clean = doi.replace("/", "_").replace(".", "_")
                out = os.path.join(output_dir, f"{clean}.pdf")
            else:
                out = os.path.join(output_dir, f"{title_safe}.pdf")
            Path(out).parent.mkdir(parents=True, exist_ok=True)

            f = pool.submit(race_downloads,
                doi=p.get("doi"), title=p.get("title"),
                arxiv_id=p.get("arxiv_id"), pmid=p.get("pmid"),
                external_ids=p.get("external_ids", {}),
                timeout=60)
            futures[f] = p

        for future in as_completed(futures, timeout=600):
            p = futures[future]
            title = p.get("title", "?")[:50]
            try:
                result = future.result(timeout=60)
                results.append(result)
                status_icon = "✅" if result.get("status") == "success" else "❌"
                method = result.get("winning_source", "?")
                print(f"  {status_icon} {title}  source={method:20s}  elapsed={result.get('elapsed', 0):5.1f}s  size={result.get('size', 0):>7d}B")
            except Exception as e:
                results.append({"title": title, "status": "error", "error": str(e)})
                print(f"  ❌ {title}  ERROR: {e}")

    elapsed = time.time() - start
    downloaded = sum(1 for r in results if r.get("status") == "success")

    record: Dict[str, Any] = {"total": len(candidates), "downloaded": downloaded, "elapsed": round(elapsed, 2), "papers": results}

    record_path = os.path.join(output_dir, "download_record.json")
    with open(record_path, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Total: {len(candidates)}  OK: {downloaded}  Time: {elapsed:.1f}s")
    print(f"Record: {record_path}")
    print(f"{'='*60}")

    return record


def run_test() -> Dict[str, Any]:
    """Run connectivity test for all download sources."""
    test_dois = {
        "arxiv": ("arxiv_pdf", "2101.00001"),
        "frontiers": ("frontiers_pdf", "10.3389/fneur.2020.00001"),
        "plos": ("plos_pdf", "10.1371/journal.pone.0230001"),
        "crossref": ("crossref_link", "10.1038/s41586-020-2649-2"),
        "unpaywall": ("unpaywall", "10.1038/s41586-020-2649-2"),
        "scihub": ("scihub_direct", "10.1016/j.cell.2020.02.001"),
        "doi2pdf": ("doi2pdf", "10.1038/s41586-020-2649-2"),
        "core": ("core", "10.1038/s41586-020-2649-2"),
        "openurl": ("openurl", "10.1038/s41586-020-2649-2"),
    }

    results = {}
    for name, test_doi in test_dois.items():
        try:
            func_map = {
                "arxiv_pdf": download_arxiv_pdf,
                "frontiers_pdf": download_frontiers_pdf,
                "plos_pdf": download_plos_pdf,
                "crossref_link": download_crossref_link,
                "unpaywall": download_unpaywall,
                "scihub_direct": download_scihub_direct,
                "doi2pdf": download_doi2pdf,
                "core": download_core,
                "openurl": download_via_openurl,
            }
            if name in func_map:
                func = func_map[name]
                content = func(test_doi)
                results[name] = "ok" if content and verify_pdf(content) else "fail"
            else:
                results[name] = "skip"
        except Exception:
            results[name] = "error"

    return results