#!/usr/bin/env python3
"""
Unified Paper Download — 论文全文下载
====================================
P0 实证，P1 原子性，P2 工程化。

流程:
    1. 收集论文链接 (从搜索输出 或 手动输入)
    2. 去重链接
    3. 并行下载所有链接

调用方式:
    # 从搜索结果批量下载
    python3 unified_download.py --batch search-results.json --output-dir /tmp/papers/

    # 单篇下载（自动识别 DOI/arXiv/PMID）
    python3 unified_download.py "10.1136/bmj.m2689" --output /tmp/paper.pdf

    # 单篇下载（指定类型）
    python3 unified_download.py 1910.13757 --type arxiv_id --output /tmp/paper.pdf

    # 连通性测试
    python3 unified_download.py --test

输入:
    DOI / arXiv ID / PMID / JSON 文件（论文列表，含 PDF 链接字段）

输出:
    PDF 文件 + download_record.json（来源、MD5、耗时）

依赖:
    pdf_download_engine — 核心下载引擎（30+ 源，OA直连/Sci-Hub/MedData）
"""

import argparse, json, os, sys, time, hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

_engine_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _engine_dir)

from pdf_download_engine import (
    race_downloads,
    verify_pdf,
    save_pdf,
    smart_download,
    normalize_doi,
    extract_arxiv_id,
    extract_pmid,
    DEFAULT_OUTPUT_DIR,
    run_test,
)

# ─── 链接提取 ──────────────────────────────────────────────────────

# 各源 PDF 链接字段名 → 统一映射
PDF_URL_FIELDS = {
    # S2
    "pdf_url", "open_access",
    # arXiv
    "arxiv_url_pdf",
    # 通用
    "oa_url", "oa_fulltext_url", "oa_pdf", "pdf_link", "download_url",
    "full_text_url", "fulltext_url", "pdf",
    # CrossRef
    "link",
    # Lens
    "arxiv_url_pdf",
}

# 链接 URL 字段（备用）
URL_FIELDS = {"url", "html_url", "link_url", "landing_page_url"}


def _extract_pdf_urls(paper: Dict[str, Any]) -> List[str]:
    """从论文字典提取所有 PDF 下载链接。"""
    urls = []
    for key in PDF_URL_FIELDS:
        val = paper.get(key)
        if isinstance(val, str) and val and val.startswith("http"):
            urls.append(val)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, str) and item.startswith("http"):
                    urls.append(item)
    # 去重
    seen = set()
    unique = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def _extract_all_urls(paper: Dict[str, Any]) -> List[str]:
    """从论文字典提取所有 URL（包含正文链接）。"""
    urls = []
    for key in URL_FIELDS:
        val = paper.get(key)
        if isinstance(val, str) and val.startswith("http"):
            urls.append(val)
    seen = set()
    unique = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


# ─── 单篇下载 ──────────────────────────────────────────────────────

