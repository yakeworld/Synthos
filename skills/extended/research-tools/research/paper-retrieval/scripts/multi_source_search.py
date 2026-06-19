#!/usr/bin/env python3
"""
Multi-source Academic Literature Search Engine
================================================
Synthos Knowledge Acquisition Atom (格物) — Execution Script

Searches 4 academic sources (Semantic Scholar, PubMed, OpenAlex, arXiv)
and outputs a unified JSON compatible with Synthos SKILL.md IO_CONTRACT.

Usage:
    python3 multi_source_search.py "llm reasoning chain of thought"
    python3 multi_source_search.py "llm reasoning" --max 10
    python3 multi_source_search.py "query" --sources pubmed,openalex
    python3 multi_source_search.py "query" --output result.json --verbose

Environment Variables:
    SEMANTIC_SCHOLAR_API_KEY  - API key for Semantic Scholar (required)

Exit Codes:
    0 - Success
    1 - All sources failed or invalid query
"""
import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import subprocess
import time
import re
from typing import List, Dict, Optional, Any

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
PUBMED_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
PUBMED_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OPENALEX_URL = "https://api.openalex.org/works"
ARXIV_URL = "https://export.arxiv.org/api/query"

DEFAULT_MAX_RESULTS = 5
DEFAULT_SOURCES = ["semantic_scholar", "pubmed", "openalex", "arxiv"]
S2_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

