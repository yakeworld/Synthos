#!/usr/bin/env python3
"""
Google Scholar 文献检索 — 学术搜索
通过 Tor SOCKS5H 访问 Google Scholar，支持论文搜索、引用数、作者检索。

注意：Google Scholar 无官方 API，有反爬机制，需要：
1. 合理请求频率（建议 5-10 秒间隔）
2. Tor 出口 IP（避免封禁）
3. 正确的 User-Agent
4. 分页解析（每页 10 条）
"""
import re
import json
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urljoin
from urllib import parse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def get_proxy():
    import os
    return {"http": os.environ.get("TOR_PROXY", "socks5h://127.0.0.1:9050"),
            "https": os.environ.get("TOR_PROXY", "socks5h://127.0.0.1:9050")}


def _build_params(params: dict) -> str:
    """Build URL query string safely."""
    parts = []
    for k, v in params.items():
        parts.append(f"{k}={quote_plus(str(v))}")
    return "&".join(parts)


def search(
    query: str,
    max_results: int = 10,
    sort_by: str = "relevance",
    start: int = 0,
    as_ylo: str = None,
    as_yhi: str = None,
    author: str = None,
    tor_proxy: bool = True,
) -> Dict:
    """Search Google Scholar."""
    if not query:
        return {"results": [], "total": 0, "query": query, "sort_by": sort_by}

    base = "https://scholar.google.com/scholar"
    params = {
        "q": query,
        "hl": "en",
        "as_sdt": "0,5",
        "start": start,
    }
    if sort_by == "date":
        params["sdtp"] = "a"
    if as_ylo:
        params["as_ylo"] = str(as_ylo)
    if as_yhi:
        params["as_yhi"] = str(as_yhi)
    if author:
        params["q"] = f"{query} author:{author}"

    query_str = _build_params(params)
    url = f"{base}?{query_str}"

    import requests

    proxies = get_proxy() if tor_proxy else None
    headers = DEFAULT_HEADERS.copy()

    results = []
    total = 0

    try:
        resp = requests.get(url, headers=headers, proxies=proxies,
                           timeout=30, allow_redirects=True)

        if resp.status_code == 403 or "captcha" in resp.text.lower():
            logger.warning("Google Scholar CAPTCHA detected, rate limited, or IP blocked")
            return {"results": [], "total": 0, "query": query, "sort_by": sort_by,
                    "error": "CAPTCHA or rate limit"}

        if resp.status_code != 200:
            logger.warning(f"HTTP {resp.status_code} from Google Scholar")
            return {"results": [], "total": 0, "query": query, "sort_by": sort_by,
                    "error": f"HTTP {resp.status_code}"}

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")

        # Parse total results
        info_div = soup.find("div", id="gs_res_cfnr")
        if info_div:
            msg = info_div.get_text()
            m = re.search(r"(\d[\d,]*)", msg)
            if m:
                total = int(m.group(1).replace(",", ""))

        # Parse results
        for g in soup.select("#gs_res_ccl .gs_r.gs_or.gs_scl"):
            paper = _parse_result(g)
            if paper:
                results.append(paper)

        logger.info(f"GS results: {len(results)} papers, total estimated: {total}")

    except Exception as e:
        logger.error(f"Google Scholar search failed: {e}")

    return {
        "results": results,
        "total": total,
        "query": query,
        "sort_by": sort_by,
        "error": None,
    }


def _parse_result(g) -> Optional[Dict]:
    """Parse a single GS result element."""
    title_el = g.select_one(".gs_rt a")
    if not title_el:
        return None

    title = title_el.get_text().strip()
    url = title_el.get("href", "")

    # If href is a hash, follow the link
    if url.startswith("#"):
        meta_div = g.select_one(".gs_r .gs_r-h, .gs_r .gs_r a[href^=http]")
        if meta_div:
            href = meta_div.get("href")
            if href and href.startswith("http"):
                url = href

    abstr_el = g.select_one(".gs_rs")
    abstract = abstr_el.get_text().strip() if abstr_el else ""

    authors = ""
    year = ""
    cites = "0"
    cited_by_url = None

    meta_el = g.select_one(".gs_a")
    if meta_el:
        meta_text = meta_el.get_text()
        parts = meta_text.split("-")
        if len(parts) >= 2:
            authors = parts[0].strip()

        cite_el = g.select_one(".gs_fl a[href*=cites]")
        if cite_el:
            cites = cite_el.get_text().strip()
            cited_by_url = cite_el.get("href", "")
            m = re.search(r"as_opubd_year=(\d{4})", cited_by_url)
            if m:
                year = m.group(1)

    if not year:
        m = re.search(r"(\d{4})", meta_text if meta_text else "")
        if m:
            year = m.group(1)

    return {
        "title": title,
        "url": url,
        "abstract": abstract,
        "authors": authors,
        "year": year,
        "citation_count": cites,
        "cited_by_url": cited_by_url,
        "source": "google_scholar",
    }


def get_citation_count(doi: str, title: str = None, author: str = None) -> Dict:
    """Get citation count for a paper by searching GS."""
    search_query = title or f"doi:{doi}"
    result = search(search_query, max_results=1)
    if result.get("results"):
        paper = result["results"][0]
        return {
            "title": paper["title"],
            "cited_by_url": paper.get("cited_by_url"),
            "citation_count_raw": paper.get("citation_count", "0"),
            "source": "google_scholar",
        }
    return {"error": "Paper not found in Google Scholar", "source": "google_scholar"}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Google Scholar Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max", type=int, default=10, help="Max results")
    parser.add_argument("--sort", choices=["relevance", "date"], default="relevance")
    parser.add_argument("--year-from", type=int, default=None)
    parser.add_argument("--year-to", type=int, default=None)
    parser.add_argument("--author", default=None)
    parser.add_argument("--no-tor", action="store_true")
    parser.add_argument("--output", "-o", default=None)

    args = parser.parse_args()

    result = search(
        args.query, max_results=args.max, sort_by=args.sort,
        as_ylo=args.year_from, as_yhi=args.year_to,
        author=args.author, tor_proxy=not args.no_tor,
    )

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Results saved to {args.output}")
    else:
        print(output)
