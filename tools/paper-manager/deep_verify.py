#!/usr/bin/env python3
"""精确搜未确认的论文"""
import os, json, requests, time, urllib.parse, xml.etree.ElementTree as ET

SS_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
HEADERS = {"User-Agent": "Mozilla/5.0"}
if SS_KEY:
    HEADERS["x-api-key"] = SS_KEY

def ss_search(query):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={urllib.parse.quote(query)}&limit=5&fields=title,externalIds,year,venue,openAccessPdf,authors"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.json().get("data", []) if r.status_code == 200 else []
    except:
        return []

def pubmed_search(query):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmode=json"
    try:
        r = requests.get(url, timeout=10)
        return r.json()['esearchresult'].get('idlist', [])
    except:
        return []

def pubmed_fetch(pmid):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml&rettype=abstract"
    try:
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.text)
        for a in root.iter('Article'):
            t = a.find('.//ArticleTitle')
            d_el = a.find('.//ELocationID[@EIdType="doi"]')
            return (t.text if t is not None else '?'), (d_el.text if d_el is not None else '?')
    except:
        return '?', '?'

# Stiglic - 用不同关键词
print("=== Stiglic2012Missing ===")
for q in ["stiglic missing data imputation", "stiglic pima 2012", "missing data imputation Pima Indian 2012"]:
    results = ss_search(q)
    if results:
        for p in results[:2]:
            doi = (p.get("externalIds") or {}).get("DOI","")
            title = (p.get("title") or "?")[:70]
            yr = p.get("year","")
            print(f"  SS: {doi} | {title} ({yr})")
    time.sleep(0.3)

# Mehta 2024 - 精确
print("\n=== Mehta2024 ===")
for q in ["Mehta PIMA dataset critical evaluation machine learning 2024", 
          "\"critical evaluation\" \"machine learning\" diabetes PIMA"]:
    results = ss_search(q)
    if results:
        for p in results[:3]:
            doi = (p.get("externalIds") or {}).get("DOI","")
            title = (p.get("title") or "?")[:70]
            yr = p.get("year","")
            auth = (p.get("authors") or [{}])[0].get("name","?")
            print(f"  SS: {doi} | {title} ({yr}) [{auth}]")
    time.sleep(0.3)

# Fernandez2018Imbalanced - 精确
print("\n=== Fernandez2018Imbalanced ===")
for q in ["Fernandez imbalanced dataset benchmark 2018", 
          "\"imbalanced dataset benchmark\" neurocomputing",
          "Fernández \"imbalanced dataset\" benchmark"]:
    results = ss_search(q)
    if results:
        for p in results[:3]:
            doi = (p.get("externalIds") or {}).get("DOI","")
            title = (p.get("title") or "?")[:70]
            yr = p.get("year","")
            auth = (p.get("authors") or [{}])[0].get("name","?")
            print(f"  SS: {doi} | {title} ({yr}) [{auth}]")
    time.sleep(0.3)

# Wen2024
print("\n=== Wen2024Leakage ===")
ids = pubmed_search("wen[au] AND data leakage[ti] AND healthcare[ti]")
if ids:
    t, doi = pubmed_fetch(ids[0])
    print(f"  PubMed: PMID={ids[0]}, DOI={doi}, Title={t[:60]}")
else:
    print("  PubMed: 无结果")
    # SS搜
    for q in ["data leakage reproducibility healthcare machine learning systematic review",
              "wen data leakage machine learning healthcare"]:
        results = ss_search(q)
        if results:
            for p in results[:3]:
                doi = (p.get("externalIds") or {}).get("DOI","")
                title = (p.get("title") or "?")[:70]
                yr = p.get("year","")
                auth = (p.get("authors") or [{}])[0].get("name","?")
                print(f"  SS: {doi} | {title} ({yr}) [{auth}]")
        time.sleep(0.3)

# Grunspun
print("\n=== Grunspun2019Quality ===")
ids = pubmed_search("grunspun[au] AND 2019[dp]")
if ids:
    t, doi = pubmed_fetch(ids[0])
    print(f"  PubMed: PMID={ids[0]}, DOI={doi}, Title={t[:60]}")
else:
    print("  PubMed: 无结果")
    for q in ["grunspun clinical prediction models", "simple approach assessing quality clinical prediction"]:
        results = ss_search(q)
        if results:
            for p in results[:3]:
                doi = (p.get("externalIds") or {}).get("DOI","")
                title = (p.get("title") or "?")[:70]
                yr = p.get("year","")
                auth = (p.get("authors") or [{}])[0].get("name","?")
                print(f"  SS: {doi} | {title} ({yr}) [{auth}]")
        time.sleep(0.3)

# Chang2024
print("\n=== Chang2024 ===")
for q in ["chang diabetes prediction ensemble PIMA IEEE Access 2024",
          "\"Pima Indians\" \"ensemble\" diabetes IEEE Access"]:
    results = ss_search(q)
    if results:
        for p in results[:3]:
            doi = (p.get("externalIds") or {}).get("DOI","")
            title = (p.get("title") or "?")[:70]
            yr = p.get("year","")
            auth = (p.get("authors") or [{}])[0].get("name","?")
            print(f"  SS: {doi} | {title} ({yr}) [{auth}]")
    time.sleep(0.3)