ARXIV_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def search_semantic_scholar(query, max_results=DEFAULT_MAX_RESULTS, use_api_key=True):
    if use_api_key and not S2_API_KEY:
        return {"papers": [], "error": "SEMANTIC_SCHOLAR_API_KEY not set"}
    params = urllib.parse.urlencode({
        "query": query, "limit": str(max_results),
        "fields": "title,authors,year,abstract,citationCount,externalIds,openAccessPdf,venue",
    })
    url = f"{SEMANTIC_SCHOLAR_URL}?{params}"
    headers = {"Accept": "application/json", "User-Agent": "Synthos/2.0 (academic-search)"}
    if use_api_key and S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        papers = []
        for p in data.get("data", [])[:max_results]:
            authors = [a["name"] for a in p.get("authors", [])]
            abstract = p.get("abstract") or "N/A"
            if isinstance(abstract, str) and len(abstract) > 500:
                abstract = abstract[:500] + "..."
            doi = (p.get("externalIds") or {}).get("DOI", "N/A")
            papers.append({
                "title": p.get("title", "N/A"), "authors": authors[:10],
                "year": p.get("year") or 0, "source": "semantic_scholar",
                "external_ids": {"DOI": doi, **(p.get("externalIds") or {})},
                "abstract": abstract,
                "url": f"https://www.semanticscholar.org/paper/{p.get('paperId', '')}",
                "pdf_url": (p.get("openAccessPdf") or {}).get("url"),
                "unique_id": {"s2_id": p.get("paperId", "")},
                "citation_count": p.get("citationCount", 0),
                "venue": p.get("venue"),
                "journal_name": p.get("venue", ""),
                "open_access": p.get("is_open_access", False),
                "relevance_score": 0.95,
                "provenance": f"source=semantic_scholar, query={query}, api_status=ok",
            })
        return {"papers": papers, "total": data.get("total", 0)}
    except urllib.error.HTTPError as e:
        return {"papers": [], "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"papers": [], "error": str(e)}


def _xml_tag(xml_data, tag):
    pattern = rf'<{tag}[^>]*>(.*?)</{tag}>'
    m = re.search(pattern, xml_data, re.DOTALL)
    return m.group(1).strip() if m else None


def search_pubmed(query, max_results=DEFAULT_MAX_RESULTS):
    safe_term = urllib.parse.quote_plus(query, safe="")
    search_url = f"{PUBMED_ESEARCH_URL}?db=pubmed&term={safe_term}&retmax=200&retmode=json"
    try:
        with urllib.request.urlopen(search_url, timeout=15) as resp:
            search_data = json.loads(resp.read())
    except Exception as e:
        return {"papers": [], "error": f"eSearch failed: {e}"}
    idlist = search_data.get("esearchresult", {}).get("idlist", [])
    if not idlist:
        return {"papers": [], "total": 0, "error": "No PMID results"}
    pmids = idlist[:max_results]
    summary_url = f"{PUBMED_ESUMMARY_URL}?db=pubmed&id={','.join(pmids)}&retmode=json"
    try:
        with urllib.request.urlopen(summary_url, timeout=30) as resp:
            summary_data = json.loads(resp.read())
    except Exception as e:
        return {"papers": [], "error": f"esummary failed: {e}"}
    # eFetch for abstracts
    abstract_map = {}
    try:
        fetch_url = f"{PUBMED_EFETCH_URL}?db=pubmed&id={','.join(pmids)}&rettype=abstract&retmode=text"
        with urllib.request.urlopen(fetch_url, timeout=30) as resp:
            xml_text = resp.read().decode("utf-8", errors="replace")
        for pmid in pmids:
            abs_text = _xml_tag(xml_text, "AbstractText") or ""
            abstract_map[pmid] = abs_text[:500] if abs_text else "N/A"
    except Exception:
        abstract_map = {pmid: "N/A (eFetch unavailable)" for pmid in pmids}
    result_section = summary_data.get("result", {})
    papers = []
    for pmid in pmids:
        entry = result_section.get(str(pmid), {})
        if not entry.get("title"):
            continue
        doi = "N/A"
        for aid in entry.get("articleids", []):
            if aid.get("idtype") == "doi":
                doi = aid["value"]
                break
        abstract = abstract_map.get(pmid, "N/A (eFetch unavailable)")
        # Get journal from eSummary
        source_journal = entry.get("source", "")
        # Check if OA via pubstatus (256 = OA)
        pubstatus = entry.get("pubstatus", "")
        is_oa = str(pubstatus) == "256" or bool(entry.get("fulljournalname"))
        papers.append({
            "title": entry.get("title", "N/A"),
            "authors": [a["name"] for a in entry.get("authors", [])][:10],
            "year": int(entry.get("pubdate", "").split()[0] or "0"),
            "source": "pubmed",
            "external_ids": {"PMID": pmid, "DOI": doi},
            "abstract": abstract,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "pdf_url": None,
            "unique_id": {"pmid": pmid},
            "citation_count": 0,
            "journal_name": source_journal,
            "open_access": is_oa,
            "relevance_score": 0.90,
            "provenance": f"source=pubmed, query={query}, api_status=ok",
        })
    return {"papers": papers, "total": len(papers)}


def _reconstruct_abstract(inverted_index):
    if not inverted_index or not isinstance(inverted_index, dict):
        return "N/A"
    pos_map = {}
    for word, positions in inverted_index.items():
        if isinstance(positions, list):
            for pos in positions:
                pos_map[pos] = word
        else:
            pos_map[positions] = word
    if not pos_map:
        return "N/A"
    abstract = " ".join(pos_map[i] for i in sorted(pos_map.keys()))
    return abstract[:500] if len(abstract) > 500 else abstract


def search_openalex(query, max_results=DEFAULT_MAX_RESULTS):
    encoded = urllib.parse.quote(query, safe="+")
    url = (
        f"{OPENALEX_URL}?search={encoded}"
        f"&per_page={min(max_results, 200)}"
        f"&select=title,authorships,abstract_inverted_index,"
        f"publication_year,cited_by_count,primary_location,doi,"
        f"open_access,best_oa_location,ids"
        f"&sort=cited_by_count"
    )
    try:
        req = urllib.request.Request(url, headers={
            "Accept": "application/json", "User-Agent": "Synthos/2.0 (academic-search)",
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        papers = []
        for p in data.get("results", [])[:max_results]:
            abstract = _reconstruct_abstract(p.get("abstract_inverted_index"))
            authors = [a.get("author", {}).get("display_name", "Unknown") for a in p.get("authorships", [])[:10]]
            doi = p.get("doi", "N/A")
            if doi and not doi.startswith("10."):
                doi = f"https://doi.org/{doi}"
            best_oa = p.get("best_oa_location")
            pdf_url = best_oa.get("pdf_url") if best_oa else None
            papers.append({
                "title": p.get("title", "N/A"), "authors": authors,
                "year": p.get("publication_year") or 0, "source": "openalex",
                "external_ids": {"DOI": doi, **(p.get("ids") or {})},
                "abstract": abstract,
                "url": f"https://openalex.org/{p.get('id', '')}",
                "pdf_url": pdf_url,
                "citation_count": p.get("cited_by_count", 0),
                "journal_name": p.get("primary_location", {}).get("source", {}).get("display_name", ""),
                "open_access": p.get("open_access", {}).get("is_oa", False),
                "estimated_citations": p.get("estimated_citations", {}).get("2025", 0),
                "relevance_score": 0.88,
                "provenance": f"source=openalex, query={query}, api_status=ok",
            })
        return {"papers": papers, "total": data.get("meta", {}).get("count", len(papers))}
    except urllib.error.HTTPError as e:
        return {"papers": [], "error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"papers": [], "error": str(e)}


def _arxiv_parse_xml(xml_data):
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        return [], 0, f"XML parse error: {e}"
    entries = root.findall("atom:entry", ARXIV_NS)
    if not entries:
        total_el = root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
        return [], int(total_el.text) if total_el is not None else 0, None
    total_el = root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
    total = int(total_el.text) if total_el is not None else 0
    papers = []
    for entry in entries:
        title = (entry.find("atom:title", ARXIV_NS).text or "").strip()
        raw_id = (entry.find("atom:id", ARXIV_NS).text or "").strip()
        arxiv_id = raw_id.split("/abs/")[-1].split("v")[0] if "/abs/" in raw_id else raw_id
        published = (entry.find("atom:published", ARXIV_NS).text or "")[:10]
        summary = (entry.find("atom:summary", ARXIV_NS).text or "").strip().replace("\n", " ")
        authors = [(a.find("atom:name", ARXIV_NS).text or "").strip() for a in entry.findall("atom:author", ARXIV_NS)]
        categories = [c.get("term", "") for c in entry.findall("atom:category", ARXIV_NS)]
        pdf_link = entry.find('.//atom:link[@rel="related"]', ARXIV_NS)
        pdf_url = pdf_link.get("href") if pdf_link is not None else None
        papers.append({
            "title": title, "authors": authors[:10],
            "year": int(published[:4]) if published else 0, "source": "arxiv",
            "external_ids": {"arXiv": arxiv_id},
            "abstract": summary[:500] if summary else "N/A",
            "url": f"https://arxiv.org/abs/{arxiv_id}", "pdf_url": pdf_url,
            "unique_id": {"arxiv_id": arxiv_id, "pdf_url": pdf_url},
            "categories": categories, "citation_count": 0,
            "relevance_score": 0.85,
            "provenance": "source=arxiv, api_status=ok, via=torsocks",
        })
    return papers, total, None


def search_arxiv(query, max_results=DEFAULT_MAX_RESULTS, use_tor=True):
    encoded = urllib.parse.quote(query, safe="+")
    url = f"{ARXIV_URL}?search_query=all:{encoded}&max_results={max_results}"
    if not use_tor:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Synthos/2.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml_data = resp.read()
            papers, total, err = _arxiv_parse_xml(xml_data)
            return {"papers": papers, "total": total, "error": err}
        except Exception as e:
            return {"papers": [], "total": 0, "error": f"Direct failed: {e}"}
    # Primary: torsocks subprocess
    try:
        result = subprocess.run(
            ["torsocks", "curl", "-s", url], capture_output=True, text=False, timeout=25,
        )
        if result.returncode == 0 and result.stdout:
            papers, total, err = _arxiv_parse_xml(result.stdout)
            return {"papers": papers, "total": total, "error": err}
        # Fallback: direct curl
        result2 = subprocess.run(
            ["curl", "-s", "--max-time", "15", url], capture_output=True, text=False, timeout=20,
        )
        if result2.returncode == 0 and result2.stdout:
            papers, total, err = _arxiv_parse_xml(result2.stdout)
            return {"papers": papers, "total": total, "error": err, "provenance_note": "via=direct_fallback"}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return {"papers": [], "total": 0, "error": "All arXiv methods failed"}


def deduplicate(papers):
    """Deduplicate by multi-key priority: PMID > DOI > arXiv ID > Semantic Scholar ID > title.
    Keeps the paper with the most complete data (most external_ids)."""
    seen = {}
    result = []
    for p in papers:
        ext = p.get("external_ids", {})
        # Primary unique keys in priority order
        uid = ext.get("PMID")
        if not uid:
            uid = ext.get("DOI", "N/A")
            if uid == "N/A":
                uid = ext.get("arXiv")
                if not uid:
                    uid = ext.get("s2_id") or ""
        if not uid or uid == "N/A":
            uid = p.get("unique_id", {}).get("s2_id", "") or ""
        if not uid:
            # Fallback to title
            uid = "title:" + p["title"].lower().strip().rstrip(".")

        if uid in seen:
            # Keep the version with more data
            existing = seen[uid]
            existing_ext = existing.get("external_ids", {})
            new_ext = p.get("external_ids", {})
            existing_count = sum(1 for v in existing_ext.values() if v and v != "N/A" and v != "")
            new_count = sum(1 for v in new_ext.values() if v and v != "N/A" and v != "")
            if new_count > existing_count:
                # Replace with more complete version
                seen[uid] = p
                # Also update result list
                idx = result.index(existing)
                result[idx] = p
        else:
            seen[uid] = p
            result.append(p)
    return result


def multi_source_search(query, sources=None, max_results=DEFAULT_MAX_RESULTS, use_tor=True, verbose=False):
    if sources is None:
        sources = DEFAULT_SOURCES
    all_papers = []
    sources_queried = []
    sources_failed = []
    sources_success = []
    source_map = {
        "semantic_scholar": lambda: search_semantic_scholar(query, max_results),
        "pubmed": lambda: search_pubmed(query, max_results),
        "openalex": lambda: search_openalex(query, max_results),
        "arxiv": lambda: search_arxiv(query, max_results, use_tor),
    }
    for source in sources:
        if source not in source_map:
            if verbose:
                print(f"  [WARN] Unknown source: {source}", file=sys.stderr)
            continue
        sources_queried.append(source)
        source_name = source.replace("_", " ").title()
        if verbose:
            print(f"  Querying {source_name}...", file=sys.stderr)
        result = source_map[source]()
        paper_count = len(result.get("papers", []))
        if result.get("error"):
            if verbose:
                print(f"    {source_name}: ERROR - {result['error']}", file=sys.stderr)
            sources_failed.append(source)
        elif paper_count > 0:
            all_papers.extend(result["papers"])
            sources_success.append(source)
            if verbose:
                print(f"    {source_name}: {paper_count} papers", file=sys.stderr)
        else:
            if verbose:
                print(f"    {source_name}: No results", file=sys.stderr)
            sources_failed.append(source)
        if source != sources[-1]:
            time.sleep(0.3)
    unique_papers = deduplicate(all_papers)
    output = {
        "papers": unique_papers, "total_found": len(unique_papers),
        "sources_queried": sources_queried, "sources_failed": sources_failed,
        "sources_success": sources_success,
        "search_meta": {
            "query": query, "sources_queried_list": sources_queried,
            "sources_success": sources_success, "sources_failed": sources_failed,
            "max_results_per_source": max_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "dedup_count": len(all_papers) - len(unique_papers), "total_raw": len(all_papers),
    }
    if verbose:
        print(f"\n  Total raw: {len(all_papers)} -> deduplicated: {len(unique_papers)}", file=sys.stderr)
        print(f"  Success: {sources_success} | Failed: {sources_failed}", file=sys.stderr)
    return output


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
        description="Synthos Multi-Source Academic Literature Search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Sources: semantic_scholar, pubmed, openalex, arxiv
Examples:
  %(prog)s "LLM chain of thought"
  %(prog)s "LLM reasoning" --max 10
  %(prog)s "LLM reasoning" --sources pubmed,openalex
  %(prog)s "LLM reasoning" --verbose --output result.json
  %(prog)s "LLM reasoning" --no-tor-arxiv
        """,
    )
    parser.add_argument("query", nargs="+", help="Search query (words separated by spaces)")
    parser.add_argument("--max", type=int, default=DEFAULT_MAX_RESULTS, help=f"Max results per source (default: {DEFAULT_MAX_RESULTS})")
    parser.add_argument("--sources", default=None, help="Comma-separated list of sources (default: all 4)")
    parser.add_argument("--all-sources", action="store_true", help="Explicitly enable all 4 sources")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print progress to stderr")
    parser.add_argument("--output", "-o", default=None, help="Write JSON result to file")
    parser.add_argument("--no-tor-arxiv", action="store_true", help="Disable Tor for arXiv (use direct HTTPS)")
    return parser.parse_args()


def print_results(output):
    papers = output["papers"]
    meta = output["search_meta"]
    print(f"\n{'=' * 70}")
    print("Synthos Literature Search Results")
    print(f"{'=' * 70}")
    print(f"Query:        {meta['query']}")
    print(f"Total Papers: {output['total_found']} (raw: {output['total_raw']}, deduped: {output['dedup_count']})")
    print(f"Sources OK:   {', '.join(meta.get('sources_success', []))}")
    if meta.get("sources_failed"):
        print(f"Sources FAIL: {', '.join(meta.get('sources_failed', []))}")
    print(f"{'=' * 70}")
    for i, p in enumerate(papers, 1):
        print(f"\n{i}. [{p['source'].upper():15s}] {p['title']}")
        if p.get("authors"):
            print(f"   Authors: {', '.join(p['authors'][:3])}")
        if p.get("year"):
            print(f"   Year: {p['year']}")
        ext = p.get("external_ids", {})
        if ext.get("DOI") and ext["DOI"] != "N/A":
            print(f"   DOI: {ext['DOI']}")
        if ext.get("arXiv"):
            print(f"   arXiv: {ext['arXiv']}")
        if ext.get("PMID"):
            print(f"   PMID: {ext['PMID']}")
        if p.get("citation_count"):
            print(f"   Citations: {p['citation_count']}")
        if p.get("relevance_score"):
            print(f"   Relevance: {p['relevance_score']}")
        print(f"   Source: {p['provenance']}")
    print(f"\n{'=' * 70}")


def main():
    args = parse_args()
    if not S2_API_KEY:
        print("ERROR: SEMANTIC_SCHOLAR_API_KEY environment variable is required.", file=sys.stderr)
        sys.exit(1)
    query = " ".join(args.query)
    sources = None
    if args.sources:
        sources = [s.strip() for s in args.sources.split(",")]
        valid = {"semantic_scholar", "pubmed", "openalex", "arxiv"}
        for s in sources:
            if s not in valid:
                print(f"ERROR: Unknown source '{s}'. Valid: {valid}", file=sys.stderr)
                sys.exit(1)
    if not query.strip():
        print("ERROR: Query is required.", file=sys.stderr)
        sys.exit(1)
    output = multi_source_search(
        query=query, sources=sources, max_results=args.max,
        use_tor=not args.no_tor_arxiv, verbose=args.verbose,
    )
    print_results(output)
    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\nResult saved to: {args.output}", file=sys.stderr)
    if output["total_found"] > 0:
        sys.exit(0)
    else:
        print(f"\nERROR: No papers found. Failed: {output['sources_failed']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
