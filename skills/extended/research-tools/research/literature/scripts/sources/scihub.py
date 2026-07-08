"""
数据源：Sci-Hub（用于获取全文下载地址）
直接从 Sci-Hub 获取 PDF 直链，作为文献检索的补充源。
"""
import os
import json
import urllib.request
import urllib.parse
from typing import Optional


class SciHub:
    """Sci-Hub 全文下载封装。
    
    作为文献检索源，返回论文的完整信息 + PDF 直链。
    按域名顺序尝试。
    """
    
    # Sci-Hub 域名（按需维护）
    DOMAINS = [
        "https://sci-hub.se",
        "https://sci-hub.ru",
        "https://sci-hub.st",
    ]
    
    def search(self, topic: str, max_results: int = 10, year_range: Optional[str] = None) -> list[dict]:
        """搜索 Sci-Hub 论文。
        
        注意：Sci-Hub 没有正式 API，只能通过搜索页面获取信息。
        这里主要用作 DOI 查询全文链接。
        """
        return []  # Sci-Hub 不支持关键词搜索，只支持 DOI 查询
    
    def search_by_doi(self, doi: str) -> Optional[dict]:
        """通过 DOI 从 Sci-Hub 获取全文链接。"""
        if not doi:
            return None
        
        # 尝试获取 PDF（会触发下载，同时拿到 URL）
        content = None
        url = ""
        
        for domain in self.DOMAINS:
            url = f"{domain}/{doi}"
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Synthos-Literature/1.0",
                    "Accept": "application/pdf",
                })
                with urllib.request.urlopen(req, timeout=60) as resp:
                    content = resp.read()
                    if len(content) > 10000 and b"%PDF" in content[:10]:
                        break
            except Exception:
                continue
        
        if content is None:
            return None
        
        # 解析 PDF 中的元数据（DOI 页面通常包含标题/作者等）
        # Sci-Hub 页面 HTML 中提取论文信息
        title = ""
        authors = []
        year = None
        
        try:
            # 先尝试获取原始页面（不触发 PDF 下载）获取元数据
            for domain in self.DOMAINS:
                page_url = f"{domain}/{doi}"
                try:
                    req = urllib.request.Request(page_url, headers={
                        "User-Agent": "Synthos-Literature/1.0",
                    })
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        html = resp.read().decode("utf-8", errors="ignore")
                    
                    # 尝试从 HTML 中提取标题
                    import re
                    title_m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
                    if title_m:
                        title = title_m.group(1).strip()
                    
                    # 从页面中提取作者和年份
                    for line in html.split('\n'):
                        if 'Author:' in line or 'author' in line.lower():
                            # 简单提取
                            pass
                    
                except Exception:
                    continue
        except Exception:
            pass
        
        if not title:
            title = f"Paper (DOI: {doi})"
        
        return {
            "title": title,
            "authors": authors,
            "year": year,
            "source": "scihub",
            "doi": doi,
            "abstract": "",
            "url": url,
            "pdf_url": url,  # Sci-Hub URL 本身就是 PDF 直链
            "local_links": [url],
            "links": {
                "scihub": url,
            },
            "citation_count": 0,
            "venue": "",
            "provenance": f"source=scihub, doi={doi}",
        }
    
    def download_by_doi(self, doi: str, timeout: int = 60, output_path: str | None = None) -> Optional[bytes]:
        """通过 DOI 从 Sci-Hub 下载 PDF。
        
        Args:
            doi: DOI
            timeout: 超时秒数
            output_path: 输出路径
        """
        content = None
        for domain in self.DOMAINS:
            url = f"{domain}/{doi}"
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Synthos-Literature/1.0",
                    "Accept": "application/pdf",
                })
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    content = resp.read()
                    if len(content) > 10000 and b"%PDF" in content[:10]:
                        break
            except Exception:
                continue
        
        if content and output_path:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(content)
        
        return content if content else None