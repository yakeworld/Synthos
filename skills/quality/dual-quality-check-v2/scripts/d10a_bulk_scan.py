#!/usr/bin/env python3
"""
d10a_bulk_scan.py — Bulk D8/D10a scan for Synthos papers directory.
Handles thebibliography, bibtex, .bbl/.aux, \input{} subfiles, .tex double-extension traps.
Usage: python3 d10a_bulk_scan.py [--base /path/to/papers] [--verbose]
"""
import os, re, sys, json

BASE = os.environ.get('PAPERS_BASE',
    '/media/yakeworld/sda2/Synthos/outputs/papers')

SKIP_DIRS = {'_todo', '_docs', '_archive_scripts', 'lit-reviews', 'scf-paper',
             'gap-paper-35-neuromorphic-eye-tracking','individualized-bppv-simulation',
             'scc-pd-biomarker','pinn-operator-learning-generalization'}

SKIP_FILES = {
    'qc_v21_local_first.py', 'download_papers.py', 'download_papers2.py',
    'download_ref_pdfs.py', 'fetch_papers.py', 'fetch_papers2.py', 'pdf_collect.py',
    'batch_qc_rerun.py', 'batch-qc-state.json', 'batch-qc-phase2-state.json',
    'batch-qc-log.md', 'batch-qc-phase2-log.md', 'BATCH_LOG.md',
    'MERGE_LOG.md', 'QUEUE.md', 'PROGRESS_REPORT.md', 'README.md',
    'discovery-note.md', 'papers-to-notebooks.md', 'qc-evolution.json',
    'agent-tracker.json', 'agent-log.md', 'notebooklm-sources.template.json',
    'quality-summary-2026-05-25.md', 'references.bib', 'references_bib.md',
    'figure1-architecture.png', 'figure1-architecture.svg',
    'scf-paper.tex', 'scf-paper.aux', 'scf-paper.bbl', 'scf-paper.blg', 'scf-paper.log',
    'scf-paper.out', 'scf-paper.pdf', 'scf-paper.spl',
    'scf-paper.md', 'scf-paper-v2.md', 'scf-paper-v2-intermediate.md', 'scf-paper_latex.md',
}

def find_tex_files(paper_dir):
    dir_name = os.path.basename(paper_dir)
    candidates = []
    for root, dirs, files in os.walk(paper_dir):
        rel = os.path.relpath(root, paper_dir)
        if rel != '.':
            parts = rel.split(os.sep)
            if any(p in ('09-background', '_archive', 'archive', 'figures', 'sections',
                         '05-figures', '09-tail') for p in parts): continue
        for f in files:
            if not f.endswith('.tex'): continue
            fp = os.path.join(root, f)
            sz = os.path.getsize(fp)
            if sz < 2000 and (f.startswith('fig_') or f.startswith('Fig_')): continue
            candidates.append((fp, f, sz))
    if not candidates: return None
    priority = [dir_name + '.tex', 'article_improved.tex', 'v4-paper.tex',
                'paper.tex', 'main.tex', 'article.tex']
    for prio in priority:
        for fp, f, _ in candidates:
            if f == prio: return fp
    best, best_cites = None, -1
    for fp, f, _ in candidates:
        try:
            with open(fp, errors='ignore') as fh: tex = fh.read()
            lines = [l for l in tex.split('\n') if not l.strip().startswith('%')]
            active = '\n'.join(lines)
            cites = len(re.findall(r'\\cite[tp]?\s*\{([^}]+)\}', active))
            if cites > best_cites: best_cites, best = cites, fp
        except: continue
    return best if best else candidates[0][0]

