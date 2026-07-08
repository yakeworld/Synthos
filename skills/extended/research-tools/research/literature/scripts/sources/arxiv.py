"""
数据源：arXiv
"""
import re
import urllib.request
from typing import Optional


class ArXiv:
    """arXiv API 封装。https://export.arxiv.org/api
    
    无 API key，有速率限制。
    
    统一接口:
        search(topic: str, max_results: int = 10) -> list[dict]
    """
    
    BASE_URL = "https://export.arxiv.org/api/query"
    
    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """检索 arXiv 文献。arXiv 使用 + 连接关键词。"""
        # 不需要 urllib.parse.quote，直接替换空格为+
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
            entries = content.split('<entry>')
            for entry in entries[1:]:
                title_m = re.search(r'<title>(.*?)</title>', entry)
                if not title_m:
                    continue
                
                title_text = title_m.group(1).strip()
                if not title_text:
                    continue
                
                summary_m = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
                summary = re.sub(r'\s+', ' ', summary_m.group(1).strip()) if summary_m else ""
                
                authors_m = re.findall(r'<author>\s*<name>(.*?)</name>', entry)
                
                doi_m = re.search(r'10\.\d{4,}/[^\s"]+', entry)
                
                published_m = re.search(r'<published>(.*?)</published>', entry)
                year = None
                if published_m:
                    try:
                        year = int(published_m.group(1)[:4])
                    except:
                        pass
                
                link_m = re.search(r'<id>https?://arxiv\.org/abs/(.*?)</id>', entry)
                arxiv_id = link_m.group(1) if link_m else ""
                
                # Extract PDF URL
                pdf_url = ""
                if "pdf/" in entry:
                    start = entry.rfind("href=")
                    if start >= 0:
                        href_val = entry[start+5:]
                        if '"' in href_val:
                            href_val = href_val.split('"')[1]
                            if ".pdf" in href_val:
                                pdf_url = href_val
                
                doi = doi_m.group(0) if doi_m else ""
                
                # arXiv 有直接 PDF 链接
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