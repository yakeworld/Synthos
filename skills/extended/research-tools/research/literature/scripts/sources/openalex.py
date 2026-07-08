"""
数据源：OpenAlex
"""
import json
import urllib.request
import urllib.parse
from typing import Optional


class OpenAlex:
    """OpenAlex API 封装。https://api.openalex.org
    
    开放学术图谱，无需 API key。
    
    统一接口:
        search(topic: str, max_results: int = 10) -> list[dict]
    """
    
    BASE_URL = "https://api.openalex.org"
    
    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """检索 OpenAlex 文献。"""
        params = {
            "search": topic,
            "per_page": str(min(max_results, 20)),
            "filter": "from_publication_date:2020-01-01",
            "sort": "cited_by_count:desc",
        }
        if year_range and "-" in year_range:
            start, end = year_range.split("-", 1)
            params["filter"] = f"from_publication_date:{start.strip()},to_publication_date:{end.strip()}-12-31"
        
        query_string = "&".join(f"{k}={urllib.parse.quote(v) if isinstance(v, str) else v}" for k, v in params.items())
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
        """转换 OpenAlex 记录。"""
        title = r.get("title", "")
        if not title:
            return None
        
        # OpenAlex authorships: authorships[i].author.display_name (NOT authorships[i].display_name)
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
            # best_oa_location can be in open_access OR at top level
            boa = oa.get("best_oa_location") or r.get("best_oa_location")
            if isinstance(boa, dict):
                pdf_link = boa.get("pdf_url", "")
                if pdf_link:
                    pdf_url = pdf_link
                    links["oa_pdf"] = pdf_link
        
        if doi:
            links["doi"] = f"https://doi.org/{doi}"
        
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
            "venue": first_authorship.get("host_organization_name", "") or r.get("primary_location", {}).get("source", {}).get("display_name", ""),
            "provenance": f"source=openalex, doi={doi}",
        }