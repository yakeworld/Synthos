#!/usr/bin/env python3
"""v69 deep candidate verification — PINN/ODE specific queries"""
import json, urllib.request, sys, urllib.parse

def pubmed_deep(query, max_titles=2):
    try:
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmode=json&retmax=3"
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read())
        count = int(data.get("esearchresult", {}).get("count", 0))
        ids = data["esearchresult"].get("idlist", [])
        titles = []
        for pid in ids[:max_titles]:
            try:
                u2 = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pid}&retmode=xml"
                with urllib.request.urlopen(u2, timeout=15) as r2:
                    xml = r2.read().decode()
                    import re
                    tm = re.findall(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', xml)
                    if tm:
                        titles.append(tm[0][:150])
            except:
                titles.append("(fetch failed)")
        return count, titles
    except Exception as e:
        return -1, [str(e)]

print("=== DEEP CANDIDATE VERIFICATION ===")
# These are the real PINN/ODE specificity checks
queries = [
    ("smooth-pursuit-PINN", "smooth pursuit*AND*('physics-informed' OR 'deep operator' OR 'neural ODE')"),
    ("head-impulse-ODE", "(head impulse OR vHIT OR 'video head impulse')*AND*'ordinary differential equation'"),
    ("VOR-cancellation-PINN", "VOR cancellation*AND*'physics-informed'"),
    ("caloric-nystagmus-ODE", "caloric*AND*nystagmus*AND*'ordinary differential equation'"),
    ("BPPV-canalith-ODE", "(canalith*OR*'canalithiasis')*AND*'ordinary differential equation'"),
    ("saccade-pursuit-switching-ODE", "(saccade*AND*pursuit*AND*switching)*AND*'ordinary differential'"),
    ("oculomotor-NeuralODE", "(oculomotor*OR'eye movement control')*AND*'neural ODE'"),
    ("vestibular-computation-PINN", "vestibular*AND*PINN"),
]

for name, query in queries:
    c, titles = pubmed_deep(query, 2)
    status = "ABSOLUTE WHITE" if c == 0 else ("WHITE for PINN/ODE" if c <= 3 else f"competitive ({c})")
    print(f"{name}: PubMed={c} | {status}")
    for t in titles:
        print(f"  -> {t}")