def scan_paper(paper_dir):
    paper_name = os.path.basename(paper_dir)
    tex_path = find_tex_files(paper_dir)
    if not tex_path: return None
    try:
        with open(tex_path, errors='ignore') as f: tex = f.read()
    except: return None

    lines = tex.split('\n')
    active = '\n'.join([l for l in lines if not l.strip().startswith('%')])
    has_cite_cmd = bool(re.findall(r'\\cite[tp]?\s*\{', active))
    has_input = bool(re.findall(r'\\input\{', active))
    has_nocite = bool(re.findall(r'\\nocite\{\*\}', active))

    tex_dir = os.path.dirname(tex_path)
    if has_input:
        for m in re.finditer(r'\\input\{([^}]+)\}', active):
            rp = m.group(1)
            # Fix: handle \input{file.tex} (already has .tex)
            sp = os.path.join(tex_dir, rp if rp.endswith('.tex') else rp + '.tex')
            if not os.path.exists(sp):
                sp = os.path.join(tex_dir, os.path.basename(rp) + '.tex')
            if os.path.exists(sp):
                try:
                    with open(sp) as sf: sub = sf.read()
                    sub_l = [l for l in sub.split('\n') if not l.strip().startswith('%')]
                    active += '\n' + '\n'.join(sub_l)
                except: pass

    result = {'paper': paper_name, 'tex_file': os.path.relpath(tex_path, BASE),
              'has_cites': has_cite_cmd, 'has_input': has_input, 'has_nocite': has_nocite,
              'tex_lines': len(lines), 'd8': 0, 'd10a_pct': 0.0,
              'orphans': [], 'zombies': [], 'mode': 'unknown', 'pdf_count': 0, 'status': ''}

    # PDF count
    for pd in [os.path.join(paper_dir, '06-references', 'pdfs'), os.path.join(paper_dir, 'pdfs')]:
        if os.path.isdir(pd):
            real = 0
            for f in os.listdir(pd):
                if not f.endswith('.pdf'): continue
                with open(os.path.join(pd, f), 'rb') as fh:
                    if fh.read(5) == b'%PDF-': real += 1
            result['pdf_count'] = real
            break

    # Detect thebibliography FIRST (before aux-based paths)
    has_thebib = '\\begin{thebibliography}' in active
    has_bibtex_cmd = bool(re.findall(r'\\bibliography\{', active))

    bib_keys = set()
    cited = set()
    for m in re.finditer(r'\\cite[tp]?\s*\{([^}]+)\}', active):
        for k in m.group(1).split(','):
            k = k.strip()
            if k: cited.add(k)

    if has_thebib:
        result['mode'] = 'thebibliography'
        bib_keys = set(re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', active))
        # Also check companion .bib files with thebibliography
        for bf in _find_bib_files(paper_dir):
            try:
                with open(bf) as fh: content = fh.read()
                if '\\begin{thebibliography}' in content:
                    bf_keys = set(re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', content))
                    if len(bf_keys) > len(bib_keys): bib_keys = bf_keys
            except: pass
    elif has_bibtex_cmd:
        result['mode'] = 'bibtex'
        bib_keys = _collect_bib_keys(paper_dir, active)
    else:
        # Try .bbl/.aux fallback
        tex_bn = os.path.splitext(os.path.basename(tex_path))[0]
        bbl = None
        for loc in [os.path.join(tex_dir, tex_bn + '.bbl'),
                    os.path.join(paper_dir, tex_bn + '.bbl')]:
            if os.path.exists(loc): bbl = loc; break
        if bbl:
            with open(bbl) as fh: content = fh.read()
            bib_keys = set(re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', content))
            result['mode'] = 'bbl_only'
        else:
            result['mode'] = 'no_bib_mechanism'

    # Filter template placeholders
    TEMPLATE = {'label', 'lamport94', 'einstein', 'knuthwebsite', 'ferriss',
                'key1', 'key2', 'key3', 'dummy', 'sample'}
    bib_keys -= TEMPLATE
    cited -= TEMPLATE

    result['d8'] = len(bib_keys)
    if bib_keys:
        matched = len(cited & bib_keys)
        result['d10a_pct'] = round(matched / len(bib_keys) * 100, 1)
        result['orphans'] = sorted(cited - bib_keys)
        result['zombies'] = sorted(bib_keys - cited)

    # Status
    if not has_cite_cmd and has_input:
        result['status'] = 'SUBFILE'
    elif not has_cite_cmd and not has_input and result['tex_lines'] < 100 and result['d8'] == 0:
        result['status'] = 'SKELETON'
    elif result['orphans']:
        result['status'] = 'ORPHAN_P0'
    elif result['d10a_pct'] >= 100 and not result['zombies']:
        result['status'] = 'CLEAN'
    elif result['d10a_pct'] >= 100 and result['zombies']:
        result['status'] = 'ZOMBIE'
    elif result['d8'] < 30 and result['d10a_pct'] >= 100:
        result['status'] = 'D8_LOW'
    else:
        result['status'] = 'ISSUE'
    return result

def _find_bib_files(paper_dir):
    bfs = []
    for root, dirs, files in os.walk(paper_dir):
        parts = os.path.relpath(root, paper_dir).split(os.sep)
        if any(p in ('09-background', '_archive', 'archive', 'figures', '05-figures') for p in parts): continue
        for f in files:
            if f.endswith('.bib'): bfs.append(os.path.join(root, f))
    return bfs

def _collect_bib_keys(paper_dir, active_tex):
    all_keys = set()
    bib_cmd = re.search(r'\\bibliography\{([^}]+)\}', active_tex)
    if bib_cmd:
        for bn in [b.strip() for b in bib_cmd.group(1).split(',')]:
            if '<' in bn and '>' in bn: continue
            for root, dirs, files in os.walk(paper_dir):
                parts = os.path.relpath(root, paper_dir).split(os.sep)
                if any(p in ('09-background', '_archive', 'archive', 'figures') for p in parts): continue
                for f in files:
                    if f.endswith('.bib') and os.path.splitext(f)[0] == bn:
                        try:
                            with open(os.path.join(root, f)) as fh:
                                all_keys.update(set(re.findall(r'@\w+\{([^,]+),', fh.read())))
                        except: pass
    if not all_keys:
        for root, dirs, files in os.walk(paper_dir):
            parts = os.path.relpath(root, paper_dir).split(os.sep)
            if any(p in ('09-background', '_archive', 'archive', 'figures') for p in parts): continue
            for f in files:
                if f.endswith('.bib'):
                    try:
                        with open(os.path.join(root, f)) as fh:
                            all_keys.update(set(re.findall(r'@\w+\{([^,]+),', fh.read())))
                    except: pass
    return all_keys

def main():
    papers = sorted(os.listdir(BASE))
    results = []
    for p in papers:
        pdir = os.path.join(BASE, p)
        if not os.path.isdir(pdir) or p in SKIP_DIRS: continue
        r = scan_paper(pdir)
        if r: results.append(r)
    
    clean = [r for r in results if r['status'] == 'CLEAN']
    orphans = [r for r in results if r['status'] == 'ORPHAN_P0']
    zombies = [r for r in results if r['status'] == 'ZOMBIE']
    
    print(f"D8/D10a Scan Report — {len(results)} papers")
    print(f"  CLEAN: {len(clean)} | P0: {len(orphans)} | ZOMBIE: {len(zombies)}")
    
    if orphans:
        print("\n🔴 P0 ORPHANS:")
        for r in orphans:
            print(f"  {r['paper']}: {len(r['orphans'])} orphans: {r['orphans'][:10]}")
    
    sys.exit(1 if orphans else 0)

if __name__ == '__main__':
    main()
