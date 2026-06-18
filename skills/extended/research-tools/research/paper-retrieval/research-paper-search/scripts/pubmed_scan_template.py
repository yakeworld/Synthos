#!/usr/bin/env python3
"""
Reusable PubMed rotation scan template.
Usage: Edit the QUERIES dict below with your 5 rotation directions.
No curl | python3 pipes — uses urllib stdlib directly.
"""
import json
import urllib.request

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=5&retmode=json&term="

# ─── Edit these for your scan ──────────────────────────────────────
QUERIES = {
    "VOR-PINN": 'vestibulo-ocular+reflex+AND+"neural+network"+AND+PINN',
    "Kappa-ML": "kappa+angle+AND+machine+learning",
    "BPPV-nystagmus": "benign+paroxysmal+positional+vertigo+AND+nystagmus+AND+machine+learning",
    "PD-saccade": "parkinson+AND+saccade+AND+machine+learning",
    "3D-Eye": "3D+AND+eye+tracking+AND+deep+learning",
}
# ────────────────────────────────────────────────────────────────────

for name, term in QUERIES.items():
    url = f"{BASE}{term}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            d = json.loads(r.read())
        ids = d.get("esearchresult", {}).get("idlist", [])
        print(f"=== {name}: {len(ids)} results ===")
        for i in ids[:5]:
            print(f"  PMID {i}")
    except Exception as e:
        print(f"=== {name}: ERROR {e} ===")
