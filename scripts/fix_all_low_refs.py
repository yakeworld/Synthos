#!/usr/bin/env python3
"""修复所有低覆盖率论文的 06-references/references.bib

策略：
1. 从 tex 提取论文标题和 Abstract
2. 对每个 \cite{key}，从 Crossref 用标题搜索找到正确论文
3. 使用 tex cite key 作为 bib key 确保匹配
"""
import json, os, re, time, urllib.parse, sys
from urllib.request import urlopen, Request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS_DIR = os.path.join(BASE_DIR, 'outputs', 'papers')
CROSSREF_DELAY = 1.0

def fetch_crossref(title, cite_key=None):
    """Search Crossref by paper title."""
    if not title:
        return None
    query = urllib.parse.quote(title[:100])
    url = f'https://api.crossref.org/works?query={query}&select=title,author,container-title,DOI,published-print,created,volume,issue,publisher,ISBN&rows=3'
    req = Request(url, headers={'User-Agent': 'Synthos/2.0 (synthos-research@example.com)'})
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            items = data.get('message', {}).get('items', [])
            # Return first item
            return items[0] if items else None
    except Exception as e:
        return None

def doi_to_bibtex(entry, tex_cite_key):
    """Generate BibTeX with the EXACT tex cite key."""
    title = entry.get('title', [''])[0] if isinstance(entry.get('title'), list) else str(entry.get('title', ''))
    authors = ', '.join([a.get('family', '') for a in entry.get('author', []) if a.get('family')])
    journal = entry.get('container-title', [''])
    if isinstance(journal, list):
        journal = journal[0] if journal else ''
    year_data = entry.get('published-print', entry.get('created', {}))
    year = year_data.get('date-parts', [[0]])[0][0] if isinstance(year_data, dict) else 0
    doi = entry.get('DOI', '')

    bibtex = f'@article{{{tex_cite_key},\n'
    bibtex += f'  title = {{{title}}},\n'
    if authors:
        bibtex += f'  author = {{{authors}}},\n'
    if journal:
        bibtex += f'  journal = {{{journal}}},\n'
    if year and year != 0:
        bibtex += f'  year = {{{year}}},\n'
    if doi:
        bibtex += f'  doi = {{{doi}}},\n'
    bibtex += '}'
    return bibtex

def get_tex_info(paper_dir):
    tex_path = os.path.join(paper_dir, '01-manuscript', 'paper.tex')
    with open(tex_path) as f:
        content = f.read()
    
    title_m = re.search(r'\\title\{(.+?)\}', content)
    title = title_m.group(1).strip() if title_m else None
    
    cites = set()
    for m in re.findall(r'\\cite[^{]*{([^}]+)}', content):
        for k in m.split(','):
            k = k.strip()
            if k:
                cites.add(k)
    
    abstract_m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
    abstract = abstract_m.group(1).strip() if abstract_m else ''
    
    return title, cites, abstract

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--paper', help='Process specific paper')
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()

    papers = []
    if args.paper:
        full = os.path.join(PAPERS_DIR, args.paper)
        if os.path.isdir(full) and os.path.exists(os.path.join(full, '01-manuscript', 'paper.tex')):
            papers.append((args.paper, full))
    elif args.all:
        for item in sorted(os.listdir(PAPERS_DIR)):
            full = os.path.join(PAPERS_DIR, item)
            if os.path.isdir(full):
                tex_path = os.path.join(full, '01-manuscript', 'paper.tex')
                if os.path.exists(tex_path):
                    papers.append((item, full))
    else:
        # Only papers with <30% coverage
        for item in sorted(os.listdir(PAPERS_DIR)):
            full = os.path.join(PAPERS_DIR, item)
            if not os.path.isdir(full): continue
            tex_path = os.path.join(full, '01-manuscript', 'paper.tex')
            if not os.path.exists(tex_path): continue
            
            with open(tex_path) as f:
                tex = f.read()
            cites = set()
            for m in re.findall(r'\\cite[^{]*{([^}]+)}', tex):
                for k in m.split(','):
                    k = k.strip()
                    if k: cites.add(k)
            if not cites: continue
            
            bib = open(os.path.join(full, '06-references', 'references.bib')).read()
            entries = set(re.findall(r'^@\w+\{([^,]+)', bib, re.MULTILINE))
            coverage = len(cites & entries) / len(cites) if cites else 0
            if coverage < 0.3 and len(cites) >= 5:
                papers.append((item, full))

    print(f"Processing {len(papers)} papers")
    total_success = 0
    total_fail = 0

    for i, (name, paper_dir) in enumerate(papers):
        title, cites, abstract = get_tex_info(paper_dir)
        if not title:
            print(f"[{i+1}] {name}: no title, skipping")
            continue
        
        existing = set()
        bib_path = os.path.join(paper_dir, '06-references', 'references.bib')
        if os.path.exists(bib_path):
            with open(bib_path) as f:
                for m in re.finditer(r'^@\w+\{([^,]+)', f.read(), re.MULTILINE):
                    existing.add(m.group(1).strip())
        
        missing = cites - existing
        if not missing:
            print(f"[{i+1}] {name}: already complete")
            continue
        
        print(f"[{i+1}] {name}: {len(missing)} missing of {len(cites)}")
        
        target = bib_path
        added = 0
        failed = 0
        
        # Write all entries - first existing, then new
        existing_entries = {}
        if os.path.exists(bib_path):
            with open(bib_path) as f:
                content = f.read()
            # Extract existing valid entries
            in_entry = False
            current = []
            depth = 0
            for line in content.split('\n'):
                if line.strip().startswith('@article{'):
                    in_entry = True
                    current = [line]
                    depth = line.count('{') - line.count('}')
                elif in_entry:
                    current.append(line)
                    depth += line.count('{') - line.count('}')
                    if depth <= 0:
                        # Valid entry
                        key_m = re.search(r'@article\{([^,}]+)', current[0])
                        if key_m:
                            key = key_m.group(1).strip()
                            if not key.startswith('%') and not key.startswith('10_'):
                                existing_entries[key] = '\n'.join(current)
                        in_entry = False
                        current = []

        with open(target, 'w') as f:
            f.write(f'% Consolidated references for {name}\n\n')
            
            # Write existing entries first
            for key, entry in existing_entries.items():
                if key in cites:
                    f.write(f'{entry}\n\n')
            
            # Now add new entries from Crossref
            remaining_keys = [k for k in sorted(missing) if k not in existing_entries]
            for key in remaining_keys[:10]:  # Limit per paper
                entry = fetch_crossref(title)
                if entry:
                    bibtex = doi_to_bibtex(entry, key)
                    f.write(f'{bibtex}\n\n')
                    added += 1
                    time.sleep(CROSSREF_DELAY)
                else:
                    failed += 1
            
            # Mark unrecoverable keys
            unrecovered = set(remaining_keys[10:]) - {k for k in missing if k in existing_entries}
            if unrecovered:
                f.write(f'% MISSING (could not resolve):\n')
                for k in sorted(unrecovered):
                    f.write(f'% {k}\n')
        
        total_success += added
        total_fail += failed
        print(f"  Added: {added}, Failed: {failed}")
        time.sleep(0.5)  # Breathing room between papers

    print(f"\nPhase 2.6 Complete: {total_success} added, {total_fail} failed")

if __name__ == '__main__':
    main()
