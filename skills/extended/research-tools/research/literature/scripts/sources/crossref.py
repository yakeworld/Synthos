"""
数据源：CrossRef（元数据补充，不用于主要检索）
"""
import os
import json
import urllib.parse
import urllib.request
from typing import Optional


class CrossRef:
    """CrossRef REST API 封装。
    
    主要用于 DOI 元数据补入和 DOI 验证。
    
    统一接口:
        search_by_title(title: str) -> dict
        verify_doi(doi: str) -> dict
    """
    
    BASE_URL = "https://api.crossref.org/works"
    
    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """通过标题检索。"""
        return self.search_by_title(topic, max_results)
    
    def search_by_title(self, title: str, max_results: int = 5) -> list[dict]:
        """通过标题检索。"""
        params = {
            "query.title": title[:100],  # Crossref 限制
            "rows": str(min(max_results, 10)),
            "mailto": "yakeworld@wmu.edu.cn",
        }
        query_string = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
        
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
        """验证 DOI 并获取元数据。"""
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
        """将 Crossref 数据转换为统一格式。"""
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
        
        # 收集 PDF 链接：URL + DOI 重定向
        doi = item.get("DOI", "")
        links: dict[str, str] = {}
        if doi:
            links["doi"] = f"https://doi.org/{doi}"
            links["crossref"] = f"https://api.crossref.org/works/{doi}"
        
        # CrossRef 本身没有 PDF 直链，但 open_access 字段有 OA 来源
        oa = item.get("open-access", {})
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
            "pdf_url": "",
            "local_links": [],
            "links": links,
            "citation_count": item.get("is-referenced-by-count", 0),
            "venue": container,
            "provenance": f"source=crossref, doi={doi}",
        }