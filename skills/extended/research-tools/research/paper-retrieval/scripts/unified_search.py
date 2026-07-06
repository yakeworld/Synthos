#!/usr/bin/env python3
"""
Unified Academic Literature Search Entry Point
===============================================
支持字段检索的学术论文检索统一入口。8 大数据库源。

用法:
    # 简单查询
    python3 unified_search.py "breast cancer diagnosis" --db crossref pubmed --limit 5

    # 字段过滤
    python3 unified_search.py "attention is all you need" author:vaswani --db crossref

    # DOI 精确检索
    python3 unified_search.py doi:10.1038/s41586-019-1799-6

    # 标题精确匹配
    python3 unified_search.py "title:attention is all you need" author:vaswani year:2017 --db crossref openalex

    # 批量检索
    python3 unified_search.py --batch queries.txt --db all --out results.json
"""

import argparse, json, os, re, sys, time, urllib.parse, urllib.request

# ─── DB config ────────────────────────────────────────────────────

_S2_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
_S2_FALLBACK_KEY = os.environ.get("S2_FALLBACK_KEY", "")
_S2_KEYS = [k for k in [_S2_API_KEY, _S2_FALLBACK_KEY] if k]

_CROSSREF_URL = "https://api.crossref.org/works"

# ─── Source imports ────────────────────────────────────────────────

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multi_source_search import search_semantic_scholar as search_s2
from openalex_search import search as search_openalex

# Load arxiv and pubmed by absolute path
_ARXIV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'arxiv', 'scripts', 'search_arxiv.py')
_PUBMED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pubmed', 'scripts', 'pubmed-urllib.py')

import importlib.util

def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    if spec and spec.loader:
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return mod

_search_arxiv_mod = _load_module(_ARXIV_PATH, 'search_arxiv') if os.path.exists(_ARXIV_PATH) else None
_search_pubmed_mod = _load_module(_PUBMED_PATH, 'pubmed_urllib') if os.path.exists(_PUBMED_PATH) else None


# ─── OpenAlex adapter ─────────────────────────────────────────────

def _search_openalex(keywords, limit=10, timeout=15, author=None):
    """Adapter: 统一参数 -> OpenAlex search() 签名"""
    try:
        result = search_openalex(query=keywords, author=author or None, max_results=limit)
        papers = []
        for w in result.get("works", []):
            # Authors
            authors = []
            for a in (w.get("authorships") or []):
                name = (a.get("author") or {}).get("display_name", "")
                if name:
                    authors.append(name)
                    if len(authors) >= 10:
                        break
            # DOI
            doi = w.get("doi", "") or ""
            if doi and not doi.startswith("http"):
                doi = f"https://doi.org/{doi}"
            # Journal
            journal = ""
            issn = ""
            pl = w.get("primary_location")
            if pl and pl.get("source"):
                journal = pl["source"].get("display_name", "")
                issn = pl["source"].get("issn", "")
            # Year
            year = w.get("publication_year", "")
            if year and isinstance(year, int):
                year = str(year)
            # Open access
            oa = w.get("open_access") or {}
            is_oa = False
            oa_url = ""
            oa_source = ""
            if isinstance(oa, dict):
                is_oa = oa.get("is_oa", False)
                oa_url = oa.get("oa_url", "")
                src = oa.get("oa_source", {})
                if isinstance(src, dict):
                    oa_source = src.get("name", "")
            # OA fulltext
            oa_fulltext = ""
            boa = w.get("best_oa_location")
            if boa and isinstance(boa, dict):
                oa_fulltext = boa.get("pdf_url", "")
            # Keywords
            kw_list = [k for k in (w.get("keywords") or []) if isinstance(k, str)][:20]
            # Primary topic
            pt = w.get("primary_topic") or {}
            topic_name = pt.get("display_name", "") if isinstance(pt, dict) else ""
            topic_doi = pt.get("doi", "") if isinstance(pt, dict) else ""

            papers.append({
                "title": w.get("title", ""),
                "authors": authors,
                "year": year,
                "doi": doi,
                "journal": journal,
                "journal_issn": issn,
                "url": doi or "",
                "source": "openalex",
                "abstract": "",
                "cited_by": w.get("cited_by_count") or 0,
                "is_oa": is_oa,
                "oa_url": oa_url,
                "oa_source": oa_source,
                "oa_fulltext_url": oa_fulltext,
                "keywords": kw_list,
                "primary_topic": topic_name,
                "primary_topic_doi": topic_doi,
                "openalex_id": w.get("id", ""),
            })
        return papers[:limit]
    except Exception as e:
        print(f"  openalex: ERROR - {e}", file=sys.stderr)
        return []