def _download_one(paper: Dict[str, Any], output_path: str = None) -> Dict[str, Any]:
    """单篇论文下载。"""
    title = paper.get("title", "unknown")[:60]
    doi = paper.get("doi", "") or ""
    arxiv_id = paper.get("arxiv_id", "") or paper.get("arxiv_full_id", "")
    pmid = paper.get("pmid", "") or ""
    source = paper.get("source", "unknown")
    external_ids = paper.get("external_ids", {})
    if isinstance(external_ids, dict):
        pmcs = external_ids.get("PubMedCentral", "")
    else:
        pmcs = ""

    # 1. 先提取已知链接（快速通道）
    known_urls = _extract_pdf_urls(paper)
    known_urls += _extract_all_urls(paper)

    # 2. 如果已有直链，直接下载（比竞速快）
    if known_urls:
        # 并行直链下载
        results = []
        start = time.time()
        for url in known_urls[:5]:  # 最多试 5 条链接
            try:
                content = smart_download(url, timeout=15)
                if content and content[:4] == b"%PDF" and len(content) > 1000:
                    elapsed = time.time() - start
                    if output_path:
                        save_pdf(content, output_path)
                        return {
                            "title": title,
                            "doi": doi,
                            "source": source,
                            "status": "success",
                            "download_method": "direct_url",
                            "url": url,
                            "path": output_path,
                            "size": len(content),
                            "md5": hashlib.md5(content).hexdigest(),
                            "elapsed": round(elapsed, 2),
                        }
            except Exception:
                continue

        # 直链全部失败 → 退回竞速引擎
        method = "direct_url" if known_urls else "engine"
    else:
        method = "engine"

    # 3. 竞速引擎兜底
    start = time.time()
    result = race_downloads(
        doi=doi or None, title=title,
        arxiv_id=arxiv_id or None,
        pmid=pmid or None,
        pmcs_id=pmcs or None,
        external_ids=external_ids if isinstance(external_ids, dict) else {},
        timeout=60,
    )

    elapsed = time.time() - start

    if result.get("status") == "success":
        content = result.get("content")
        src = result.get("winning_source", "unknown")
        size = result.get("size", 0)
        md5 = result.get("md5", "")

        if content and verify_pdf(content):
            path = save_pdf(content, output_path) if output_path else "stdout"
            return {
                "title": title,
                "doi": doi,
                "source": source,
                "status": "success",
                "download_method": method,
                "engine_source": src,
                "path": path,
                "size": size,
                "md5": md5,
                "elapsed": round(elapsed, 2),
            }
        else:
            return {
                "title": title, "doi": doi, "source": source,
                "status": "failed", "download_method": method,
                "error": "invalid PDF content",
                "elapsed": round(elapsed, 2),
            }
    else:
        return {
            "title": title, "doi": doi, "source": source,
            "status": "failed", "download_method": method,
            "error": "engine_failed",
            "details": result.get("papers", []),
            "elapsed": round(elapsed, 2),
        }


def _download_single(identifier: str, output: str, id_type: str = "doi") -> Dict[str, Any]:
    """手动输入标识符下载。"""
    doi = arxiv_id = pmid = ""
    if id_type == "arxiv_id":
        arxiv_id = identifier
    elif id_type == "pmid":
        pmid = identifier
    elif id_type == "doi":
        doi = normalize_doi(identifier) if identifier.startswith("10.") else ""

    output_path = output or os.path.join(DEFAULT_OUTPUT_DIR, f"download_{int(time.time())}.pdf")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    return _download_one(
        {"title": identifier, "doi": doi, "arxiv_id": arxiv_id, "pmid": pmid},
        output_path
    )


# ─── 批量下载 ──────────────────────────────────────────────────────

