"""CNKI search source — Chinese academic paper search via kns.cnki.net API.

RSSHub-discovered API (routes/cnki/author.ts):
- POST https://kns.cnki.net/kns8s/brief/grid
- Form data with QueryJson (author name + institution)
- No captcha, no browser automation needed

Search types:
  1. author: 按作者+单位搜索论文
  2. journal: 按期刊缩写获取论文目录
  3. debut: 网络首发论文
"""
import re, json, logging, os, urllib.request, urllib.parse
from typing import Optional

logger = logging.getLogger(__name__)

HOST = 'https://kns.cnki.net'
SEARCH_URL = f'{HOST}/kns8s/brief/grid'

# Product codes for full database search
PRODUCT_STR = 'YSTT4HG0,LSTPFY1C,RMJLXHZ3,JQIRZIYA,JUP3MUPD,1UR4K4HZ,BPBAFJ5S,R79MZMCB,MPMFIG1A,EMRPGLPA,J708GVCE,ML4DRIDX,WQ0UVIAA,NB3BWEHK,XVLO76FD,HR1YT1Z9,BLZOG7CK,PWFIRAGL,NN3FJMUV,NLBO1Z6R'
KUAKU_CODE = 'YSTT4HG0,LSTPFY1C,JUP3MUPD,MPMFIG1A,EMRPGLPA,WQ0UVIAA,BLZOG7CK,PWFIRAGL,NN3FJMUV,NLBO1Z6R'


def _build_author_query(name: str, company: str, page: int = 1, page_size: int = 20) -> str:
    """Build form data for CNKI author search."""
    params = urllib.parse.urlencode({
        'boolSearch': 'true',
        'QueryJson': json.dumps({
            'Platform': '',
            'Resource': 'CROSSDB',
            'Classid': 'WD0FTY92',
            'Products': '',
            'QNode': {
                'QGroup': [
                    {
                        'Key': 'Subject',
                        'Title': '',
                        'Logic': 0,
                        'Items': [],
                        'ChildItems': [
                            {
                                'Key': 'input[data-tipid=gradetxt-1]',
                                'Title': '作者',
                                'Logic': 0,
                                'Items': [{
                                    'Key': 'input[data-tipid=gradetxt-1]',
                                    'Title': '作者',
                                    'Logic': 0,
                                    'Field': 'AU',
                                    'Operator': 'DEFAULT',
                                    'Value': name,
                                    'Value2': '',
                                }],
                                'ChildItems': [],
                            },
                            {
                                'Key': 'input[data-tipid=gradetxt-2]',
                                'Title': '作者单位',
                                'Logic': 0,
                                'Items': [{
                                    'Key': 'input[data-tipid=gradetxt-2]',
                                    'Title': '作者单位',
                                    'Logic': 0,
                                    'Field': 'AF',
                                    'Operator': 'FUZZY',
                                    'Value': company,
                                    'Value2': '',
                                }],
                                'ChildItems': [],
                            },
                        ],
                    },
                    {
                        'Key': 'ControlGroup',
                        'Title': '',
                        'Logic': 0,
                        'Items': [],
                        'ChildItems': [],
                    },
                ],
            },
            'ExScope': '0',
            'SearchType': 3,
            'Rlang': 'CHINESE',
            'KuaKuCode': KUAKU_CODE,
        }, ensure_ascii=False),
        'pageNum': str(page),
        'pageSize': str(page_size),
        'sortField': 'PT',
        'sortType': 'desc',
        'dstyle': 'listmode',
        'productStr': PRODUCT_STR,
        'aside': f'（作者：{name}(精确)）AND（作者单位：{company}(模糊)）',
        'searchFrom': '资源范围：总库;  时间范围：更新时间：不限;',
        'CurPage': str(page),
    }, doseq=True)
    return params


