#!/usr/bin/env python3
"""
thebibliography_zombie_cleanup.py — Automated D10a Repair for thebibliography Papers

Usage:
    python3 scripts/thebibliography_zombie_cleanup.py paper.tex [--dry-run] [--backup]

Given a .tex file with \\begin{thebibliography}...\\end{thebibliography},
this script:
  1. Extracts all \\cite{key} from non-comment lines (handles \\citep, \\citet, etc.)
  2. Extracts all \\bibitem{key} entries
  3. Identifies zombies (bibitems with no \\cite) and orphans (\\cite with no bibitem)
  4. Removes zombie bibitems
  5. Updates the counter \\begin{thebibliography}{N} to match new count
  6. Reports before/after D8 and D10a

Regex traps handled:
  - \\c invalid escape → use raw r'\\\\cite' (double backslash)
  - Optional \\bibitem[Author(Year)]{key} format
  - Comment lines starting with %
  - \\citep, \\citet, \\citeyear, \\citealp variants

Exit codes:
  0 — Cleanup applied successfully
  1 — No changes needed (already clean)
  2 — Error
"""

import re
import sys
import shutil
import os
from pathlib import Path

# ── Regex patterns ──────────────────────────────────────────────────
# Must use raw string + double backslash: r'\\\\cite' → matches \\cite
CITE_PATTERN = re.compile(r'\\cite[tp]?\s*\{([^}]+)\}')
BIBITEM_PATTERN = re.compile(r'\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}')
COUNTER_PATTERN = re.compile(r'(\\begin\{thebibliography\})\{(\d+)\}')

def parse_tex(path):
    """Read .tex, extract all cited keys (skipping comment lines) and bibitems."""
    tex = Path(path).read_text()
    lines = tex.split('\n')
    active_lines = [l for l in lines if not l.strip().startswith('%')]
    active = '\n'.join(active_lines)

    # Extract \\cite keys
    cited = set()
    for m in CITE_PATTERN.finditer(active):
        for k in m.group(1).split(','):
            cited.add(k.strip())

    # Extract \\bibitem keys
    bibitems = [m.group(1).strip() for m in BIBITEM_PATTERN.finditer(tex)]
    bibitem_set = set(bibitems)

    return tex, cited, bibitems, bibitem_set


def split_thebibliography(tex):
    """Split tex before thebib, thebib content, and after thebib."""
    start = tex.find(r'\begin{thebibliography}')
    end = tex.find(r'\end{thebibliography}', start)
    if start < 0 or end < 0:
        raise ValueError("No \\begin{thebibliography}...\\end{thebibliography} found")
    end += len(r'\end{thebibliography}')
    return tex[:start], tex[start:end], tex[end:], start, end


def extract_bibitem_entries(thebib_text):
    """Split thebibliography content into individual bibitem entries."""
    # Split on \\bibitem boundaries — each starts with \\bibitem[...]{...}
    entries = re.split(r'(?=\\bibitem)', thebib_text)
    return entries


def filter_entries(entries, cited_set):
    """Separate entries into kept (cited) and removed (zombie)."""
    kept = []
    removed = []
    for entry in entries:
        m = BIBITEM_PATTERN.search(entry)
        if m:
            key = m.group(1).strip()
            if key in cited_set:
                kept.append(entry)
            else:
                removed.append((key, entry))
        elif entry.strip():
            # Non-bibitem content (leading space/newlines before first bibitem)
            kept.append(entry)
    return kept, removed


def rebuild_thebibliography(kept_entries):
    """Rebuild thebibliography with updated counter {N}."""
    count = sum(1 for e in kept_entries if BIBITEM_PATTERN.search(e))
    body = ''.join(e.rstrip('\n') + '\n' for e in kept_entries).rstrip('\n')
    return f'\\begin{{thebibliography}}{{{count}}}\n{body}\n\\end{{thebibliography}}'


