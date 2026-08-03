#!/usr/bin/env python3
"""Phase 2: 引用完整性批量修复"""
import json, os, re, time, sys, urllib.parse
from urllib.request import urlopen, Request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS_DIR = os.path.join(BASE_DIR, 'outputs', 'papers')
CITE_RE = r'\\cite[^{]*{([^}]+)}'
BIB_RE = r'@\w+\{([^,]+)'
MAX_PAPERS = 15
CROSSREF_DELAY = 0.8

def parse_key(key):
    """Parse author-year citation key like 'randleman2008staging' into author + year + rest."""
    match = re.match(r'^([a-z]+)(\d{4})(.*)$', key)
    if match:
        author = match.group(1).capitalize()
        year = match.group(2)
        rest = match.group(3)
        return author, year, rest
    return key, None, None

def fetch_crossref(key):
    """Search Crossref using author+year from the citation key."""
    author, year, rest = parse_key(key)
    if not author or not year:
        return None

    # Build query: author + year + any additional words from key
    query_parts = [author, year]
    if rest:
        # Convert camelCase or concatenated words into separate terms
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', rest)
        query_parts.extend(words[:2])  # Max 2 extra words

    query = '+'.join(query_parts)
    params = urllib.parse.urlencode({
        'query': query,
        'select': 'title,author,container-title,DOI,published-print,created,volume,issue,publisher',
        'rows': '1'
    })
    url = f'https://api.crossref.org/works?{params}'
    req = Request(url, headers={'User-Agent': 'Synthos/2.0 (synthos-research@example.com)'})
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            items = data.get('message', {}).get('items', [])
            if items:
                return items[0]
    except Exception:
        pass
    return None

def doi_to_bibtex(entry):
    key_part = entry.get('author', [{}])[0].get('family', 'Unknown')[:15]
    year_data = entry.get('published-print', entry.get('created', {}))
    year = year_data.get('date-parts', [[0]])[0][0] if isinstance(year_data, dict) else 0
    key = f'{key_part}{year}'[:20]
    bibtex = f'@article{{{key},\n'
    title = entry.get('title', [''])[0] if isinstance(entry.get('title'), list) else str(entry.get('title', ''))
    bibtex += f'  title = {{{title}}},\n'
    authors = ', '.join([a.get('family', '') for a in entry.get('author', []) if a.get('family')])
    if authors:
        bibtex += f'  author = {{{authors}}},\n'
    journal = entry.get('container-title', [''])
    if isinstance(journal, list):
        journal = journal[0] if journal else ''
    if journal:
        bibtex += f'  journal = {{{journal}}},\n'
    if year and year != 0:
        bibtex += f'  year = {{{year}}},\n'
    doi = entry.get('DOI', '')
    if doi:
        bibtex += f'  doi = {{{doi}}},\n'
    bibtex += '}'
    return bibtex, key

def get_cite_keys(tex_path):
    with open(tex_path) as f:
        content = f.read()
    matches = re.findall(CITE_RE, content)
    keys = set()
    for m in matches:
        for k in m.split(','):
            keys.add(k.strip())
    return keys

def get_all_bib_entries(paper_dir):
    all_entries = {}
    bib_files = []
    for root, dirs, files in os.walk(paper_dir):
        for f in files:
            if not f.endswith('.bib'):
                continue
            path = os.path.join(root, f)
            if os.path.islink(path) and not os.path.exists(path):
                continue
            if not os.path.isfile(path):
                continue
            try:
                with open(path) as bf:
                    content = bf.read()
                has_real = bool(re.search(r'^@\w+\{', content, re.MULTILINE))
                if has_real:
                    bib_files.append(path)
                    for m in re.finditer(BIB_RE, content):
                        key = m.group(1).strip()
                        if key not in all_entries:
                            all_entries[key] = path
            except Exception:
                pass
    return all_entries, bib_files

def main():
    papers = []
    for item in sorted(os.listdir(PAPERS_DIR)):
        full = os.path.join(PAPERS_DIR, item)
        if not os.path.isdir(full):
            continue
        tex_path = os.path.join(full, '01-manuscript', 'paper.tex')
        if not os.path.exists(tex_path):
            continue

        tex_keys = get_cite_keys(tex_path)
        if not tex_keys:
            continue

        all_entries, bib_files = get_all_bib_entries(full)
        missing = tex_keys - set(all_entries.keys())
        coverage = len(tex_keys & set(all_entries.keys())) / len(tex_keys) if tex_keys else 0

        papers.append({
            'name': item, 'path': full, 'cites': tex_keys,
            'all_entries': all_entries, 'bib_files': bib_files,
            'missing': list(missing), 'coverage': coverage,
        })

    papers.sort(key=lambda p: p['coverage'])
    print(f"Phase 2: {len(papers)} papers ({sum(1 for p in papers if p['coverage'] == 0)} zero coverage)")
    print()

    total_added = 0
    total_failed = 0
    results = []

    for i, paper in enumerate(papers[:MAX_PAPERS]):
        print(f"[{i+1}/{MAX_PAPERS}] {paper['name']}")
        print(f"  Coverage: {paper['coverage']:.0%}, Missing: {len(paper['missing'])}")

        if not paper['missing']:
            results.append({'name': paper['name'], 'added': 0, 'status': 'complete'})
            continue

        target_bib = None
        for pp in [
            os.path.join(paper['path'], '01-manuscript', 'references.bib'),
            os.path.join(paper['path'], '01-manuscript', 'reference_enhanced.bib'),
        ]:
            if os.path.isfile(pp) and not os.path.islink(pp):
                target_bib = pp
                break
        if not target_bib and paper['bib_files']:
            target_bib = max(paper['bib_files'], key=lambda f: os.path.getsize(f))
        if not target_bib:
            target_bib = os.path.join(paper['path'], '06-references', 'references.bib')
            os.makedirs(os.path.dirname(target_bib), exist_ok=True)

        added = 0
        failed = []
        for key in paper['missing'][:6]:
            entry = fetch_crossref(key)
            if entry:
                bibtex, bkey = doi_to_bibtex(entry)
                with open(target_bib, 'a') as f:
                    f.write(f'\n{bibtex}\n')
                paper['all_entries'][key] = target_bib
                added += 1
                total_added += 1
                time.sleep(CROSSREF_DELAY)
            else:
                failed.append(key)
                total_failed += 1

        print(f"  Added: {added}, Failed: {len(failed)}")
        results.append({'name': paper['name'], 'added': added, 'failed': len(failed)})
        print()

    result_path = os.path.join(BASE_DIR, 'scripts', 'phase2_results.json')
    with open(result_path, 'w') as f:
        json.dump({
            'total_papers': len(papers),
            'papers_processed': len(results),
            'total_added': total_added,
            'total_failed': total_failed,
            'results': results,
        }, f, indent=2, ensure_ascii=False)

    print(f"Phase 2 Complete: {total_added} added, {total_failed} failed across {len(results)} papers")

if __name__ == '__main__':
    main()
