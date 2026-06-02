#!/usr/bin/env python3
"""
Bulk D8/D10a/D9 Scan — scan all papers in outputs/papers/ in one pass.

Usage:
    python3 scripts/bulk_d8_scan.py [--papers-dir /path/to/papers]

Features:
    - Priority file selection: prefers article_improved > v4-paper > paper > main > article > others
    - D10a computation: matches \cite keys from .tex against .bib and thebibliography entries
    - Detects orphan citations (cite key not in bib)
    - Detects zombie entries (bib key not cited)
    - Detects nocite{*} workarounds
    - Reports the "active" .tex file used per paper

Output: Tab-separated table showing D8, D10a, orphans, zombies, active tex per paper.
"""

import re, os, glob, sys, argparse, json


def find_best_tex_file(tex_files):
    """Pick the single best .tex file by priority.
    
    Priority (high to low):
        article_improved.tex > v4-paper.tex > paper.tex > main.tex > 
        article.tex > other.tex
    
    Returns the most-preferred file, or None if empty.
    """
    priority_order = [
        'article_improved.tex',
        'v4-paper.tex',
        'paper.tex',
        'main.tex',
        'article.tex',
    ]
    for pname in priority_order:
        for tf in tex_files:
            if tf.endswith(pname) and not '09-background' in tf and not '_todo' in tf:
                return tf
    # Fallback: return the largest non-draft .tex
    best = None
    best_size = 0
    for tf in tex_files:
        if '09-background' in tf or '_todo' in tf:
            continue
        try:
            sz = os.path.getsize(tf)
            if sz > best_size:
                best_size = sz
                best = tf
        except OSError:
            continue
    return best


def count_real_pdfs(pdf_dir):
    """Count PDFs verified by %PDF- header."""
    count = 0
    if not os.path.isdir(pdf_dir):
        return 0
    for f in os.listdir(pdf_dir):
        if not f.endswith('.pdf'):
            continue
        try:
            with open(os.path.join(pdf_dir, f), 'rb') as fh:
                if fh.read(5) == b'%PDF-':
                    count += 1
        except OSError:
            continue
    return count


