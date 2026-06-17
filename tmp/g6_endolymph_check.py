#!/usr/bin/env python3
"""G6 verification for endolymph-hydropressure-ode — 6 PubMed queries."""
import json, urllib.request, time, sys
from urllib.parse import quote_plus

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def search(term, retmax=20):
    safe = quote_plus(term, safe='')
    url = f"{BASE}esearch.fcgi?db=pubmed&term={safe}&retmax={retmax}&retmode=json"
    with urllib.request.urlopen(url, timeout=15) as r:
        d = json.loads(r.read())
    ids = d.get("esearchresult", {}).get("idlist", [])
    return len(ids), ids

def fetch_abstract(pmid):
    url = f"{BASE}efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract&retmode=text"
    with urllib.request.urlopen(url, timeout=15) as r:
        return r.read().decode('utf-8', errors='replace')

queries = [
    ('Q1', '"endolymphatic hydrops" AND ODE'),
    ('Q2', '"endolymphatic hydrops" AND PINN'),
    ('Q3', '"Meniere\'s disease" AND "dynamical model"'),
    ('Q4', '"endolymphatic hydrops" AND "differential equation"'),
    ('Q5', '"endolymphatic hydrops" AND "computational model"'),
    ('Q6', '"Meniere\'s disease" AND "computational model" AND ODE'),
]

for label, q in queries:
    try:
        cnt, pmids = search(q)
        print(f"{label}: {q}")
        print(f"  Count: {cnt}, PMIDs: {pmids}")
        if cnt > 0 and pmids:
            print(f"  --- Abstract for PMID {pmids[0]} ---")
            print(fetch_abstract(pmids[0]))
            print(f"  --- End abstract ---")
        time.sleep(0.5)  # rate limit
    except Exception as e:
        print(f"{label}: ERROR {e}")
    print()
