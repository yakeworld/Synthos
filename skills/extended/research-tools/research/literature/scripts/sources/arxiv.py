#!/usr/bin/env python3
"""数据源：arXiv

职责: 检索预印本文献（CS、物理、数学、EE 等），提供直接 PDF 下载。
设计决策:
- 无 API key，公共 API，有速率限制（3 req/秒）
- XML 解析（非 JSON），使用正则而非 XML 解析器（arXiv XML 命名空间复杂）
- 直接 PDF 链接: arxiv.org/pdf/{id}.pdf（100% 可用）
- 无引用数、无作者详情（仅姓名列表）
限制:
- 仅预印本，非同行评审出版物
- 无 abstract 截断（500 字符）
- 无 citation_count
- XML 解析可能因 arXiv 格式变化而失效

API 协议:
  GET https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={N}
  认证: 无
  响应: Atom XML

依赖: re, urllib (stdlib)
"""
import re
import urllib.request
from typing import Optional


class ArXiv:
    """arXiv API 封装。

    无 API key，有速率限制（3 req/秒）。

    搜索策略:
      - 空格替换为 +（arXiv API 要求，非标准 URL 编码）
      - search_query=all:{query} 在所有字段中搜索
      - max_results 上限 50

    参数映射:
      search() 输入: topic (str), max_results (int), year_range (str|None)
        → API: search_query=all:{topic}, max_results
        year_range 未使用（arXiv 不支持年份过滤）

    数据流:
      用户查询 → arXiv API → Atom XML
      → 正则提取: title, summary, authors, published, arxiv_id, DOI, PDF URL
      → 标准化纸（arXiv 有 100% 可用 PDF 链接）

    arXiv ID 格式: "2301.12345" → arxiv.org/abs/2301.12345
    PDF 链接: arxiv.org/pdf/2301.12345.pdf
    """

    BASE_URL = "https://export.arxiv.org/api/query"

    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """检索 arXiv 文献。arXiv 使用 + 连接关键词。

        参数:
            topic: 搜索关键词
            max_results: 最大结果数（API 上限 50，超出则截断）
            year_range: 未使用（arXiv API 不支持年份过滤）
        返回:
            list[dict]: 标准化论文列表。
            注意: arXiv 的 title 和 abstract 可能含 LaTeX 标记。
        异常:
            不抛异常。网络错误返回 []。
        原理:
            - arXiv 是 CS/EE/物理预印本平台，所有论文有免费 PDF
            - XML 解析使用正则而非 etree，因为 arXiv Atom XML 包含
              混合内容（text + CDATA + 嵌套标签），正则更可靠
            - DOI 可能不存在（预印本可能无正式 DOI）
            - 标题中的 LaTeX 格式（如 $O(n)$）需调用方自行清理
        示例:
            >>> a = ArXiv()
            >>> papers = a.search("transformer attention", max_results=5)
            >>> len(papers) <= 5
            True
        """
        # arXiv API 要求空格替换为 +，非标准 URL 编码
        query = topic.replace(" ", "+")

        params = f"search_query=all:{query}&start=0&max_results={min(max_results, 50)}"
        url = f"{self.BASE_URL}?{params}"

        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Synthos-Literature/1.0",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode()

            papers = []
            entries = content.split("<entry>")
            for entry in entries[1:]:  # 跳过第一个空分割
                title_m = re.search(r"<title>(.*?)</title>", entry)
                if not title_m:
                    continue

                title_text = title_m.group(1).strip()
                if not title_text:
                    continue

                # 摘要: 清理空白
                summary_m = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
                summary = re.sub(r"\s+", " ", summary_m.group(1).strip()) if summary_m else ""

                # 作者列表
                authors_m = re.findall(r"<author>\s*<name>(.*?)</name>", entry)

                # DOI（可能不存在）
                doi_m = re.search(r'10\.d{4,}/[^\s"]+', entry)

                # 发表年份
                published_m = re.search(r"<published>(.*?)</published>", entry)
                year = None
                if published_m:
                    try:
                        year = int(published_m.group(1)[:4])
                    except Exception:
                        pass

                # arXiv ID
                link_m = re.search(r"<id>https?://arxiv\.org/abs/(.*?)</id>", entry)
                arxiv_id = link_m.group(1) if link_m else ""

                # 提取 PDF URL（从 href 属性）
                pdf_url = ""
                if "pdf/" in entry:
                    start = entry.rfind("href=")
                    if start >= 0:
                        href_val = entry[start+5:]
                        if "'" in href_val or '"' in href_val:
                            delimiter = "'" if "'" in href_val else '"'
                            href_val = href_val.split(delimiter)[1]
                            if ".pdf" in href_val:
                                pdf_url = href_val

                doi = doi_m.group(0) if doi_m else ""

                links: dict[str, str] = {
                    "abs": f"https://arxiv.org/abs/{arxiv_id}",
                    "pdf": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                    "html": f"https://arxiv.org/html/{arxiv_id}",
                    "source": f"https://arxiv.org/abs/{arxiv_id}",
                }
                if doi:
                    links["doi"] = f"https://doi.org/{doi}"

                if pdf_url:
                    links["direct_pdf"] = pdf_url

                paper = {
                    "title": title_text,
                    "authors": authors_m,
                    "year": year,
                    "source": "arxiv",
                    "doi": doi,
                    "abstract": summary[:500],
                    "url": f"https://arxiv.org/abs/{arxiv_id}",
                    "pdf_url": pdf_url,
                    "local_links": [pdf_url] if pdf_url else [],
                    "links": links,
                    "citation_count": 0,
                    "venue": "arXiv preprint",
                    "provenance": f"source=arxiv, id={arxiv_id}",
                }
                papers.append(paper)

            return papers

        except Exception:
            return []
