#!/usr/bin/env python3
"""数据源：OpenAlex

职责: 通过 OpenAlex API 检索开放学术图谱，覆盖所有学科。
设计决策:
- 无需 API key，公共 API
- 搜索时按引用数排序（sort=cited_by_count:desc），优先高质量论文
- 默认 from_publication_date=2020，避免旧文献淹没
- best_oa_location 自动获取 OA PDF 链接
限制:
- 作者信息通过 authorships 间接获取（非扁平作者列表）
- 不返回 PDF 直链（仅 OA 链接，可能跳转到 publisher 页面）
- 搜索结果有延迟（非实时索引）

API 协议:
  GET https://api.openalex.org/works?search={query}&per_page=N&sort=cited_by_count:desc&filter=from_publication_date:2020-01-01
  认证: 无
  响应: {"results": [{...}], "meta": {"count": N}}

依赖: urllib (stdlib)
"""
import json
import urllib.request
import urllib.parse
from typing import Optional


class OpenAlex:
    """OpenAlex API 封装。

    开放学术图谱，无需 API key。覆盖 2500+ 万论文，所有学科。

    搜索策略:
      - 关键词搜索 → 按引用数降序排列 → 过滤 2020 年后
      - best_oa_location 自动获取 OA PDF
      - authorships → author.display_name → 作者列表

    参数映射:
      search() 输入: topic (str), max_results (int), year_range (str|None)
        → API: search, per_page, filter (from_publication_date/to_publication_date), sort
      search_by_doi(): 未实现（OpenAlex 支持 /works/DOI 端点，但未封装）

    数据流:
      用户查询 → OpenAlex works API → 解析 results
      → 提取 title, authors (via authorships), year (via authorships.pub_date)
      → best_oa_location → pdf_url
      → 标准化纸
    """

    BASE_URL = "https://api.openalex.org"

    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """检索 OpenAlex 文献。

        参数:
            topic: 搜索关键词
            max_results: 最大结果数（API 上限 200，安全值 20）
            year_range: 年份范围，格式 "2020-2024"
        返回:
            list[dict]: 标准化论文列表，按引用数降序。
            注意：OpenAlex 的 abstract 是 inverted_index 格式（{word: position}），
            需调用方自行反转为可读文本。
        异常:
            不抛异常。网络错误返回 []。
        原理:
            - OpenAlex 是所有学科的广谱覆盖源，特别适合交叉学科搜索
            - cited_by_count:desc 排序确保先返回高影响力论文
            - from_publication_date:2020 过滤避免低质量/过时论文
            - 当 S2/PubMed 无结果时，OpenAlex 是很好的补充源
        示例:
            >>> o = OpenAlex()
            >>> papers = o.search("brain computer interface", max_results=5)
            >>> len(papers) <= 5
            True
        """
        params = {
            "search": topic,
            "per_page": str(min(max_results, 20)),
            "filter": "from_publication_date:2020-01-01",
            "sort": "cited_by_count:desc",
        }
        if year_range and "-" in year_range:
            start, end = year_range.split("-", 1)
            params["filter"] = (
                f"from_publication_date:{start.strip()}"
                f",to_publication_date:{end.strip()}-12-31"
            )

        query_string = "&".join(
            f"{k}={urllib.parse.quote(v) if isinstance(v, str) else v}"
            for k, v in params.items()
        )
        url = f"{self.BASE_URL}/works?{query_string}"

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Synthos-Literature/1.0",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())

            results = data.get("results", [])
            papers = []
            for r in results[:max_results]:
                paper = self._to_paper(r)
                if paper:
                    papers.append(paper)
            return papers

        except Exception:
            return []

    def _to_paper(self, r: dict) -> Optional[dict]:
        """转换 OpenAlex 记录为标准化格式。

        字段映射:
          r.authorships[].author.display_name → authors (按引用数排序)
          r.authorships[].publication_date → year
          r.doi → doi (去除 https://doi.org/ 前缀)
          r.best_oa_location.pdf_url → pdf_url
          r.abstract_inverted_index → abstract (inverted_index 格式)
          r.cited_by_count → citation_count

        返回:
            dict or None
        """
        title = r.get("title", "")
        if not title:
            return None

        # OpenAlex 作者通过 authorships 间接获取
        # authorships[i].author.display_name — 注意不是 authorships[i].display_name
        authors = []
        for ashp in (r.get("authorships") or []):
            if isinstance(ashp, dict):
                author_obj = ashp.get("author") or {}
                name = author_obj.get("display_name", "")
                if name:
                    authors.append(name)

        first_authorship = r.get("authorships", [{}])[0] if r.get("authorships") else {}
        pub_date = first_authorship.get("publication_date", "")

        doi = r.get("doi", "")
        if doi and doi.startswith("https://doi.org/"):
            doi = doi.replace("https://doi.org/", "")

        # 构建 links 字典
        links: dict[str, str] = {
            "openalex": f"https://openalex.org/{r.get('id', '')}",
        }
        oa = r.get("open_access", {})
        pdf_url = ""
        if isinstance(oa, dict):
            oa_url = oa.get("oa_url", "")
            if oa_url:
                links["oa"] = oa_url
            # best_oa_location 可能在 open_access 内或顶级
            boa = oa.get("best_oa_location") or r.get("best_oa_location")
            if isinstance(boa, dict):
                pdf_link = boa.get("pdf_url", "")
                if pdf_link:
                    pdf_url = pdf_link
                    links["oa_pdf"] = pdf_link

        if doi:
            links["doi"] = f"https://doi.org/{doi}"

        # venue/host_organization 获取期刊名
        host = first_authorship.get("host_organization_name", "")
        if not host:
            host = (
                r.get("primary_location", {})
                .get("source", {})
                .get("display_name", "")
            )

        return {
            "title": title,
            "authors": authors,
            "year": int(pub_date.split("-")[0]) if pub_date else None,
            "source": "openalex",
            "doi": doi,
            "abstract": r.get("abstract_inverted_index", {}),
            "url": r.get("doi", "") or r.get("open_access", {}).get("oa_url", ""),
            "pdf_url": pdf_url,
            "local_links": [],
            "links": links,
            "citation_count": r.get("cited_by_count", 0),
            "venue": host,
            "provenance": f"source=openalex, doi={doi}",
        }
