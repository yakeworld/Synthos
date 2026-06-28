#!/usr/bin/env python3
"""Daily intelligence briefing — unified data collection phase.

Collects arXiv new listings, GitHub trending, HN top stories, and The Verge headlines.
Outputs a single JSON file consumable by the composition step.

Cron-safe: all scripts saved to /tmp first, then executed as standalone files.
No curl|python3 pipes (blocked by cron security scanner).
No execute_code (blocked in cron mode).
"""

import urllib.request
import json
import re
import sys
from datetime import datetime, timezone, timedelta

# ============================================================
# arXiv paper fetching
# ============================================================
def fetch_arxiv(category, limit=25):
    """Fetch paper titles from arXiv new listings.
    
    Key parsing detail: arXiv HTML uses single-quoted attributes:
    class='list-title mathjax'
    The title appears inside: <span class='descriptor'>Title:</span> followed by text
    
    Common failure mode: using double quotes in regex when HTML has single quotes.
    """
    url = f"https://arxiv.org/list/cs.{category}/new"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", errors="ignore")
        
        blocks = re.split(r"<dt>", html)
        papers = []
        for block in blocks[1:]:
            if "list-title" not in block:
                continue
            id_match = re.search(r"arXiv:(\d+\.\d+)", block)
            if not id_match:
                continue
            # Single quotes in HTML — class='descriptor' — use raw string with escaped quotes
            desc_match = re.search(r'class=[\x27"].*?Title:</span>.*?([^<]+)', block, re.DOTALL)
            if desc_match:
                title = desc_match.group(1).strip()
                if title and len(title) > 10:
                    papers.append({"id": id_match.group(1), "title": title})
                    if len(papers) >= limit:
                        break
        return papers
    except Exception as e:
        print(f"  arXiv cs.{category} error: {e}", file=sys.stderr)
        return []

# ============================================================
# GitHub trending
# ============================================================
def fetch_github_trending():
    try:
        url = "https://api.github.com/search/repositories?q=created:>2026-06-17&sort=stars&order=desc&per_page=10"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/vnd.github.v3+json"
        })
        data = json.loads(urllib.request.urlopen(req, timeout=15).read())
        repos = []
        for r in data.get('items', [])[:10]:
            repos.append({
                'stars': r.get('stargazers_count', 0),
                'name': r.get('full_name', ''),
                'description': r.get('description', 'N/A') or 'No description',
                'language': r.get('language', 'Other') or 'Other'
            })
        return repos
    except Exception as e:
        print(f"  GitHub error: {e}", file=sys.stderr)
        return []

# ============================================================
# Hacker News
# ============================================================
def fetch_hackernews():
    try:
        ids = json.loads(urllib.request.urlopen("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10).read())
        stories = []
        for eid in ids[:25]:
            try:
                data = json.loads(urllib.request.urlopen(f"https://hacker-news.firebaseio.com/v0/item/{eid}.json", timeout=5).read())
                if data.get('type') == 'story':
                    stories.append({
                        "title": data.get('title', ''),
                        "score": data.get('score', 0),
                        "descendants": data.get('descendants', 0)
                    })
            except:
                pass
        stories.sort(key=lambda x: x['score'], reverse=True)
        return [(s['title'], s['score'], s['descendants']) for s in stories[:15]]
    except Exception as e:
        print(f"  HN error: {e}", file=sys.stderr)
        return []

# ============================================================
# The Verge
# ============================================================
def fetch_theverge():
    try:
        html = urllib.request.urlopen("https://www.theverge.com/", timeout=15).read().decode("utf-8", errors="ignore")
        # The Verge uses classless DOM — extract href + text pairs
        headlines = re.findall(r'href="(/[^"]+)">\s*([^<]{15,})</a>', html)
        seen = set()
        unique = []
        for href, text in headlines:
            if href not in seen and len(text) > 15:
                seen.add(href)
                unique.append({'url': href, 'title': text})
        return unique[:15]
    except Exception as e:
        print(f"  The Verge error: {e}", file=sys.stderr)
        return []

# ============================================================
# Main
# ============================================================
def main():
    output = sys.argv[1] if len(sys.argv) > 1 else "/tmp/daily_briefing_data.json"
    
    results = {}
    
    print("Fetching arXiv cs.CV...", file=sys.stderr)
    results['cs_cv'] = fetch_arxiv('CV', 25)
    
    print("Fetching arXiv cs.AI...", file=sys.stderr)
    results['cs_ai'] = fetch_arxiv('AI', 25)
    
    print("Fetching arXiv cs.LG...", file=sys.stderr)
    results['cs_lg'] = fetch_arxiv('LG', 25)
    
    print("Fetching GitHub trending...", file=sys.stderr)
    results['github'] = fetch_github_trending()
    
    print("Fetching Hacker News...", file=sys.stderr)
    results['hn'] = fetch_hackernews()
    
    print("Fetching The Verge...", file=sys.stderr)
    results['verge'] = fetch_theverge()
    
    with open(output, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    for k, v in results.items():
        if isinstance(v, list):
            print(f"  {k}: {len(v)} items", file=sys.stderr)
        elif isinstance(v, dict):
            print(f"  {k}: {len(v)} items", file=sys.stderr)

if __name__ == '__main__':
    main()
