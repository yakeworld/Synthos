#!/usr/bin/env python3
"""数据源：Semantic Scholar

职责: 通过 S2 Graph API v1 检索英文学术文献，返回包含完整 PDF 链接集的论文数据。
设计决策: 
- 单 key 认证（SEMANTIC_SCHOLAR_API_KEY 环境变量）
- 搜索时一次性拉取 openAccessPdf + pdfUrls + urls + externalIds，下载时零额外请求
- 不用于 DOI 精确检索（search_by_doi 仅作兜底）
限制:
- 必须设置 SEMANTIC_SCHOLAR_API_KEY，否则返回空列表
- S2 返回的 PDF 链接可能过期，需要在 download 层处理
- rate limit: 1000 req/小时 per key

API 协议:
  GET https://api.semanticscholar.org/graph/v1/paper/search
  GET https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}
  认证: x-api-key header
  响应: {data: [{...}]}

依赖: urllib (stdlib)
"""
import os
import json
import urllib.parse
import urllib.request
from typing import Optional


class SemanticScholar:
    """Semantic Scholar API v1 封装。

    搜索返回的 paper dict 包含完整的 PDF 链接集：
    - pdf_url: 免费 PDF 直链（openAccessPdf 优先）
    - local_links: 免费 CDN 直链数组
    - links: 所有可用链接（含 publisher 页面、DOI 重定向等）

    参数映射:
      search() 输入: topic (str), max_results (int), year_range (str|None)
        → API 参数: query, limit, from_year, to_year, fields
      search_by_doi() 输入: doi (str)
        → API URL: /paper/DOI:{doi}

    数据流:
      用户查询 → S2 API → 解析 openAccessPdf/pdfUrls/urls/externalIds
      → 构建 {pdf_url, local_links, links}  → 返回标准化纸
    """

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    # S2 API key — 单 key（SEMANTIC_SCHOLAR_API_KEY 环境变量）
    API_KEYS = [
        os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "").strip().strip('"').strip("'")
    ]

    def __init__(self, api_key_index: int = 0):
        self._key_index = api_key_index
        self.api_key = self.API_KEYS[self._key_index % len(self.API_KEYS)] if self.API_KEYS else ""

    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """检索文献。收集所有 PDF 链接。

        参数:
            topic: 搜索关键词（支持多词空格分隔）
            max_results: 每源最大结果数（API 上限 20，超出则截断）
            year_range: 年份范围，格式 "2020-2024" 或 "2020"（仅返回 2020 年后）
        返回:
            list[dict]: 标准化论文列表，每项包含:
                title, authors, year, doi, abstract, url, pdf_url,
                local_links, links, citation_count, venue, source
        异常:
            不抛异常。网络错误、key 失效、空结果均返回空列表 []。
            这是设计选择：单个源失败不应阻断管线。
        原理:
            - S2 是综合性最强的英文学术搜索源，覆盖 PubMed、CrossRef、arXiv
            - openAccessPdf 字段优先，因为 S2 的 PDF 直链通常有效
            - pdfUrls 包含多个 CDN 链接（ResearchGate 等）
            - 去重由 cmd_search 按 DOI 处理，此处不重复
        示例:
            >>> s = SemanticScholar()
            >>> papers = s.search("vestibular neuritis", max_results=5)
            >>> len(papers) <= 5
            True
        """
        if not self.api_key:
            return []

        # 参数映射:
        #   topic → query (S2 搜索参数)
        #   max_results → limit (API 上限 20)
        #   year_range → from_year/to_year
        url = f"{self.BASE_URL}/paper/search"
        params = {
            "query": topic,
            "limit": str(min(max_results, 20)),  # S2 硬性上限 20
            "fields": (
                "title,authors,year,openAccessPdf,externalIds,venue,"
                "citationCount,tldr,abstract,publicationTypes,urls,pdfUrls"
            ),
        }
        if year_range:
            if "-" in year_range:
                start, end = year_range.split("-", 1)
                params["from_year"] = start.strip()
                params["to_year"] = end.strip()
            else:
                params["from_year"] = year_range.replace("since:", "")

        query_string = "&".join(
            f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()
        )
        full_url = f"{url}?{query_string}"

        req = urllib.request.Request(full_url, headers={
            "x-api-key": self.api_key,
            "User-Agent": "Synthos-Literature/1.0",  # S2 要求 UA 标识
        })

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())

            papers = []
            for p in data.get("data", []):
                paper = self._to_paper(p)
                if paper:
                    papers.append(paper)
            return papers

        except Exception:
            # 任何异常都直接返回空列表，不重试（单 key，无备用）
            return []

    def search_by_doi(self, doi: str) -> Optional[dict]:
        """通过 DOI 检索单篇文献。

        参数:
            doi: DOI 字符串（如 "10.1038/s41586-019-1799-6"）
        返回:
            dict or None: 标准化论文或 None（DOI 不存在/网络错误）
        原理:
            - S2 的 /paper/DOI:{doi} 端点是 S2 内部 ID，非标准 DOI
            - 此方法仅用作 DOI 精确检索兜底，search() 是主力
        """
        if not self.api_key:
            return None

        url = f"{self.BASE_URL}/paper/DOI:{doi}"
        req = urllib.request.Request(url, headers={
            "x-api-key": self.api_key,
            "User-Agent": "Synthos-Literature/1.0",
        })

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
            return self._to_paper(data) if data else None
        except Exception:
            return None

    def _to_paper(self, data: dict) -> Optional[dict]:
        """将 S2 原始数据转换为统一 Paper 格式，包含完整 PDF 链接集。

        字段映射:
          S2 openAccessPdf → pdf_url (最优先免费 PDF 直链)
          S2 pdfUrls → local_links + links (免费 CDN 直链)
          S2 urls → links (论文相关 URL：PMC, GitHub, 项目页等)
          S2 externalIds → doi, arxiv_id
          S2 tldr/abstract → abstract

        返回:
            dict 或 None (title 为空时过滤)
        """
        if not data:
            return None

        title = data.get("title", "")
        if not title:
            return None

        external_ids = data.get("externalIds", {})

        # 作者：S2 返回两种格式 — list of str 或 list of dict
        # str 格式: ["John Doe", "Jane Smith"]
        # dict 格式: [{"name": "John Doe", "authorId": "..."}]
        authors = []
        for a in data.get("authors", []):
            if isinstance(a, dict):
                name = a.get("name", "")
            elif isinstance(a, str):
                name = a
            else:
                name = str(a)
            if name:
                authors.append(name)

        # 收集所有 PDF 链接（按优先级排序）
        pdf_url = ""
        local_links = []
        links = {}

        # 1. openAccessPdf — 最优先，S2 直接提供免费 PDF 直链
        oa_pdf = data.get("openAccessPdf")
        if isinstance(oa_pdf, dict):
            url_val = oa_pdf.get("url", "")
            if url_val:
                pdf_url = url_val
                links["openAccessPdf"] = url_val

        # 2. pdfUrls — S2 收集的 PDF URL 列表（可能含 ResearchGate 等）
        #    每项有 {url, name, quality}，quality 为 "LAYOUT" 或 "TIGHT"
        pdf_urls = data.get("pdfUrls", [])
        if isinstance(pdf_urls, list):
            for item in pdf_urls:
                if isinstance(item, dict):
                    url_val = item.get("url", "")
                    if url_val:
                        source = item.get("name", "") or "pdfUrl"
                        links[f"pdfUrl({source})"] = url_val
                        if not pdf_url:
                            pdf_url = url_val
                elif isinstance(item, str) and item.startswith("http"):
                    links["pdfUrl"] = item
                    if not pdf_url:
                        pdf_url = item

        # 3. urls — S2 收集的论文相关 URL（含 PMC、GitHub、项目页等）
        #    注意：这些通常是 HTML 页面，非 PDF 直链
        urls = data.get("urls", [])
        if isinstance(urls, list):
            for url_val in urls:
                if isinstance(url_val, str) and url_val.startswith("http"):
                    links["url"] = url_val

        # 4. 构建 local_links（仅含 PDF 直链，供 download 层遍历）
        if pdf_url:
            local_links.append(pdf_url)
        for k, v in links.items():
            if v != pdf_url and (v.endswith(".pdf") or "/pdf" in v.lower()):
                local_links.append(v)

        return {
            "title": title,
            "authors": authors,
            "year": data.get("year"),
            "source": "semantic_scholar",
            "doi": external_ids.get("DOI", ""),
            "arxiv_id": external_ids.get("arXiv", ""),
            "abstract": data.get("abstract", "") or data.get("tldr", ""),
            "url": f"https://www.semanticscholar.org/paper/{data.get('paperId', '')}",
            "pdf_url": pdf_url,
            "local_links": local_links,
            "links": links,
            "citation_count": data.get("citationCount", 0),
            "venue": data.get("venue", ""),
            "provenance": "source=semantic_scholar",
        }