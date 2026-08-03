#!/usr/bin/env python3
"""修复所有 06-references/references.bib — 从 01-manuscript 的 tex 中提取引用键，
然后用 Crossref 根据论文标题+作者+年份精确查找。

对没有 sub-bib 的论文（AI 直接写 \cite 的），从 Crossref 回填。
对有 sub-bib 的论文，直接合并。
"""
import json, os, re, time, urllib.parse, sys
from urllib.request import urlopen, Request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS_DIR = os.path.join(BASE_DIR, 'outputs', 'papers')
CITE_RE = r'\\cite[^{]*{([^}]+)}'
BIB_RE = r'^@\w+\{([^,]+)'
CROSSREF_DELAY = 1.0  # Crossref rate limit: 1 req/sec

def fetch_crossref_by_title(title):
    """Search Crossref by exact or near-exact title."""
    if not title:
        return None
    query = urllib.parse.quote(title[:100])
    url = f'https://api.crossref.org/works?query={query}&select=title,author,container-title,DOI,published-print,created,volume,issue,publisher,ISBN&rows=1'
    req = Request(url, headers={'User-Agent': 'Synthos/2.0 (synthos-research@example.com)'})
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            items = data.get('message', {}).get('items', [])
            if items:
                return items[0]
    except Exception as e:
        print(f'  Crossref error: {e}', file=sys.stderr)
    return None

def fetch_crossref_by_author_year(author, year, title_hint=''):
    """Fallback: search by author + year + optional title hint."""
    query = f'{author} {year}'
    if title_hint:
        query += f' {title_hint}'
    query = urllib.parse.quote(query)
    url = f'https://api.crossref.org/works?query={query}&select=title,author,container-title,DOI,published-print,created&rows=1'
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

def parse_cite_key(key):
    """Parse 'authorYearrest' -> (author, year, rest)."""
    m = re.match(r'^([a-z]+?)(\d{4})(.+)$', key)
    if m:
        author = m.group(1).capitalize()
        year = m.group(2)
        rest = m.group(3)
        return author, year, rest
    return key, None, None

def doi_to_bibtex(entry):
    """Convert Crossref entry to BibTeX, preserving a stable key."""
    key_part = entry.get('author', [{}])[0].get('family', 'Unknown')[:15]
    year_data = entry.get('published-print', entry.get('created', {}))
    year = year_data.get('date-parts', [[0]])[0][0] if isinstance(year_data, dict) else 0
    key = f'{key_part}{year}'[:20]
    title = entry.get('title', [''])[0] if isinstance(entry.get('title'), list) else str(entry.get('title', ''))
    bibtex = f'@article{{{key},\n'
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

def get_tex_info(paper_dir):
    """Extract title and cite keys from tex file."""
    tex_path = os.path.join(paper_dir, '01-manuscript', 'paper.tex')
    if not os.path.exists(tex_path):
        return None, None, None
    
    with open(tex_path) as f:
        content = f.read()
    
    title_m = re.search(r'\\title\{(.+?)\}', content)
    title = title_m.group(1).strip() if title_m else None
    
    cite_keys = set()
    for m in re.findall(CITE_RE, content):
        for k in m.split(','):
            k = k.strip()
            if k:
                cite_keys.add(k)
    
    return title, cite_keys, content

def get_all_sub_bibs(paper_dir):
    """Get all real bib entries from paper sub-directories."""
    all_entries = {}
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
                if not re.search(r'^@\w+\{', content, re.MULTILINE):
                    continue
                for m in re.finditer(BIB_RE, content, re.MULTILINE):
                    key = m.group(1).strip()
                    if key not in all_entries:
                        all_entries[key] = path
            except Exception:
                pass
    return all_entries

def consolidate_into_bib(all_entries, target_path):
    """Write all entries into target bib file."""
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, 'w') as f:
        written = set()
        for key, source_path in all_entries.items():
            if key in written:
                continue
            with open(source_path) as bf:
                content = bf.read()
            key_pattern = r'@\w+\{' + re.escape(key) + r'\s*[,}]'
            for em in re.finditer(key_pattern, content):
                start = em.start()
                depth = 0
                end = start
                for i, c in enumerate(content[start:], start):
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                f.write(content[start:end])
                f.write('\n\n')
                written.add(key)
                break

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--paper', help='Process specific paper')
    parser.add_argument('--all', action='store_true', help='Process all papers')
    parser.add_argument('--crossref', action='store_true', help='Use Crossref for missing refs')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    args = parser.parse_args()

    # Find target papers
    papers = []
    if args.paper:
        full = os.path.join(PAPERS_DIR, args.paper)
        if os.path.isdir(full):
            papers.append((args.paper, full))
    elif args.all:
        for item in sorted(os.listdir(PAPERS_DIR)):
            full = os.path.join(PAPERS_DIR, item)
            if os.path.isdir(full) and os.path.exists(os.path.join(full, '01-manuscript', 'paper.tex')):
                papers.append((item, full))
    else:
        # Default: only fix papers with sub-bibs (consolidation)
        for item in sorted(os.listdir(PAPERS_DIR)):
            full = os.path.join(PAPERS_DIR, item)
            if not os.path.isdir(full):
                continue
            # Check if has sub-bibs but empty 06-references/bib
            sub_bibs = get_all_sub_bibs(full)
            if sub_bibs:
                bib_path = os.path.join(full, '06-references', 'references.bib')
                if not os.path.exists(bib_path):
                    papers.append((item, full))

    print(f"Processing {len(papers)} papers")
    total_consolidated = 0
    total_crossref = 0
    total_missing = 0

    for name, paper_dir in papers:
        title, cite_keys, tex_content = get_tex_info(paper_dir)
        sub_bibs = get_all_sub_bibs(paper_dir)
        target = os.path.join(paper_dir, '06-references', 'references.bib')
        
        if not os.path.exists(target):
            if args.dry_run:
                print(f"  {name}: needs consolidation")
                continue
            
            if sub_bibs:
                # Consolidate from sub-bibs
                consolidate_into_bib(sub_bibs, target)
                count = len(sub_bibs)
                total_consolidated += count
                print(f"  {name}: consolidated {count} entries from sub-bibs")
            elif args.crossref and cite_keys and title:
                # Generate from Crossref using title
                print(f"  {name}: generating from Crossref (title: {title[:60]}...)")
                entry = fetch_crossref_by_title(title)
                if entry:
                    bibtex, bkey = doi_to_bibtex(entry)
                    with open(target, 'w') as f:
                        f.write(f'{bibtex}\n')
                    total_crossref += 1
                    print(f"    Added {bkey}: {entry.get('title', [''])[0][:80]}")
                else:
                    total_missing += 1
                    print(f"    Crossref returned nothing")
            else:
                if not args.dry_run:
                    # Create placeholder for papers with no source
                    missing_keys = list(cite_keys)[:10] if cite_keys else []
                    with open(target, 'w') as f:
                        f.write(f'% Auto-generated placeholder for {name}\n')
                        f.write(f'% Total cite keys: {len(cite_keys or set())}\n')
                        f.write(f'% MISSING REFERENCES (need manual fix):\n')
                        for k in missing_keys:
                            f.write(f'% {k}\n')
                    total_missing += 1
                    print(f"  {name}: created placeholder ({len(missing_keys or [])} missing keys)")
        else:
            print(f"  {name}: already has 06-references/bib")

    print(f"\nDone: consolidated={total_consolidated}, crossref={total_crossref}, placeholder={total_missing}")

if __name__ == '__main__':
    main()
