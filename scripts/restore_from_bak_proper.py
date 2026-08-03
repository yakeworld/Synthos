#!/usr/bin/env python3
"""从 .bak 备份精确恢复参考文献 — 使用 tex cite key 作为 bib key"""
import json, os, re, time, sys
from urllib.request import urlopen, Request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS_DIR = os.path.join(BASE_DIR, 'outputs', 'papers')

def extract_real_bib_entries(content):
    """Extract clean @article entries from .bak content.
    Skip @comment wrappers and DOI-keyed entries."""
    entries = {}
    # Use line-by-line approach for accuracy
    lines = content.split('\n')
    in_entry = False
    current_entry = []
    current_key = None
    brace_depth = 0
    
    for line in lines:
        if in_entry:
            current_entry.append(line)
            brace_depth += line.count('{') - line.count('}')
            if brace_depth <= 0:
                # End of entry
                block = '\n'.join(current_entry)
                # Check if this is a real entry
                has_title = 'title' in block.lower()
                has_author = 'author' in block.lower()
                if has_title and has_author:
                    # Extract key from first line
                    key_m = re.search(r'@article\{([^,}]+)', current_entry[0])
                    if key_m:
                        key = key_m.group(1).strip()
                        # Skip DOI-keyed or comment entries
                        if not key.startswith('10_') and not key.startswith('%'):
                            entries[key] = block
                in_entry = False
                current_entry = []
                current_key = None
        else:
            if line.strip().startswith('@article{') or line.strip().startswith('@comment{@article{'):
                in_entry = True
                current_entry = [line]
                brace_depth = line.count('{') - line.count('}')

    return entries

def match_keys(tex_cites, bib_entries):
    """Match tex cite keys to bib entry keys using author+year."""
    matches = {}
    for cite_key in tex_cites:
        # Parse author+year from cite key: 'carey2003' -> ('carey', '2003')
        m = re.match(r'^([a-z]+?)(\d{4})(.*)$', cite_key)
        if not m:
            continue
        cite_author = m.group(1).lower()
        cite_year = m.group(2)
        
        for bib_key, bib_entry in bib_entries.items():
            # Extract author and year from bib entry
            author_m = re.search(r'author\s*=\s*\{([^}]+)\}', bib_entry, re.IGNORECASE)
            year_m = re.search(r'year\s*=\s*\{(\d{4})\}', bib_entry, re.IGNORECASE)
            
            if author_m and year_m:
                bib_author = author_m.group(1).lower()
                bib_year = year_m.group(1)
                
                # Match: same year AND author name appears in bib author list
                if cite_year == bib_year and cite_author in bib_author:
                    matches[cite_key] = bib_entry
                    break
                
                # Also try matching just the year with short author name
                if cite_year == bib_year:
                    short_authors = [a.strip().lower() for a in bib_author.split(',') if len(a.strip()) > 2]
                    if cite_author in short_authors or any(cite_author in a for a in short_authors):
                        matches[cite_key] = bib_entry
                        break
    
    return matches

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--paper', help='Process specific paper')
    parser.add_argument('--all', action='store_true', help='Process all papers')
    args = parser.parse_args()

    papers = []
    if args.paper:
        full = os.path.join(PAPERS_DIR, args.paper)
        if os.path.isdir(full):
            papers.append((args.paper, full))
    elif args.all:
        for item in sorted(os.listdir(PAPERS_DIR)):
            full = os.path.join(PAPERS_DIR, item)
            if os.path.isdir(full):
                tex_path = os.path.join(full, '01-manuscript', 'paper.tex')
                if os.path.exists(tex_path):
                    papers.append((item, full))
    else:
        # Default: only papers with 0% coverage
        for item in sorted(os.listdir(PAPERS_DIR)):
            full = os.path.join(PAPERS_DIR, item)
            if not os.path.isdir(full): continue
            tex_path = os.path.join(full, '01-manuscript', 'paper.tex')
            if not os.path.exists(tex_path): continue
            
            tex = open(tex_path).read()
            cites = set()
            for m in re.findall(r'\\cite[^{]*{([^}]+)}', tex):
                for k in m.split(','):
                    k = k.strip()
                    if k: cites.add(k)
            
            bib = open(os.path.join(full, '06-references', 'references.bib')).read()
            entries = set(re.findall(r'^@\w+\{([^,]+)', bib, re.MULTILINE))
            coverage = len(cites & entries) / len(cites) if cites else 0
            
            if coverage < 0.5:
                papers.append((item, full))

    print(f"Processing {len(papers)} papers")
    
    total_fixed = 0
    total_need_crossref = 0
    
    for name, full in papers:
        tex_path = os.path.join(full, '01-manuscript', 'paper.tex')
        tex = open(tex_path).read()
        
        cites = set()
        for m in re.findall(r'\\cite[^{]*{([^}]+)}', tex):
            for k in m.split(','):
                k = k.strip()
                if k:
                    cites.add(k)
        if not cites:
            continue
        
        title_m = re.search(r'\\title\{(.+?)\}', tex)
        title = title_m.group(1).strip() if title_m else None
        
        # Check for .bak
        bak_path = os.path.join(full, '06-references', 'references.bib.bak')
        if os.path.exists(bak_path):
            with open(bak_path) as f:
                bak_content = f.read()
            
            bak_entries = extract_real_bib_entries(bak_content)
            matches = match_keys(cites, bak_entries)
            
            if matches:
                target = os.path.join(full, '06-references', 'references.bib')
                os.makedirs(os.path.dirname(target), exist_ok=True)
                
                with open(target, 'w') as f:
                    f.write(f'% Consolidated references for {name}\n\n')
                    written = 0
                    for cite_key in sorted(cites):
                        if cite_key in matches:
                            f.write(f'{matches[cite_key]}\n\n')
                            written += 1
                    remaining = cites - set(matches.keys())
                    if remaining:
                        for k in sorted(remaining):
                            f.write(f'% MISSING: {k}\n')
                
                total_fixed += 1
                print(f"  {name}: restored {written}/{len(cites)} from .bak")
                continue
            else:
                print(f"  {name}: .bak found but no matching keys")
        else:
            print(f"  {name}: no .bak, needs Crossref")
            total_need_crossref += 1

    print(f"\nDone: restored={total_fixed}, need_crossref={total_need_crossref}")

if __name__ == '__main__':
    main()
