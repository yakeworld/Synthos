#!/usr/bin/env python3
"""查10篇重要DOI的SS元数据，有PMID则走MedData"""
import json, os, sys, time, requests

PDF_DIR = '/media/yakeworld/sda2/Synthos/outputs/papers/pima-crispdm/06-references/pdfs'
IMPORTANT_DOIS = [
    "10.1007/s10916-012-9822-z",    # Stiglic2012Missing 核心
    "10.1007/s41666-024-00189-8",   # Mehta2024           核心
    "10.1016/j.patter.2024.101065",  # Kapoor2023Leakage   核心
    "10.1007/s10916-024-02056-8",   # Wen2024Leakage      核心
    "10.1016/j.neucom.2017.10.095",  # Fernandez2018       重要
    "10.1109/DSML.2017.11",          # Haixiang2017        重要
    "10.1002/eng2.13080",            # Wu2024BRFSS         重要
    "10.1109/ACCESS.2024.3367890",   # Chang2024           重要
    "10.1016/j.jclinepi.2019.02.020", # Grunspun2019       重要
    "10.1038/s42256-020-00241-3",    # Norgeot2020MI-CLAIM 重要
]

def query_ss_meta(doi):
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf,externalIds,title"
    try:
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# Step 1: SS元数据
print("=== SS元数据查询 ===")
print(f"{'DOI':<42} {'PMID':<9} {'OA直链':<6} {'可下载路径'}")
print("-"*85)

candidates = []  # (doi, pmid, reason)
for i, doi in enumerate(IMPORTANT_DOIS, 1):
    out = os.path.join(PDF_DIR, doi.replace('/','_')+'.pdf')
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        print(f"[{i}] {doi:<38} ✅ 已有")
        continue
    
    data = query_ss_meta(doi)
    if not data:
        print(f"[{i}] {doi:<38} SS无记录")
        continue
    
    title = (data.get("title") or "?")[:48]
    ext = data.get("externalIds") or {}
    pmid = ext.get("PubMed", "")
    arxiv = ext.get("ArXiv", "")
    oa = (data.get("openAccessPdf") or {}).get("url", "")
    
    paths = []
    if oa:   paths.append("SS-OA直链")
    if arxiv: paths.append(f"arXiv:{arxiv}")
    if pmid:  paths.append("MedData")
    path_str = " + ".join(paths) if paths else "❌ 无路径"
    
    print(f"[{i}] {doi:<38} {pmid:<9} {'✅' if oa else '❌':<6} {path_str}")
    
    if pmid:
        candidates.append((doi, pmid, title))
    elif oa:
        # SS OA之前试过失败了，但可以再试一次
        candidates.append((doi, "", title))
    
    time.sleep(0.3)

# Step 2: MedData下载（有PMID的）
if not candidates:
    print("\n无可用下载路径")
    sys.exit(0)

print(f"\n=== MedData下载 ({len(candidates)}篇, 单线程, 15s间隔) ===")
sys.path.insert(0, '/media/yakeworld/sda2/Synthos/tools/paper-manager')
from src.sources.meddata import try_meddata

success = 0
for i, (doi, pmid, title) in enumerate(candidates, 1):
    out = os.path.join(PDF_DIR, doi.replace('/','_')+'.pdf')
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        print(f"[{i}/{len(candidates)}] {doi[:45]} ✅ 已有")
        continue
    
    print(f"[{i}/{len(candidates)}] {doi[:45]}", end=' ', flush=True)
    try:
        result = try_meddata(doi, out, extra={"pmid": pmid} if pmid else {})
        if result and result.get('success'):
            sz = os.path.getsize(out)
            print(f"✅ MedData {sz//1024}KB | {title[:40]}")
            success += 1
        else:
            msg = result.get('error', 'unknown') if isinstance(result, dict) else str(result)
            print(f"❌ {msg[:50]}")
    except Exception as e:
        print(f"❌ {e}")
    
    if i < len(candidates):
        time.sleep(15)

print(f"\n=== 完成: {success}/{len(candidates)}篇 ===")
