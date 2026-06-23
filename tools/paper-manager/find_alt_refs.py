#!/usr/bin/env python3
"""按标题找真实DOI + 替代文献建议"""
import json, requests, time, urllib.parse

papers = [
    ("Stiglic2012Missing", "Missing data imputation in the Pima Indian Diabetes Dataset", "J Med Syst 2012", "核心"),
    ("Mehta2024", "critical evaluation machine learning models diabetes prediction benchmarking data leakage PIMA", "J Healthc Inform Res 2024", "核心"),
    ("Kapoor2023Leakage", "Leakage and the reproducibility crisis in machine learning-based science", "Patterns 2024", "核心"),
    ("Wen2024Leakage", "Data leakage and reproducibility in machine learning for healthcare", "J Med Syst 2024", "核心"),
    ("Fernandez2018Imbalanced", "An imbalanced dataset benchmark", "Neurocomputing 2018", "重要"),
    ("Haixiang2017Imbalanced", "Learning from class-imbalanced data Review methods and applications", "IEEE 2017", "重要"),
    ("Wu2024BRFSS", "Explainable machine learning for efficient diabetes prediction", "Engineering Reports 2024", "重要"),
    ("Chang2024", "High-accuracy diabetes prediction ensemble machine learning Pima", "IEEE Access 2024", "重要"),
    ("Grunspun2019Quality", "simple approach assessing quality clinical prediction models", "J Clin Epidemiol 2019", "重要"),
    ("Norgeot2020MI-CLAIM", "Minimum information about clinical artificial intelligence modeling MI-CLAIM checklist", "Nat Mach Intell 2020", "重要"),
]

def ss_search(query):
    try:
        r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={urllib.parse.quote(query)}&limit=5&fields=title,externalIds,year,venue,openAccessPdf",
                        timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            return r.json().get("data", [])
        return []
    except:
        return []

print(f"{'Key':<22} {'DOI(旧)':<38} {'DOI(真实)':<38} {'OA':<4} {'Venue'}")
print("="*150)

for key, query, venue_old, prio in papers:
    results = ss_search(query)
    best = None
    for r in results:
        ext = r.get("externalIds") or {}
        if ext.get("DOI"):
            best = r
            break
    if not best and results:
        best = results[0]
    
    if best:
        ext = best.get("externalIds") or {}
        real_doi = ext.get("DOI", "❌")
        oa = "✅" if (best.get("openAccessPdf") or {}).get("url") else "❌"
        title = (best.get("title") or "?")[:40]
        venue = (best.get("venue") or "?")[:15]
        year = best.get("year", "?")
        print(f"{key:<22} {real_doi if len(real_doi)>10 else '?':<38} ✅ {real_doi:<38} {oa:<4} {venue} ({year}) {title}")
    else:
        print(f"{key:<22} {'❌ SS搜不到':<38} {'':<42} 需要替代文献")
    
    time.sleep(0.5)

print("\n=== 替代文献建议 ===")
print("""
【核心替代】
- Stiglic2012Missing → 用 Demsar 2013 (Statistical comparisons of classifiers over multiple data sets) 
                        或 Van Buuren 2018 (Flexible Imputation of Missing Data)
- Mehta2024 → 用这篇找相同主题: SMOTE 相关综述或 PIMA benchmark 论文
- Kapoor2023Leakage → 搜索 Patterns 期刊官网，可能 PDF 可直接下载
- Wen2024Leakage → 用 Google Scholar 找相同主题高引论文

【重要替代】  
- Fernandez2018Imbalanced → IMbalanced 综述有很多: He 2009 (IEEE TKDE) / Branco 2016
- Haixiang2017Imbalanced → 同上
- Norgeot2020MI-CLAIM → Nature MI 论文通常 OA，官网可下
""")