# ─── PubMed adapter ────────────────────────────────────────────────

def _search_pubmed(keywords, limit=10, timeout=15, date_range=None):
    """PubMed: search -> esummary detail fetch -> unified format"""
    # Adjust params
    retmax = min(limit, 5)
    extra_params = {}
    if date_range:
        extra_params["date_range"] = date_range
    try:
        search_fn = _search_pubmed_mod.search if _search_pubmed_mod else None
        if not search_fn:
            return []
        count, pmids = search_fn(keywords, date_range=date_range, retmax=retmax) if keywords else (0, [])
    except Exception:
        return []

    results = []
    if not pmids:
        return []
    # Fetch detail via esummary
    try:
        ids_str = ",".join(pmids[:retmax])
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read())
        docs = data.get("result", {})
        for pmid in list(docs.keys())[:retmax]:
            if pmid == "uids":
                continue
            doc = docs[pmid]
            title = doc.get("title", "")
            if not title:
                continue
            pubdate = doc.get("pubdate", "")
            epubdate = doc.get("epubdate", "")
            year = pubdate[:4] if pubdate and len(pubdate) >= 4 else ""
            source_str = doc.get("source", "")
            authors = []
            for a in doc.get("authors", []):
                aname = a.get("name", "") if isinstance(a, dict) else str(a)
                if aname:
                    authors.append(aname)
            # DOI
            doi = ""
            for aid in doc.get("articleids", []):
                if isinstance(aid, dict) and aid.get("idtype") == "doi":
                    doi = aid.get("value", "")
                    break
            if not doi:
                eloc = doc.get("elocationid", "")
                if eloc.startswith("doi: "):
                    doi = eloc[5:].strip()
            volume = doc.get("volume", "")
            issue = doc.get("issue", "")
            pages = doc.get("pages", "")
            journal_full = doc.get("fulljournalname", "")
            lang = ", ".join(doc.get("lang", [])) if doc.get("lang") else ""
            issn = doc.get("issn", "")
            essn = doc.get("essn", "")
            pubstatus = doc.get("pubstatus", "")
            attributes = doc.get("attributes", [])
            has_abstract = "Has Abstract" in attributes
            references_count = len(doc.get("references", []))
            history = doc.get("history", [])
            results.append({
                "title": title,
                "authors": authors[:10],
                "year": year,
                "doi": doi,
                "journal": source_str,
                "journal_full": journal_full,
                "pmid": pmid,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "source": "pubmed",
                "abstract": "",
                "pubdate": pubdate,
                "epubdate": epubdate,
                "volume": volume,
                "issue": issue,
                "pages": pages,
                "lang": lang,
                "issn": issn,
                "pubstatus": pubstatus,
                "has_abstract": has_abstract,
                "references_count": references_count,
                "history": history,
            })
    except Exception as e:
        print(f"  pubmed: detail fetch error - {e}", file=sys.stderr)
    return results


# ─── CrossRef ──────────────────────────────────────────────────────

