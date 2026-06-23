#!/usr/bin/env python3
"""针对下载失败的DOI，只走Semantic Scholar openAccessPdf路径重试。"""
import json, os, sys, time, requests

BIB = '/media/yakeworld/sda2/Synthos/outputs/papers/pima-crispdm/06-references/references.bib'
PDF_DIR = '/media/yakeworld/sda2/Synthos/outputs/papers/pima-crispdm/06-references/pdfs'
os.makedirs(PDF_DIR, exist_ok=True)

# 从输出提取失败DOI
FAILED_DOIS = [
    "10.1002/eng2.13080",
    "10.1007/s10916-012-9822-z",
    "10.1007/s10916-024-02056-8",
    "10.1007/s41666-024-00189-8",
    "10.1016/j.jclinepi.2019.02.020",
    "10.1016/j.neucom.2017.10.095",
    "10.1016/j.patter.2024.101065",
    "10.1016/j.procs.2023.01.015",
    "10.1038/s42256-020-00241-3",
    "10.1056/NEJMp1703288",
    "10.1109/ACCESS.2024.3367890",
    "10.1109/DSML.2017.11",
    "10.1186/s43067-023-00074-5",
    "10.24432/C5QG71",
    "10.31315/telematika.v20i2.9676",
]

# 从bib查篇名
def get_bib_title(doi):
    with open(BIB) as f:
        text = f.read()
    # 按entry分割
    entries = text.split('\n@')
    for e in entries:
        if doi in e:
            for line in e.split('\n'):
                if line.strip().startswith('title'):
                    t = line.split('=', 1)[-1].strip().strip('{').strip('}').strip('"').strip(',')
                    return t[:80]
    return '?'

def query_ss_oa(doi):
    """查SS openAccessPdf，500ms timeout"""
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf,externalIds,title"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            oa = (data.get("openAccessPdf") or {})
            url = oa.get("url", "")
            title = (data.get("title") or "?")[:60]
            ext = (data.get("externalIds") or {})
            pmid = ext.get("PubMed", "")
            return url, title, pmid
        elif r.status_code == 404:
            return "", "(not in SS)", ""
        else:
            return "", f"(SS {r.status_code})", ""
    except Exception as e:
        return "", f"(SS error: {e})", ""

# --- 主循环 ---
print(f"=== Semantic Scholar openAccessPdf 重试: {len(FAILED_DOIS)}篇 ===")
print()

oa_ok, oa_miss, no_ss = 0, 0, 0

for i, doi in enumerate(FAILED_DOIS, 1):
    out = os.path.join(PDF_DIR, doi.replace('/', '_') + '.pdf')

    # 已存在则跳过
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        print(f"[{i}/{len(FAILED_DOIS)}] ✅ 已存在  {doi[:55]}")
        continue

    print(f"[{i}/{len(FAILED_DOIS)}] {doi[:55]}", end=' ', flush=True)
    oa_url, title, pmid = query_ss_oa(doi)

    if oa_url:
        # 有OA直链，下载
        try:
            r2 = requests.get(oa_url, timeout=30, allow_redirects=True,
                              headers={'User-Agent': 'Hermes/1.0'})
            if r2.status_code == 200 and len(r2.content) > 1000:
                with open(out, 'wb') as f:
                    f.write(r2.content)
                sz = len(r2.content) // 1024
                print(f"✅ SS-OA {sz}KB | {title}")
                oa_ok += 1
            else:
                print(f"❌ SS-OA {r2.status_code} {len(r2.content)}B | {title}")
                oa_miss += 1
        except Exception as e:
            print(f"❌ SS-OA error: {e}")
            oa_miss += 1
    else:
        print(f"⏭ 无OA直链 {title}")
        no_ss += 1

    # 礼貌间隔
    time.sleep(0.5)

print()
print(f"=== 完成: ✅ {oa_ok}篇新下载 | ⏭ {oa_miss}篇有OA但下载失败 | ❌ {no_ss}篇SS无OA直链 ===")
