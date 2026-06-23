#!/usr/bin/env python3
"""带SS API Key查真实DOI + 尝试SS OA下载"""
import os, sys, json, requests, time

SS_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
PDF_DIR = '/media/yakeworld/sda2/Synthos/outputs/papers/pima-crispdm/06-references/pdfs'

HEADERS = {"User-Agent": "Mozilla/5.0"}
if SS_KEY:
    HEADERS["x-api-key"] = SS_KEY

def ss_search(query):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={requests.utils.quote(query)}&limit=3&fields=title,externalIds,year,venue,openAccessPdf"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json().get("data", [])
        elif r.status_code == 429:
            print(f"    429限速")
            return []
        return []
    except Exception as e:
        print(f"    error: {e}")
        return []

papers = [
    ("Stiglic2012Missing", "Missing data imputation Pima Indian Diabetes Dataset", "核心"),
    ("Mehta2024", "critical evaluation machine learning diabetes prediction PIMA dataset",
     "核心"),
    ("Kapoor2023Leakage", "Leakage and the reproducibility crisis in machine learning based science",
     "核心"),
    ("Wen2024Leakage", "Data leakage and reproducibility in machine learning for healthcare",
     "核心"),
    ("Fernandez2018Imbalanced", "imbalanced dataset benchmark", "重要"),
    ("Haixiang2017Imbalanced", "Learning from class imbalanced data review methods applications",
     "重要"),
    ("Wu2024BRFSS", "Explainable machine learning efficient diabetes prediction BRFSS",
     "重要"),
    ("Chang2024", "High accuracy diabetes prediction using ensemble machine learning Pima Indians",
     "重要"),
    ("Grunspun2019Quality", "simple approach assessing quality clinical prediction models",
     "重要"),
    ("Norgeot2020MI-CLAIM", "Minimum information about clinical artificial intelligence modeling MI-CLAIM",
     "重要"),
]

print(f"{'Key':<22} {'Bib DOI':<40} {'SS DOI':<40} {'OA':<5} {'Title'}")
print("="*130)

for key, query, prio in papers:
    results = ss_search(query)
    if results:
        best = results[0]
        ext = best.get("externalIds") or {}
        real_doi = ext.get("DOI", "")
        title = (best.get("title") or "?")[:45]
        oa_url = (best.get("openAccessPdf") or {}).get("url", "")
        oa_flag = "✅" if oa_url else "❌"
        venue = (best.get("venue") or "?")[:20]
        year = best.get("year", "?")
        
        print(f"{key:<22} {'(bib)':<40} {real_doi:<40} {oa_flag:<5} {title}")
        print(f"{'':<22} {'':<40} {venue:<40} {year}")
        
        # 如果有OA直链，尝试下载
        if oa_url:
            out = os.path.join(PDF_DIR, real_doi.replace('/', '_') + '.pdf')
            if not (os.path.exists(out) and os.path.getsize(out) > 1000):
                try:
                    r2 = requests.get(oa_url, timeout=30, allow_redirects=True,
                                      headers={"User-Agent": "Mozilla/5.0"})
                    if r2.status_code == 200 and len(r2.content) > 1000 and r2.content[:4] == b'%PDF':
                        with open(out, 'wb') as f:
                            f.write(r2.content)
                        print(f"{'':<22} {'':<40} {'→ SS-OA ✅':<40} {len(r2.content)//1024}KB")
                    else:
                        print(f"{'':<22} {'':<40} {'→ SS-OA ❌':<40} {r2.status_code}/{len(r2.content)}B")
                except Exception as e:
                    print(f"{'':<22} {'':<40} {'→ SS-OA ❌':<40} {e}")
            else:
                print(f"{'':<22} {'':<40} {'→ 已有':<40}")
    else:
        print(f"{key:<22} {'(bib)':<40} {'SS搜不到':<40}")
    
    time.sleep(0.5)  # 礼貌

print("\n=== 下载结果检查 ===")
import glob
valid = [f for f in glob.glob(os.path.join(PDF_DIR, '*.pdf')) if os.path.getsize(f) > 1000]
print(f"有效PDF总数: {len(valid)}")

# 列出bib DOI对应已下
bib_dois = set()
import re
with open('/media/yakeworld/sda2/Synthos/outputs/papers/pima-crispdm/06-references/references.bib') as f:
    for line in f:
        m = re.search(r'doi\s*=\s*[\{\"]?(10\.\d{4,}/[^,}\"\s]+)', line, re.I)
        if m:
            bib_dois.add(m.group(1))
print(f"bib DOI总数: {len(bib_dois)}")
print(f"覆盖率: {len(valid)}/{len(bib_dois)}")
