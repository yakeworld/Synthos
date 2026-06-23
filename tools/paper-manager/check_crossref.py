#!/usr/bin/env python3
"""Crossref + Unpaywall 查10篇DOI的可下载路径"""
import json, os, sys, time, requests

PDF_DIR = '/media/yakeworld/sda2/Synthos/outputs/papers/pima-crispdm/06-references/pdfs'

IMPORTANT_DOIS = [
    ("10.1007/s10916-012-9822-z",    "Stiglic2012Missing", "核心"),
    ("10.1007/s41666-024-00189-8",   "Mehta2024",          "核心"),
    ("10.1016/j.patter.2024.101065", "Kapoor2023Leakage",  "核心"),
    ("10.1007/s10916-024-02056-8",   "Wen2024Leakage",     "核心"),
    ("10.1016/j.neucom.2017.10.095", "Fernandez2018",      "重要"),
    ("10.1109/DSML.2017.11",         "Haixiang2017",       "重要"),
    ("10.1002/eng2.13080",           "Wu2024BRFSS",        "重要"),
    ("10.1109/ACCESS.2024.3367890",  "Chang2024",          "重要"),
    ("10.1016/j.jclinepi.2019.02.020","Grunspun2019",      "重要"),
    ("10.1038/s42256-020-00241-3",   "Norgeot2020",        "重要"),
]

def crossref_lookup(doi):
    """Crossref REST API查元数据"""
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}", timeout=10,
                         headers={"User-Agent": "Hermes/1.0 (mailto:yakeworld@wmu.edu.cn)"})
        if r.status_code == 200:
            data = r.json()["message"]
            info = {}
            info["title"] = (data.get("title") or [""])[0][:60]
            info["publisher"] = data.get("publisher", "")
            info["type"] = data.get("type", "")
            info["URL"] = data.get("URL", "")
            # 查看是否有关联的resource/URL
            links = data.get("link", [])
            info["links"] = [l["URL"] for l in links if l.get("URL")]
            info["ISSN"] = data.get("ISSN", [])
            info["member"] = data.get("member", "")
            info["published"] = data.get("published-online", {}).get("date-parts", [[None]])[0]
            return info
        return None
    except Exception as e:
        return None

def unpaywall_lookup(doi):
    """Unpaywall查OA状态"""
    try:
        r = requests.get(f"https://api.unpaywall.org/v2/{doi}?email=yakeworld@wmu.edu.cn", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {
                "oa_status": data.get("oa_status", "closed"),
                "best_oa_url": (data.get("best_oa_location") or {}).get("url_for_pdf", ""),
                "is_oa": data.get("is_oa", False),
                "host_type": (data.get("best_oa_location") or {}).get("host_type", ""),
            }
        return None
    except:
        return None

print(f"{'DOI':<42} {'Key':<22} {'Crossref URL':<55} {'Link':<40}")
print("-"*160)

for doi, key, prio in IMPORTANT_DOIS:
    out = os.path.join(PDF_DIR, doi.replace('/','_')+'.pdf')
    has = "✅" if (os.path.exists(out) and os.path.getsize(out) > 1000) else "❌"
    
    cr = crossref_lookup(doi)
    upw = unpaywall_lookup(doi)
    
    cr_url = (cr or {}).get("URL", "-")[:50] if cr else "❌ 无记录"
    links = []
    if cr and cr.get("links"):
        links = cr["links"]
    
    upw_info = ""
    if upw:
        if upw["is_oa"]:
            upw_info = f"OA[{upw['oa_status']}] {upw['best_oa_url'][:40]}"
        else:
            upw_info = f"Closed({upw['host_type']})"
    
    print(f"{doi:<42} {key:<22} {cr_url:<55} {upw_info}")
    for l in links[:3]:
        print(f"{'':<42} {'':<22} {'':<55} {l[:50]}")
    print()
    time.sleep(0.5)