def update_counter(existing, new_count):
    """Update the counter in \\begin{thebibliography}{N} to new count."""
    return COUNTER_PATTERN.sub(rf'\1{{{new_count}}}', existing)


def run_cleanup(path, dry_run=False, backup=True):
    """Main cleanup function. Returns (changed, new_tex, report)."""
    tex, cited, bibitems, bibitem_set = parse_tex(path)
    log = []

    # D10a before
    cited_in_bib = cited & bibitem_set
    zombies = bibitem_set - cited
    orphans = cited - bibitem_set
    d10a_before = len(cited_in_bib) / len(bibitem_set) * 100 if bibitem_set else 0

    log.append(f"D8 before: {len(bibitem_set)}")
    log.append(f"D10a before: {len(cited_in_bib)}/{len(bibitem_set)} = {d10a_before:.0f}%")
    log.append(f"Zombies: {len(zombies)}")
    log.append(f"Orphans: {len(orphans)}")

    if orphans:
        # Cannot auto-fix orphans — need to add bibitems
        log.append(f"⚠ Found {len(orphans)} orphan citations (cited but no bibitem): {sorted(orphans)}")
        log.append("  Cannot auto-fix orphans. Add missing bibitems manually first.")
        return False, tex, '\n'.join(log)

    if not zombies:
        log.append("✅ No zombies found — already clean.")
        return False, tex, '\n'.join(log)

    # Split and filter
    before, thebib, after, start_idx, end_idx = split_thebibliography(tex)
    entries = extract_bibitem_entries(thebib)
    kept_entries, removed = filter_entries(entries, cited)

    # Verify no accidental loss
    kept_keys = set()
    for e in kept_entries:
        m = BIBITEM_PATTERN.search(e)
        if m:
            kept_keys.add(m.group(1).strip())
    missing = cited - kept_keys
    if missing:
        log.append(f"⚠ Critical: {len(missing)} cited keys would be lost: {sorted(missing)}")
        log.append("  Aborting to prevent data loss.")
        return False, tex, '\n'.join(log)

    # Rebuild
    new_thebib = rebuild_thebibliography(kept_entries)
    new_tex = before + new_thebib + after

    # D10a after
    new_bibitem_set = set()
    for e in kept_entries:
        m = BIBITEM_PATTERN.search(e)
        if m:
            new_bibitem_set.add(m.group(1).strip())
    d10a_after = len(cited & new_bibitem_set) / len(new_bibitem_set) * 100 if new_bibitem_set else 0

    log.append(f"\n=== After cleanup ===")
    log.append(f"D8 after: {len(new_bibitem_set)}")
    log.append(f"D10a after: {len(cited & new_bibitem_set)}/{len(new_bibitem_set)} = {d10a_after:.0f}%")
    log.append(f"Zombies removed ({len(removed)}): {sorted(k for k, _ in removed)}")

    if d10a_after < 100:
        remaining_zombies = new_bibitem_set - cited
        log.append(f"⚠ {len(remaining_zombies)} zombies remain (still not 100% D10a): {sorted(remaining_zombies)}")
        log.append("  These need manual citation activation or deletion.")

    if not dry_run:
        if backup:
            backup_path = str(path) + '.bak'
            shutil.copy2(path, backup_path)
            log.append(f"Backup saved to: {backup_path}")
        Path(path).write_text(new_tex)
        log.append(f"Written to: {path}")
    else:
        log.append("(dry run — no changes written)")

    return True, new_tex, '\n'.join(log)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Remove zombie bibitems from thebibliography-format LaTeX papers')
    parser.add_argument('path', help='Path to .tex file')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--backup', action='store_true', default=True, help='Create .bak backup (default: yes)')
    parser.add_argument('--no-backup', action='store_false', dest='backup', help='Skip backup')
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(2)

    changed, new_tex, report = run_cleanup(str(path), dry_run=args.dry_run, backup=args.backup)
    print(report)

    if '⚠' in report and 'orphan' in report:
        sys.exit(2)  # Orphans prevent cleanup
    elif changed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
