#!/usr/bin/env python3
"""Test _download_single in isolation."""
import sys, time, os, json
os.environ["SEMANTIC_SCHOLAR_API_KEY"] = "YOUR_API_KEY_HERE"

_engine_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _engine_dir)

# Manually replicate _download_single
from pdf_download_engine import (
    race_downloads, verify_pdf, save_pdf, smart_download,
    normalize_doi, extract_arxiv_id, extract_pmid,
    DEFAULT_OUTPUT_DIR,
)
from unified_download import _download_one

print(f"[0] Engine dir: {_engine_dir}", flush=True)

identifier = "2307.11274"
output_path = "/tmp/test_ds.pdf"

print(f"[1] _download_single setup...", flush=True)
start = time.time()

result = _download_one(
    {"title": identifier, "doi": "", "arxiv_id": "2307.11274", "pmid": "", "source": "arxiv", "arxiv_url_pdf": "https://arxiv.org/pdf/2307.11274.pdf"},
    output_path
)

elapsed = time.time() - start
print(f"[2] Result in {elapsed:.1f}s", flush=True)
print(json.dumps(result, indent=2, ensure_ascii=False))
sys.exit(0 if result.get("status") == "success" else 1)