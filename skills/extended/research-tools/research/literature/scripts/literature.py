#!/usr/bin/env python3
"""文献检索统一 CLI 入口

职责: 统一的文献检索/下载/验证管线 CLI。
所有 PDF 下载通过 bban.top CDN 直连完成（https://sci.bban.top/pdf/{DOI}.pdf）。
所有操作通过 subcommand 路由：search, download, verify, pipeline, test。

架构:
  search → 多源检索 → 合并去重 → JSON 输出
  download → 论文 JSON → 遍历链接 → 下载 PDF → 报告
  pipeline → search + download + MedData 兜底 → 完整报告
  verify → 论文目录 → BIB/PDF 状态 → 报告
  test → 所有源连通性测试

设计决策:
- 统一 CLI 入口，隐藏底层 sources/ 和 download/ 模块
- 搜索时按 DOI 去重，避免同一论文多个来源重复
- download 遍历 {pdf_url, local_links, links} 按优先级下载，无需竞速
- MedData 作为 pipeline 中 PDF 未找到的兜底源
- 所有函数不抛异常，错误通过 errors 数组报告

数据流:
  用户输入 → literature.py → sources/*.py (search) → 标准化纸
  → 去重 → JSON 输出
  JSON → download/ → smart_download() → verify_pdf() → 保存 PDF
  → 报告

限制:
- 需要 SEMANTIC_SCHOLAR_API_KEY 环境变量（S2 源）
- 部分源需要网络环境支持（Sci-Hub 等可能受限）
- 搜索结果的 PDF 链接可能过期

退出码:
  0: 成功
  1: 用法错误（缺少 subcommand 或参数）

依赖: sources/, download/ (同目录下), urllib (stdlib), json (stdlib)
"""
import sys
import os
import json
import argparse
import re
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from sources import SOURCE_REGISTRY, DEFAULT_SOURCES
from download import smart_download, run_test, verify_pdf, normalize_doi, safe_filename, download_scihub, try_meddata


def parse_query(raw: str):
    """解析查询字符串中的字段过滤（DOI/author/title 精确检索）。
    
    返回: (keywords: str, fields: dict)
    - doi:xxx / 10.xxx → fields={"_is_doi": True, "doi": "xxx"}
    - title:xxx → fields={"_is_title": True, "title": "xxx"}
    - author:xxx → fields={"author": "xxx"}
    - year:xxx → fields={"year": "xxx"}
    """
    raw = raw.strip()
    if raw.startswith("doi:"):
        return (raw[4:].strip(), {"_is_doi": True})
    if re.match(r'^10\.\d{4,}/', raw):
        return (raw, {"_is_doi": True})

    fields = {}
    keywords_parts = []
    current_field = None
    current_value = []

    for token in raw.split():
        m = re.match(r'^(title|author|year|journal|doi|volume|issue):(.+)$', token, re.IGNORECASE)
        if m:
            if current_field and current_value:
                val = ' '.join(current_value)
                if current_field == "doi":
                    fields["_is_doi"] = True
                    fields["doi"] = val
                else:
                    fields[current_field] = val
            current_field = m.group(1).lower()
            current_value = [m.group(2)]
        else:
            if current_field:
                current_value.append(token)
            else:
                keywords_parts.append(token)

    if current_field and current_value:
        val = ' '.join(current_value)
        if current_field == "doi":
            fields["_is_doi"] = True
            fields["doi"] = val
        else:
            fields[current_field] = val

    keywords = ' '.join(keywords_parts)
    return (keywords, fields)


def apply_fields_to_topic(topic: str, fields: dict) -> tuple:
    """根据字段映射到各源实际可用的查询。返回 (topic, extra_params)"""
    extra = {}
    if fields.get("_is_doi"):
        # DOI 精确检索 — 返回到 cmd_search 后特殊处理
        return (topic, {"_is_doi": fields.get("doi", "")})
    if fields.get("_is_title"):
        return (fields.get("title", topic), {})
    if fields.get("author"):
        extra["author"] = fields["author"]
    if fields.get("year"):
        extra["year"] = fields["year"]
    return (topic, extra)


