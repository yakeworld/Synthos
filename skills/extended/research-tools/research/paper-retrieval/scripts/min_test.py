#!/usr/bin/env python3
import sys, time, os, hashlib
os.environ["SEMANTIC_SCHOLAR_API_KEY"] = "YOUR_API_KEY_HERE"

_engine_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _engine_dir)

from pdf_download_engine import smart_download, save_pdf, verify_pdf

print(f"Working dir: {os.getcwd()}", flush=True)
print(f"Engine dir: {_engine_dir}", flush=True)

# Test the full flow from _download_single -> _download_one
identifier = "2307.11274"
output = "/tmp/min_test.pdf"

print(f"[1] Setting up...", flush=True)
start = time.time()

print(f"[2] Calling smart_download...", flush=True)
content = smart_download("https://arxiv.org/pdf/2307.11274.pdf", timeout=15)
print(f"[3] Got {len(content) if content else 0} bytes in {time.time()-start:.1f}s", flush=True)

if content:
    print(f"[4] Verifying...", flush=True)
    if verify_pdf(content):
        print(f"[5] Valid PDF, saving...", flush=True)
        path = save_pdf(content, output)
        print(f"[6] Saved to {path}", flush=True)
    else:
        print(f"[5] Invalid PDF!", flush=True)
else:
    print(f"[3] No content!", flush=True)
