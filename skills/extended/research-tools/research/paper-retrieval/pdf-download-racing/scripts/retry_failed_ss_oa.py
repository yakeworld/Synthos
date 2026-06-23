#!/usr/bin/env python3
"""针对批量下载失败的DOI，只走Semantic Scholar openAccessPdf路径重试。

用法:
  python3 scripts/retry_failed_ss_oa.py

或用自定义DOI列表:
  python3 -c "
from pathlib import Path
exec(Path('scripts/retry_failed_ss_oa.py').read_text().split('# --- 主循环 ---')[0])
FAILED_DOIS = ['10.xxxx/xxx', '10.yyyy/yyy']
# --- 主循环 ---
..."
"""
import json, os, sys, time, requests

PDF_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'pdfs')
os.makedirs(PDF_DIR, exist_ok=True)

def query_ss_oa(doi):
    """查SS openAccessPdf"""
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf,externalIds,title"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            oa = (data.get("openAccessPdf") or {})
            return oa.get("url", ""), (data.get("title") or "?")[:60], (data.get("externalIds") or {}).get("PubMed", "")
        elif r.status_code == 404:
            return "", "(not in SS)", ""
        return "", f"(SS {r.status_code})", ""
    except Exception as e:
        return "", f"(error: {e})", ""

def retry_failed(failed_dois, pdf_dir=PDF_DIR):
    """Run SS OA retry on a list of DOIs. Returns counts."""
    oa_ok, oa_miss, no_ss = 0, 0, 0
    for i, doi in enumerate(failed_dois, 1):
        out = os.path.join(pdf_dir, doi.replace('/', '_') + '.pdf')
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            continue
        print(f"[{i}/{len(failed_dois)}] {doi[:55]}", end=' ', flush=True)
        oa_url, title, pmid = query_ss_oa(doi)
        if oa_url:
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
                    print(f"❌ SS-OA {r2.status_code} {len(r2.content)}B")
                    oa_miss += 1
            except Exception as e:
                print(f"❌ SS-OA error: {e}")
                oa_miss += 1
        else:
            print(f"⏭ 无OA直链 {title}")
            no_ss += 1
        time.sleep(0.5)
    return oa_ok, oa_miss, no_ss

# --- 主循环 ---
if __name__ == '__main__':
    FAILED_DOIS = sys.argv[1:] if len(sys.argv) > 1 else []
    if not FAILED_DOIS:
        print("Usage: python3 retry_failed_ss_oa.py <doi1> <doi2> ...")
        print("Or set FAILED_DOIS in script.")
        sys.exit(1)
    oa_ok, oa_miss, no_ss = retry_failed(FAILED_DOIS)
    print(f"\n✅ {oa_ok}新下载 | ⏭ {oa_miss}OA下载失败 | ❌ {no_ss}无OA直链")
