#!/usr/bin/env python3
"""Batch D10a scan for thebibliography papers. Independent verification — does not trust state.json.

v3.18.8 — Fixed routing bug: thebibliography now takes priority over \bibliography{}.
          Added comment-line filtering (Trap #39). Fixed ~10 false positives.

Usage: python3 d10a-batch-scan.py [paper_id ...]
  No args: scan all thebibliography papers in papers/
  With args: scan only specified papers

Output: CSV of paper_id, bib_count, cite_count, zombie_count, orphan_count, D10a%, current_qs
"""

import json, re, os, sys

PAPERS_DIR = os.environ.get('PAPERS_DIR', '/media/yakeworld/sda2/Synthos/outputs/papers')

def load_queue(papers_dir):
    qpath = os.path.join(papers_dir, 'paper-queue.json')
    if os.path.exists(qpath):
        with open(qpath) as f:
            return json.load(f)
    return {'papers': []}

def scan_paper(paper_dir, paper_id):
    """Scan a single paper. Returns dict with D10a stats or None if not thebibliography."""
    tex_path = os.path.join(paper_dir, '01-manuscript/paper.tex')
    if not os.path.exists(tex_path):
        tex_path = os.path.join(paper_dir, 'paper.tex')
    if not os.path.exists(tex_path):
        return None

    with open(tex_path) as f:
        tex = f.read()

    # Detect mode: thebibliography vs BibTeX
    # CRITICAL: skip commented-out thebibliography (%% \begin{thebibliography})
    # PRIORITY: real thebibliography ALWAYS wins over \bibliography{} (Trap #38 fix v3.18.8)
    #   elsarticle templates often have BOTH: real thebibliography + %% \bibliography{references}
    #   The old routing (not has_real_thebib OR has_bibcmd → BibTeX) misrouted 
    #   thebibliography papers with template \bibliography{} to BibTeX mode,
    #   causing false zombie counts when .bib keys differed from bibitem keys.
    has_real_thebib = False
    for line in tex.split('\n'):
        stripped = line.strip()
        if stripped.startswith('%%') or stripped.startswith('%'):
            continue
        if '\\begin{thebibliography}' in stripped:
            has_real_thebib = True
            break

    has_bibcmd = False
    for line in tex.split('\n'):
        stripped = line.strip()
        if stripped.startswith('%%') or stripped.startswith('%'):
            continue
        if '\\bibliography{' in stripped:
            has_bibcmd = True
            break

    if has_real_thebib:
        # thebibliography mode — always use this if real thebibliography exists
        bib_keys = set(re.findall(r'\\bibitem\{([^}]+)\}', tex))
        mode = 'thebibliography'
        bib_source = 'inline'
    elif has_bibcmd:
        # BibTeX mode — check .bib file
        bib_keys = set()
        for root, dirs, files in os.walk(paper_dir):
            for f in files:
                if f.endswith('.bib'):
                    with open(os.path.join(root, f)) as fh:
                        bib = fh.read()
                    bib_keys |= set(re.findall(r'@\w+\{([^,]+),', bib))
            if bib_keys:
                break
        mode = 'BibTeX' if bib_keys else 'MISSING'
        bib_source = '.bib file' if bib_keys else 'none'
    else:
        bib_keys = set()
        mode = 'MISSING'
        bib_source = 'none'

    # Detect citation style (same as canonical P0 pre-check)
    if '\\citep{' in tex or '\\citet{' in tex:
        cp = r'\\(?:cite|citep|citet|citenp|citealp|citealt)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}'
    elif '\\cite{' in tex:
        cp = r'\\cite[tp]?\s*\{([^}]+)\}'
    else:
        cp = r'\\cite[tp]?\s*\{([^}]+)\}'

    # Extract cite keys — LINE-BY-LINE with comment filtering (Trap #39 fix v3.18.8)
    # Old global re.finditer(cp, tex) captured cites in LaTeX comments (e.g. 
    #   '% BPPV \cite{furman2019} ...' on line 1), inflating D10a.
    tex_cites = set()
    for line in tex.split('\n'):
        stripped = line.strip()
        if stripped.startswith('%'):
            continue
        for m in re.finditer(cp, line):
            for k in m.group(1).split(','):
                k = k.strip()
                if k and k not in ('<label>', 'lamport94'):
                    tex_cites.add(k)

    matched = tex_cites & bib_keys
    orphan = tex_cites - bib_keys
    zombie = bib_keys - tex_cites
    d10a = (len(matched) / max(len(bib_keys), 1) * 100) if bib_keys else 0.0

    return {
        'paper_id': paper_id,
        'mode': mode,
        'bib_source': bib_source,
        'bib_count': len(bib_keys),
        'cite_count': len(tex_cites),
        'matched': len(matched),
        'orphan_count': len(orphan),
        'zombie_count': len(zombie),
        'd10a': round(d10a, 1),
        'orphan_keys': sorted(orphan),
        'zombie_keys': sorted(zombie),
    }


def main():
    queue = load_queue(PAPERS_DIR)
    queue_map = {p['paper_id']: p for p in queue['papers']}

    targets = sys.argv[1:] if len(sys.argv) > 1 else None

    results = []
    for entry in os.listdir(PAPERS_DIR):
        if not os.path.isdir(os.path.join(PAPERS_DIR, entry)):
            continue
        if entry.startswith('_'):
            continue
        if targets and entry not in targets:
            continue

        result = scan_paper(os.path.join(PAPERS_DIR, entry), entry)
        if result is None:
            continue

        # Only report thebibliography papers with issues
        if result['mode'] == 'thebibliography' and (result['zombie_count'] > 0 or result['orphan_count'] > 0 or result['cite_count'] == 0):
            qp = queue_map.get(entry, {})
            result['queue_qs'] = qp.get('quality_score', '?')
            result['queue_gate'] = qp.get('gate_status', '?')
            results.append(result)

    # Sort by zombie count descending
    results.sort(key=lambda r: r['zombie_count'], reverse=True)

    print(f"{'paper_id':<55} {'bib':>4} {'cite':>5} {'zom':>4} {'orph':>4} {'D10a':>6} {'qs':>4} {'gate':>12}")
    print("-" * 100)
    for r in results:
        print(f"{r['paper_id']:<55} {r['bib_count']:>4} {r['cite_count']:>5} {r['zombie_count']:>4} {r['orphan_count']:>4} {r['d10a']:>5.0f}% {r.get('queue_qs','?'):>4} {r.get('queue_gate','?'):>12}")
        if r['zombie_keys']:
            print(f"  zombies: {r['zombie_keys'][:8]}")
        if r['orphan_keys']:
            print(f"  orphans: {r['orphan_keys'][:8]}")

    print(f"\nTotal thebibliography papers with issues: {len(results)}")

    # Stats
    zero_cite = [r for r in results if r['cite_count'] == 0 and r['bib_count'] > 0]
    if zero_cite:
        print(f"\nZero-citation papers ({len(zero_cite)}): {[r['paper_id'] for r in zero_cite]}")

if __name__ == '__main__':
    main()
