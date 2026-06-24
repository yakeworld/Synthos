#!/usr/bin/env python3
"""
Targeted D10a scan for a single paper directory or article_todo workspace.
Handles ALL citation command variants: \cite{}, \citep{}, \citet{}.
Also handles comma-separated multi-cites like \citep{key1,key2}.

Usage:
  python3 d10a-targeted-scan.py /path/to/paper.tex
  python3 d10a-targeted-scan.py --dir ~/桌面/article_todo/

Unlike d10a-batch-scan.py, this script:
  - Matches natbib \citep{} and \citet{} (NOT just \cite{})
  - Works on article_todo workspace (not just main pipeline)
  - Excludes LaTeX comment lines (starting with %)
  - Reports orphans, zombies, and D10a percentage
  - Handles both .bbl and inline thebibliography

Created: RP-6 (2026-06-24) — natbib blind spot discovered when
 3d-eyeball-iris-segmentation reported D10a=0% by batch scan
 but actual D10a=100% (28/28 \citep keys matched 28/28 .bbl bibitems).
"""

import re
import os
import sys
import glob


def extract_cites(tex_content: str) -> set:
    """Extract all citation keys from tex, excluding comment lines."""
    keys = set()
    for line in tex_content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('%'):
            continue
        # Match \cite{...}, \citep{...}, \citet{...}
        for m in re.finditer(r'\\(?:cite|citep|citet)\{([^}]+)\}', stripped):
            for k in m.group(1).split(','):
                keys.add(k.strip())
    return keys


def extract_bibitems(bbl_content: str) -> set:
    """Extract bibitem keys from .bbl or inline thebibliography."""
    return set(re.findall(r'\\bibitem\{([^}]+)\}', bbl_content))


def scan_paper(tex_path: str) -> dict:
    """Scan a single paper for D10a metrics."""
    paper_dir = os.path.dirname(tex_path)
    paper_name = os.path.splitext(os.path.basename(tex_path))[0]

    with open(tex_path) as f:
        tex = f.read()

    # Find .bbl — prefer matching basename, then any .bbl
    bbl_path = os.path.join(paper_dir, paper_name + '.bbl')
    if not os.path.exists(bbl_path):
        bbl_files = glob.glob(os.path.join(paper_dir, '*.bbl'))
        if bbl_files:
            bbl_path = bbl_files[0]

    bbl_content = ''
    bbl_source = 'none'
    if os.path.exists(bbl_path):
        with open(bbl_path) as f:
            bbl_content = f.read()
        bbl_source = os.path.basename(bbl_path)

    # Also check inline thebibliography in tex
    tex_bibitems = extract_bibitems(tex)
    bbl_bibitems = extract_bibitems(bbl_content)

    # Use bbl bibitems if available, else tex inline
    bibitem_keys = bbl_bibitems if bbl_bibitems else tex_bibitems
    source_type = 'bbl' if bbl_bibitems else ('inline' if tex_bibitems else 'none')

    cite_keys = extract_cites(tex)

    orphans = sorted(cite_keys - bibitem_keys)
    zombies = sorted(bibitem_keys - cite_keys)

    if cite_keys:
        d10a = len(cite_keys & bibitem_keys) / len(cite_keys) * 100
    else:
        d10a = 100.0  # No cites = no orphans

    return {
        'tex_path': tex_path,
        'bbl_path': bbl_path if bbl_source != 'none' else None,
        'source_type': source_type,
        'cite_count': len(cite_keys),
        'bibitem_count': len(bibitem_keys),
        'common': len(cite_keys & bibitem_keys),
        'd10a': d10a,
        'orphans': orphans,
        'zombies': zombies,
    }


def scan_directory(base_dir: str, threshold: float = 95.0) -> list:
    """Scan all papers in a directory tree."""
    results = []
    for tex_path in glob.glob(os.path.join(base_dir, '**/*.tex'), recursive=True):
        basename = os.path.basename(tex_path)
        # Skip template files
        if basename in ('cover_letter.tex', 'elsarticle-template-num.tex',
                         'Sage_LaTeX_Guidelines.tex'):
            continue
        # Skip files without \begin{document} (templates, fragments)
        with open(tex_path) as f:
            head = f.read(2000)
        if '\\begin{document}' not in head:
            continue
        result = scan_paper(tex_path)
        results.append(result)

    # Deduplicate: prefer the tex with most cites per paper directory
    by_dir = {}
    for r in results:
        d = os.path.dirname(r['tex_path'])
        if d not in by_dir or r['cite_count'] > by_dir[d]['cite_count']:
            by_dir[d] = r

    return sorted(by_dir.values(), key=lambda r: r['d10a'])


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Targeted D10a scan handling natbib variants')
    parser.add_argument('path', nargs='?', help='Path to .tex file or directory')
    parser.add_argument('--dir', action='store_true', help='Treat path as directory')
    parser.add_argument('--threshold', type=float, default=95.0,
                        help='D10a threshold for flagging (default: 95.0)')
    args = parser.parse_args()

    if not args.path:
        parser.print_help()
        return

    if args.dir or os.path.isdir(args.path):
        results = scan_directory(args.path)
        below = [r for r in results if r['d10a'] < args.threshold]
        print(f"Scanned {len(results)} papers in {args.path}")
        print(f"Below {args.threshold}%: {len(below)}")
        print()
        for r in below:
            rel = os.path.relpath(r['tex_path'], args.path)
            print(f"⚠️  {rel}: D10a={r['d10a']:.1f}% ({r['cite_count']}c/{r['bibitem_count']}b)")
            if r['orphans']:
                print(f"    Orphans({len(r['orphans'])}): {r['orphans'][:10]}")
            if r['zombies']:
                print(f"    Zombies({len(r['zombies'])}): {r['zombies'][:10]}")
            print()
        if not below:
            print("All papers at or above threshold ✅")
    else:
        result = scan_paper(args.path)
        print(f"Paper: {result['tex_path']}")
        print(f"BBL: {'✅ ' + result['bbl_path'] if result['bbl_path'] else '❌ none'}")
        print(f"Source: {result['source_type']}")
        print(f"Cites: {result['cite_count']}, Bibitems: {result['bibitem_count']}")
        print(f"Common: {result['common']}, D10a: {result['d10a']:.1f}%")
        if result['orphans']:
            print(f"Orphans({len(result['orphans'])}): {result['orphans']}")
        if result['zombies']:
            print(f"Zombies({len(result['zombies'])}): {result['zombies']}")


if __name__ == '__main__':
    main()
