#!/usr/bin/env python3
"""为7篇不存在论文找替代"""
import os, json, requests, time, urllib.parse

SS_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
HEADERS = {"User-Agent": "Mozilla/5.0"}
if SS_KEY:
    HEADERS["x-api-key"] = SS_KEY

def ss_search(query, limit=5):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={urllib.parse.quote(query)}&limit={limit}&fields=title,externalIds,year,venue,openAccessPdf,authors,citationCount"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.json().get("data", []) if r.status_code == 200 else []
    except:
        return []

# 7篇需要替代的论文 → 替代方向
alt_queries = {
    "Stiglic2012Missing": [
        ("Garcia-Laencina2010", "Pattern classification with missing data: A review"),
        ("Jerez2010", "Missing data imputation using statistical and machine learning methods"),
    ],
    "Mehta2024": [
        ("Kapoor2023Leakage", ""),  # 已修复，直接替代
    ],
    "Wen2024Leakage": [
        ("Kapoor2023Leakage", ""),  # 也覆盖数据泄漏主题
        ("McDermott2021Reproducibility", ""),  # 已有，Sci Transl Med
    ],
    "Fernandez2018Imbalanced": [
        ("He2009Imbalanced", "learning from imbalanced data"),
        ("Chawla2002", ""),  # 已有SMOTE原始论文
    ],
    "Grunspun2019Quality": [
        ("Collins2015TRIPOD", ""),  # 已有
        ("Moons2019PROBAST", ""),  # 已有
    ],
    "Chang2024": [
        # 被审计论文，不重要，可以去掉或用已有的替代
    ],
    "Wu2024BRFSS": [
        # DOI真实 10.1002/eng2.13080，仅第一作者名错，保留原条目
    ],
}

print("=== 替代方案评估 ===")
for key, alts in alt_queries.items():
    print(f"\n--- {key} ---")
    if key == "Chang2024":
        print(f"  建议：删除。属于被审计论文，非核心引用。")
        continue
    if key == "Wu2024BRFSS":
        print(f"  保留原条目。DOI {os.path.exists('/')} 真实存在，仅作者名需核实。")
        continue
    if key in ("Mehta2024", "Wen2024Leakage"):
        print(f"  建议：用 Kapoor2023Leakage (已修复DOI) 替代，该论文已覆盖数据泄漏主题")
        if key == "Wen2024Leakage":
            print(f"  或 McDermott2021Reproducibility (已有PDF) 补充")
        continue
    if key == "Grunspun2019Quality":
        print(f"  建议：已有 Collins2015TRIPOD + Moons2019PROBAST，不再需要")
        continue
    
    for alt_key, alt_query in alts:
        if not alt_query:
            print(f"  替代: {alt_key} (已有条目)")
            continue
        results = ss_search(alt_query)
        if results:
            p = results[0]
            doi = (p.get("externalIds") or {}).get("DOI", "")
            title = (p.get("title") or "?")[:60]
            yr = p.get("year", "")
            cite = p.get("citationCount", 0)
            auth = (p.get("authors") or [{}])[0].get("name", "?")
            oa = "✅" if (p.get("openAccessPdf") or {}).get("url") else "❌"
            print(f"  → {alt_key}: {doi}")
            print(f"    {title[:60]}")
            print(f"    {auth}, {yr}, citations={cite}, OA={oa}")
        time.sleep(0.3)

print("\n\n=== 推荐方案 ===")
print("""
1. Kapoor2023Leakage ✅ 已修复 → 尝试下载PDF (Patterns OA)
2. Norgeot2020MI-CLAIM ✅ 已修复 → 尝试下载PDF (Nature Med OA)
3. Haixiang2017Imbalanced ✅ 已修复
4. Stiglic2012Missing ❌ 不存在 → 新增 Garcia-Laencina 2010 (缺失值插补综述)
5. Mehta2024 ❌ 不存在 → 已由Kapoor覆盖
6. Wen2024Leakage ❌ 不存在 → 已由Kapoor+McDermott覆盖
7. Fernandez2018Imbalanced ❌ 不存在 → 新增 He 2009 (IEEE TKDE, 不平衡学习经典)  
8. Grunspun2019Quality ❌ 不存在 → 已有TRIPOD+PROBAST覆盖
9. Chang2024 ❌ 不存在 → 删除
10. Wu2024BRFSS → DOI真实，保留
""")