def cmd_search(args):
    """执行多源检索（支持字段过滤、DOI精确检索）。"""
    raw_query = " ".join(args.topic)
    sources = args.sources or DEFAULT_SOURCES
    max_results = args.max or 10

    # 解析字段过滤
    keywords, fields = parse_query(raw_query)
    
    # 如果有 DOI 精确检索，直接调用各源的 search_by_doi
    if fields.get("_is_doi"):
        doi = fields["_is_doi"] if not isinstance(fields.get("_is_doi"), bool) else str(fields.get("_is_doi", ""))
        # 实际上 _is_doi 为 True 时 doi 字段是真实 DOI
        actual_doi = fields.get("doi", raw_query)
        all_papers = []
        seen = set()
        for source_name in sources:
            source_name_lower = source_name.lower()
            if source_name_lower not in SOURCE_REGISTRY:
                continue
            try:
                source_cls = SOURCE_REGISTRY[source_name_lower]
                source = source_cls()
                if hasattr(source, "search_by_doi"):
                    result = source.search_by_doi(actual_doi)
                    if result:
                        result.setdefault("source", source_name_lower)
                        key = actual_doi
                        if key not in seen:
                            seen.add(key)
                            all_papers.append(result)
            except Exception:
                continue
        if all_papers:
            print(json.dumps({
                "topic": raw_query,
                "papers": all_papers,
                "total": len(all_papers),
                "sources_queried": [s.lower() for s in sources if s.lower() in SOURCE_REGISTRY],
                "errors": [],
            }, indent=2, ensure_ascii=False))
        return

    # 普通检索 — 解析字段
    topic, extra_params = apply_fields_to_topic(keywords, fields)
    # 如果只有字段无关键词，用字段值作为关键词
    if not topic:
        topic = keywords if keywords else raw_query

    all_papers = []
    sources_queried = []
    errors = []

    for source_name in sources:
        source_name_lower = source_name.lower()
        if source_name_lower not in SOURCE_REGISTRY:
            errors.append(f"Unknown source: {source_name}")
            continue

        source_cls = SOURCE_REGISTRY[source_name_lower]
        try:
            source = source_cls()
            year_range = getattr(args, "year_range", None) or None
            # 合并 extra_params 和 year_range
            search_kwargs = {"max_results": max_results}
            if year_range:
                search_kwargs["year_range"] = year_range
            if extra_params.get("author"):
                search_kwargs["author"] = extra_params["author"]
            if extra_params.get("year"):
                search_kwargs["year"] = extra_params["year"]
            
            papers = source.search(topic, **search_kwargs)
            all_papers.extend(papers)
            sources_queried.append(source_name_lower)
        except Exception as e:
            errors.append(f"{source_name}: {e}")

    # 按 DOI 去重
    seen = set()
    deduped = []
    for p in all_papers:
        key = p.get("doi") or p.get("title", "")[:50]
        if key and key not in seen:
            seen.add(key)
            deduped.append(p)

    print(json.dumps({
        "topic": topic,
        "papers": deduped,
        "total": len(deduped),
        "sources_queried": sources_queried,
        "errors": errors,
    }, indent=2, ensure_ascii=False))


