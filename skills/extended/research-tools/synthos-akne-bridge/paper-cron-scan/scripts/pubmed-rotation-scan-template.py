#!/usr/bin/env python3
"""
Multi-batch PubMed + OpenAlex scan template for paper-cron-scan.
Template for building rotation scan + candidate hunt + OpenAlex cross-check.

Usage: Create to /tmp/scan_vXXX.py → python3 /tmp/scan_vXXX.py → update tracker → append log.

Key patterns:
1. All external API calls go through Python scripts (no curl pipes)
2. PubMed and OpenAlex interleaved (different servers, no shared rate limit)
3. 5-7 queries per batch, 0.5s delay between, 0.5-0.8s between batches
4. All queries use urllib.parse.quote() for URL safety
5. All scripts write to /tmp/ to avoid polluting project directory

Rate-limit resilience (v159):
- NIH API is now cascading (None for most queries after ~3-5 successful ones)
- When most queries return None: trust historical patterns for rotation directions
- OpenAlex is the primary validator — it is never rate-limited
- Always record scan version vXX even if rate-limited
"""

import json, time, urllib.request, urllib.parse

# Constants
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term="
OA_BASE = "https://api.openalex.org/works?search="

def pubmed_count(query):
    """Return PubMed count. Returns None on API error (rate-limit, timeout, etc.)."""
    try:
        q = query.replace(" ", "+")
        url = BASE + urllib.parse.quote(q, safe='+')
        req = urllib.request.Request(url, headers={"User-Agent": "synthos-cron/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode()
            start = data.find("<Count>")
            if start == -1:
                return None
            end = data.find("</Count>", start)
            val = int(data[start+7:end])
            if "<Error>" in data:
                return -1
            return val
    except Exception:
        return None

def oa_count(query):
    """Return OpenAlex count. Never rate-limited."""
    try:
        url = OA_BASE + urllib.parse.quote(query, safe='+') + "&per_page=3&select=title,abstract_inverted_index"
        req = urllib.request.Request(url, headers={"User-Agent": "synthos-cron/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("count", 0)
    except Exception:
        return None

# ---- Example scan structure ----

def run_scan(scan_version="vXXX"):
    print(f"=== Scan {scan_version} ===")
    
    # Batch 1: Rotation (5 directions)
    rotations = {
        "VOR-PINN": "vestibulo-ocular-reflex+PINN+neural+ODE+dynamics",
        "Kappa-ML": "kappa+angle+calibration+machine+learning+eye",
        "BPPV-nystagmus-ML": "benign+paroxysmal+positional+vertigo+nystagmus+deep+learning",
        "PD-saccade": "parkinson+saccade+eye+movement+computational+model",
        "3D-Eye": "3D+eye+tracking+gaze+estimation+deep+learning",
    }
    
    rot_results = {}
    for name, q in rotations.items():
        c = pubmed_count(q)
        rot_results[name] = c
        print(f"  {name}: PubMed={c}")
        time.sleep(0.5)
    
    # Batch 2: New candidates (5-7)
    # ... add new candidate queries here ...
    
    # Batch 3: OpenAlex cross-check for PubMed=0 candidates
    # OpenAlex is primary validator
    oa_checks = {
        # name → query
    }
    for name, q in oa_checks.items():
        c = oa_count(q)
        print(f"  {name}: OpenAlex={c}")
        time.sleep(0.5)
    
    return rot_results

if __name__ == "__main__":
    run_scan()
