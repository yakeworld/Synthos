#!/usr/bin/env python3
"""
Batch download reference PDFs from .bib files and upload to NotebookLM.
Pipeline: .bib → extract DOIs → parallel download (racing engine with MedData) → upload

Supports MedData auto-login via environment variables:
    export MEDDATA_USERNAME="wzsrmyy"
    export MEDDATA_PASSWORD="xxx"

Usage:
    python3 download_and_upload.py
"""
import sys, os, re, subprocess, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "/media/yakeworld/sda2/Synthos/outputs/papers"
TOOL = "/media/yakeworld/sda2/Synthos/tools/paper-manager"
PY = "/usr/bin/python3"
ENV = os.environ.copy()  # inherits MEDDATA_USERNAME/PASSWORD if set

# Paper directory → NotebookLM project ID (edit as needed for new papers)
TARGETS = {
    "bppv-otoconia-simulation": "95509a49",
    "iris-yolo": "b6698e12",
    "cuteye-model": "468528f8",
}


def extract_dois(bib_path):
    dois = set()
    with open(bib_path) as f:
        for line in f:
            m = re.search(r'doi\s*=\s*[\{"]?(10\.\d{4,}/[^,}"\s]+)', line, re.I)
            if m:
                dois.add(m.group(1).strip())
    return sorted(dois)


def download_one(doi, out_path, timeout=60):
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return "exists", out_path
    cmd = f"cd {TOOL} && {PY} download_one.py '{doi}' '{out_path}'"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                      timeout=timeout, env=ENV)  # pass MEDDATA creds
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return "ok", out_path
    return "fail", out_path


def upload_to_nb(pdf_path, project_id):
    title = f"ref-{Path(pdf_path).stem}"
    cmd = f"notebooklm source add '{pdf_path}' --title '{title}' -n {project_id} --type file"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return r.returncode == 0


def process_paper(paper_dir, project_id, max_downloads=15):
    bibs = list(Path(f"{BASE}/{paper_dir}").glob("*.bib"))
    if not bibs:
        print(f"  ⚠️  No .bib found")
        return {"total": 0, "ok": 0, "existing": 0, "fail": 0, "uploaded": 0}

    dois = extract_dois(str(bibs[0]))
    if not dois:
        print(f"  ⚠️  No DOIs in {bibs[0].name}")
        return {"total": 0, "ok": 0, "existing": 0, "fail": 0, "uploaded": 0}

    if len(dois) > max_downloads:
        dois = dois[:max_downloads]

    pdf_dir = f"{BASE}/{paper_dir}/pdfs"
    os.makedirs(pdf_dir, exist_ok=True)

    stats = {"total": len(dois), "ok": 0, "existing": 0, "fail": 0, "uploaded": 0}
    print(f"  {len(dois)} DOIs to process...")

    with ThreadPoolExecutor(max_workers=3) as pool:
        fmap = {}
        for doi in dois:
            fname = doi.replace("/", "_").replace(".", "-") + ".pdf"
            out = f"{pdf_dir}/{fname}"
            fmap[pool.submit(download_one, doi, out)] = (doi, out)

        for f in as_completed(fmap, timeout=180):
            doi, out = fmap[f]
            try:
                status, _ = f.result(timeout=5)
            except Exception:
                status = "fail"

            if status == "ok":
                stats["ok"] += 1
                if upload_to_nb(out, project_id):
                    stats["uploaded"] += 1
                    print(f"    ✅ {doi[:45]} → uploaded")
                else:
                    print(f"    ✅ {doi[:45]} → upload FAILED")
            elif status == "exists":
                stats["existing"] += 1
                print(f"    ⏭ {doi[:45]} (exists)")
            else:
                stats["fail"] += 1
                print(f"    ❌ {doi[:45]}")

    return stats


def main():
    print("=" * 60)
    print("参考PDF批量下载 → 上传到NotebookLM")
    print("(支持MedData自动登录: MEDDATA_USERNAME + MEDDATA_PASSWORD)")
    print("=" * 60)

    all_stats = {}
    for paper_dir, project_id in TARGETS.items():
        print(f"\n📁 {paper_dir} → {project_id}")
        all_stats[paper_dir] = process_paper(paper_dir, project_id)

    print("\n" + "=" * 60)
    print("汇总")
    print("=" * 60)
    total_ok = total_up = total_all = 0
    for paper, s in all_stats.items():
        print(f"  {paper}: {s['ok']}/{s['total']} DL, {s['uploaded']} UP")
        total_ok += s["ok"]
        total_up += s["uploaded"]
        total_all += s["total"]
    print(f"\n总计: {total_ok}/{total_all} 已下载, {total_up} 已上传NotebookLM")


if __name__ == "__main__":
    main()
