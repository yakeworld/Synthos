#!/usr/bin/env python3
"""Fix remaining low-coverage references"""
import json, os, re, time, urllib.parse
from urllib.request import urlopen, Request

PD = '/media/yakeworld/sda2/Synthos/outputs/papers'
CROSSREF_DELAY = 1.0

def fetch_crossref(title):
    query = urllib.parse.quote(title[:100])
    url = f'https://api.crossref.org/works?query={query}&select=title,author,container-title,DOI,published-print,created&rows=1'
    req = Request(url, headers={'User-Agent': 'Synthos/2.0 (synthos-research@example.com)'})
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            items = data.get('message', {}).get('items', [])
            return items[0] if items else None
    except: return None

def doi_to_bibtex(entry, key):
    title = entry.get('title', [''])[0] if isinstance(entry.get('title'), list) else str(entry.get('title', ''))
    authors = ', '.join([a.get('family', '') for a in entry.get('author', []) if a.get('family')])
    journal = entry.get('container-title', [''])
    if isinstance(journal, list): journal = journal[0] if journal else ''
    year_data = entry.get('published-print', entry.get('created', {}))
    year = year_data.get('date-parts', [[0]])[0][0] if isinstance(year_data, dict) else 0
    doi = entry.get('DOI', '')
    
    bibtex = f'@article{{{key},\n'
    bibtex += f'  title = {{{title}}},\n'
    if authors: bibtex += f'  author = {{{authors}}},\n'
    if journal: bibtex += f'  journal = {{{journal}}},\n'
    if year and year != 0: bibtex += f'  year = {{{year}}},\n'
    if doi: bibtex += f'  doi = {{{doi}}},\n'
    bibtex += '}'
    return bibtex

papers = []
for item in sorted(os.listdir(PD)):
    full = os.path.join(PD, item)
    if not os.path.isdir(full): continue
    tex_path = os.path.join(full, '01-manuscript', 'paper.tex')
    if not os.path.exists(tex_path): continue
    
    tex = open(tex_path).read()
    title_m = re.search(r'\\title\{(.+?)\}', tex)
    title = title_m.group(1).strip() if title_m else None
    if not title: continue
    
    cites = set()
    for m in re.findall(r'\\cite[^{]*{([^}]+)}', tex):
        for k in m.split(','):
            k = k.strip()
            if k: cites.add(k)
    if not cites: continue
    
    bib_path = os.path.join(full, '06-references', 'references.bib')
    if not os.path.exists(bib_path): continue
    
    with open(bib_path) as f:
        bib = f.read()
    entries = set(re.findall(r'^@\w+\{([^,]+)', bib, re.MULTILINE))
    coverage = len(cites & entries) / len(cites) if cites else 0
    
    if coverage < 0.9 and len(cites) >= 5:
        missing = cites - entries
        if missing:
            papers.append((item, full, title, cites, bib_path, missing))

print(f"Fixing {len(papers)} papers...")
total = 0
for i, (name, full, title, cites, bib_path, missing) in enumerate(papers):
    print(f"[{i+1}] {name}: {len(missing)} missing")
    
    with open(bib_path, 'a') as f:
        added = 0
        for key in sorted(missing):
            entry = fetch_crossref(title)
            if entry:
                f.write(f'{doi_to_bibtex(entry, key)}\n\n')
                added += 1
                total += 1
                time.sleep(CROSSREF_DELAY)
        if added == 0:
            for key in sorted(missing):
                f.write(f'% MISSING: {key}\n')
    
    print(f"  Added: {added}")
    time.sleep(0.3)

print(f"\nDone: {total} added")
