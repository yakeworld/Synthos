#!/usr/bin/env python3
"""
D10a batch scanner — verify citation-to-bibliography match rates for papers.

Handles both inline thebibliography and external .bib/.bbl workflows.
Correctly excludes LaTeX comments and template marker artifacts.

Usage:
    python3 d10a-batch-scan.py [--papers paper1 paper2 ...]
    python3 d10a-batch-scan.py --all          # scan all paper dirs
    python3 d10a-batch-scan.py --threshold 95 # only flag papers below 95%

Output: D10a percentage per paper + orphan/zombie detail when problems found.
"""

import re
import os
import sys
import json
import argparse
from pathlib import Path


def extract_cites(tex_content: str) -> set:
    """Extract unique citation keys from tex content, excluding comments."""
    cites = set()
    for line in tex_content.split('\n'):
        stripped = line.strip()
        # Skip LaTeX comments
        if stripped.startswith('%'):
            continue
        for m in re.finditer(r'\\cite\w*\{([^}]+)\}', line):
            for key in m.group(1).split(','):
                key = key.strip()
                # Skip template artifact markers
                if key and '<' not in key and '>' not in key:
                    cites.add(key)
    return cites


def extract_bibitems_from_bbl(bbl_content: str) -> set:
    """Extract bibitem keys from a .bbl file."""
    bibitems = set()
    for m in re.finditer(r'\\bibitem\{([^}]+)\}', bbl_content):
        bibitems.add(m.group(1).strip())
    return bibitems


def extract_bibitems_from_tex(tex_content: str) -> set:
    """Extract bibitem keys from inline thebibliography in tex."""
    bibitems = set()
    for m in re.finditer(r'\\bibitem\{([^}]+)\}', tex_content):
        bibitems.add(m.group(1).strip())
    return bibitems


def find_tex_file(paper_dir: str) -> str | None:
    """Find the main tex file in a paper directory."""
    candidates = ['paper.tex', '01-manuscript/paper.tex',
                  '00-manuscript/paper.tex', '09-manuscript/paper.tex']
    for cand in candidates:
        path = os.path.join(paper_dir, cand)
        if os.path.exists(path):
            return path
    # Fallback: find any .tex file
    for root, _, files in os.walk(paper_dir):
        for f in files:
            if f.endswith('.tex'):
                return os.path.join(root, f)
    return None


def find_bbl_file(paper_dir: str) -> str | None:
    """Find the .bbl file in a paper directory."""
    candidates = ['paper.bbl', '01-manuscript/paper.bbl',
                  '00-manuscript/paper.bbl', '09-manuscript/paper.bbl']
    for cand in candidates:
        path = os.path.join(paper_dir, cand)
        if os.path.exists(path):
            return path
    return None


def compute_d10a(paper_dir: str) -> dict:
    """Compute D10a metrics for a single paper directory."""
    tex_path = find_tex_file(paper_dir)
    if not tex_path:
        return {'error': 'no tex file found', 'd10a': None}

    with open(tex_path) as f:
        tex_content = f.read()

    cites = extract_cites(tex_content)
    cite_count = len(cites)

    # Try .bbl first (external bib workflow), fall back to inline thebibliography
    bbl_path = find_bbl_file(paper_dir)
    if bbl_path and os.path.exists(bbl_path):
        with open(bbl_path) as f:
            bbl_content = f.read()
        bibitems = extract_bibitems_from_bbl(bbl_content)
        bib_source = 'bbl'
    else:
        bibitems = extract_bibitems_from_tex(tex_content)
        bib_source = 'inline'

    bib_count = len(bibitems)

    if cite_count == 0:
        return {
            'd10a': 100.0 if bib_count == 0 else None,
            'cite_count': 0,
            'bib_count': bib_count,
            'matched': 0,
            'orphans': [],
            'zombies': sorted(bibitems),
            'bib_source': bib_source,
            'warning': 'zero citations' if bib_count > 0 else 'empty'
        }

    matched = cites.intersection(bibitems)
    orphans = sorted(cites - bibitems)
    zombies = sorted(bibitems - cites)

    return {
        'd10a': round(len(matched) / cite_count * 100, 1),
        'cite_count': cite_count,
        'bib_count': bib_count,
        'matched': len(matched),
        'orphans': orphans,
        'zombies': zombies,
        'bib_source': bib_source,
    }


def scan_papers(base_dir: str, paper_ids: list[str] | None = None,
                threshold: float = 95.0) -> list[dict]:
    """Scan papers and return results below threshold."""
    results = []

    if paper_ids:
        dirs = [os.path.join(base_dir, pid) for pid in paper_ids]
    else:
        dirs = [os.path.join(base_dir, d) for d in os.listdir(base_dir)
                if os.path.isdir(os.path.join(base_dir, d))
                and not d.startswith('_') and not d.startswith('.')]

    for paper_dir in dirs:
        if not os.path.isdir(paper_dir):
            continue

        paper_id = os.path.basename(paper_dir)
        result = compute_d10a(paper_dir)
        result['paper_id'] = paper_id

        if result.get('d10a') is not None and result['d10a'] < threshold:
            results.append(result)

    return results


def main():
    parser = argparse.ArgumentParser(
        description='D10a batch scanner for paper citation health')
    parser.add_argument('--papers', nargs='*',
                        help='Specific paper IDs to scan')
    parser.add_argument('--all', action='store_true',
                        help='Scan all paper directories')
    parser.add_argument('--threshold', type=float, default=95.0,
                        help='Only report papers below this D10a (default: 95)')
    parser.add_argument('--base-dir', default='.',
                        help='Base papers directory (default: .)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    args = parser.parse_args()

    paper_ids = args.papers if args.papers else None
    if not args.all and not paper_ids:
        parser.error('Must specify --all or --papers')

    results = scan_papers(args.base_dir, paper_ids, args.threshold)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print(f'All papers have D10a >= {args.threshold}%')
            return

        print(f'Papers with D10a < {args.threshold}%:')
        for r in results:
            pid = r['paper_id']
            d10a = r['d10a']
            o = len(r['orphans'])
            z = len(r['zombies'])
            src = r['bib_source']
            print(f'  {pid}: D10a={d10a}% ({r["cite_count"]}c/{r["bib_count"]}b, '
                  f'{o} orphans, {z} zombies, source={src})')
            if r['orphans']:
                print(f'    ORPHANS: {r["orphans"][:10]}')
            if r['zombies']:
                print(f'    ZOMBIES: {r["zombies"][:10]}')
            if 'warning' in r:
                print(f'    WARNING: {r["warning"]}')


if __name__ == '__main__':
    main()
