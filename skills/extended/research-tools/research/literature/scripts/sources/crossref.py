#!/usr/bin/env python3
"""数据源：CrossRef（元数据补充，不用于主要检索）

职责: 通过 CrossRef REST API 补充论文元数据和 DOI 验证。
设计决策:
- 不用于主要检索（结果质量低、无 PDF 链接），主要作为元数据补入源
- 通过 search_by_title 补充 DOI/abstract/citation_count
- 通过 verify_doi 验证 DOI 有效性
- 联系信息必须包含（CrossRef 要求，否则可能被限流）
限制:
- 无 PDF 直链（Open Access 论文有 OA PDF 链接）
- 搜索结果质量不稳定（标题搜索 vs 全文搜索）
- 某些期刊（如 Springer）的元数据不完整

API 协议:
  GET https://api.crossref.org/works?query.title={title}&rows={N}&mailto={email}
  GET https://api.crossref.org/works/{doi}
  认证: 无（但必须包含 mailto）
  响应: {"message": {"items": [{...}]}}

依赖: urllib (stdlib)
"""
import os
import json
import urllib.parse
import urllib.request
from typing import Optional


class CrossRef:
    """CrossRef REST API 封装。

    主要用于 DOI 元数据补入和 DOI 验证。

    搜索策略:
      - search_by_title: 通过标题前缀匹配（CrossRef 限制 100 字符）
      - verify_doi: 通过 DOI 精确获取元数据

    参数映射:
      search_by_title() 输入: title (str), max_results (int)
        → API: query.title, rows, mailto
      verify_doi() 输入: doi (str)
        → API URL: /works/{doi}

    数据流:
      用户查询 → search_by_title → 提取 title, authors, DOI, venue, year
      → 标准化纸（无 PDF 链接，仅有 DOI 页面和可能的 OA PDF）

    联系邮箱: yakeworld@wmu.edu.cn（CrossRef 要求，用于 abuse 联系）
    """

    BASE_URL = "https://api.crossref.org/works"

    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """通过标题检索。

        注意: 这是 search_by_title 的别名。CrossRef 不推荐作为主要检索源。
        建议用法: 用 S2/PubMed/OpenAlex 检索，用 CrossRef 补充 DOI 和引用数。

        参数:
            topic: 搜索关键词（作为标题查询）
            max_results: 最大结果数（API 上限 10）
            year_range: 未使用
        返回:
            list[dict]: 标准化论文列表（无 PDF 链接）。
        """
        return self.search_by_title(topic, max_results)

    def search_by_title(self, title: str, max_results: int = 5) -> list[dict]:
        """通过标题检索。

        参数:
            title: 论文标题（自动截断至 100 字符，CrossRef API 限制）
            max_results: 最大结果数（API 上限 10）
        返回:
            list[dict]: 标准化论文列表。
        异常:
            不抛异常。网络错误返回 []。
        """
        params = {
            "query.title": title[:100],  # Crossref 限制
            "rows": str(min(max_results, 10)),
            "mailto": "yakeworld@wmu.edu.cn",
        }
        query_string = "&".join(
            f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()
        )

        try:
            req = urllib.request.Request(
                f"{self.BASE_URL}?{query_string}",
                headers={"User-Agent": "Synthos-Literature/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            items = data.get("message", {}).get("items", [])
            papers = []
            for item in items[:max_results]:
                paper = self._to_paper(item)
                if paper:
                    papers.append(paper)
            return papers

        except Exception:
            return []

    def verify_doi(self, doi: str) -> Optional[dict]:
        """验证 DOI 并获取元数据。

        参数:
            doi: DOI 字符串（如 "10.1038/s41586-019-1799-6"）
        返回:
            dict or None: 标准化论文或 None（DOI 无效）
        原理:
            - CrossRef 的 /works/{doi} 端点返回最准确的元数据
            - 此方法常用于 DOI 验证和补充
        """
        url = f"{self.BASE_URL}/{doi}"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Synthos-Literature/1.0",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            item = data.get("message", {})
            if item:
                return self._to_paper(item)
            return None

        except Exception:
            return None

    def _to_paper(self, item: dict) -> Optional[dict]:
        """将 Crossref 数据转换为统一格式。

        字段映射:
          item.title[0] → title
          item.author[].given + item.author[].family → authors
          item.container-title[0] → venue
          item.published-print.date-parts → year
          item.DOI → doi
          item.is-referenced-by-count → citation_count
          item.open-access.pdf_url → pdf_url (仅 OA 论文)

        返回:
            dict or None
        """
        title = item.get("title", [""])[0] if isinstance(item.get("title"), list) else item.get("title", "")
        if not title:
            return None

        authors = []
        for a in item.get("author", []):
            family = a.get("family", "")
            given = a.get("given", "")
            name = f"{given} {family}".strip() if given else family
            if name:
                authors.append(name)

        container = item.get("container-title", [""])[0] if isinstance(item.get("container-title"), list) else item.get("container-title", "")

        pub_date = item.get("published-print", {}) or item.get("published-online", {})
        year = None
        if isinstance(pub_date, dict):
            year = pub_date.get("date-parts", [[]])[0][0] if pub_date.get("date-parts") else None

        # 收集 PDF 链接
        doi = item.get("DOI", "")
        links: dict[str, str] = {}
        if doi:
            links["doi"] = f"https://doi.org/{doi}"
            links["crossref"] = f"https://api.crossref.org/works/{doi}"

        # CrossRef 本身没有 PDF 直链，但 open_access 字段有 OA 来源
        oa = item.get("open-access", {})
        pdf_url = ""
        if isinstance(oa, dict):
            pdf_url = oa.get("pdf_url", "")
            if pdf_url:
                links["oa_pdf"] = pdf_url

        return {
            "title": title,
            "authors": authors,
            "year": year,
            "source": "crossref",
            "doi": doi,
            "abstract": item.get("abstract", ""),
            "url": f"https://doi.org/{doi}",
            "pdf_url": pdf_url,
            "local_links": [pdf_url] if pdf_url else [],
            "links": links,
            "citation_count": item.get("is-referenced-by-count", 0),
            "venue": container,
            "provenance": f"source=crossref, doi={doi}",
        }
