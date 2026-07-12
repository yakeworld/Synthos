#!/usr/bin/env python3
"""
调度器 — 串行顺序下载。
管线层：按顺序依次尝试各 tier，每一层独立返回明确结果。
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import config
from .utils import verify_pdf, save_pdf
from .tier1_oa import (
    download_arxiv_pdf, download_frontiers_pdf, download_plos_pdf,
    download_crossref_link, download_unpaywall, download_pubmed_central,
    search_pmc_for_pubmed,
)
from .scientific_hub import download as download_scihub_direct
from .tier3_backup import download_libgen  # 已在 tier3 中
from .tier3_backup import download_libgen
from .meddata import try_meddata
from .tier4_publishers import (
    normalize_doi, download_s2_pdf, download_biorxiv_pdf, download_core,
    download_doi2pdf, download_via_openurl, download_sciencedirect,
    download_springer, download_wiley, download_ieee, download_acm,
)


def sequential_download(
    doi: str | None = None, title: str | None = None,
    arxiv_id: str | None = None, pmid: str | None = None,
    pmcs_id: str | None = None, external_ids: dict | None = None,
    timeout: int = 30, save_dir: str | None = None,
) -> Dict[str, Any]:
    """按顺序尝试各层下载，返回每一层的结果。"""
    results: List[Dict[str, Any]] = []
    start_time = time.time()
    winner = {"content": None, "source": None}

    def _run(name, fn, desc, max_timeout):
        """执行一个下载层，返回结果。"""
        t0 = time.time()
        try:
            content = fn()
            elapsed = round(time.time() - t0, 1)
            if content and verify_pdf(content):
                result = {
                    "layer": name,
                    "source": desc,
                    "status": "success",
                    "elapsed": elapsed,
                    "size": len(content),
                    "md5": hashlib.md5(content).hexdigest(),
                }
                if not winner["content"]:
                    winner["content"] = content
                    winner["source"] = desc
                return result
            else:
                return {
                    "layer": name, "source": desc,
                    "status": "no_pdf", "elapsed": elapsed,
                }
        except Exception as e:
            elapsed = round(time.time() - t0, 1)
            return {
                "layer": name, "source": desc,
                "status": "error", "error": str(e),
                "elapsed": elapsed,
            }

    # ── Tier 0: Semantic Scholar ──
    if doi:
        ext_ids = {}
        if external_ids and isinstance(external_ids, dict):
            ext_ids = external_ids
        results.append(_run(
            "tier0",
            lambda: download_s2_pdf(doi=doi, external_ids=ext_ids),
            "Semantic Scholar OA", timeout
        ))

    # ── Tier 1: OA Direct ──
    if doi:
        ndoi = normalize_doi(doi)
        results.append(_run("tier1",
            lambda: download_crossref_link(ndoi),
            "CrossRef OA", timeout))
        results.append(_run("tier1",
            lambda: download_unpaywall(ndoi),
            "Unpaywall", timeout))
        results.append(_run("tier1",
            lambda: download_frontiers_pdf(ndoi),
            "Frontiers", timeout))
        results.append(_run("tier1",
            lambda: download_plos_pdf(ndoi),
            "PLOS", timeout))
        results.append(_run("tier1",
            lambda: download_core(ndoi),
            "CORE", timeout))
        results.append(_run("tier1",
            lambda: download_doi2pdf(ndoi),
            "DOI2PDF", timeout))

    if pmid:
        results.append(_run("tier1",
            lambda: _try_pmc_via_pmid(pmid),
            "PMC via PMID", timeout))

    if pmcs_id:
        results.append(_run("tier1",
            lambda: download_pubmed_central(pmcs_id),
            "PMC", timeout))

    if arxiv_id:
        results.append(_run("tier1",
            lambda: download_arxiv_pdf(arxiv_id),
            "arXiv", timeout))

    # ── Tier 2: Sci-Hub (bban.top CDN 直连) ──
    if doi:
        results.append(_run("tier2",
            lambda: download_scihub_direct(doi),
            "Sci-Hub bban.top", timeout))

    # ── Tier 3: Backup ──
    if doi:
        results.append(_run("tier3",
            lambda: try_meddata(doi=doi, output_path=".") if doi else None,
            "MedData", timeout))
        if title:
            results.append(_run("tier3",
                lambda: download_libgen(title=title),
                "LibGen", timeout))

    # ── Tier 4: Publishers ──
    if doi:
        ndoi = normalize_doi(doi)
        results.append(_run("tier4",
            lambda: download_sciencedirect(ndoi),
            "ScienceDirect", timeout))
        results.append(_run("tier4",
            lambda: download_springer(ndoi, title or ""),
            "Springer", timeout))
        results.append(_run("tier4",
            lambda: download_wiley(ndoi),
            "Wiley", timeout))
        results.append(_run("tier4",
            lambda: download_ieee(ndoi),
            "IEEE", timeout))
        results.append(_run("tier4",
            lambda: download_acm(ndoi),
            "ACM", timeout))

    elapsed = round(time.time() - start_time, 2)

    # 保存成功的 PDF
    content = winner.get("content") or None
    if content and save_dir:
        name = (doi or title or "unknown")[:50]
        out = Path(save_dir) / f"{name}.pdf"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(content)

    return {
        "layers": results,
        "status": "success" if winner.get("content") else "failed",
        "content": winner.get("content"),
        "winning_source": winner.get("source") or "none",
        "elapsed": elapsed,
        "size": len(winner.get("content")) if winner.get("content") else 0,
        "md5": hashlib.md5(winner.get("content")).hexdigest() if winner.get("content") else "",
    }


def _try_pmc_via_pmid(pmid: str) -> Optional[bytes]:
    """Search PMC via PMID, then download."""
    pmcs = search_pmc_for_pubmed(pmid)
    if pmcs:
        return download_pubmed_central(pmcs)
    return None


def run_test() -> Dict[str, Any]:
    """连通性测试：对每一层独立测试。"""
    test_cases = [
        ("tier0", "s2_pdf", "10.1038/s41586-020-2649-2", download_s2_pdf),
        ("tier1", "crossref", "10.1038/s41586-020-2649-2", download_crossref_link),
        ("tier1", "unpaywall", "10.1038/s41586-020-2649-2", download_unpaywall),
        ("tier1", "frontiers", "10.3389/fneur.2020.00001", download_frontiers_pdf),
        ("tier1", "plos", "10.1371/journal.pone.0230001", download_plos_pdf),
        ("tier1", "core", "10.1038/s41586-020-2649-2", download_core),
        ("tier1", "doi2pdf", "10.1038/s41586-020-2649-2", download_doi2pdf),
        ("tier2", "scihub", "10.1016/j.cell.2020.02.001", download_scihub_direct),
        ("tier2", "scihub_bban", "10.1016/j.jcrs.2019.04.024", download_scihub_direct),
        ("tier3", "meddata", "10.1016/j.cell.2020.02.001", lambda: try_meddata(doi="10.1016/j.cell.2020.02.001", output_path=".")),
    ]

    results = {}
    for layer, name, doi, func in test_cases:
        try:
            content = func()
            results[f"{layer}/{name}"] = "ok" if content and verify_pdf(content) else "fail"
        except Exception:
            results[f"{layer}/{name}"] = "error"

    return results


if __name__ == "__main__":
    # 示例：单篇下载
    import argparse
    parser = argparse.ArgumentParser(description="Sequential paper download")
    parser.add_argument("--doi", help="DOI to download")
    parser.add_argument("--title", help="Title for backup download")
    parser.add_argument("--pmid", help="PMID for MedData")
    parser.add_argument("--save", help="Save directory")
    args = parser.parse_args()

    result = sequential_download(
        doi=args.doi, title=args.title, pmid=args.pmid,
        save_dir=args.save,
    )

    print(json.dumps({
        k: v for k, v in result.items() if k != "content"
    }, indent=2, ensure_ascii=False))

    for layer in result.get("layers", []):
        print(f"  {layer['layer']:5s} {layer['source']:20s} → {layer['status']}")