def _download_batch(input_path: str, output_dir: str = None, batch_fmt: str = "json") -> Dict[str, Any]:
    """批量下载。"""
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        if batch_fmt == "ndjson":
            papers = [json.loads(line) for line in f if line.strip()]
        else:
            data = json.load(f)
            if isinstance(data, list):
                papers = data
            elif isinstance(data, dict):
                papers = data.get("papers", data.get("results", []))
            else:
                print(f"ERROR: unsupported format", file=sys.stderr)
                sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Download — {len(papers)} papers")
    print(f"{'='*60}")
    print(f"Input:  {input_path}")
    print(f"Output: {output_dir}")
    print(f"{'='*60}\n")

    results = []
    max_workers = min(8, len(papers))

    start = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {}
        for p in papers:
            if not p.get("title"):
                results.append({"title": "?", "status": "skipped", "reason": "no title"})
                continue
            # 生成输出文件名
            title_safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in p.get("title", "?")[:60])
            doi = p.get("doi", "") or ""
            if doi:
                clean = doi.replace("/", "_").replace(".", "_")
                out = os.path.join(output_dir, f"{clean}.pdf")
            else:
                out = os.path.join(output_dir, f"{title_safe}.pdf")
            Path(out).parent.mkdir(parents=True, exist_ok=True)
            f = pool.submit(_download_one, p, out)
            futures[f] = p

        for future in as_completed(futures, timeout=600):
            p = futures[future]
            title = p.get("title", "?")[:50]
            try:
                result = future.result(timeout=60)
                results.append(result)
                status_icon = "✅" if result["status"] == "success" else "❌"
                method = result.get("download_method", "?")
                print(f"  {status_icon} {title}  method={method:15s}  elapsed={result.get('elapsed', 0):5.1f}s  size={result.get('size', 0):>7d}B")
            except Exception as e:
                results.append({"title": title, "status": "error", "error": str(e)})
                print(f"  ❌ {title}  ERROR: {e}")

    elapsed = time.time() - start
    downloaded = sum(1 for r in results if r.get("status") == "success")
    failed = sum(1 for r in results if r.get("status") in ("failed", "error"))

    record = {
        "total": len(papers),
        "downloaded": downloaded,
        "failed": failed,
        "elapsed": round(elapsed, 2),
        "papers": results,
    }

    record_path = os.path.join(output_dir, "download_record.json")
    with open(record_path, "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Total:   {len(papers)}")
    print(f"OK:      {downloaded}")
    print(f"Failed:  {failed}")
    print(f"Time:    {elapsed:.1f}s")
    print(f"Record:  {record_path}")
    print(f"{'='*60}")

    return record


# ─── CLI ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Unified Paper Download — 论文全文下载",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单篇 DOI 下载
  %(prog)s 10.1136/bmj.m2689

  # 单篇 arXiv 下载
  %(prog)s 2307.11274 --type arxiv_id

  # 从搜索结果批量下载
  %(prog)s --batch search-results.json

  # 连通性测试
  %(prog)s --test
        """
    )
    parser.add_argument("identifier", nargs="?", default=None,
                        help="DOI / arXiv ID / PMID / 论文标题")
    parser.add_argument("--output", "-o", default=None, help="输出 PDF 路径")
    parser.add_argument("--type", "-t", default="doi",
                        choices=["doi", "arxiv_id", "pmid"],
                        help="标识符类型 (默认: doi)")
    parser.add_argument("--output-dir", "-d", default=None,
                        help="输出目录 (默认: ./outputs/papers/pdfs)")
    parser.add_argument("--batch", "-b", default=None,
                        help="批量文件（JSON 列表 或 JSONL）")
    parser.add_argument("--format", "-f", default="json",
                        choices=["json", "ndjson"],
                        help="批量文件格式 (默认: json)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出")
    parser.add_argument("--test", action="store_true",
                        help="连通性测试")

    args = parser.parse_args()

    if args.test:
        result = run_test()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        ok = sum(1 for v in result.values() if v == "ok")
        print(f"\nPassed: {ok}/{len(result)}")
        sys.exit(0)

    if args.batch:
        _download_batch(args.batch, args.output_dir, batch_fmt=args.format)
        sys.exit(1)

    if not args.identifier:
        print("ERROR: 需要 identifier 或 --batch", file=sys.stderr)
        sys.exit(1)

    # 单篇
    result = _download_single(args.identifier, args.output, args.type)

    if args.verbose:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        icon = "✅" if result["status"] == "success" else "❌"
        print(f"{icon} {result['status']} — {result.get('title', '?')[:50]}")
        if result["status"] in ("success",):
            print(f"   Method:   {result.get('download_method', '?')}")
            print(f"   Source:   {result.get('engine_source', result.get('url', '?'))}")
            print(f"   Size:     {result.get('size', 0)} bytes")
            print(f"   MD5:      {result.get('md5', '?')}")
            print(f"   Path:     {result.get('path', '?')}")
            print(f"   Time:     {result.get('elapsed', 0):.1f}s")

    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()