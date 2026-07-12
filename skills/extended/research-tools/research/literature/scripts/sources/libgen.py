"""
LibGen (Library Genesis) — 学术文献、书籍、论文的综合影子图书馆。

当前可用域名（2026-07-12 实测）:
- libgen.bz — 主站（HTTP 200, 完整页面, 无需代理）✅
- libgen.cc — 可用（HTTP 200, 重定向页, 需跳转）
- libgen.to — 可用（HTTP 200, 重定向页, 需跳转）

API 形式: HTML 搜索（index.php?req=...&column=...&deftype=...）
下载: HTML get.php 链接

不依赖 API key，直接 HTTP 请求。
"""
import requests
import re
import os
from urllib.parse import urljoin, quote


# 主域名（实测可用）
PRIMARY_DOMAIN = "https://libgen.bz"
BACKUP_DOMAINS = [
    "https://libgen.cc",
    "https://libgen.to",
]


class LibGen:
    """LibGen 搜索与下载 — 论文+书籍的综合知识库。"""
    
    def __init__(self, domain=None):
        self.domain = domain or PRIMARY_DOMAIN
    
    def _fetch(self, endpoint):
        """GET request with domain fallback."""
        for url in [f"{self.domain}{endpoint}"] + [f"{d}{endpoint}" for d in BACKUP_DOMAINS]:
            try:
                resp = requests.get(url, timeout=15, allow_redirects=True)
                if resp.status_code == 200 and len(resp.content) > 5000:
                    return resp.text
            except Exception:
                continue
        return None
    
    def search(self, topic, max_results=10, year_range=None):
        """
        Search LibGen by title/author.
        """
        papers = []
        endpoint = f"/index.php?req={quote(topic)}&column=title&deftype=0"
        html = self._fetch(endpoint)
        
        if not html:
            return []
        
        # Parse table rows
        tr_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL)
        rows = tr_pattern.findall(html)
        
        for row in rows:
            if any(x in row for x in ['navbar', 'dropdown', 'menu', 'search', 'tablelibgen']):
                continue
            
            # Extract td content
            tds_raw = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            tds = [re.sub(r'<[^>]+>', '', t).strip() for t in tds_raw]
            
            if len(tds) < 5:
                continue
            
            # Skip rows that are just navigation
            if any(t.startswith('href=') or 'navbar' in t for t in tds):
                continue
            
            # Parse structured data
            # Format: [full_row, title/journal info, author, year, publisher?, language, pages, size, format, links]
            full_text = ' '.join(tds)
            
            # Extract DOI
            doi_match = re.search(r'DOI:\s*(\d+[^\s\r\n]+)', full_text)
            doi = doi_match.group(1) if doi_match else ""
            
            # Extract title
            title_match = re.search(r'href="edition\.php\?id=\d+">([^<]+)</a>', full_text)
            title = title_match.group(1).strip() if title_match else ""
            
            # Extract journal
            journal_match = re.search(r'^([^<]+?)\s*<a', full_text)
            journal = journal_match.group(1).strip() if journal_match else ""
            
            # Extract author
            author = tds[1] if len(tds) > 1 else ""
            
            # Extract year
            year = tds[3] if len(tds) > 3 else ""
            
            # Extract size
            size = tds[6] if len(tds) > 6 else ""
            
            # Extract format
            fmt = tds[7] if len(tds) > 7 else ""
            
            # Extract links (get.php, edition.php)
            links_raw = re.findall(r'href="([^"]*(?:get\.php|edition\.php)[^"]*)"', full_text)
            
            # Build paper dict
            if title:
                year_num = re.search(r'(\d{4})', year)
                year_int = int(year_num.group(1)) if year_num else None
                
                links = {}
                for link in links_raw[:3]:
                    if 'get.php' in link:
                        links["download"] = urljoin(self.domain, link)
                    elif 'edition.php' in link:
                        links["entry"] = urljoin(self.domain, link)
                
                papers.append({
                    "title": title,
                    "authors": [a.strip() for a in author.split(';') if a.strip()],
                    "year": year_int,
                    "source": "libgen",
                    "doi": doi,
                    "abstract": f"{journal}" if journal else "",
                    "url": links.get("entry", self.domain),
                    "pdf_url": links.get("download", ""),
                    "local_links": [links["download"]] if links.get("download") else [],
                    "links": links,
                    "citation_count": None,
                    "venue": journal,
                    "provenance": f"source=libgen",
                    "is_free": True,
                    "pmc": None,
                    "arxiv_id": None,
                    "size": size,
                    "format": fmt,
                })
            
            if len(papers) >= max_results:
                break
        
        return papers[:max_results]
    
    def search_by_doi(self, doi):
        """Search by DOI. Returns first matching paper or None."""
        endpoint = f"/index.php?req={quote(doi)}&column=doi&deftype=0"
        html = self._fetch(endpoint)
        
        if not html:
            return None
        
        tr_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL)
        rows = tr_pattern.findall(html)
        
        for row in rows:
            if any(x in row for x in ['navbar', 'dropdown', 'menu', 'search', 'tablelibgen']):
                continue
            
            tds_raw = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            tds = [re.sub(r'<[^>]+>', '', t).strip() for t in tds_raw]
            
            if len(tds) < 3 or not any(doi.lower() in t.lower() for t in tds):
                continue
            
            full_text = ' '.join(tds)
            doi_match = re.search(r'DOI:\s*(\d+[^\s\r\n]+)', full_text)
            title_match = re.search(r'href="edition\.php\?id=\d+">([^<]+)</a>', full_text)
            author_match = re.search(r'href="author\.php\?id=\d+">([^<]+)</a>', full_text)
            
            if title_match:
                title = title_match.group(1).strip()
                author = author_match.group(1) if author_match else ""
                links_raw = re.findall(r'href="([^"]*(?:get\.php|edition\.php)[^"]*)"', full_text)
                
                links = {}
                for link in links_raw[:3]:
                    if 'get.php' in link:
                        links["download"] = urljoin(self.domain, link)
                    elif 'edition.php' in link:
                        links["entry"] = urljoin(self.domain, link)
                
                return {
                    "title": title,
                    "authors": [a.strip() for a in author.split(';') if a.strip()],
                    "year": None,
                    "source": "libgen",
                    "doi": doi_match.group(1) if doi_match else doi,
                    "abstract": "",
                    "url": links.get("entry", self.domain),
                    "pdf_url": links.get("download", ""),
                    "local_links": [links["download"]] if links.get("download") else [],
                    "links": links,
                    "citation_count": None,
                    "venue": "",
                    "provenance": f"source=libgen",
                    "is_free": True,
                    "pmc": None,
                    "arxiv_id": None,
                    "size": "",
                    "format": "",
                }
        
        return None
    
    def search_by_md5(self, md5):
        """Search by MD5 hash (most direct)."""
        endpoint = f"/index.php?md5={md5}&column=md5&deftype=0"
        html = self._fetch(endpoint)
        if not html:
            return None
        
        # Same parsing logic as search()
        tr_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL)
        rows = tr_pattern.findall(html)
        
        for row in rows:
            if any(x in row for x in ['navbar', 'dropdown', 'menu', 'search', 'tablelibgen']):
                continue
            
            tds_raw = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            tds = [re.sub(r'<[^>]+>', '', t).strip() for t in tds_raw]
            
            if ' '.join(tds).lower().startswith('no results'):
                return None
            
            full_text = ' '.join(tds)
            title_match = re.search(r'href="edition\.php\?id=\d+">([^<]+)</a>', full_text)
            if title_match:
                title = title_match.group(1).strip()
                links_raw = re.findall(r'href="([^"]*(?:get\.php|edition\.php)[^"]*)"', full_text)
                
                links = {}
                for link in links_raw[:3]:
                    if 'get.php' in link:
                        links["download"] = urljoin(self.domain, link)
                    elif 'edition.php' in link:
                        links["entry"] = urljoin(self.domain, link)
                
                return {
                    "title": title,
                    "authors": [],
                    "year": None,
                    "source": "libgen",
                    "doi": "",
                    "abstract": "",
                    "url": links.get("entry", self.domain),
                    "pdf_url": links.get("download", ""),
                    "local_links": [links["download"]] if links.get("download") else [],
                    "links": links,
                    "citation_count": None,
                    "venue": "",
                    "provenance": f"source=libgen",
                    "is_free": True,
                    "pmc": None,
                    "arxiv_id": None,
                    "size": "",
                    "format": "",
                }
        
        return None