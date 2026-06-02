#!/usr/bin/env python3
"""
Robust D10a/D8 scanner — avoids 3 known traps:
  1. Commented-out \begin{thebibliography} (read as active)
  2. \bibliography{} template placeholders like <your bibdatabase>
  3. .tex/.bib files in subdirectories (01-manuscript/, 06-references/)

Usage:
  python3 robust-d10a-scanner-2026-06-01.py /path/to/paper.tex [--verbose]

Tested 2026-06-01 across 48 papers in Synthos outputs/papers/.
"""

import re, os, sys

def check_paper(tex_path, verbose=False):
    if not os.path.exists(tex_path):
        return {'error': f'File not found: {tex_path}'}
    
    with open(tex_path, encoding='utf-8', errors='replace') as f:
        tex = f.read()
    
    # Split into lines, keep only non-comment lines
    lines = tex.split('\n')
    active_lines = [l for l in lines if not l.strip().startswith('%')]
    active = '\n'.join(active_lines)
    
    # Extract \cite{} keys (only from active lines)
    cites = set()
    for m in re.finditer(r'\\cite[tp]?\s*\{([^}]+)\}', active):
        for k in m.group(1).split(','):
            k = k.strip()
            if k: cites.add(k)
    
    # Detect mode: thebibliography vs bibtex (only in ACTIVE lines)
    has_thebib = r'\begin{thebibliography}' in active
    
    # Find \bibliography{} command (only active)
    bib_cmd = None
    for l in active_lines:
        if 'bibliography{' in l:
            bib_cmd = l.strip()
            break
    
    bib_keys = set()
    mode = 'unknown'
    
    if has_thebib:
        # Extract bibitem keys from active lines
        bib_keys = set(re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', active))
        mode = 'thebib'
        
    elif bib_cmd:
        mode = 'bibtex'
        tex_dir = os.path.dirname(os.path.abspath(tex_path))
        
        # Parse multiple bib files from \bibliography{file1,file2,...}
        bib_refs = re.findall(r'\\bibliography\{([^}]+)\}', active)
        for ref in bib_refs:
            for part in ref.split(','):
                part = part.strip()
                # Skip template placeholders like <your bibdatabase>
                if '<' in part or '>' in part or not part:
                    continue
                if verbose:
                    print(f'  Looking for bib file: {part}')
                
                # Try candidate paths
                candidates = [
                    os.path.join(tex_dir, part + '.bib'),
                    os.path.join(tex_dir, part),
                    os.path.join(tex_dir, '..', '06-references', 'references.bib'),
                    os.path.join(tex_dir, '..', '06-references', part + '.bib'),
                    os.path.join(tex_dir, '..', '..', '06-references', 'references.bib'),
                    os.path.join(tex_dir, '..', part + '.bib'),
                ]
                
                found = False
                for c in candidates:
                    c = os.path.normpath(c)
                    if os.path.exists(c):
                        try:
                            with open(c, encoding='utf-8', errors='replace') as fb:
                                content = fb.read()
                            kk = re.findall(r'@\w+\{([^,]+),', content)
                            bib_keys.update(kk)
                            if verbose:
                                print(f'  Found bib: {c} ({len(kk)} entries)')
                            found = True
                            break
                        except: pass
                
                # Try symlink resolution if direct path failed
                if not found:
                    for c in [os.path.join(tex_dir, part + '.bib'),
                              os.path.join(tex_dir, part)]:
                        c = os.path.normpath(c)
                        if os.path.islink(c):
                            target = os.readlink(c)
                            if not target.startswith('/'):
                                target = os.path.join(os.path.dirname(c), target)
                            if os.path.exists(target):
                                try:
                                    with open(target, encoding='utf-8', errors='replace') as fb:
                                        content = fb.read()
                                    kk = re.findall(r'@\w+\{([^,]+),', content)
                                    bib_keys.update(kk)
                                    if verbose:
                                        print(f'  Resolved symlink: {c} -> {target} ({len(kk)} entries)')
                                    found = True
                                    break
                                except: pass
    else:
        # No bibliography found at all
        mode = 'none'
    
    orphan = cites - bib_keys
    zombie = bib_keys - cites
    d8 = len(bib_keys)
    d10a_pct = len(cites & bib_keys) / len(bib_keys) * 100 if bib_keys else (100 if not cites else 0)
    d10a_ok = len(orphan) == 0
    
    result = {
        'mode': mode,
        'd8': d8,
        'd8_ok': d8 >= 30,
        'cites': len(cites),
        'bib_entries': len(bib_keys),
        'orphan': len(orphan),
        'zombie': len(zombie),
        'd10a_pct': d10a_pct,
        'd10a_ok': d10a_ok,
        'has_bib_cmd': bib_cmd is not None,
        'bib_cmd_text': bib_cmd,
        'orphan_list': sorted(orphan)[:15],
        'zombie_list': sorted(zombie)[:15],
    }
    return result


if __name__ == '__main__':
    verbose = '--verbose' in sys.argv
    papers = [a for a in sys.argv[1:] if not a.startswith('--')]
    
    if not papers:
        print('Usage: python3 robust-d10a-scanner-2026-06-01.py paper.tex [--verbose]')
        sys.exit(1)
    
    for p in papers:
        r = check_paper(p, verbose)
        if 'error' in r:
            print(f'{p}: ERROR: {r["error"]}')
            continue
        
        mode_s = r['mode']
        d8_v = r['d8']
        d8_ok_s = 'OK' if r['d8_ok'] else 'LOW'
        d10a_v = r['d10a_pct']
        if r['d10a_ok']:
            d10a_label = 'OK'
        else:
            d10a_label = str(r['orphan']) + ' orphans'
        zombie_v = r['zombie']
        name_s = os.path.basename(p)
        print(f'{name_s:40s} | mode={mode_s:6s} | D8={d8_v:3d} ({d8_ok_s}) | D10a={d10a_v:5.1f}% ({d10a_label}) | {zombie_v} zombies')
        if verbose and r['zombie_list']:
            zl = r['zombie_list']
            print(f'  Zombies: {", ".join(zl[:10])}')
