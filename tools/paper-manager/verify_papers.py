#!/usr/bin/env python3
"""逐篇查证8篇论文的真实DOI"""
import os, json, requests, time, re

SS_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
HEADERS = {"User-Agent": "Mozilla/5.0"}
if SS_KEY:
    HEADERS["x-api-key"] = SS_KEY

def ss_search(query, year=None):
    """SS搜索，year做过滤"""
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={__import__('urllib.parse').parse.quote(query)}&limit=5&fields=title,externalIds,year,venue,openAccessPdf,authors"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json().get("data", [])
        return []
    except:
        return []

papers = [
    # (key, search_query, expected_year, expected_first_author)
    ("Stiglic2012Missing", "Missing data imputation Pima Indian Diabetes", 2012, "Stiglic"),
    ("Mehta2024", "critical evaluation machine learning models diabetes prediction PIMA data leakage", 2024, "Mehta"),
    ("Wen2024Leakage", "Data leakage reproducibility machine learning healthcare systematic review", 2024, "Wen"),
    ("Fernandez2018Imbalanced", "imbalanced dataset benchmark", 2018, "Fernandez"),
    ("Haixiang2017Imbalanced", "learning class imbalanced data review methods applications", 2017, "Haixiang"),
    ("Wu2024BRFSS", "Explainable machine learning efficient diabetes prediction BRFSS hyperparameter tuning SHAP", 2024, "Wu"),
    ("Chang2024", "High accuracy diabetes prediction ensemble machine learning Pima Indians", 2024, "Chang"),
    ("Grunspun2019Quality", "simple approach assessing quality clinical prediction models", 2019, "Grunspun"),
]

for key, query, exp_year, exp_author in papers:
    print(f"\n{'='*60}")
    print(f"【{key}】")
    
    results = ss_search(query)
    
    if not results:
        print(f"  SS: 无结果")
        # 试PubMed
        pubmed_query = f"{exp_author}[au] AND {query[:60].replace(' ','+')}"
        print(f"  → 跳PubMed搜索")
        time.sleep(0.5)
        continue
    
    # 看top结果是否匹配
    found_match = False
    for i, paper in enumerate(results):
        ext = paper.get("externalIds") or {}
        doi = ext.get("DOI", "")
        title = (paper.get("title") or "?")[:70]
        year = paper.get("year", 0)
        venue = (paper.get("venue") or "?")[:30]
        authors = paper.get("authors") or []
        first_author = (authors[0].get("name","") if authors else "")
        oa = "✅" if (paper.get("openAccessPdf") or {}).get("url") else "❌"
        
        # 判断是否匹配：年份相近 + 第一作者姓匹配 + 标题关键词匹配
        year_ok = abs(year - exp_year) <= 2 if year else False
        author_ok = exp_author.lower() in first_author.lower()
        
        mark = ""
        if year_ok and author_ok:
            mark = " ← ✅ 匹配!"
            found_match = True
        
        if i == 0 or found_match:
            print(f"  [{i+1}] DOI: {doi}")
            print(f"       Title: {title}")
            print(f"       {venue}, {year}, 第一作者: {first_author}")
            print(f"       OA: {oa} {mark}")
        
        if found_match:
            break
    
    if not found_match:
        print(f"  ❌ 未找到匹配论文 (期待 {exp_author}, {exp_year})")
        print(f"  最佳结果: {results[0].get('title','?')[:60] if results else '无'}")
    
    time.sleep(0.5)

print("\n\n=== PubMed补充搜索 ===")
# 对SS搜不到/不确定的，用PubMed精确查
pubmed_checks = [
    ("Stiglic2012", "stiglic[au] AND \"J Med Syst\"[ta] AND 2012[dp]"),
    ("Mehta2024", "mehta[au] AND \"J Healthc Inform Res\"[ta] AND 2024[dp]"),
    ("Wen2024", "wen[au] AND data leakage[ti] AND reproducibility[ti]"),
    ("Grunspun2019", "grunspun[au] AND 2019[dp]"),
    ("Chang2024", "chang[au] AND diabetes[ti] AND ensemble[ti] AND 2024[dp]"),
]

for key, query in pubmed_checks:
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={__import__('urllib.parse').parse.quote(query)}&retmode=json"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        ids = data['esearchresult'].get('idlist', [])
        if ids:
            # 获取详情
            r2 = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids[0]}&retmode=xml&rettype=abstract", timeout=10)
            xml = r2.text
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml)
            for a in root.iter('Article'):
                t = a.find('.//ArticleTitle')
                d_el = a.find('.//ELocationID[@EIdType="doi"]')
                title = t.text[:60] if t is not None and t.text else '?'
                doi = d_el.text if d_el is not None else '?'
                print(f"  {key}: PMID={ids[0]}, DOI={doi}, Title={title}")
        else:
            print(f"  {key}: PubMed无结果")
    except Exception as e:
        print(f"  {key}: error {e}")
    time.sleep(0.5)
