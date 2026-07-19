#!/usr/bin/env python3
"""文献检索与下载综合诊断。

三阶段：
  1. 检索测试 — 遍历每个源，搜索"BPPV"，统计耗时/数量/DOI覆盖率/PDF链接
  2. DOI解析测试 — 用已知DOI测试各源的 search_by_doi
  3. 下载测试 — 遍历各下载层tier，用已知DOI测PDF获取
"""

import json
import os
import sys
import time
import traceback
import concurrent.futures
from typing import Any, Dict, Optional

# ── 加入 literature.py 脚本路径 ──
LIT_SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if LIT_SCRIPTS not in sys.path:
    sys.path.insert(0, LIT_SCRIPTS)

from sources import SOURCE_REGISTRY, DEFAULT_SOURCES
from download import (
    verify_pdf,
    download_scihub,
    download_crossref_link,
    download_frontiers_pdf,
    download_plos_pdf,
    download_unpaywall,
    download_doi2pdf,
    download_core,
    download_springer,
    download_wiley,
)
from download.tier4_publishers import download_s2_pdf
from download.tier1_oa import download_pubmed_central, search_pmc_for_pubmed
from download.meddata import try_meddata as download_meddata


# ═══════════════════════════════════════════════
# 测试数据
# ═══════════════════════════════════════════════

SEARCH_QUERY = "BPPV vestibular"
SEARCH_MAX = 3
SEARCH_TIMEOUT = 12  # 每源最大等待秒数（PubMed 偶需~10s）

# 测试用 DOI（要求确认可下载）
KNOWN_DOIS = {
    "oa_frontiers": "10.3389/fneur.2020.00001",
    "oa_plos": "10.1371/journal.pone.0230001",
    "scopus_elsevier": "10.1016/j.jclinepi.2020.05.018",
    "scihub_verified": "10.1016/j.jcrs.2019.04.024",
    "scihub_cell": "10.1016/j.cell.2020.02.001",
    "nature_sample": "10.1038/s41586-020-2649-2",
}

# 每层下载测试用例: (层名, 用例名, DOI, 下载函数)
DOWNLOAD_CASES = [
    # Tier 0: S2 PDF
    ("tier0", "s2_pdf", KNOWN_DOIS["nature_sample"],
     lambda doi=KNOWN_DOIS["nature_sample"]: download_s2_pdf(doi=doi)),
    # Tier 1: OA 直链
    ("tier1", "crossref", KNOWN_DOIS["nature_sample"],
     lambda doi=KNOWN_DOIS["nature_sample"]: download_crossref_link(doi)),
    ("tier1", "unpaywall", KNOWN_DOIS["nature_sample"],
     lambda doi=KNOWN_DOIS["nature_sample"]: download_unpaywall(doi)),
    ("tier1", "frontiers", KNOWN_DOIS["oa_frontiers"],
     lambda doi=KNOWN_DOIS["oa_frontiers"]: download_frontiers_pdf(doi)),
    ("tier1", "plos", KNOWN_DOIS["oa_plos"],
     lambda doi=KNOWN_DOIS["oa_plos"]: download_plos_pdf(doi)),
    ("tier1", "core", KNOWN_DOIS["nature_sample"],
     lambda doi=KNOWN_DOIS["nature_sample"]: download_core(doi)),
    ("tier1", "doi2pdf", KNOWN_DOIS["nature_sample"],
     lambda doi=KNOWN_DOIS["nature_sample"]: download_doi2pdf(doi)),
    ("tier1", "springer", KNOWN_DOIS["scopus_elsevier"],
     lambda doi=KNOWN_DOIS["scopus_elsevier"]: download_springer(doi)),
    ("tier1", "wiley", KNOWN_DOIS["scopus_elsevier"],
     lambda doi=KNOWN_DOIS["scopus_elsevier"]: download_wiley(doi)),
    # Tier 2: Sci-Hub (bban.top CDN)
    ("tier2", "scihub", KNOWN_DOIS["scihub_cell"],
     lambda doi=KNOWN_DOIS["scihub_cell"]: download_scihub(doi)),
    ("tier2", "scihub_bban", KNOWN_DOIS["scihub_verified"],
     lambda doi=KNOWN_DOIS["scihub_verified"]: download_scihub(doi)),
    # Tier 3: 备份
    ("tier3", "meddata", KNOWN_DOIS["scihub_cell"],
     lambda doi=KNOWN_DOIS["scihub_cell"]: download_meddata(doi=doi, output_path=".")),
]


# ═══════════════════════════════════════════════
# 检索测试
# ═══════════════════════════════════════════════

def test_search_source(name: str, source_cls) -> Dict[str, Any]:
    """测试单个检索源的连通性和结果质量。"""
    result = {
        "source": name,
        "status": "error",
        "error": None,
        "time_s": None,
        "n_results": 0,
        "has_doi": False,
        "has_pdf_link": False,
    }
    try:
        def _run():
            inst = source_cls()
            return inst.search(SEARCH_QUERY, max_results=SEARCH_MAX)
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(_run)
            papers = fut.result(timeout=SEARCH_TIMEOUT)
        elapsed = round(time.time() - start, 2)
        result["time_s"] = elapsed
        result["n_results"] = len(papers)
        if papers:
            result["has_doi"] = any(p.get("doi") for p in papers)
            result["has_pdf_link"] = any(
                p.get("pdf_url") or p.get("openAccessPdf") or
                p.get("links") or p.get("local_links")
                for p in papers
            )
            # 采样第一条
            p0 = papers[0]
            result["sample_title"] = p0.get("title", "")[:80]
            result["sample_doi"] = p0.get("doi", "")
            result["sample_source"] = p0.get("source", "")
            result["has_pdf_url_field"] = bool(p0.get("pdf_url") or p0.get("openAccessPdf"))
        result["status"] = "ok" if papers else "empty"
    except concurrent.futures.TimeoutError:
        result["status"] = "error"
        result["error"] = f"timeout > {SEARCH_TIMEOUT}s"
    except Exception as e:
        tb = traceback.format_exc()
        result["status"] = "error"
        result["error"] = f"{type(e).__name__}: {str(e)[:120]}"
    return result


