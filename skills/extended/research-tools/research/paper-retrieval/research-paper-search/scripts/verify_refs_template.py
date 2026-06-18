#!/usr/bin/env python3
"""
Reference Verification Template — verify paper references via OpenAlex.
Usage: python3 verify_refs.py <paper_dir>/01-manuscript/

Adapt the `refs` dict to match your paper's references.
"""
import urllib.request, json, time, urllib.parse

def oa(query):
    """OpenAlex search — bare spaces work in Python 3.12 urllib."""
    url = f"https://api.openalex.org/works?search={query}&per_page=3"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            results = []
            for w in d.get("results", [])[:3]:
                results.append(f"{w.get('title','?')} ({w.get('publication_year','?')}) DOI={w.get('doi','?')}")
            return results
    except Exception as e:
        return [f"ERR: {e}"]

# === CONFIGURE: Add references for your paper ===
refs = {
    "Domain References": [
        ("RefKey", "search query terms"),
    ],
}

# === RUN ===
for category, items in refs.items():
    print(f"--- {category} ---")
    for key, query in items:
        time.sleep(1.2)
        results = oa(query)
        for r in results[:2]:
            if not r.startswith("ERR"):
                print(f"  {key}: {r}")
    print()
