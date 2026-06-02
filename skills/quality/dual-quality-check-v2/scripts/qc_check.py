#!/usr/bin/env python3
"""D8 + D10a quality check: Runs on either mode A (.bib) or mode B (inline thebibliography).

Usage:
    python3 qc_check.py <paper_dir>
    python3 qc_check.py <paper_dir>/paper.tex

Outputs: D8 count, D10a coverage %, any orphans/zombies.
"""

import re
import sys
import os
from pathlib import Path


def extract_cite_keys(tex_content: str) -> set:
    """Extract all keys from \\cite{...}, \\citep{...}, \\citet{...} commands."""
    keys = set()
    for m in re.finditer(r'\\cite[pt]?\{([^}]+)\}', tex_content):
        for k in m.group(1).split(','):
            keys.add(k.strip())
    return keys


def mode_b_inline(tex_content: str, tex_path: Path):
    """D8/D10a using inline \\bibitem entries (no .bib file)."""
    bibitem_keys = set(re.findall(r'\\bibitem\{(\w+)\}', tex_content))
    tex_cites = extract_cite_keys(tex_content)

    orphan_cites = tex_cites - bibitem_keys
    uncited = bibitem_keys - tex_cites
    total = len(bibitem_keys)
    covered = len(bibitem_keys & tex_cites)
    coverage = covered / total * 100 if total > 0 else 0

    print(f"Mode B: inline thebibliography")
    print(f"  D8: {total} bibitem entries -> {'PASS' if total >= 30 else 'FAIL (' + str(total) + '/30)'}")
    print(f"  D10a: {covered}/{total} = {coverage:.1f}% -> {'PASS' if coverage >= 80 else 'FAIL'}")
    if orphan_cites:
        print(f"  ⚠  ORPHAN CITES ({len(orphan_cites)}): {sorted(orphan_cites)}")
    if uncited:
        print(f"  ZOMBIE BIBITEMS ({len(uncited)}): {sorted(uncited)}")
    return total, coverage


def mode_a_bibtex(tex_content: str, bib_content: str):
    """D8/D10a using .bib file."""
    bib_keys = set()
    for m in re.finditer(r'@(\w+)\{(\w+)', bib_content):
        if m.group(1) != 'Comment' and not m.group(2).startswith('jabref') and not m.group(2).startswith('database'):
            bib_keys.add(m.group(2))

    tex_cites = extract_cite_keys(tex_content)
    uncited = bib_keys - tex_cites
    total = len(bib_keys)
    covered = len(tex_cites & bib_keys)
    coverage = covered / total * 100 if total > 0 else 0

    print(f"Mode A: .bib file")
    print(f"  D8: {total} bib entries -> {'PASS' if total >= 30 else 'FAIL (' + str(total) + '/30)'}")
    print(f"  D10a: {covered}/{total} = {coverage:.1f}% -> {'PASS' if coverage >= 80 else 'FAIL'}")
    if uncited:
        print(f"  ZOMBIE ({len(uncited)}): {sorted(uncited)}")
    return total, coverage


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 qc_check.py <paper_dir_or_tex>")
        sys.exit(1)

    target = Path(sys.argv[1])
    if target.is_file() and target.suffix == '.tex':
        tex_path = target
        paper_dir = target.parent
    elif target.is_dir():
        tex_candidates = list(target.glob('paper.tex')) + list(target.glob('*.tex'))
        if not tex_candidates:
            print(f"No .tex file found in {target}")
            sys.exit(1)
        tex_path = tex_candidates[0]
        paper_dir = target
    else:
        print(f"Invalid target: {target}")
        sys.exit(1)

    with open(tex_path) as f:
        tex_content = f.read()

    # Auto-detect mode
    if '\\begin{thebibliography}' in tex_content:
        mode_b_inline(tex_content, tex_path)
    else:
        bib_paths = list(paper_dir.glob('**/ref.bib')) + list(paper_dir.glob('**/*.bib'))
        if not bib_paths:
            print("No .bib file found. Trying inline mode...")
            if re.search(r'\\bibitem\{', tex_content):
                mode_b_inline(tex_content, tex_path)
            else:
                print("No bibliography found at all. Check the paper structure.")
                sys.exit(1)
        else:
            with open(bib_paths[0]) as f:
                bib_content = f.read()
            mode_a_bibtex(tex_content, bib_content)


if __name__ == '__main__':
    main()
