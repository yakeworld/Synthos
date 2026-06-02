#!/usr/bin/env python3
"""Check .tex citation keys against .bib entry keys. Reports mismatches."""

import re
import sys


def check_citations(tex_path: str, bib_path: str) -> bool:
    """Return True if all citations match, False if mismatches found."""
    with open(tex_path) as f:
        tex = f.read()
    with open(bib_path) as f:
        bib = f.read()

    tex_keys = set()
    for c in re.findall(r'\\cite\{([^}]+)\}', tex):
        for key in c.split(','):
            tex_keys.add(key.strip())

    bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib))

    missing = tex_keys - bib_keys
    extra = bib_keys - tex_keys

    print(f"TeX keys: {len(tex_keys)}, Bib keys: {len(bib_keys)}")

    if missing:
        print(f"\nKeys in .tex but NOT in .bib ({len(missing)}):")
        for k in sorted(missing):
            # Find fuzzy matches in bib
            # Strip common suffixes: OP, PA, FS, ID, etc.
            candidates = [b for b in bib_keys if b.lower().startswith(k.lower()[:6])]
            if candidates:
                print(f"  {k}  →  candidates: {candidates[:3]}")
            else:
                print(f"  {k}  →  NO candidates found")
        return False
    else:
        print("All citations matched!")
        return True


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: check_citations.py paper.tex reference.bib")
        sys.exit(1)
    ok = check_citations(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