def _search_crossref(keywords, limit=10, timeout=15, author=None):
    """CrossRef via subprocess curl"""
    params = (
        f"query.title={urllib.parse.quote(keywords)}"
        f"&rows={limit}"
        f"&sort=relevance"
        f"&select=title,author,DOI,container-title,issued,link,reference,license,alternative-id"
    )
    if author:
        params += f"&query.author={urllib.parse.quote(author)}"
    url = f"{_CROSSREF_URL}?{params}"
    try:
        r = __import__('subprocess').run(
            ["curl", "-s", "-w", "\n%{http_code}", url,
             "-H", "Accept: application/json",
             "-H", "User-Agent: Synthos/1.0"],
            capture_output=True, text=True, timeout=timeout
        )
        lines = r.stdout.strip().split("\n")
        code = int(lines[-1]) if lines else 0
        body = "\n".join(lines[:-1])
        if code != 200:
            return []
        data = json.loads(body)
    except (json.JSONDecodeError, ValueError, __import__('subprocess').TimeoutExpired):
        return []

    items = data.get("message", {}).get("items", [])
    if not items:
        return []

    results = []
    for item in items:
        title_list = item.get("title") or []
        title = title_list[0] if title_list else ""
        if not title:
            continue
        authors = []
        for al in item.get("author", []):
            name = f"{al.get('given', '')} {al.get('family', '')}".strip()
            if name:
                authors.append(name)
        doi = item.get("DOI", "") or ""
        journal = (item.get("container-title") or [""])[0] if item.get("container-title") else ""
        issued = item.get("issued", {}) or item.get("published-print", {})
        year = (issued.get("date-parts", [[]])[0][0] if issued.get("date-parts") else "")
        ref_count = item.get("reference", []) or []
        license_info = item.get("license", []) or []
        license_url = license_start = ""
        for lic in license_info:
            if isinstance(lic, dict) and lic.get("URL"):
                license_url = lic["URL"]
                s = lic.get("start", "")
                if s:
                    license_start = str(s)
                break
        alt_ids = item.get("alternative-id", []) or []
        results.append({
            "title": title,
            "authors": authors[:10],
            "year": year,
            "doi": doi,
            "journal": journal,
            "url": doi,
            "source": "crossref",
            "abstract": "",
            "reference_count": len(ref_count),
            "cited_by": 0,
            "license_url": license_url,
            "license_start": license_start,
            "alternative_ids": alt_ids,
        })
    return results[:limit]


# ─── Semantic Scholar ──────────────────────────────────────────────

def _search_s2(keywords, limit=10, timeout=15, author=None):
    """Semantic Scholar — 需要 API key"""
    if not _S2_KEYS:
        print(f"  s2: NO API KEY SET", file=sys.stderr)
        return []
    # Use first available key (round-robin could be added)
    headers = {
        "Accept": "application/json",
        "User-Agent": "Synthos/2.0 (academic-search)",
        "x-api-key": _S2_KEYS[0],
    }
    params = urllib.parse.urlencode({
        "query": keywords,
        "limit": str(min(limit, 20)),
        "fields": "title,authors,year,abstract,citationCount,externalIds,openAccessPdf,venue",
    })
    if author:
        params += f"&authors={urllib.parse.quote(author)}"
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  s2: ERROR - {e}", file=sys.stderr)
        # Try fallback key
        if len(_S2_KEYS) > 1:
            headers["x-api-key"] = _S2_KEYS[1]
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read())
            except Exception as e2:
                print(f"  s2: FALLBACK KEY ERROR - {e2}", file=sys.stderr)
                return []
        else:
            return []

    papers = []
    for p in data.get("data", [])[:limit]:
        authors = [a["name"] for a in p.get("authors", [])]
        abstract = (p.get("abstract") or "").strip()
        if len(abstract) > 2000:
            abstract = abstract[:2000] + "..."
        ext = p.get("externalIds") or {}
        doi = ext.get("DOI", "") or ""
        # Get OA PDF URL
        pdf_url = ""
        oa_pdf = p.get("openAccessPdf")
        if oa_pdf and isinstance(oa_pdf, dict):
            pdf_url = oa_pdf.get("url", "")
        citation_count = p.get("citationCount", 0)
        papers.append({
            "title": p.get("title", ""),
            "authors": authors[:10],
            "year": p.get("year") or "",
            "doi": doi,
            "journal": p.get("venue", ""),
            "url": f"https://www.semanticscholar.org/paper/{p.get('paperId', '')}",
            "source": "s2",
            "abstract": abstract,
            "cited_by": citation_count,
            "pdf_url": pdf_url,
            "open_access": p.get("is_open_access", False),
            "external_ids": ext,
        })
    return papers[:limit]


# ─── arXiv ─────────────────────────────────────────────────────────