def scan_paper(path, name):
    """Scan a single paper directory and return quality metrics."""
    entry = {
        'name': name,
        'd8': 0,
        'd8_pass': False,
        'd10a_pct': 0.0,
        'orphan_cites': [],
        'zombie_entries': [],
        'cite_count': 0,
        'bib_count': 0,
        'refs_count': 0,
        'has_nocite': False,
        'has_qc': False,
        'has_thebibliography': False,
        'active_tex': '',
    }

    # QC report
    entry['has_qc'] = (
        os.path.isfile(os.path.join(path, '07-quality', 'quality-report.md'))
        or os.path.isfile(os.path.join(path, 'quality-report.md'))
    )

    # Find tex and bib files
    tex_files = []
    bib_files = []
    for search_dir in [path,
                       os.path.join(path, '01-manuscript'),
                       os.path.join(path, '02-submission')]:
        if os.path.isdir(search_dir):
            tex_files.extend(glob.glob(os.path.join(search_dir, '*.tex')))

    for search_dir in [path,
                       os.path.join(path, '06-references')]:
        if os.path.isdir(search_dir):
            bib_files.extend(glob.glob(os.path.join(search_dir, '*.bib')))

    # Pick the active .tex
    main_tex = find_best_tex_file(tex_files)
    if not main_tex:
        return entry
    entry['active_tex'] = os.path.relpath(main_tex, path)

    # Extract cites from active tex
    try:
        with open(main_tex, errors='replace') as f:
            tex_content = f.read()
    except OSError:
        return entry

    # Exclude comment lines for cite extraction
    tex_lines = [l for l in tex_content.split('\n') if not l.strip().startswith('%')]
    active_tex_content = '\n'.join(tex_lines)

    cite_set = set()
    for m in re.finditer(r'\\cite[tp]?\s*\{([^}]+)\}', active_tex_content):
        for k in m.group(1).split(','):
            cite_set.add(k.strip())
    entry['cite_count'] = len(cite_set)

    # Check for nocite
    if re.search(r'\\nocite\{[^}]*\}', tex_content):
        entry['has_nocite'] = True

    # Bib extraction
    if bib_files:
        # Use the primary .bib (prefer references.bib)
        main_bib = None
        for bf in bib_files:
            if bf.endswith('references.bib') or bf.endswith('ref.bib'):
                main_bib = bf
                break
        if not main_bib:
            main_bib = bib_files[0]

        try:
            with open(main_bib) as f:
                bib_content = f.read()
        except OSError:
            return entry

        bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib_content))
        entry['bib_count'] = len(bib_keys)
        entry['d8'] = len(bib_keys)
        entry['d8_pass'] = entry['d8'] >= 30

        # D10a
        orphan = cite_set - bib_keys
        zombie = bib_keys - cite_set
        cited_clean = cite_set & bib_keys
        entry['d10a_pct'] = round(100.0 * len(cited_clean) / len(bib_keys), 1) if bib_keys else 0.0
        entry['orphan_cites'] = sorted(orphan)
        entry['zombie_entries'] = sorted(zombie)

    else:
        # Thebibliography mode
        bib_keys = set(re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', tex_content))
        entry['bib_count'] = len(bib_keys)
        entry['d8'] = len(bib_keys)
        entry['d8_pass'] = entry['d8'] >= 30
        entry['has_thebibliography'] = True

        orphan = cite_set - bib_keys
        zombie = bib_keys - cite_set
        entry['d10a_pct'] = round(100.0 * len(cite_set & bib_keys) / len(bib_keys), 1) if bib_keys else 0.0
        entry['orphan_cites'] = sorted(orphan)
        entry['zombie_entries'] = sorted(zombie)

    # D9 proxy: refs-md PDF count
    entry['refs_count'] = count_real_pdfs(os.path.join(path, 'refs-md'))

    return entry


def main():
    parser = argparse.ArgumentParser(description='Bulk D8/D10a/D9 scan across all papers')
    parser.add_argument('--papers-dir', default=None,
                        help='Path to outputs/papers/ directory')
    parser.add_argument('--json', action='store_true',
                        help='Output JSON instead of table')
    parser.add_argument('--sort-by', choices=['d8', 'name', 'd10a', 'cites'], default='d8',
                        help='Sort results (default: d8 ascending)')
    parser.add_argument('--flag-only', action='store_true',
                        help='Show only papers with issues (D8<30 or D10a<100)')
    args = parser.parse_args()

    # Auto-detect papers directory
    papers_dir = args.papers_dir
    if not papers_dir:
        for candidate in [
            '/media/yakeworld/sda2/Synthos/outputs/papers',
            os.path.expanduser('~/Synthos/outputs/papers'),
        ]:
            if os.path.isdir(candidate):
                papers_dir = candidate
                break

    if not papers_dir or not os.path.isdir(papers_dir):
        print(f"ERROR: Cannot find papers directory. Use --papers-dir", file=sys.stderr)
        sys.exit(1)

    # Scan all directories
    results = {}
    for d in sorted(os.listdir(papers_dir)):
        path = os.path.join(papers_dir, d)
        if not os.path.isdir(path) or d.startswith('_'):
            continue
        results[d] = scan_paper(path, d)

    if args.json:
        output = {}
        for name, e in results.items():
            output[name] = {
                'd8': e['d8'],
                'd8_pass': e['d8_pass'],
                'd10a': e['d10a_pct'],
                'cite_count': e['cite_count'],
                'bib_count': e['bib_count'],
                'orphans': len(e['orphan_cites']),
                'zombies': len(e['zombie_entries']),
                'has_nocite': e['has_nocite'],
                'has_qc': e['has_qc'],
                'refs_count': e['refs_count'],
                'active_tex': e['active_tex'],
            }
        print(json.dumps(output, indent=2))
        return

    # Print table
    sort_key = {
        'd8': lambda x: x[1]['d8'],
        'name': lambda x: x[0],
        'd10a': lambda x: x[1]['d10a_pct'],
        'cites': lambda x: x[1]['cite_count'],
    }[args.sort_by]
    sorted_results = sorted(results.items(), key=sort_key)

    header = f"{'Paper Name':50s} | {'D8':4s} | {'D10a':6s} | {'Orph':5s} | {'Zomb':5s} | {'QC':3s} | {'nocite':6s} | Active .tex"
    print(header)
    print("-" * len(header))

    issues = []
    for name, e in sorted_results:
        if args.flag_only and e['d8'] >= 30 and e['d10a_pct'] >= 100:
            continue

        d10a_str = f"{e['d10a_pct']:5.0f}%" if e['bib_count'] > 0 else "N/A"
        flag = ""
        if e['d10a_pct'] < 100 and e['bib_count'] > 0:
            flag = " ⚠️"
        elif e['d8'] < 30 and e['d8'] > 0:
            flag = " ⚠️"

        qc_str = "✅" if e['has_qc'] else "❌"
        print(f"{name:50s} | {e['d8']:4d} | {d10a_str:>6s}{flag} | {len(e['orphan_cites']):5d} | {len(e['zombie_entries']):5d} | {qc_str:3s} | {str(e['has_nocite']):6s} | {e['active_tex']}")

        if e['orphan_cites']:
            issues.append(f"  🟠 ORPHANS ({len(e['orphan_cites'])}): {name} — {', '.join(e['orphan_cites'][:5])}")
        if e['d10a_pct'] < 100 and e['bib_count'] > 0:
            issues.append(f"  ❌ D10a={e['d10a_pct']:.0f}% — {name} ({len(e['zombie_entries'])} zombies)")
        if e['has_nocite']:
            issues.append(f"  ❌ nocite workaround — {name}")
        if e['d8'] < 30 and e['d8'] > 0:
            issues.append(f"  ⚠️ D8={e['d8']} < 30 — {name}")
        if not e['has_qc'] and e['d8'] >= 30 and e['d10a_pct'] >= 100:
            issues.append(f"  ℹ️ QC missing — {name} (otherwise clean)")

    print(f"\n{'='*80}")
    print(f"Summary: {len(results)} papers scanned")
    print(f"  D8≥30:      {sum(1 for e in results.values() if e['d8_pass'])}/{sum(1 for e in results.values() if e['d8'] > 0)}")
    print(f"  D10a=100%:  {sum(1 for e in results.values() if e['d10a_pct'] >= 100)}/{sum(1 for e in results.values() if e['d8'] > 0)}")
    print(f"  D9(refs):   {sum(1 for e in results.values() if e['refs_count'] > 0)}/{len(results)}")
    print(f"  nocite:     {sum(1 for e in results.values() if e['has_nocite'])}")
    print(f"  QC reports: {sum(1 for e in results.values() if e['has_qc'])}/{len(results)}")

    if issues:
        print(f"\nIssues ({len(issues)}):")
        for issue in issues:
            print(issue)
    else:
        print(f"\nNo issues found.")


if __name__ == '__main__':
    main()
