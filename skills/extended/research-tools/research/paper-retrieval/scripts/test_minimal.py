#!/usr/bin/env python3
"""Test: minimal CLI wrapper."""
import sys, os, time, json, hashlib

_engine_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _engine_dir)

from pdf_download_engine import smart_download, save_pdf, verify_pdf, DEFAULT_OUTPUT_DIR

print(f"TOPLEVEL: engine_dir={_engine_dir}", flush=True)
print(f"TOPLEVEL: exists={os.path.exists(_engine_dir + '/pdf_download_engine.py')}", flush=True)

identifier = "2307.11274"
output = "/tmp/test_minimal.pdf"

print(f"STEP 1: Starting download...", flush=True)
start = time.time()

# Direct arxiv download
content = smart_download("https://arxiv.org/pdf/2307.11274.pdf", timeout=15)
print(f"STEP 2: Got {len(content) if content else 0} bytes in {time.time()-start:.1f}s", flush=True)

if content and verify_pdf(content):
    path = save_pdf(content, output)
    print(f"STEP 3: Saved to {path}, {len(content)} bytes", flush=True)
    print(f"STEP 4: MD5={hashlib.md5(content).hexdigest()}", flush=True)
    sys.exit(0)
else:
    print("STEP 3: FAILED", flush=True)
    sys.exit(1)