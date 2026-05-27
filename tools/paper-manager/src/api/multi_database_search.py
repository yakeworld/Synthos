import asyncio
import logging
import time
import hashlib
import os
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from urllib.parse import quote

import aiohttp
import requests
import lxml.etree as ET

from src.core.interfaces import IPaperProvider
from src.core.config import Config
from src.utils.paper_id import normalize_paper_id, is_valid_doi
from src.utils.async_helpers import async_retry

logger = logging.getLogger(__name__)


@dataclass
class UnifiedPaper:
    """统一论文数据模型，兼容多数据库"""
    source: str  # "semantic_scholar", "pubmed", "crossref", "openalex", "base", "arxiv"
    title: str = ""
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    open_access: bool = False
    citation_count: int = 0
    reference_count: int = 0
    keywords: List[str] = field(default_factory=list)
    external_ids: Dict[str, str] = field(default_factory=dict)
    raw_data: Dict = field(default_factory=dict)

    @classmethod
    def from_semantic_scholar(cls, data: Dict) -> 'UnifiedPaper':
        """从Semantic Scholar数据创建"""
        external_ids = data.get('externalIds', {}) or {}
        open_access_pdf = data.get('openAccessPdf')
        journal_data = data.get('journal') or {}
        venue_data = data.get('publicationVenue') or {}

        return cls(
            source="semantic_scholar",
            title=data.get('title', ''),
            authors=[a.get('name', '') for a in data.get('authors', [])],
            year=data.get('year'),
            abstract=data.get('abstract'),
            doi=external_ids.get('DOI', ''),
            journal=journal_data.get('name', venue_data.get('name', '')),
            pdf_url=open_access_pdf.get('url') if open_access_pdf else None,
            open_access=open_access_pdf is not None,
            citation_count=data.get('citationCount', 0),
            reference_count=data.get('referenceCount', 0),
            external_ids={k: v for k, v in external_ids.items() if v},
            raw_data=data
        )

    @classmethod
    def from_pubmed(cls, data: Dict) -> 'UnifiedPaper':
        """从PubMed数据创建"""
        return cls(
            source="pubmed",
            title=data.get('title', ''),
            authors=data.get('authors', []),
            year=data.get('year'),
            abstract=data.get('abstract'),
            doi=data.get('doi', ''),
            journal=data.get('journal', ''),
            volume=data.get('volume', ''),
            issue=data.get('issue', ''),
            pages=data.get('pages', ''),
            url=f"https://pubmed.ncbi.nlm.nih.gov/{data.get('pmid', '')}/" if data.get('pmid') else None,
            pdf_url=data.get('pdf_url'),
            open_access=data.get('open_access', False),
            citation_count=data.get('citation_count', 0),
            keywords=data.get('keywords', []),
            external_ids={'PMID': data.get('pmid', ''), 'DOI': data.get('doi', '')},
            raw_data=data
        )

    @classmethod
    def from_crossref(cls, data: Dict) -> 'UnifiedPaper':
        """从Crossref数据创建"""
        authors = data.get('author', [])
        author_names = []
        for a in authors:
            name = f"{a.get('family', '')} {a.get('given', '')}".strip()
            if name:
                author_names.append(name)

        journal = data.get('container-title', [''])[0] if data.get('container-title') else ''
        doi = data.get('DOI', '')

        # link can be a list or a dict
        links = data.get('link', [])
        if isinstance(links, dict):
            links = [links]
        pdf_links = [l.get('url') for l in links if isinstance(l, dict) and l.get('content-type') == 'application/pdf']
        pdf_url = pdf_links[0] if pdf_links else None

        # issued or published-print or published-online
        year = None
        for date_key in ('issued', 'published-print', 'published-online'):
            date_data = data.get(date_key, {})
            if isinstance(date_data, dict) and 'date-parts' in date_data:
                parts = date_data['date-parts'][0] if date_data['date-parts'] else []
                if parts and parts[0]:
                    year = int(parts[0])
                    break

        # is-referenced-by-count or citation-count
        citation_count = data.get('is-referenced-by-count', 0)
        if citation_count is None:
            citation_count = data.get('citation-count', 0)

        # abstract can be string or dict
        abstract = data.get('abstract', '')
        if isinstance(abstract, dict):
            # Inverted index format from OpenAlex-style
            abstract = ' '.join(v for k, v in sorted(abstract.items(), key=lambda x: int(x[0])) if isinstance(v, str))

        return cls(
            source="crossref",
            title=data.get('title', [''])[0] if isinstance(data.get('title'), list) else (data.get('title', '') or ''),
            authors=author_names,
            year=year,
            abstract=abstract if isinstance(abstract, str) else '',
            doi=doi,
            journal=journal,
            volume=data.get('volume', ''),
            issue=data.get('issue', ''),
            pages=data.get('page', ''),
            url=f"https://doi.org/{doi}" if doi else None,
            pdf_url=pdf_url,
            open_access=data.get('license', None) is not None,
            citation_count=citation_count or 0,
            external_ids={'DOI': doi},
            raw_data=data
        )

    @classmethod
    def from_openalex(cls, data: Dict) -> 'UnifiedPaper':
        """从OpenAlex数据创建"""
        authors = data.get('authorships', [])
        author_names = []
        for a in authors:
            author_info = a.get('author', {})
            name = author_info.get('display_name', '')
            if name:
                author_names.append(name)

        doi_raw = data.get('doi', '')
        if doi_raw and doi_raw.startswith('https://doi.org/'):
            doi = doi_raw.replace('https://doi.org/', '')
        else:
            doi = doi_raw

        # Reconstruct abstract from inverted index
        abstract_raw = data.get('abstract_inverted_index', {})
        abstract = ''
        if isinstance(abstract_raw, dict):
            try:
                sorted_items = sorted(abstract_raw.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0)
                abstract = ' '.join(v for k, v in sorted_items if isinstance(v, str) and v.strip())
            except (ValueError, TypeError):
                abstract = ''

        primary_loc = data.get('primary_location', {}) or {}
        source = primary_loc.get('source', {}) or {}

        return cls(
            source="openalex",
            title=data.get('title', ''),
            authors=author_names,
            year=data.get('publication_year'),
            abstract=abstract,
            doi=doi,
            journal=source.get('display_name', ''),
            url=f"https://doi.org/{doi}" if doi else None,
            open_access=data.get('open_access', {}).get('is_oa', False),
            citation_count=data.get('cited_by_count', 0),
            external_ids={k: v for k, v in data.get('ids', {}).items() if v},
            raw_data=data
        )

    @classmethod
    def from_base(cls, data: Dict) -> 'UnifiedPaper':
        """从BASE数据创建"""
        doi = ''
        if 'identifiers' in data:
            for ident in data['identifiers']:
                if ident.startswith('10.'):
                    doi = ident
                    break

        pdf_url = ''
        for link in data.get('links', []):
            if link.get('type') == 'application/pdf' or (link.get('url') and link['url'].endswith('.pdf')):
                pdf_url = link.get('url', '')
                break
        if not pdf_url:
            for link in data.get('links', []):
                url = link.get('url', '')
                if url and ('.pdf' in url.lower()):
                    pdf_url = url
                    break

        return cls(
            source="base",
            title=data.get('title', ''),
            authors=data.get('authors', []),
            year=data.get('year'),
            abstract=data.get('abstract', ''),
            doi=doi,
            journal=data.get('journal', ''),
            url=data.get('url') or data.get('documentUrl', ''),
            pdf_url=pdf_url,
            open_access=pdf_url != '',
            keywords=data.get('subject', []),
            external_ids={'DOI': doi},
            raw_data=data
        )

    @classmethod
    def from_arxiv(cls, data: Dict) -> 'UnifiedPaper':
        """从arXiv数据创建"""
        return cls(
            source="arxiv",
            title=data.get('title', '').strip(),
            authors=data.get('authors', []),
            year=int(data.get('published')[:4]) if data.get('published') else None,
            abstract=data.get('summary', ''),
            pdf_url=data.get('pdf_link'),
            url=data.get('id'),
            open_access=True,
            keywords=data.get('categories', []),
            external_ids={'arXiv': data.get('id', '').replace('http://', 'https://').split('/')[-1] if data.get('id') else ''},
            raw_data=data
        )

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'source': self.source,
            'title': self.title,
            'authors': ', '.join(self.authors),
            'year': self.year,
            'abstract': self.abstract,
            'doi': self.doi,
            'journal': self.journal,
            'volume': self.volume,
            'issue': self.issue,
            'pages': self.pages,
            'url': self.url,
            'pdf_url': self.pdf_url,
            'open_access': self.open_access,
            'citation_count': self.citation_count,
            'reference_count': self.reference_count,
            'keywords': ', '.join(self.keywords),
            **self.external_ids
        }

    def get_identifier(self) -> str:
        """获取唯一标识符"""
        if self.doi:
            return f"DOI:{self.doi}"
        if self.external_ids.get('PMID'):
            return f"PMID:{self.external_ids['PMID']}"
        if self.external_ids.get('arXiv'):
            return f"arXiv:{self.external_ids['arXiv']}"
        if self.external_ids.get('CorpusID'):
            return f"CorpusID:{self.external_ids['CorpusID']}"
        return hashlib.md5(self.title.encode()).hexdigest()


