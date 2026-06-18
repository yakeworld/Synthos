#!/usr/bin/env python3
"""D8/D10a scan: cross-file citation matching between .tex \cite{} and .bib entries.

Usage: python3 d8-d10a-scan.py <paper-root-directory>

Scans all paper directories under <paper-root>, producing a markdown report
with D8 (bib count), D10a (match %), orphans, zombies, and .bbl status.
"""

import os
import re
import sys

NON_PAPER_DIRS = {'_docs', '_todo', 'lit-reviews'}


def extract_cite_keys(tex_path):
    """Extract all \cite{} keys from a LaTeX file."""
    with open(tex_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    patterns = [
        r'\\cite(?:p|t|author|year|yearpar|inline)?\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}',
        r'\\fullcite\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}',
        r'\\nocite\s*\{([^}]+)\}',
    ]
    keys = set()
    for pat in patterns:
        for m in re.finditer(pat, content):
            for k in m.group(1).split(','):
                k = k.strip()
                if k:
                    keys.add(k)
    return keys


def extract_bib_keys(bib_path):
    """Extract BibTeX entry keys from a .bib file."""
    with open(bib_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    keys = set()
    for m in re.finditer(r'@(?:[a-zA-Z]+)\{([^,}]+),', content):
        k = m.group(1).strip()
        # Skip @Comment, jabref-meta, and similar non-entry comments
        if k and not k.startswith('%') and not k.startswith('@'):
            keys.add(k)
    return keys


def find_bib_file(paper_dir):
    """Find the primary .bib file with priority: 06-references > root > anywhere."""
    bib_path = os.path.join(paper_dir, '06-references', 'references.bib')
    if os.path.isfile(bib_path):
        return bib_path
    fallback = os.path.join(paper_dir, 'references.bib')
    if os.path.isfile(fallback):
        return fallback
    # Last resort: search all subdirectories
    for dirpath, _, filenames in os.walk(paper_dir):
        for f in filenames:
            if f.endswith('.bib'):
                return os.path.join(dirpath, f)
    return None


def find_tex_with_cites(paper_dir):
    """Find the primary .tex file with \\cite{} patterns.

    Priority: 01-manuscript/paper.tex > any paper.tex > any .tex with cites.
    """
    preferred = os.path.join(paper_dir, '01-manuscript', 'paper.tex')
    if os.path.isfile(preferred):
        keys = extract_cite_keys(preferred)
        if keys:
            return preferred, keys

    # Fall back: find any .tex with cites
    results = []
    for dirpath, _, filenames in os.walk(paper_dir):
        for f in filenames:
            if f.endswith('.tex'):
                full = os.path.join(dirpath, f)
                keys = extract_cite_keys(full)
                if keys:
                    results.append((full, keys))

    if not results:
        return None, None

    # Prefer paper.tex, then the one with most cite keys
    results.sort(key=lambda x: (0 if os.path.basename(x[0]).endswith('paper.tex') else 1, -len(x[1])))
    return results[0]


def check_bbl(paper_dir):
    """Check if a compiled .bbl artifact exists anywhere in the paper tree."""
    for dirpath, _, filenames in os.walk(paper_dir):
        for f in filenames:
            if f.endswith('.bbl'):
                return True
    return False


def scan_paper(name, paper_dir):
    """Scan a single paper directory and return metrics dict."""
    tex_path, cite_keys = find_tex_with_cites(paper_dir)
    if not tex_path or not cite_keys:
        return None

    bib_path = find_bib_file(paper_dir)
    if not bib_path:
        bib_keys = set()
    else:
        bib_keys = extract_bib_keys(bib_path)

    d8 = len(bib_keys)
    orphans = sorted(cite_keys - bib_keys)
    zombies = sorted(bib_keys - cite_keys)

    if cite_keys:
        matched = len(cite_keys & bib_keys)
        d10a_pct = round(100.0 * matched / len(cite_keys), 1)
    else:
        d10a_pct = 100.0

    return {
        'name': name,
        'tex': os.path.relpath(tex_path, paper_dir),
        'd8': d8,
        'd10a': d10a_pct,
        'orphans': orphans,
        'zombies': zombies,
        'bbl': check_bbl(paper_dir),
        'total_cites': len(cite_keys),
        'total_bib': len(bib_keys),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 d8-d10a-scan.py <paper-root-directory>")
        sys.exit(1)

    papers_dir = sys.argv[1]
    if not os.path.isdir(papers_dir):
        print(f"Error: {papers_dir} is not a directory")
        sys.exit(1)

    results = []
    for name in sorted(os.listdir(papers_dir)):
        paper_dir = os.path.join(papers_dir, name)
        if not os.path.isdir(paper_dir) or name in NON_PAPER_DIRS:
            continue
        r = scan_paper(name, paper_dir)
        if r:
            results.append(r)

    # Print report
    print("=" * 70)
    print("📊 D8/D10a Cross-Reference Scan Report")
    print("=" * 70)
    print()

    header = f"{'Paper':<42} {'D8':>4} {'D10a':>6} {'Orphans':>7} {'Zombies':>7} {'BBL':>5}"
    print(header)
    print("-" * len(header))

    problem_papers = []
    healthy = 0

    for r in results:
        d10a_str = f"{r['d10a']}%"
        bbl_str = "✅" if r['bbl'] else "❌"
        orph_count = len(r['orphans'])
        zm_count = len(r['zombies'])
        is_problem = r['d10a'] < 100.0 or r['d8'] < 30

        nd = r['name'][:39] + "..." if len(r['name']) > 42 else r['name']
        print(f"{nd:<42} {r['d8']:>4} {d10a_str:>6} {orph_count:>7} {zm_count:>7} {bbl_str:>5}")

        if is_problem:
            problem_papers.append(r)
        else:
            healthy += 1

    total = len(results)
    print()
    print("=" * 70)

    if problem_papers:
        print(f"🔴 Problem papers ({len(problem_papers)}):")
        print()
        for r in problem_papers:
            issues = []
            # Classify severity
            if r['d8'] == 0:
                issues.append(f"D8=0 (no bib)")
            elif r['d10a'] < 100.0:
                issues.append(f"D10a={r['d10a']}%")
            if r['orphans']:
                issues.append(f"orphans: {', '.join(r['orphans'][:5])}")
                if len(r['orphans']) > 5:
                    issues.append(f"... +{len(r['orphans'])-5} more")
            if r['zombies']:
                issues.append(f"zombies: {', '.join(r['zombies'][:5])}")
                if len(r['zombies']) > 5:
                    issues.append(f"... +{len(r['zombies'])-5} more")
            if r['d8'] < 30 and r['d8'] > 0:
                issues.append(f"D8={r['d8']} (<30)")
            if not r['bbl']:
                issues.append("no .bbl")

            detail = "; ".join(issues)
            print(f"  - {r['name']}: {detail}")

    print()
    print(f"📋 Total: {total}, Healthy: {healthy}, Problems: {len(problem_papers)}")
    print("=" * 70)


if __name__ == '__main__':
    main()
