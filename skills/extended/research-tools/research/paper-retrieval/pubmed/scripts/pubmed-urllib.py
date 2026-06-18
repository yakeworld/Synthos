#!/usr/bin/env python3
"""
Reusable PubMed search using urllib stdlib (no curl).
Safe for Hermes cron environment — avoids tirith:curl_pipe_shell blocking.

Usage:
  python3 pubmed-urllib.py "term"  → prints count + PMID list
  python3 pubmed-urllib.py "term" "2024/01/01..2026/06/08" → date-filtered
  python3 pubmed-urllib.py --abstract "PMID1,PMID2" → prints abstracts
"""
import json
import sys
import urllib.request
from urllib.parse import quote_plus

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def search(term, date_range=None, retmax=10):
    """Search PubMed and return count + PMID list."""
    query = term
    if date_range:
        query += f' AND "{date_range}"[Date - Publication]'
    safe_term = quote_plus(query, safe='')
    url = f"{BASE}esearch.fcgi?db=pubmed&term={safe_term}&retmax={retmax}&retmode=json"
    with urllib.request.urlopen(url, timeout=15) as r:
        d = json.loads(r.read())
    ids = d.get("esearchresult", {}).get("idlist", [])
    return len(ids), ids

def fetch_abstract(pmid_list):
    """Fetch abstracts for a list of PMIDs."""
    url = f"{BASE}efetch.fcgi?db=pubmed&id={','.join(pmid_list)}&rettype=abstract&retmode=text"
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode('utf-8', errors='replace')

def main():
    args = sys.argv[1:]
    
    if args and args[0] == '--abstract':
        if len(args) < 2:
            print("Usage: pubmed-urllib.py --abstract PMIDs comma-separated")
            return
        pmids = args[1].split(',')
        print(fetch_abstract(pmids))
        return
    
    term = args[0] if args else ""
    date = args[1] if len(args) > 1 else None
    
    count, pmids = search(term, date)
    print(f"Count: {count}")
    print(f"PMIDs: {pmids}")

if __name__ == '__main__':
    main()