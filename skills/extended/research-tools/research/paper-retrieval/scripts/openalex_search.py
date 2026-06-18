#!/usr/bin/env python3
"""
OpenAlex Search - 学术论文数据库搜索
250M+论文, 无需API key, 无速率限制

API quirks (v53+):
- sort=relevancy 永远返回 0 -> 必须用 sort=cited_by_count + filter=cited_by_count:1-
- count 在 meta.count, 不在根级别
- Python 3.12 urllib.parse.quote(query, safe='+') 保留+并编码空格
- per_page 最大 200 (默认 25)
- 所有 filter 参数必须合并为单个 filter= 查询字符串
"""
import sys
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Optional

BASE = 'https://api.openalex.org'

def search(
    query: str = None,
    doi: str = None,
    author: str = None,
    from_publication_date: str = None,
    to_publication_date: str = None,
    cited_by_count_gte: int = None,
    max_results: int = 25,
    sort: str = 'cited_by_count',
    additional_filters: dict = None,
) -> dict:
    """
    Search OpenAlex works.
    
    Returns {works: list[dict], count: int, used_query: str}
    """
    filter_parts = ['cited_by_count:1-']  # Always filter zero-citation papers
    
    params = {'per_page': str(min(max_results, 200))}
    
    if doi:
        params['doi'] = doi
    else:
        if query:
            # Python 3.12: use quote(query, safe='+') to keep + as-space
            encoded = urllib.parse.quote(query, safe='+')
            params['search'] = encoded
        if author:
            filter_parts.append(f'author_names:{author}')
        if from_publication_date:
            params['from_publication_date'] = from_publication_date
        if to_publication_date:
            params['to_publication_date'] = to_publication_date
    
    if cited_by_count_gte:
        filter_parts.append(f'cited_by_count:{cited_by_count_gte}-')
    
    if additional_filters:
        for k, v in additional_filters.items():
            filter_parts.append(f'{k}:{v}-')
    
    params['filter'] = ','.join(filter_parts)
    params['sort'] = sort
    
    url = f'{BASE}/works?' + '&'.join(f'{k}={v}' for k, v in params.items())
    req = urllib.request.Request(url, headers={
        'Accept': 'application/json',
        'User-Agent': 'SynthosAgent/2.0'
    })
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    
    works = data.get('results', [])
    count = data.get('meta', {}).get('count', len(works))
    
    formatted = []
    for w in works:
        entry = {
            'title': w.get('title', 'N/A'),
            'doi': w.get('doi', 'N/A'),
            'authors': [],
            'year': None,
            'cited_by_count': w.get('cited_by_count', 0),
            'journal': None,
            'abstract_inverted_index': w.get('abstract_inverted_index'),
            'url': w.get('best_oa_location', {}).get('url') if w.get('best_oa_location') else None,
            'open_access': w.get('open_access', {}).get('is_oa', False),
            'source': 'openalex',
            'provenance': f'source=openalex, query={query or doi or "N/A"}, api_status=ok',
        }
        
        authorships = w.get('authorships', [])
        if authorships:
            entry['authors'] = [
                a.get('author', {}).get('display_name', 'Unknown')
                for a in authorships[:10]
            ]
        
        pub_date = w.get('publication_date', '')
        if pub_date:
            entry['year'] = pub_date[:4]
        
        primary_loc = w.get('primary_location', {})
        source = primary_loc.get('source', {})
        if source:
            entry['journal'] = source.get('display_name', '')
        
        formatted.append(entry)
    
    return {'works': formatted, 'count': count, 'used_query': url}


def get_work_by_doi(doi: str) -> Optional[dict]:
    """Get a single work by DOI."""
    url = f'{BASE}/works/{doi}'
    req = urllib.request.Request(url, headers={
        'Accept': 'application/json',
        'User-Agent': 'SynthosAgent/2.0'
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data


def get_citations(doi: str, max_results: int = 25) -> List[dict]:
    """Get citations for a work."""
    url = f'{BASE}/works/{doi}/cited_by?per_page={min(max_results, 200)}&sort=cited_by_count&filter=cited_by_count:1-'
    req = urllib.request.Request(url, headers={
        'Accept': 'application/json',
        'User-Agent': 'SynthosAgent/2.0'
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data.get('results', [])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='OpenAlex Search')
    parser.add_argument('query', nargs='?', default=None, help='Search query')
    parser.add_argument('--doi', default=None, help='Get work by DOI')
    parser.add_argument('--author', default=None, help='Filter by author')
    parser.add_argument('--cited-gte', type=int, default=None, help='Min cited by count')
    parser.add_argument('--max', type=int, default=10, help='Max results')
    parser.add_argument('--sort', default='cited_by_count', choices=['cited_by_count', 's2_standard'])
    args = parser.parse_args()
    
    if args.doi:
        work = get_work_by_doi(args.doi)
        print(json.dumps(work, indent=2, ensure_ascii=False)[:5000])
    elif args.query:
        result = search(args.query, max_results=args.max, sort=args.sort, cited_by_count_gte=args.cited_gte)
        print(json.dumps(result, indent=2, ensure_ascii=False)[:5000])
    else:
        print('Usage: python openalex_search.py <query> or --doi <doi>')
        sys.exit(1)