def cmd_download(args):
    """从论文 JSON 下载 PDF（遍历链接，无竞速）。"""
    input_file = args.input if args.input else args.paper
    output_dir = args.output_dir or "/tmp/pdfs"
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, encoding="utf-8") as f:
        data = json.load(f)

    papers = data.get("papers", data if isinstance(data, list) else [])
    downloaded = []
    failed = []
    skipped = []

    for p in papers:
        title = p.get("title", "unknown")[:40]
        safe_title = title.replace(" ", "_").replace("/", "_")[:60]
        doi = p.get("doi", "")

        # 按优先级遍历: pdf_url → local_links → links
        links_to_try = []

        if p.get("pdf_url") and p["pdf_url"].startswith("http"):
            links_to_try.append(("pdf_url", p["pdf_url"]))

        local_links = p.get("local_links", [])
        if isinstance(local_links, list):
            for url in local_links:
                if isinstance(url, str) and url.startswith("http"):
                    links_to_try.append(("local_link", url))

        # Sci-Hub CDN 兜底: 有 DOI 时直连 bban.top
        if doi:
            links_to_try.append(("sci_hub_cdn", f"https://sci.bban.top/pdf/{doi}.pdf"))

        links = p.get("links", {})
        if isinstance(links, dict):
            for name, url in links.items():
                if isinstance(url, str) and url.startswith("http"):
                    links_to_try.append((f"link:{name}", url))

        success = False
        for source_name, url in links_to_try:
            try:
                content = smart_download(url, timeout=30)
                if content and verify_pdf(content):
                    out_path = os.path.join(output_dir, f"{safe_title}.pdf")
                    with open(out_path, "wb") as f:
                        f.write(content)
                    p["pdf_local"] = out_path
                    downloaded.append({
                        "title": title,
                        "doi": doi,
                        "path": out_path,
                        "source": source_name,
                        "size": len(content),
                    })
                    success = True
                    break
            except Exception:
                continue

        if not success:
            failed.append({"title": title, "doi": doi, "reason": "no valid link"})

    report = {
        "status": "complete",
        "total": len(papers),
        "downloaded": len(downloaded),
        "failed": failed,
        "files": [d["path"] for d in downloaded],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


def cmd_verify(args):
    """验证论文目录引用完整性。"""
    paper_dir = args.paper_dir
    if not os.path.exists(paper_dir):
        print(json.dumps({"error": f"Directory not found: {paper_dir}"}, indent=2))
        return

    bib_files = [f for f in os.listdir(paper_dir) if f.endswith(".bib")]
    pdf_files = [f for f in os.listdir(paper_dir) if f.endswith(".pdf")]

    print(json.dumps({
        "status": "complete",
        "bib_files": bib_files,
        "pdf_files": pdf_files,
    }, indent=2))


def cmd_pipeline(args):
    """完整管线：搜索 → 下载（遍历链接）→ 报告。"""
    topic = " ".join(args.topic)
    sources = args.sources or DEFAULT_SOURCES
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Search
    results = {}
    for source_name in sources:
        if source_name not in SOURCE_REGISTRY:
            continue
        source_cls = SOURCE_REGISTRY[source_name]
        try:
            source = source_cls()
            papers = source.search(topic, max_results=args.max)
            results[source_name] = papers
        except Exception:
            results[source_name] = []

    # Step 2: Merge and deduplicate
    all_papers = []
    seen = set()
    for papers in results.values():
        for p in papers:
            key = p.get("doi") or p.get("title", "")[:50]
            if key and key not in seen:
                seen.add(key)
                all_papers.append(p)

    # Step 3: Save search results
    with open(os.path.join(output_dir, "search_results.json"), "w", encoding="utf-8") as f:
        json.dump({
            "topic": topic,
            "sources_queried": list(results.keys()),
            "total": len(all_papers),
            "papers": all_papers,
        }, f, ensure_ascii=False, indent=2)

    # Step 4: Download PDFs from collected links
    downloaded = 0
    failed_links = []

    for p in all_papers[:30]:
        title = p.get("title", "unknown")[:40]
        safe_title = title.replace(" ", "_").replace("/", "_")[:60]

        # 遍历链接
        links_to_try = []
        if p.get("pdf_url") and p["pdf_url"].startswith("http"):
            links_to_try.append(("pdf_url", p["pdf_url"]))

        local_links = p.get("local_links", [])
        if isinstance(local_links, list):
            for url in local_links:
                if isinstance(url, str) and url.startswith("http"):
                    links_to_try.append(("local_link", url))

        # Sci-Hub CDN 兜底: 有 DOI 时直连 bban.top
        if doi:
            links_to_try.append(("sci_hub_cdn", f"https://sci.bban.top/pdf/{doi}.pdf"))

        links = p.get("links", {})
        if isinstance(links, dict):
            for name, url in links.items():
                if isinstance(url, str) and url.startswith("http"):
                    links_to_try.append((f"link:{name}", url))

        success = False
        for source_name, url in links_to_try:
            try:
                content = smart_download(url, timeout=30)
                if content and verify_pdf(content):
                    pdf_path = os.path.join(output_dir, f"{safe_title}.pdf")
                    with open(pdf_path, "wb") as f:
                        f.write(content)
                    p["pdf_local"] = pdf_path
                    downloaded += 1
                    success = True
                    break
            except Exception:
                continue

        if not success:
            # MedData 兜底
            doi = p.get("doi", "") or ""
            if doi:
                try:
                    content = download_meddata(doi=doi)
                    if content and verify_pdf(content):
                        pdf_path = os.path.join(output_dir, f"{safe_title}_meddata.pdf")
                        with open(pdf_path, "wb") as f:
                            f.write(content)
                        p["pdf_local"] = pdf_path
                        downloaded += 1
                        success = True
                except Exception:
                    pass

        if not success:
            failed_links.append({"title": title, "doi": doi})

    # Step 5: Report
    with open(os.path.join(output_dir, "pipeline_report.json"), "w", encoding="utf-8") as f:
        json.dump({
            "topic": topic,
            "total_papers": len(all_papers),
            "sources_queried": list(results.keys()),
            "pdfs_downloaded": downloaded,
            "failed_links": failed_links,
        }, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "status": "complete",
        "topic": topic,
        "total_papers": len(all_papers),
        "sources_queried": list(results.keys()),
        "pdfs_downloaded": downloaded,
        "failed_links": len(failed_links),
        "search_results": os.path.join(output_dir, "search_results.json"),
        "report": os.path.join(output_dir, "pipeline_report.json"),
    }, indent=2))


