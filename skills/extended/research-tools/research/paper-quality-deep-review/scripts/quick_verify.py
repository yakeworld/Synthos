#!/usr/bin/env python3
"""
Quick Verification Script
Quickly verify that the paper quality deep review skill can be loaded and all dependencies are available.
"""
import sys
import os
import json

def check_dependencies():
    """Check if all required dependencies are available"""
    print("=== Checking Dependencies ===\n")
    
    # Check PDF download engine
    print("1. PDF Download Engine:")
    engine_path = "/media/yakeworld/sda2/Synthos/skills/extended/research-tools/research/paper-retrieval/scripts/pdf_download_engine.py"
    if os.path.exists(engine_path):
        print(f"   ✅ pdf_download_engine.py exists at {engine_path}")
        
        # Check key functions
        with open(engine_path) as f:
            content = f.read()
            functions = [
                "download_scihub_direct",
                "download_scihub_via_tor",
                "download_meddata",
                "race_downloads",
                "verify_pdf",
                "download_s2_pdf",
                "download_crossref_oa",
                "download_unpaywall",
                "download_arxiv",
            ]
            for func in functions:
                if f"def {func}" in content:
                    print(f"   ✅ {func}")
                else:
                    print(f"   ❌ {func} not found")
    else:
        print(f"   ❌ pdf_download_engine.py not found at {engine_path}")
    
    # Check environment variables
    print("\n2. Environment Variables:")
    env_vars = {
        "MEDDATA_USERNAME": "MedData username",
        "MEDDATA_PASSWORD": "MedData password",
        "SEMANTIC_SCHOLAR_API_KEY": "Semantic Scholar API key",
        "TOR_PROXY": "Tor proxy URL",
    }
    for var, desc in env_vars.items():
        if os.environ.get(var):
            if var == "SEMANTIC_SCHOLAR_API_KEY":
                print(f"   ✅ {var}: {os.environ[var][:8]}...")
            else:
                print(f"   ✅ {var}: {'*' * len(os.environ[var])}")
        else:
            print(f"   ❌ {var}: NOT SET")
    
    # Check Python packages
    print("\n3. Python Packages:")
    packages = [
        ("requests", "HTTP requests"),
        ("curl_cffi", "TLS fingerprint"),
        ("bs4", "HTML parsing"),
        ("json", "JSON parsing"),
        ("hashlib", "MD5 hashing"),
        ("subprocess", "subprocess"),
        ("urllib", "URL handling"),
        ("re", "Regex"),
        ("time", "Time"),
    ]
    for pkg, desc in packages:
        try:
            __import__(pkg)
            print(f"   ✅ {pkg:15s} ({desc})")
        except ImportError:
            print(f"   ❌ {pkg:15s} ({desc}) NOT FOUND")
    
    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    check_dependencies()