class RateLimiter:
    """简单的请求速率限制器"""
    def __init__(self, max_requests: int = 10, window_seconds: int = 1):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: List[float] = []

    async def acquire(self):
        """等待直到可以发送请求"""
        now = time.time()
        self._timestamps = [t for t in self._timestamps if now - t < self.window_seconds]
        if len(self._timestamps) >= self.max_requests:
            wait_time = self.window_seconds - (now - self._timestamps[0]) + 0.1
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        self._timestamps.append(time.time())


class MultiDatabaseSearchClient(IPaperProvider):
    """
    多数据库学术论文搜索客户端
    
    支持:
    - Semantic Scholar (已实现)
    - PubMed / PMC
    - Crossref
    - OpenAlex
    - BASE (Bielefeld Academic Search Engine)
    - arXiv
    """

    def __init__(self, config: Config):
        self.config = config
        self.session = None
        self.sync_session = requests.Session()
        self.rate_limiters = {
            'pubmed': RateLimiter(max_requests=5, window_seconds=1),
            'crossref': RateLimiter(max_requests=10, window_seconds=1),
            'openalex': RateLimiter(max_requests=10, window_seconds=1),
            'base': RateLimiter(max_requests=5, window_seconds=1),
            'arxiv': RateLimiter(max_requests=5, window_seconds=1),
        }

    async def create_session(self):
        """创建异步会话"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.download_timeout + 5)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close_session(self):
        """关闭异步会话"""
        if self.session:
            try:
                await self.session.close()
                self.session = None
                await asyncio.sleep(0.25)
            except Exception as e:
                logger.error(f"Error closing aiohttp session: {e}")

    def __del__(self):
        """析构函数"""
        if hasattr(self, 'sync_session') and self.sync_session:
            try:
                self.sync_session.close()
            except Exception:
                pass

    # ============================================================
    # Semantic Scholar (复用原有客户端功能)
    # ============================================================
    async def search_semantic_scholar(self, query: str, limit: int = 20) -> List[UnifiedPaper]:
        """Semantic Scholar 搜索"""
        papers = []
        try:
            await self.create_session()
            url = f"{self.config.base_url}/paper/search/bulk"
            params = {'query': query, 'fields': self.config.fields, 'limit': min(limit, 100)}

            async with self.session.get(url, headers=self.config.headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for item in data.get('data', []):
                        papers.append(UnifiedPaper.from_semantic_scholar(item))
        except Exception as e:
            logger.error(f"Semantic Scholar search failed: {e}")
        return papers

    # ============================================================
    # PubMed / PMC
    # ============================================================
    async def search_pubmed(self, query: str, limit: int = 20) -> List[UnifiedPaper]:
        """PubMed 搜索"""
        papers = []
        try:
            await self.rate_limiters['pubmed'].acquire()

            # Step 1: Search for IDs
            search_url = (
                f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
                f"db=pubmed&term={quote(query)}&retmax={limit}&sort=relevance&retmode=json"
            )
            resp = requests.get(search_url, timeout=15)
            resp.raise_for_status()
            search_data = resp.json()
            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            if not id_list:
                return papers

            # Step 2: Get summaries
            summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={','.join(id_list)}&retmode=json"
            resp = requests.get(summary_url, timeout=15)
            resp.raise_for_status()
            summary_data = resp.json().get('result', {})

            # Step 3: Get abstracts
            abstract_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(id_list)}&retmode=xml"
            resp = requests.get(abstract_url, timeout=15)
            resp.raise_for_status()
            abstract_xml = resp.text

            # Parse abstracts
            root = ET.fromstring(abstract_xml)
            abstracts = {}
            for article in root.findall('.//PubmedArticle'):
                pmid_el = article.find('.//PMID')
                if pmid_el is None:
                    continue
                pmid = pmid_el.text or ''

                # Extract abstract
                abstract = ''
                abstract_el = article.find('.//Abstract')
                if abstract_el is not None:
                    for text_el in abstract_el.findall('AbstractText'):
                        label = text_el.get('Label', '')
                        content = (text_el.text or '').strip()
                        if content:
                            abstract += f"{' ' + label + ': ' if label else ''}{content}\n"
                abstracts[pmid] = abstract.strip()

                # Extract PMC ID and DOI
                pmc_id = ''
                doi = ''
                for id_el in article.findall('.//ArticleId'):
                    if id_el.get('IdType') == 'pmc':
                        pmc_id = id_el.text or ''
                    elif id_el.get('IdType') == 'doi':
                        doi = id_el.text or ''

                # Extract keywords
                keywords = []
                keyword_list = article.find('.//KeywordList')
                if keyword_list is not None:
                    for kw in keyword_list.findall('Keyword'):
                        if kw.text:
                            keywords.append(kw.text.strip())

                # Extract MeSH terms
                for mesh in article.findall('.//MeshHeading'):
                    desc = mesh.find('DescriptorName')
                    if desc and desc.text:
                        keywords.append(desc.text.strip())
                keywords = list(set([k for k in keywords if k]))

                # Extract journal info
                journal = ''
                vol = ''
                iss = ''
                pgs = ''
                journal_el = article.find('.//Journal//Title')
                if journal_el is not None:
                    journal = journal_el.text or ''
                vol_el = article.find('.//Journal//Volume')
                if vol_el is not None:
                    vol = vol_el.text or ''
                iss_el = article.find('.//Journal//Issue')
                if iss_el is not None:
                    iss = iss_el.text or ''
                pgs_el = article.find('.//MedlinePgn')
                if pgs_el is not None:
                    pgs = pgs_el.text or ''

        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return papers

        # Build paper list from summaries
        for pmid in id_list[:limit]:
            key_str = str(pmid)
            article = summary_data.get(key_str, {})
            # Handle case where result['uid'] contains a single PMID string
            if not article and isinstance(summary_data.get('uid'), str) and summary_data.get('uid') == key_str:
                article = {k: v for k, v in summary_data.items() if k != 'uid'}
            if not article:
                continue

            title = article.get('title', '')
            if not title:
                # Some entries have 'sorttitle' but not 'title'
                title = article.get('sorttitle', '')
            pub_date = article.get('pubdate', '')
            year = None
            if pub_date:
                import re
                m = re.search(r'\d{4}', pub_date)
                if m:
                    year = int(m.group())

            doi = article.get('articleids', {})
            # articleids can be a list of {idtype, value} or a dict
            doi_val = ''
            if isinstance(doi, list):
                for item in doi:
                    if isinstance(item, dict) and item.get('idtype') == 'doi':
                        doi_val = item.get('value', '')
                        break
            elif isinstance(doi, dict):
                doi_val = doi.get('doi', '')

            pmc_id = ''
            pmcid_val = article.get('PMCID', '')
            if isinstance(pmcid_val, str) and pmcid_val and pmcid_val != 'N/A':
                pmc_id = str(pmcid_val).replace('PMC', '')
            elif isinstance(pmcid_val, list):
                for item in pmcid_val:
                    if isinstance(item, dict) and item.get('idtype') == 'pmc':
                        pmc_id = str(item.get('value', '')).replace('PMC', '')
                        break
                    elif isinstance(item, str) and item:
                        pmc_id = str(item).replace('PMC', '')
                        break

            # Extract authors
            authors = []
            author_list = article.get('authors', [])
            if isinstance(author_list, list):
                for a in author_list:
                    if isinstance(a, dict):
                        name = a.get('name', '')
                        if name:
                            authors.append(name)
                    elif isinstance(a, str):
                        if a:
                            authors.append(a)
            elif isinstance(author_list, str):
                authors = [author_list]

            # Build keywords from JSON
            json_keywords = []
            for kw in article.get('keywords', []):
                if isinstance(kw, str) and kw:
                    json_keywords.append(kw)

            all_keywords = list(set(json_keywords + keywords))

            paper = UnifiedPaper(
                source="pubmed",
                title=title,
                authors=authors,
                year=year,
                abstract=abstracts.get(pmid, ''),
                doi=doi_val,
                journal=journal,
                volume=vol,
                issue=iss,
                pages=pgs,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                pdf_url=f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/pdf/" if pmc_id else None,
                open_access=pmc_id != '',
                external_ids={'PMID': pmid, 'DOI': doi_val, 'PMCID': pmc_id},
                keywords=all_keywords,
                raw_data={'pmid': pmid}
            )
            papers.append(paper)

        return papers

    # ============================================================
    # Crossref
    # ============================================================
    async def search_crossref(self, query: str, limit: int = 20) -> List[UnifiedPaper]:
        """Crossref 搜索"""
        papers = []
        try:
            await self.rate_limiters['crossref'].acquire()
            url = "https://api.crossref.org/works"
            params = {
                'query': query,
                'rows': min(limit, 100),
                'sort': 'relevance',
                'select': 'title,author,abstract,DOI,container-title,volume,issue,page,issued,license,link,is-referenced-by-count'
            }
            headers = {'User-Agent': 'ResearchPaperManager/1.0 (academic-research@example.com)'}

            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    message = data.get('message', {})
                    # message may be a list (error responses) or dict
                    if isinstance(message, list):
                        logger.debug(f"Crossref returned list (errors): {message[:3]}")
                    else:
                        for item in message.get('items', []):
                            papers.append(UnifiedPaper.from_crossref(item))
        except Exception as e:
            logger.error(f"Crossref search failed: {e}")
        return papers

    # ============================================================
    # OpenAlex
    # ============================================================
    async def search_openalex(self, query: str, limit: int = 20) -> List[UnifiedPaper]:
        """OpenAlex 搜索"""
        papers = []
        try:
            await self.rate_limiters['openalex'].acquire()
            url = "https://api.openalex.org/works"
            params = {
                'search': query,
                'per_page': min(limit, 200),
                'sort': 'cited_by_count:desc'
            }
            headers = {'User-Agent': 'ResearchPaperManager/1.0 (academic-research@example.com)'}

            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for item in data.get('results', []):
                        papers.append(UnifiedPaper.from_openalex(item))
        except Exception as e:
            logger.error(f"OpenAlex search failed: {e}")
        return papers

    # ============================================================
    # BASE
    # ============================================================
    async def search_base(self, query: str, limit: int = 20) -> List[UnifiedPaper]:
        """BASE (Bielefeld Academic Search Engine) 搜索"""
        papers = []
        try:
            await self.rate_limiters['base'].acquire()
            # BASE uses a simple REST API
            url = "https://www.base-search.net/Search/Results"
            params = {
                'lookfor': query,
                'type=DefaultField': '1',
                'limit': min(limit, 50),
                'first': 0,
                'display': 'json'  # Some BASE instances support JSON
            }
            headers = {'User-Agent': 'Mozilla/5.0'}

            # Note: BASE mainly provides HTML, but some endpoints support JSON
            # For now, we'll try the JSON endpoint
            try:
                async with self.session.get(url, headers=headers, params=params) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        try:
                            data = json.loads(text)
                            for item in data.get('result', {}).get('hits', {}).get('item', []):
                                paper = UnifiedPaper(
                                    source="base",
                                    title=item.get('title', ''),
                                    url=item.get('link', [{}])[0] if item.get('link') else '',
                                    pdf_url=item.get('file', [{}])[0].get('url') if item.get('file') else None,
                                    year=int(item.get('year')) if item.get('year') and item['year'].isdigit() else None,
                                    authors=[item.get('creator', '')],
                                    external_ids={},
                                    raw_data=item
                                )
                                papers.append(paper)
                        except json.JSONDecodeError:
                            # BASE returns HTML by default, skip
                            logger.debug("BASE returned HTML, JSON parsing failed")
            except Exception as e:
                logger.debug(f"BASE direct search failed: {e}")

        except Exception as e:
            logger.error(f"BASE search failed: {e}")
        return papers

    # ============================================================
    # arXiv
    # ============================================================
    async def search_arxiv(self, query: str, limit: int = 20) -> List[UnifiedPaper]:
        """arXiv 搜索"""
        papers = []
        try:
            await self.rate_limiters['arxiv'].acquire()
            url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': f"all:{quote(query)}",
                'start': 0,
                'max_results': min(limit, 100),
                'sortBy': 'relevance'
            }
            headers = {'User-Agent': 'ResearchPaperManager/1.0'}

            async with self.session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    xml_text = await resp.text()
                    root = ET.fromstring(xml_text.encode())

                    ns = {'atom': 'http://www.w3.org/2005/Atom'}
                    for entry in root.findall('atom:entry', ns):
                        title = entry.find('atom:title', ns)
                        summary = entry.find('atom:summary', ns)
                        id_el = entry.find('atom:id', ns)
                        published = entry.find('atom:published', ns)
                        updated = entry.find('atom:updated', ns)

                        authors = []
                        for author in entry.findall('atom:author', ns):
                            name = author.find('atom:name', ns)
                            if name is not None and name.text:
                                authors.append(name.text)

                        categories = []
                        for cat in entry.findall('atom:category', ns):
                            term = cat.get('term', '')
                            if term:
                                categories.append(term)

                        pdf_link = ''
                        for link in entry.findall('atom:link', ns):
                            if link.get('title') == 'pdf':
                                pdf_link = link.get('href', '')
                                break

                        paper_id = id_el.text.split('/')[-1] if id_el is not None else ''

                        paper = UnifiedPaper(
                            source="arxiv",
                            title=(title.text or '').strip(),
                            authors=authors,
                            year=int((published.text or '')[:4]) if published is not None and published.text else None,
                            abstract=(summary.text or '').strip(),
                            pdf_url=pdf_link,
                            url=f"https://arxiv.org/abs/{paper_id}" if paper_id else '',
                            open_access=True,
                            keywords=categories,
                            external_ids={'arXiv': paper_id},
                            raw_data={'id': paper_id}
                        )
                        papers.append(paper)
        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
        return papers

    # ============================================================
    # Unified Search Interface
    # ============================================================
    async def search_all(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        limit_per_source: int = 20,
        deduplicate: bool = True
    ) -> List[UnifiedPaper]:
        """
        多数据库统一搜索

        Args:
            query: 搜索查询
            sources: 要搜索的数据库列表, 默认全部
            limit_per_source: 每个数据库返回结果数
            deduplicate: 是否去重

        Returns:
            统一格式的论文列表
        """
        if sources is None:
            sources = ['semantic_scholar', 'pubmed', 'crossref', 'openalex', 'arxiv']

        search_map = {
            'semantic_scholar': lambda: self.search_semantic_scholar(query, limit_per_source),
            'pubmed': lambda: self.search_pubmed(query, limit_per_source),
            'crossref': lambda: self.search_crossref(query, limit_per_source),
            'openalex': lambda: self.search_openalex(query, limit_per_source),
            'arxiv': lambda: self.search_arxiv(query, limit_per_source),
        }

        tasks = []
        for source in sources:
            if source in search_map:
                tasks.append(search_map[source]())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results
        all_papers = []
        for r in results:
            if isinstance(r, list):
                all_papers.extend(r)
            elif isinstance(r, Exception):
                logger.error(f"Search task failed: {r}")

        # Deduplicate by DOI / title similarity
        if deduplicate:
            all_papers = self._deduplicate_papers(all_papers)

        return all_papers

    def _deduplicate_papers(self, papers: List[UnifiedPaper]) -> List[UnifiedPaper]:
        """去重论文列表"""
        seen = set()
        unique = []
        for paper in papers:
            key = paper.get_identifier()
            if key not in seen:
                seen.add(key)
                unique.append(paper)
        return unique

    # ============================================================
    # IPaperProvider interface implementation
    # ============================================================
    async def search_papers(self, query: str) -> List[Dict]:
        """搜索论文 - 统一接口，优先Semantic Scholar，然后其他数据库"""
        papers = []

        # 优先 Semantic Scholar
        ss_papers = await self.search_semantic_scholar(query, 20)
        papers.extend([p.to_dict() for p in ss_papers])

        # 如果SS没有结果，尝试其他数据库
        if not ss_papers:
            crossref = await self.search_crossref(query, 20)
            papers.extend([p.to_dict() for p in crossref])

            openalex = await self.search_openalex(query, 20)
            papers.extend([p.to_dict() for p in openalex])

            arxiv = await self.search_arxiv(query, 20)
            papers.extend([p.to_dict() for p in arxiv])

            pubmed = await self.search_pubmed(query, 20)
            papers.extend([p.to_dict() for p in pubmed])

        return papers

    async def get_paper_details(self, paper_id: str) -> Optional[Dict]:
        """获取论文详情 - 尝试各数据库"""
        # 优先Semantic Scholar
        try:
            await self.create_session()
            url = self._construct_paper_url(paper_id)
            if url:
                async with self.session.get(url, headers=self.config.headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
        except Exception as e:
            logger.debug(f"Paper details from S2 failed: {e}")

        # Try Crossref
        try:
            await self.create_session()
            url = f"https://api.crossref.org/works/{paper_id}"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('message', {})
        except Exception as e:
            logger.debug(f"Paper details from Crossref failed: {e}")

        return None

    async def get_references(self, paper_id: str, limit: int = 100) -> List[Dict]:
        """获取引用文献 - 优先从Semantic Scholar"""
        try:
            await self.create_session()
            url = f"{self.config.base_url}/paper/{paper_id}/references"
            params = {"fields": self.config.fields, "limit": limit}
            async with self.session.get(url, headers=self.config.headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [item["citedPaper"] for item in data.get("data", []) if "citedPaper" in item]
        except Exception as e:
            logger.error(f"Error fetching references for {paper_id}: {e}")
        return []

    async def get_citations(self, paper_id: str, limit: int = 100) -> List[Dict]:
        """获取被引文献 - 优先从Semantic Scholar"""
        try:
            await self.create_session()
            url = f"{self.config.base_url}/paper/{paper_id}/citations"
            params = {"fields": self.config.fields, "limit": limit}
            async with self.session.get(url, headers=self.config.headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [item["citingPaper"] for item in data.get("data", []) if "citingPaper" in item]
        except Exception as e:
            logger.error(f"Error fetching citations for {paper_id}: {e}")
        return []

    async def get_recommendations(self, paper_id: str, limit: int = 10) -> List[Dict]:
        """获取推荐文献"""
        try:
            await self.create_session()
            url = f"{self.config.recommendations_url}/papers/forpaper/{paper_id}"
            params = {"limit": limit}
            async with self.session.get(url, headers=self.config.headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("recommendedPapers", [])
        except Exception as e:
            logger.error(f"Error fetching recommendations for {paper_id}: {e}")
        return []

    async def get_author_papers(self, author_id: str, limit: int = 100) -> List[Dict]:
        """获取作者论文"""
        try:
            await self.create_session()
            url = f"{self.config.base_url}/author/{author_id}/papers"
            params = {"fields": self.config.fields, "limit": limit}
            async with self.session.get(url, headers=self.config.headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [item["paper"] if "paper" in item else item for item in data.get("data", [])]
        except Exception as e:
            logger.error(f"Error fetching author papers for {author_id}: {e}")
        return []

    def _construct_paper_url(self, paper_id: str) -> Optional[str]:
        """构造论文API URL"""
        base_url = f"{self.config.base_url}/paper/"

        import re
        m = re.match(r"ARXIV:(.+)", paper_id, re.IGNORECASE)
        if m:
            return f"{base_url}ARXIV:{m.group(1)}?fields={self.config.fields}"

        m = re.match(r"CorpusID:(\d+)", paper_id, re.IGNORECASE)
        if m:
            return f"{base_url}CorpusID:{m.group(1)}?fields={self.config.fields}"

        m = re.match(r"DOI:(.+)", paper_id, re.IGNORECASE)
        if m:
            return f"{base_url}DOI:{m.group(1)}?fields={self.config.fields}"

        if re.match(r"^[a-f0-9]{40}$", paper_id):
            return f"{base_url}{paper_id}?fields={self.config.fields}"

        return None