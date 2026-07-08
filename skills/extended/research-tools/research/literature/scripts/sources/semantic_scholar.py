"""
数据源：Semantic Scholar
直接读取 ~/.bashrc 获取 API key。
搜索时收集所有 PDF 链接（openAccessPdf + local_links + publisher links）。
"""
import os
import json
import urllib.parse
import urllib.request
from typing import Optional


class SemanticScholar:
    """Semantic Scholar API v1 封装。
    
    搜索返回的 paper dict 包含完整的 PDF 链接集：
    - pdf_url: 免费 PDF 直链（openAccessPdf）
    - local_links: 免费 CDN 直链数组
    - links: 所有可用链接（含 publisher 页面、DOI 重定向等）
    """
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    # S2 API keys — 主备双 key，优先主 key
    API_KEYS=[os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "").strip().strip('"').strip("'"),
              os.environ.get("S2_FALLBACK_KEY", "").strip().strip('"').strip("'")
    ]  # 过滤空值
    API_KEYS=[k for k in API_KEYS if k]
    
    def __init__(self, api_key_index: int = 0):
        self._key_index = api_key_index
        self.api_key = self.API_KEYS[self._key_index % len(self.API_KEYS)] if self.API_KEYS else ""
    
    def _try_next_key(self):
        """失败时切换到下一个 key。"""
        if len(self.API_KEYS) > 1:
            self._key_index = (self._key_index + 1) % len(self.API_KEYS)
            self.api_key = self.API_KEYS[self._key_index % len(self.API_KEYS)]
            return True
        return False
    
    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """检索文献。收集所有 PDF 链接。"""
        if not self.api_key:
            return []
        
        url = f"{self.BASE_URL}/paper/search"
        params = {
            "query": topic,
            "limit": str(min(max_results, 20)),
            "fields": "title,authors,year,openAccessPdf,externalIds,venue,citationCount,tldr,abstract,publicationTypes,urls,pdfUrls",
        }
        if year_range:
            if "-" in year_range:
                start, end = year_range.split("-", 1)
                params["from_year"] = start.strip()
                params["to_year"] = end.strip()
            else:
                params["from_year"] = year_range.replace("since:", "")
        
        query_string = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
        full_url = f"{url}?{query_string}"
        
        req = urllib.request.Request(full_url, headers={
            "x-api-key": self.api_key,
            "User-Agent": "Synthos-Literature/1.0",
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
            if self._try_next_key():
                return self.search(topic, max_results, year_range)
            return []
    
    def search_by_doi(self, doi: str) -> Optional[dict]:
        """通过 DOI 检索单篇文献。"""
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
            if self._try_next_key():
                return self.search_by_doi(doi)
            return None
    
    def _to_paper(self, data: dict) -> Optional[dict]:
        """将 S2 原始数据转换为统一 Paper 格式，包含完整 PDF 链接集。"""
        if not data:
            return None
        
        title = data.get("title", "")
        if not title:
            return None
        
        external_ids = data.get("externalIds", {})
        
        # 作者
        authors = []
        year = data.get("year")
        for a in data.get("authors", []):
            if isinstance(a, dict):
                name = a.get("name", "")
            elif isinstance(a, str):
                name = a
            else:
                name = str(a)
            if name:
                authors.append(name)
        
        # 收集所有 PDF 链接
        pdf_url = ""
        local_links = []
        links = {}
        
        # 1. openAccessPdf — 最优先
        oa_pdf = data.get("openAccessPdf")
        if isinstance(oa_pdf, dict):
            url_val = oa_pdf.get("url", "")
            if url_val:
                pdf_url = url_val
                links["openAccessPdf"] = url_val
        
        # 2. pdfUrls — S2 提供的 PDF URL 列表
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
                    links[f"pdfUrl"] = item
                    if not pdf_url:
                        pdf_url = item
        
        # 3. urls — S2 收集的论文相关 URL（含 PMC、GitHub、项目页等）
        urls = data.get("urls", [])
        if isinstance(urls, list):
            for url_val in urls:
                if isinstance(url_val, str) and url_val.startswith("http"):
                    links[f"url"] = url_val
        
        # 4. 构建 local_links（仅含 PDF 直链）
        if pdf_url:
            local_links.append(pdf_url)
        for k, v in links.items():
            if v != pdf_url and (v.endswith(".pdf") or "/pdf" in v.lower()):
                local_links.append(v)
        
        return {
            "title": title,
            "authors": authors,
            "year": year,
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