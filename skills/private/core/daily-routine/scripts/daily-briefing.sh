#!/usr/bin/env bash
# Daily intelligence briefing — data collection phase
# Run before composition; writes JSON to a known path.
# Usage: bash daily-briefing.sh [output_json_path]

set -euo pipefail
OUTPUT="${1:-/tmp/daily_briefing_data.json}"

echo "Collecting arXiv cs.CV..."
curl -sL -m 20 -H "User-Agent: Mozilla/5.0" \
  "https://arxiv.org/list/cs.CV/new" | python3 -c "
import sys, re
html = sys.stdin.read()
blocks = re.split(r'<dt>', html)
papers = []
for block in blocks[1:]:
    if 'list-title' not in block: continue
    id_m = re.search(r'arXiv:(\d+\.\d+)', block)
    if not id_m: continue
    desc_m = re.search(r'''class=['\"]descriptor['\"].*?Title:</span>.*?([^<]+)''', block, re.DOTALL)
    if desc_m:
        t = desc_m.group(1).strip()
        if t and len(t) > 10:
            papers.append({'id': id_m.group(1), 'title': t})
            if len(papers) >= 25: break
import json
json.dump(papers, open('/tmp/arxiv_cv.json','w'), ensure_ascii=False, indent=2)
print(f'  {len(papers)} papers')
"

echo "Collecting arXiv cs.AI..."
curl -sL -m 20 -H "User-Agent: Mozilla/5.0" \
  "https://arxiv.org/list/cs.AI/new" | python3 -c "
import sys, re
html = sys.stdin.read()
blocks = re.split(r'<dt>', html)
papers = []
for block in blocks[1:]:
    if 'list-title' not in block: continue
    id_m = re.search(r'arXiv:(\d+\.\d+)', block)
    if not id_m: continue
    desc_m = re.search(r'''class=['\"]descriptor['\"].*?Title:</span>.*?([^<]+)''', block, re.DOTALL)
    if desc_m:
        t = desc_m.group(1).strip()
        if t and len(t) > 10:
            papers.append({'id': id_m.group(1), 'title': t})
            if len(papers) >= 25: break
import json
json.dump(papers, open('/tmp/arxiv_ai.json','w'), ensure_ascii=False, indent=2)
print(f'  {len(papers)} papers')
"

echo "Collecting arXiv cs.LG..."
curl -sL -m 20 -H "User-Agent: Mozilla/5.0" \
  "https://arxiv.org/list/cs.LG/new" | python3 -c "
import sys, re
html = sys.stdin.read()
blocks = re.split(r'<dt>', html)
papers = []
for block in blocks[1:]:
    if 'list-title' not in block: continue
    id_m = re.search(r'arXiv:(\d+\.\d+)', block)
    if not id_m: continue
    desc_m = re.search(r'''class=['\"]descriptor['\"].*?Title:</span>.*?([^<]+)''', block, re.DOTALL)
    if desc_m:
        t = desc_m.group(1).strip()
        if t and len(t) > 10:
            papers.append({'id': id_m.group(1), 'title': t})
            if len(papers) >= 25: break
import json
json.dump(papers, open('/tmp/arxiv_lg.json','w'), ensure_ascii=False, indent=2)
print(f'  {len(papers)} papers')
"

echo "Collecting GitHub Trending..."
curl -sL -m 15 -H "User-Agent: Mozilla/5.0" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/search/repositories?q=created:>2026-06-17&sort=stars&order=desc&per_page=10" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
items = d.get('items',[])[:10]
repos = [{'stars': r.get('stargazers_count',0), 'name': r.get('full_name',''), 'description': r.get('description','N/A') or 'No description', 'language': r.get('language','Other') or 'Other'} for r in items]
json.dump(repos, open('/tmp/github_trending.json','w'), ensure_ascii=False, indent=2)
print(f'  {len(repos)} repos')
"

echo "Collecting Hacker News..."
curl -sL -m 15 "https://hacker-news.firebaseio.com/v0/topstories.json" | python3 -c "
import sys, json, urllib.request
ids = json.load(sys.stdin)[:25]
stories = []
for eid in ids:
    try:
        d = json.loads(urllib.request.urlopen(f'https://hacker-news.firebaseio.com/v0/item/{eid}.json', timeout=5).read())
        if d.get('type') == 'story':
            stories.append({'title': d.get('title',''), 'score': d.get('score',0), 'descendants': d.get('descendants',0)})
    except: pass
stories.sort(key=lambda x: x['score'], reverse=True)
json.dump(stories[:15], open('/tmp/hn_stories.json','w'), ensure_ascii=False, indent=2)
print(f'  {len(stories)} stories')
"

echo "Collecting The Verge..."
curl -sL -m 15 -H "User-Agent: Mozilla/5.0" "https://www.theverge.com/" | python3 -c "
import sys, re
html = sys.stdin.read()
links = re.findall(r'href=\"(/([^\"]+))\">\\s*([^<]{15,})</a>', html)
seen = set()
unique = []
for href, full, text in links:
    if href not in seen and len(text) > 15:
        seen.add(href)
        unique.append({'url': href, 'title': text})
json.dump(unique[:15], open('/tmp/verge_headlines.json','w'), ensure_ascii=False, indent=2)
print(f'  {len(unique)} headlines')
"

echo "Assembling ${OUTPUT}..."
python3 -c "
import json
files = ['/tmp/arxiv_cv.json','/tmp/arxiv_ai.json','/tmp/arxiv_lg.json','/tmp/github_trending.json','/tmp/hn_stories.json','/tmp/verge_headlines.json']
d = {}
for f in files:
    try:
        with open(f) as fh: d.update({f.split('/')[-1].replace('.json',''): json.load(fh)})
    except: pass
with open('${OUTPUT}', 'w') as f: json.dump(d, f, ensure_ascii=False, indent=2)
print(f'Written to ${OUTPUT}')
"

# Cleanup temp files
rm -f /tmp/arxiv_cv.json /tmp/arxiv_ai.json /tmp/arxiv_lg.json /tmp/github_trending.json /tmp/hn_stories.json /tmp/verge_headlines.json

echo "Done."