def _parse_results(html: str) -> list[dict]:
    """Parse CNKI search results HTML into paper dicts."""
    papers = []
    # Extract paper rows from the table
    # CNKI returns HTML with <tr> rows, first row is header
    rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
    
    for row in rows[1:]:  # Skip header row
        # Title + link
        title_match = re.search(r'<a[^>]*class="fz14"[^>]*>(.*?)</a>', row, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ''
        title = re.sub(r'<[^>]+>', '', title)  # Strip inner HTML
        
        # Filename for detail URL
        fn_match = re.search(r'data-filename="([^"]+)"', row)
        filename = fn_match.group(1) if fn_match else ''
        
        # Authors
        auth_match = re.search(r'<td[^>]*class="author"[^>]*>(.*?)</td>', row, re.DOTALL)
        authors = re.sub(r'<[^>]+>', '', auth_match.group(1)).strip() if auth_match else ''
        
        # Source/Journal
        src_match = re.search(r'<td[^>]*class="source"[^>]*>(.*?)</td>', row, re.DOTALL)
        source = re.sub(r'<[^>]+>', '', src_match.group(1)).strip() if src_match else ''
        
        # Date
        date_match = re.search(r'<td[^>]*class="date"[^>]*>(.*?)</td>', row, re.DOTALL)
        date = re.sub(r'<[^>]+>', '', date_match.group(1)).strip() if date_match else ''
        
        if title and filename:
            papers.append({
                'title': title,
                'filename': filename,
                'url': f'https://cnki.net/kcms/detail/detail.aspx?filename={filename}&dbcode=CJFD',
                'authors': authors,
                'source': source,
                'date': date,
            })
    
    return papers


def search_author(name: str, company: str, max_results: int = 20) -> list[dict]:
    """Search CNKI for papers by author at institution.
    
    Args:
        name: Author name (Chinese)
        company: Institution name (Chinese, e.g. '温州市人民医院')
        max_results: Max papers to return (default 20)
    
    Returns:
        List of paper dicts with title, url, authors, source, date
    """
    params = _build_author_query(name, company, page=1, page_size=min(max_results, 50))
    
    req = urllib.request.Request(
        SEARCH_URL,
        data=params.encode('utf-8'),
        headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'Referer': f'{HOST}/kns8s/AdvSearch?classid=WD0FTY92',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='replace')
            return _parse_results(html)
    except Exception as e:
        logger.debug(f"CNKI search error: {e}")
        return []


def search_journal(journal_code: str, max_results: int = 20) -> list[dict]:
    """Search CNKI for latest papers in a journal.
    
    Args:
        journal_code: Journal abbreviation (e.g. 'LKGP' for 眼科)
        max_results: Max papers to return
    
    Returns:
        List of paper dicts
    """
    # Try RSS first (fastest path)
    rss_url = f'https://rss.cnki.net/kns/rss.aspx?Journal={journal_code}&Virtual=knavi'
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            rss_data = resp.read().decode('utf-8', errors='replace')
            papers = []
            # Simple XML parsing for RSS items
            items = re.findall(r'<item>(.*?)</item>', rss_data, re.DOTALL)
            for item in items[:max_results]:
                title_m = re.search(r'<title>(.*?)</title>', item)
                link_m = re.search(r'<link>(.*?)</link>', item)
                desc_m = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
                auth_m = re.search(r'<author>(.*?)</author>', item)
                date_m = re.search(r'<pubDate>(.*?)</pubDate>', item)
                
                title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else ''
                papers.append({
                    'title': title,
                    'url': link_m.group(1).strip() if link_m else '',
                    'authors': auth_m.group(1).strip() if auth_m else '',
                    'description': re.sub(r'<[^>]+>', '', desc_m.group(1)).strip()[:200] if desc_m else '',
                    'date': date_m.group(1).strip() if date_m else '',
                    'source': f'CNKI期刊({journal_code})',
                })
            if papers:
                return papers
    except Exception as e:
        logger.debug(f"CNKI RSS failed: {e}")
    
    # Fallback: scrape journal page
    navi_url = f'https://navi.cnki.net/knavi/journals/{journal_code}/yearList?pIdx=0'
    try:
        req = urllib.request.Request(navi_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
            # Extract year/issue code
            code_m = re.search(r'<a[^>]*value="([^"]+)"', html)
            if not code_m:
                return []
            code = code_m.group(1)
            
            # Get papers for this issue
            paper_url = f'https://navi.cnki.net/knavi/journals/{journal_code}/papers?yearIssue={code}&pageIdx=0&pcode=CJFD,CCJD'
            req2 = urllib.request.Request(paper_url, headers={'User-Agent': 'Mozilla/5.0'}, method='POST')
            with urllib.request.urlopen(req2, timeout=15) as resp2:
                html2 = resp2.read().decode('utf-8', errors='replace')
                return _parse_results(html2)
    except Exception as e:
        logger.debug(f"CNKI journal fallback failed: {e}")
    
    return []


def get_paper_detail(filename: str) -> Optional[dict]:
    """Get detailed info for a CNKI paper by filename.
    
    Args:
        filename: CNKI filename (from search results)
    
    Returns:
        Paper detail dict with abstract
    """
    url = f'https://cnki.net/kcms/detail/detail.aspx?filename={filename}&dbcode=CJFD'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
            
            # Extract abstract
            abs_m = re.search(r'class="abstract-text"[^>]*>(.*?)</(?:div|span)>', html, re.DOTALL)
            abstract = re.sub(r'<[^>]+>', '', abs_m.group(1)).strip() if abs_m else ''
            
            # Extract keywords
            kw_m = re.search(r'关键词[：:]\s*(.*?)</', html, re.DOTALL)
            keywords = re.sub(r'<[^>]+>', '', kw_m.group(1)).strip() if kw_m else ''
            
            return {
                'url': url,
                'abstract': abstract[:500],
                'keywords': keywords[:200],
            }
    except Exception as e:
        logger.debug(f"CNKI detail error: {e}")
    return None
