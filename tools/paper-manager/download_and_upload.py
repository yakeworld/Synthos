#!/usr/bin/env python3
"""
Batch download reference PDFs from .bib files and upload to NotebookLM.
Targets: BPPV (95509a49), 3D眼球 (b6698e12), CutEye (468528f8)
"""
import sys, os, re, subprocess, json, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/media/yakeworld/sda2/Synthos/outputs/papers"
TOOL = "/media/yakeworld/sda2/Synthos/tools/paper-manager"
PY = "/usr/bin/python3"

# Paper dir → NotebookLM project ID
TARGETS = {
    "bppv-otoconia-simulation": "95509a49",
    "iris-yolo": "b6698e12",
    "cuteye-model": "468528f8",
}

def extract_dois(bib_path):
    """Extract DOIs from .bib file."""
    dois = set()
    with open(bib_path) as f:
        for line in f:
            m = re.search(r'doi\s*=\s*[\{"]?(10\.\d{4,}/[^,}"\s]+)', line, re.I)
            if m:
                dois.add(m.group(1).strip())
    return sorted(dois)

def download_one(doi, out_path, timeout=60):
    """Download a single DOI PDF via the racing engine."""
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return "exists"
    cmd = f"cd {TOOL} && {PY} download_one.py '{doi}' '{out_path}'"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return "ok"
    return "fail"

def upload_to_notebooklm(pdf_path, project_id, title=None):
    """Upload a PDF to NotebookLM project."""
    if not title:
        title = f"ref-{Path(pdf_path).stem}"
    cmd = f"notebooklm source add '{pdf_path}' --title '{title}' -n {project_id} --type file 2>/dev/null"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return "✅" if r.returncode == 0 else f"❌ {r.stderr[:100]}"

def process_paper(paper_dir, project_id, max_downloads=10):
    """Process all DOIs for a paper."""
    bibs = list(Path(f"{BASE}/{paper_dir}").glob('references.bib'))
    if not bibs:
        bibs = list(Path(f"{BASE}/{paper_dir}").glob('*.bib'))
    if not bibs:
        print(f"  ⚠️  No .bib found")
        return {"total": 0, "ok": 0, "existing": 0, "fail": 0, "uploaded": 0}
    
    bib_path = str(bibs[0])
    dois = extract_dois(bib_path)
    if not dois:
        print(f"  ⚠️  No DOIs in {bib_path.name}")
        return {"total": 0, "ok": 0, "existing": 0, "fail": 0, "uploaded": 0}
    
    # Limit to first N for speed
    if len(dois) > max_downloads:
        dois = dois[:max_downloads]
    
    pdf_dir = f"{BASE}/{paper_dir}/pdfs"
    os.makedirs(pdf_dir, exist_ok=True)
    
    stats = {"total": len(dois), "ok": 0, "existing": 0, "fail": 0, "uploaded": 0}
    
    print(f"  {len(dois)} DOIs to process...")
    
    # Download up to 3 in parallel
    with ThreadPoolExecutor(max_workers=3) as pool:
        future_map = {}
        for doi in dois:
            fname = doi.replace('/', '_').replace('.','-') + ".pdf"
            out = f"{pdf_dir}/{fname}"
            future = pool.submit(download_one, doi, out)
            future_map[future] = (doi, out)
        
        for future in as_completed(future_map, timeout=180):
            doi, out = future_map[future]
            try:
                status = future.result(timeout=5)
            except Exception:
                status = "fail"
            
            if status == "ok":
                stats["ok"] += 1
                # Upload to NotebookLM
                up = upload_to_notebooklm(out, project_id)
                if "✅" in up:
                    stats["uploaded"] += 1
                print(f"    ✅ {doi[:45]} → uploaded {up}")
            elif status == "exists":
                stats["existing"] += 1
                print(f"    ⏭ {doi[:45]} (exists)")
            else:
                stats["fail"] += 1
                print(f"    ❌ {doi[:45]}")
    
    return stats


def main():
    print("=" * 60)
    print("参考文献PDF批量下载 & 上传到NotebookLM")
    print("=" * 60)
    
    all_stats = {}
    for paper_dir, project_id in TARGETS.items():
        print(f"\n📁 {paper_dir} → project {project_id}")
        all_stats[paper_dir] = process_paper(paper_dir, project_id, max_downloads=15)
    
    # 汇总
    print("\n" + "=" * 60)
    print("汇总")
    print("=" * 60)
    total_ok = total_uploaded = total_all = 0
    for paper, s in all_stats.items():
        print(f"  {paper}: {s['ok']}/{s['total']}已下载, {s['uploaded']}已上传")
        total_ok += s['ok']
        total_uploaded += s['uploaded']
        total_all += s['total']
    print(f"\n总计: {total_ok}/{total_all} OK, {total_uploaded} uploaded to NotebookLM")

if __name__ == "__main__":
    main()
