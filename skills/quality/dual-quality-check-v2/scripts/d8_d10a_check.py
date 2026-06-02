#!/usr/bin/env python3
"""
D8 + D10a quality check for a paper directory.
Usage: python3 scripts/d8_d10a_check.py <paper_dir>

Detects mode A (.bib file) or mode B (inline thebibliography) automatically.
Reports: D8 count, D10a coverage, zombie refs, orphan cites.
"""
import re
import sys
import os
import json

def find_main_tex(paper_dir):
    """Find the main .tex file using weighted heuristics.
    
    Priority (highest to lowest):
    1. filename matching dirname (e.g. paper-dir/paper-dir.tex)
    2. 'paper.tex' — most common canonical name
    3. filename containing dirname substring (e.g. paper-dir/paper-dir-v3.tex)
    4. Largest .tex file by size (heuristic: main file is longest)
    5. Any .tex file
    
    Among equal-priority candidates, prefer the one containing
    \\documentclass or \\begin{document}.
    """
    all_tex = [f for f in os.listdir(paper_dir) 
               if f.endswith('.tex') and os.path.isfile(os.path.join(paper_dir, f))]
    if not all_tex:
        return None
    
    dirname = os.path.basename(paper_dir)
    
    def score(f):
        s = 0
        # Exact dirname prefix = best match
        if f.startswith(dirname):
            s = 100
        # Canonical paper.tex
        elif f == 'paper.tex':
            s = 90
        # Contains dirname substring
        elif dirname in f:
            s = 50
        else:
            # Size-based heuristic
            s = 10
        
        # Bonus: check if it's a root document (has \\documentclass or \\begin{document})
        try:
            with open(os.path.join(paper_dir, f)) as fh:
                head = fh.read(2048)
                if '\\documentclass' in head or '\\begin{document}' in head:
                    s += 20
        except:
            pass
        
        # Bonus: larger files are more likely the main paper
        try:
            sz = os.path.getsize(os.path.join(paper_dir, f))
            s += min(sz // 10000, 10)  # +1 per 10KB, max +10
        except:
            pass
        
        return s
    
    scored = [(score(f), f) for f in all_tex]
    scored.sort(key=lambda x: -x[0])
    return scored[0][1]

def check_paper(paper_dir):
    # Find the main .tex file
    main_tex = find_main_tex(paper_dir)
    if not main_tex:
        print("ERROR: No .tex file found")
        return None
    
    tex_path = os.path.join(paper_dir, main_tex)
    with open(tex_path) as f:
        content = f.read()
    
    result = {'paper': os.path.basename(paper_dir), 'file': main_tex}
    
    # Detect mode: inline thebibliography?
    has_inline = '\\begin{thebibliography}' in content
    
    if has_inline:
        # Mode B: inline thebibliography
        bibitems = set(re.findall(r'\\bibitem\{([^}]+)\}', content))
        result['mode'] = 'B (inline thebibliography)'
    else:
        # Mode A: .bib file
        bib_path = os.path.join(paper_dir, 'references.bib')
        if os.path.exists(bib_path):
            with open(bib_path) as f:
                bib_content = f.read()
            bibitems = set(re.findall(r'@\w+\{([^,\s]+)', bib_content))
            result['mode'] = 'A (.bib file)'
        else:
            bibitems = set()
            result['mode'] = 'A (no .bib file found)'
    
    # Extract all cited keys
    tex_cites = set()
    for m in re.finditer(r'\\cite[pt]?\{([^}]+)\}', content):
        for k in m.group(1).split(','):
            tex_cites.add(k.strip())
    
    result['d8'] = len(bibitems)
    result['cited_count'] = len(tex_cites & bibitems)
    result['d10a_coverage'] = round(len(tex_cites & bibitems) / len(bibitems) * 100, 1) if bibitems else 0
    result['zombie_refs'] = sorted(bibitems - tex_cites)
    result['orphan_cites'] = sorted(tex_cites - bibitems)
    result['d8_pass'] = result['d8'] >= 30
    result['d10a_pass'] = result['d10a_coverage'] >= 80.0 and not result['orphan_cites']
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/d8_d10a_check.py <paper_dir>")
        sys.exit(1)
    
    paper_dir = sys.argv[1]
    if not os.path.isdir(paper_dir):
        print(f"ERROR: {paper_dir} is not a directory")
        sys.exit(1)
    
    result = check_paper(paper_dir)
    if not result:
        sys.exit(1)
    
    # Print summary
    print(f"Paper: {result['paper']}")
    print(f"TeX file: {result['file']}")
    print(f"Mode: {result['mode']}")
    print(f"D8: {result['d8']} refs  {'✅ PASS' if result['d8_pass'] else '❌ FAIL (<30)'}")
    print(f"D10a: {result['d10a_coverage']}% coverage  {'✅ PASS' if result['d10a_pass'] else '❌ FAIL (<80% or orphans)'}")
    print(f"Cited: {result['cited_count']}/{result['d8']}")
    
    if result['zombie_refs']:
        print(f"\n⚠ Zombie refs ({len(result['zombie_refs'])}):")
        for z in result['zombie_refs']:
            print(f"  • {z}")
    
    if result['orphan_cites']:
        print(f"\n⚠ Orphan cites ({len(result['orphan_cites'])}):")
        for o in result['orphan_cites']:
            print(f"  • {o}")
    
    # JSON output for script consumption
    print(f"\n---JSON---")
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
