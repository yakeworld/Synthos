#!/usr/bin/env python3
"""v69 rotation scan — 5 directions + candidate verification"""
import json, urllib.request, sys

def pubmed_count(query):
    try:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmode=json&retmax=3"
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read())
        count = int(data.get("esearchresult", {}).get("count", 0))
        ids = data["esearchresult"].get("idlist", [])
        titles = []
        for pid in ids[:3]:
            try:
                u2 = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pid}&retmode=xml"
                with urllib.request.urlopen(u2, timeout=15) as r2:
                    xml = r2.read().decode()
                    # extract title
                    import re
                    titles_match = re.findall(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', xml)
                    if titles_match:
                        titles.append(titles_match[0][:120])
            except:
                titles.append("(fetch failed)")
        return count, titles
    except Exception as e:
        return -1, [str(e)]

def openalex_count(query):
    try:
        url = f"https://api.openalex.io/works?search={urllib.parse.quote(query)}&per_page=3&format=json"
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read())
        total = data.get("meta", {}).get("count", 0)
        titles = []
        for w in data.get("results", [])[:3]:
            titles.append(w.get("title", "")[:120])
        return total, titles
    except Exception as e:
        return -1, [str(e)]

# === 5 Rotation Directions ===
rotations = [
    ("VOR-PINN", "vestibulo-ocular-reflex*AND*PINN*AND*ordinary differential"),
    ("Kappa-ML", "kappa angle*AND*(machine learning OR deep learning)"),
    ("BPPV-nystagmus-ML", "benign paroxysmal positional vertigo*AND*nystagmus*AND*(machine learning OR deep learning OR neural network)"),
    ("PD-saccade", "parkinson*AND*saccade*AND*(machine learning OR deep learning)"),
    ("3D-Eye", "3D eye tracking AND gaze AND (deep learning OR convolutional)"),
]

# === Candidate Verification ===
candidates = [
    ("smooth-pursuit-PINN", "smooth pursuit eye movement*AND*PINN*AND*neural"),
    ("head-impulse-ODE", "head impulse test*AND*ODE*AND*ordinary differential"),
    ("VOR-cancellation-PINN", "VOR cancellation*AND*PINN*AND*neural differential"),
    ("caloric-nystagmus-ODE", "caloric nystagmus*AND*ordinary differential*AND*model"),
    ("BPPV-canalith-ODE", "canalith repositioning*AND*ordinary differential*AND*ODE"),
]

print("=== ROTATION SCAN ===")
for name, query in rotations:
    c, titles = pubmed_count(query)
    oa_c, oa_t = openalex_count(query)
    print(f"{name}: PubMed={c} (titles: {' | '.join(titles[:2])}), OpenAlex={oa_c} (titles: {' | '.join(oa_t[:2])})")

print("\n=== CANDIDATE VERIFICATION ===")
for name, query in candidates:
    c, titles = pubmed_count(query)
    oa_c, oa_t = openalex_count(query)
    print(f"{name}: PubMed={c} (titles: {' | '.join(titles[:2])}), OpenAlex={oa_c} (titles: {' | '.join(oa_t[:2])})")

print("\n=== NEW HIGH-VALUE SCAN ===")
new_cands = [
    ("cervico-ocular-PINN", "cervico-ocular reflex*AND*PINN*AND*neural"),
    ("pupillary-adaptation-PINN", "pupillary adaptation*AND*PINN*AND*neural"),
    ("vestibular-tremor-PINN", "vestibular tremor*AND*PINN*AND*neural"),
    ("ocular-thermal-NeuralODE", "inner ear thermal*AND*neural ODE"),
    ("saccade-pursuit-switching-PINN", "saccade pursuit switching*AND*PINN*AND*neural differential"),
]
for name, query in new_cands:
    c, titles = pubmed_count(query)
    oa_c, oa_t = openalex_count(query)
    print(f"{name}: PubMed={c} (titles: {' | '.join(titles[:2])}), OpenAlex={oa_c} (titles: {' | '.join(oa_t[:2])})")