def test_search_sources() -> Dict[str, Any]:
    """测试所有注册的检索源。"""
    sources = dict(SOURCE_REGISTRY)  # 浅拷贝
    results = {}
    for name, cls in sources.items():
        results[name] = test_search_source(name, cls)
    return {
        "description": f"检索源测试 (query='{SEARCH_QUERY}', max={SEARCH_MAX})",
        "n_sources": len(results),
        "n_ok": sum(1 for r in results.values() if r["status"] == "ok"),
        "n_error": sum(1 for r in results.values() if r["status"] == "error"),
        "n_empty": sum(1 for r in results.values() if r["status"] == "empty"),
        "sources": results,
    }


# ═══════════════════════════════════════════════
# DOI 解析测试
# ═══════════════════════════════════════════════

def test_doi_resolution() -> Dict[str, Any]:
    """测试各源的 DOI 精确解析。"""
    doi = KNOWN_DOIS["scihub_verified"]
    results = {}
    for name, cls in SOURCE_REGISTRY.items():
        inst = cls()
        search_by_doi = getattr(inst, "search_by_doi", None)
        if not search_by_doi:
            results[name] = {"status": "skipped", "reason": "no search_by_doi"}
            continue
        sub = {"doi": doi, "status": "error", "error": None, "time_s": None}
        try:
            start = time.time()
            paper = search_by_doi(doi)
            sub["time_s"] = round(time.time() - start, 2)
            if paper:
                sub["status"] = "ok"
                sub["title"] = paper.get("title", "")[:80]
                sub["matched_doi"] = bool(paper.get("doi"))
            else:
                sub["status"] = "miss"
        except Exception as e:
            sub["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        results[name] = sub
    return {
        "description": f"DOI 精确解析测试 (doi={doi})",
        "results": results,
    }


# ═══════════════════════════════════════════════
# 下载测试
# ═══════════════════════════════════════════════

def test_download() -> Dict[str, Any]:
    """测试各下载层。"""
    # 单测试超时（秒），防止某层 hang 住整个诊断
    PER_TEST_TIMEOUT = 20
    results = {}
    for layer, name, doi, func in DOWNLOAD_CASES:
        key = f"{layer}/{name}"
        sub = {"layer": layer, "name": name, "doi": doi, "status": "pending"}
        try:
            start = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                fut = pool.submit(func)
                content = fut.result(timeout=PER_TEST_TIMEOUT)
            elapsed = round(time.time() - start, 2)
            sub["time_s"] = elapsed
            if content and verify_pdf(content):
                sub["status"] = "ok"
                sub["bytes"] = len(content)
            elif content:
                sub["status"] = "fail"
                sub["bytes"] = len(content)
                sub["reason"] = "not valid PDF"
            else:
                sub["status"] = "fail"
                sub["reason"] = "empty result"
        except concurrent.futures.TimeoutError:
            sub["status"] = "error"
            sub["error"] = f"timeout > {PER_TEST_TIMEOUT}s"
        except Exception as e:
            sub["status"] = "error"
            sub["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        results[key] = sub
    return {
        "description": "PDF 下载管线测试 (各层独立测试)",
        "n_tests": len(DOWNLOAD_CASES),
        "n_ok": sum(1 for r in results.values() if r["status"] == "ok"),
        "n_fail": sum(1 for r in results.values() if r["status"] == "fail"),
        "n_error": sum(1 for r in results.values() if r["status"] == "error"),
        "tiers": results,
    }


# ═══════════════════════════════════════════════
# 综合入口
# ═══════════════════════════════════════════════

def comprehensive_test() -> Dict[str, Any]:
    """三阶段综合诊断。"""
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "summary": {},
    }

    # Phase 1: 检索
    report["search"] = test_search_sources()
    report["summary"]["search_ok"] = report["search"]["n_ok"]
    report["summary"]["search_error"] = report["search"]["n_error"]
    report["summary"]["search_empty"] = report["search"]["n_empty"]

    # Phase 2: DOI 解析
    report["doi_resolution"] = test_doi_resolution()
    report["summary"]["doi_ok"] = sum(1 for r in report["doi_resolution"]["results"].values() if r["status"] == "ok")
    report["summary"]["doi_miss"] = sum(1 for r in report["doi_resolution"]["results"].values() if r["status"] == "miss")
    report["summary"]["doi_error"] = sum(1 for r in report["doi_resolution"]["results"].values() if r["status"] == "error")

    # Phase 3: 下载
    report["download"] = test_download()
    report["summary"]["download_ok"] = report["download"]["n_ok"]
    report["summary"]["download_fail"] = report["download"]["n_fail"]
    report["summary"]["download_error"] = report["download"]["n_error"]

    # 总结
    report["summary"]["overall"] = "all_ok" if (
        report["search"]["n_error"] == 0 and
        report["download"]["n_ok"] > 0
    ) else "partial_failure"

    return report


if __name__ == "__main__":
    report = comprehensive_test()
    print(json.dumps(report, indent=2, ensure_ascii=False))