def cmd_test(args):
    """连通性测试。"""
    print(json.dumps(run_test(), indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="文献检索统一入口")
    subparsers = parser.add_subparsers(dest="command")

    # search
    sp = subparsers.add_parser("search", help="多源检索")
    sp.add_argument("topic", nargs="+", help="搜索主题")
    sp.add_argument("--sources", nargs="+", help="搜索源列表")
    sp.add_argument("--max", type=int, default=10, help="最大结果数")
    sp.add_argument("--year-range", help="年份范围，如 2020-2024")
    sp.set_defaults(func=cmd_search)

    # download (from paper JSON)
    sp = subparsers.add_parser("download", help="从论文 JSON 下载 PDF")
    sp.add_argument("--input", "-i", help="论文 JSON 文件")
    sp.add_argument("--paper", "-p", help="论文 JSON 文件（alias）")
    sp.add_argument("--output-dir", "-d", help="输出目录")
    sp.set_defaults(func=cmd_download)

    # verify
    sp = subparsers.add_parser("verify", help="验证引用")
    sp.add_argument("--paper-dir", required=True, help="论文目录")
    sp.set_defaults(func=cmd_verify)

    # pipeline
    sp = subparsers.add_parser("pipeline", help="完整管线")
    sp.add_argument("topic", nargs="+", help="搜索主题")
    sp.add_argument("--sources", nargs="+", help="搜索源")
    sp.add_argument("--max", type=int, default=10)
    sp.add_argument("--output-dir", "-d", required=True, help="输出目录")
    sp.set_defaults(func=cmd_pipeline)

    # test
    sp = subparsers.add_parser("test", help="连通性测试")
    sp.set_defaults(func=cmd_test)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()