def _search_arxiv(keywords, limit=10, timeout=15, author=None):
    """arXiv search"""
    if not _search_arxiv_mod:
        return []
    try:
        result = _search_arxiv_mod.search(query=keywords, author=author, max_results=min(limit, 40), sort="relevance")
    except Exception as e:
        print(f"  arxiv: ERROR - {e}", file=sys.stderr)
        return []

    # result is parsed XML entries; the search function prints directly but we need JSON output
    # Let's do it directly:
    return _search_arxiv_direct(keywords, limit, timeout, author)


def _search_arxiv_direct(keywords, limit=10, timeout=15, author=None):
    """Direct arXiv XML parsing for JSON output"""
    try:
        import xml.etree.ElementTree as ET
        NS = {'a': 'http://www.w3.org/2005/Atom', 'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'}
        parts = [f'all:{urllib.parse.quote(keywords)}']
        if author:
            parts.append(f'au:{urllib.parse.quote(author)}')
        params = {
            'search_query': '+AND+'.join(parts),
            'max_results': str(min(limit, 40)),
            'sortBy': 'relevance',
            'sortOrder': 'descending',
        }
        url = "https://export.arxiv.org/api/query?" + "&".join(f"{k}={v}" for k, v in params.items())
        req = urllib.request.Request(url, headers={'User-Agent': 'Synthos/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        root = ET.fromstring(data)
        entries = root.findall('a:entry', NS)
    except Exception as e:
        print(f"  arxiv: ERROR - {e}", file=sys.stderr)
        return []

    results = []
    for entry in entries[:limit]:
        title = entry.find('a:title', NS).text.strip().replace('\n', ' ') if entry.find('a:title', NS) is not None else ""
        if not title:
            continue
        raw_id = entry.find('a:id', NS).text.strip() if entry.find('a:id', NS) is not None else ""
        full_id = raw_id.split('/abs/')[-1] if '/abs/' in raw_id else raw_id
        arxiv_id = full_id.split('v')[0]
        published = entry.find('a:published', NS).text[:10] if entry.find('a:published', NS) is not None else ""
        updated = entry.find('a:updated', NS).text[:10] if entry.find('a:updated', NS) is not None else ""
        authors = [a.find('a:name', NS).text for a in entry.findall('a:author', NS) if a.find('a:name', NS) is not None]
        summary = entry.find('a:summary', NS).text.strip().replace('\n', ' ') if entry.find('a:summary', NS) is not None else ""
        cats = [c.get('term') for c in entry.findall('a:category', NS)]
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
        abs_url = f"https://arxiv.org/abs/{arxiv_id}"

        results.append({
            "title": title,
            "authors": authors,
            "year": published[:4] if published else "",
            "doi": "",
            "journal": "",
            "url": abs_url,
            "source": "arxiv",
            "abstract": summary,
            "cited_by": 0,
            "arxiv_id": arxiv_id,
            "arxiv_full_id": full_id,
            "arxiv_url_pdf": pdf_url,
            "arxiv_url_abs": abs_url,
            "arxiv_categories": cats,
            "published": published,
            "updated": updated,
        })
    return results[:limit]


# ─── DOAJ ──────────────────────────────────────────────────────────

def _search_doaj(keywords, limit=10, timeout=15, author=None):
    """DOAJ - Directory of Open Access Journals"""
    url = f"https://doaj.org/api/search/articles/v2?query={urllib.parse.quote(keywords)}&size={min(limit, 10)}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  doaj: ERROR - {e}", file=sys.stderr)
        return []

    results = []
    for doc in data.get("results", [])[:limit]:
        bib = doc.get("bibjson", {})
        title = bib.get("title", "")
        if not title:
            continue
        authors = []
        for a in bib.get("author", [])[:10]:
            if isinstance(a, dict):
                name = a.get("name", "")
                if name:
                    authors.append(name)
            elif isinstance(a, str):
                authors.append(a)
        year = bib.get("year", "")
        journal_obj = bib.get("journal", {})
        journal_name = ""
        journal_issn = ""
        if isinstance(journal_obj, dict):
            journal_name = journal_obj.get("title-short", "") or journal_obj.get("title", "")
            for issn_item in journal_obj.get("issn", []):
                if isinstance(issn_item, dict) and issn_item.get("media_type") == "electronic":
                    journal_issn = issn_item.get("$", "")
                elif isinstance(issn_item, str):
                    journal_issn = issn_item
                    break
        links = bib.get("links", {})
        html_url = links.get("html", "") or ""
        doi = ""
        for ident in bib.get("identifier", []):
            if isinstance(ident, dict) and ident.get("type") == "doi":
                doi = ident.get("id", "")
                break
        results.append({
            "title": title,
            "authors": authors[:10],
            "year": str(year) if year else "",
            "doi": doi,
            "journal": journal_name,
            "url": html_url,
            "source": "doaj",
            "abstract": "",
            "cited_by": 0,
            "is_oa": True,
            "journal_issn": journal_issn,
        })
    return results[:limit]


# ─── Unpaywall ─────────────────────────────────────────────────────


# ─── DB Map ────────────────────────────────────────────────────────

_DB_MAP = {
    "s2": _search_s2,
    "crossref": _search_crossref,
    "openalex": _search_openalex,
    "pubmed": _search_pubmed,
    "arxiv": _search_arxiv,
    "doaj": _search_doaj,
    }


# ─── Field parser ──────────────────────────────────────────────────

def parse_query(raw):
    """
    解析查询字符串中的字段过滤。
    返回: (keywords: str, fields: dict)
    """
    raw = raw.strip()
    if raw.startswith("doi:"):
        return (raw[4:].strip(), {"_is_doi": True})
    if re.match(r'^10\.\d{4,}/', raw):
        return (raw, {"_is_doi": True})

    fields = {}
    keywords_parts = []
    current_field = None
    current_value = []

    for token in raw.split():
        m = re.match(r'^(title|author|year|journal|doi|volume|issue):(.+)$', token, re.IGNORECASE)
        if m:
            if current_field and current_value:
                val = ' '.join(current_value)
                if current_field == "doi":
                    fields["_is_doi"] = True
                    fields["doi"] = val
                else:
                    fields[current_field] = val
            current_field = m.group(1).lower()
            current_value = [m.group(2)]
        else:
            if current_field:
                current_value.append(token)
            else:
                keywords_parts.append(token)

    if current_field and current_value:
        val = ' '.join(current_value)
        if current_field == "doi":
            fields["_is_doi"] = True
            fields["doi"] = val
        else:
            fields[current_field] = val

    return (' '.join(keywords_parts), fields)


# ─── Unified search ────────────────────────────────────────────────

def search_with_fields(query, databases=None, max_results=50, max_time=60):
    """
    统一检索入口 — 支持字段过滤。

    返回: list[dict] — 每篇: title, authors, year, doi, source, url, abstract, cited_by, + source-specific fields
    """
    if databases is None:
        databases = ["crossref", "openalex"]

    keywords, fields = parse_query(query)

    all_papers = []
    seen_titles = set()
    t_start = time.time()

    for db in databases:
        if time.time() - t_start > max_time:
            break

        search_fn = _DB_MAP.get(db)
        if not search_fn:
            print(f"  {db}: UNKNOWN DB", file=sys.stderr)
            continue

        try:
            t0 = time.time()
            extra = {"limit": max_results, "timeout": max_time}

            # --- Source-specific field handling ---
            if db == "crossref":
                if fields.get("_is_doi"):
                    extra["limit"] = 1
                    keywords = fields.get("doi", keywords)
                elif fields.get("_is_title"):
                    keywords = fields.get("title", keywords)
                if "author" in fields:
                    extra["author"] = fields["author"]

            elif db == "s2":
                if "author" in fields:
                    extra["author"] = fields["author"]

            elif db == "openalex":
                if "author" in fields:
                    extra["author"] = fields["author"]

            elif db == "pubmed":
                if "author" in fields:
                    keywords = f"{keywords} author:{fields['author']}"
                if "year" in fields:
                    extra["date_range"] = f"{fields['year']}/pd"
                # PubMed: limit -> retmax internally, but _search_pubmed uses 'limit' param
                # Keep 'limit' for _search_pubmed, 'date_range' also passed
                pass

            elif db == "arxiv":
                if "author" in fields:
                    extra["author"] = fields["author"]

            # --- Execute search ---
            if db == "crossref":
                results = _search_crossref(keywords, **extra) if keywords else []
            elif db == "pubmed":
                results = _search_pubmed(keywords, **extra) if keywords else []
            elif db == "s2":
                results = _search_s2(keywords, **extra) if keywords else []
            elif db == "arxiv":
                results = _search_arxiv(keywords, **extra) if keywords else []
            elif db == "doaj":
                results = _search_doaj(keywords, **extra) if keywords else []
            else:
                results = search_fn(keywords, **extra) if keywords else []

            # --- Post-processing ---
            # Year filter
            if "year" in fields:
                results = [p for p in results if p.get("year") and str(p["year"]) == fields["year"]]

            elapsed = time.time() - t0
            for p in results:
                p["source"] = db
                title = p.get("title", "").strip()
                if not title:
                    continue
                norm = title.lower()
                if norm not in seen_titles:
                    seen_titles.add(norm)
                    all_papers.append(p)

            print(f"  {db}: {len(results)} results ({elapsed:.1f}s)", file=sys.stderr)

        except Exception as e:
            print(f"  {db}: ERROR - {e}", file=sys.stderr)

        # Rate limiting
        if db in ("s2", "pubmed"):
            time.sleep(1.0)
        else:
            time.sleep(0.3)

    return all_papers


# ─── CLI ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="统一学术文献检索 — 支持字段过滤",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
查询语法:
  简单:          python3 unified_search.py "breast cancer"
  作者过滤:      python3 unified_search.py "attention is all you need" author:vaswani
  DOI 检索:      python3 unified_search.py doi:10.1038/s41586-019-1799-6
  标题匹配:      python3 unified_search.py "title:attention is all you need"
  组合:          python3 unified_search.py "deep learning" author:hinton year:2017

数据库源:
  s2        Semantic Scholar (需要 SEMANTIC_SCHOLAR_API_KEY)
  crossref  CrossRef DOI 元数据 (无需密钥)
  openalex  OpenAlex 开放学术图谱 (无需密钥)
  pubmed    PubMed 生物医学数据库 (无需密钥)
  arxiv     arXiv 预印本 (无需密钥)
  doaj      DOAJ 开放获取期刊 (无需密钥)

支持字段: title, author, year, doi, journal, volume, issue
  - 字段以 field:value 形式追加在关键词查询之后
  - bare 'doi:xxx' 或 '10.xxx' 为 DOI 精确检索
  - bare 'title:xxx' 为标题精确匹配

示例:
  python3 unified_search.py "attention is all you need" author:vaswani --db crossref openalex
  python3 unified_search.py doi:10.1038/s41586-019-1799-6
  python3 unified_search.py --batch queries.txt --db all --out results.json
        """
    )
    parser.add_argument("query", nargs="*", default=[],
                        help="查询词（支持空格）+ 可选字段（author:x year:y doi:z）")
    parser.add_argument("--db", nargs="+", default=["crossref", "openalex"],
                        help="数据库源（默认: crossref openalex）")
    parser.add_argument("--limit", type=int, default=50, help="最大结果数")
    parser.add_argument("--out", default="search-results.json", help="输出 JSON 文件")
    parser.add_argument("--batch", default=None, help="批量文件（每行一个查询）")
    parser.add_argument("--timeout", type=int, default=60, help="每源超时秒数")
    parser.add_argument("--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    # Build query list
    queries = []
    if args.query:
        queries = [' '.join(args.query)]
    elif args.batch:
        with open(args.batch) as f:
            queries = [line.strip() for line in f if line.strip()]

    if not queries:
        print("ERROR: 需要 --query, --batch, --doi, 或 --title", file=sys.stderr)
        sys.exit(1)

    if args.db and args.db[0] == "all":
        args.db = ["s2", "crossref", "openalex", "pubmed", "arxiv", "doaj"]

    all_results = []
    for i, q in enumerate(queries):
        print(f"\n[{i+1}/{len(queries)}] {q}", file=sys.stderr)
        papers = search_with_fields(q, databases=args.db,
                                     max_results=args.limit, max_time=args.timeout)
        all_results.extend(papers)
        if args.verbose:
            for p in papers:
                print(f"  {p['title'][:80]} ({p['source']})")

    with open(args.out, "w") as f:
        json.dump({
            "total_queries": len(queries),
            "total_papers": len(all_results),
            "papers": all_results,
        }, f, indent=2, ensure_ascii=False)

    print(f"\nTotal: {len(all_results)} papers -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
