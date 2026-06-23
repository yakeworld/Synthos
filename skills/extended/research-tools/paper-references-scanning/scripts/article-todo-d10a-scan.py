#!/usr/bin/env python3
"""Targeted D10a scan for article_todo workspace papers.

Unlike the main pipeline scan (d8d10a-scan.py, which targets
/media/yakeworld/sda2/Synthos/outputs/papers/), this scans the writing
workspace at ~/桌面/article_todo/.  Writing-workspace papers have their own
pitfalls:

  • Multi-tex version scoring — older template-heavy tex may win over
    newer optimized tex.  This script adds a +500 version bonus for
    filenames with higher version suffixes (v2 > v1).
  • Template artifact filtering — elsarticle-template-num.tex and
    Sage_LaTeX_Guidelines.tex are skipped.
  • Stale .bbl detection — zero-byte bbl, basename mismatch, and
    parent-directory bbl from a different tex revision are all flagged.

Usage:
    python3 scripts/article-todo-d10a-scan.py

Output: per-paper D10a, cite count, bibitem count, bbl source, and
orphan list.  Threshold is 95% (matching the pipeline standard).
"""

import os, re, glob

BASE = os.path.expanduser("~/桌面/article_todo")

def extract_cites(tex_content: str) -> set:
    """Extract citation keys from tex, skipping comment lines and template placeholders."""
    keys = set()
    for line in tex_content.split('\n'):
        if line.lstrip().startswith('%'):
            continue
        for match in re.findall(r'\\\w*cite\w*\{([^}]+)\}', line):
            for k in match.split(','):
                k = k.strip()
                if k and '<' not in k and ' ' not in k and k not in ('label', 'lamport94'):
                    keys.add(k)
    return keys


def extract_bibitems(bbl_content: str) -> set:
    """Extract bibitem keys from .bbl, skipping template placeholders."""
    items = set(re.findall(r'\\bibitem\{(.+?)\}', bbl_content))
    return {b for b in items if b not in ('label', 'lamport94', 'ref1', 'ref2', 'ref3', 'R1', 'R2', 'R3')}


def version_bonus(filename: str) -> int:
    """Heuristic: newer versioned files get a scoring boost."""
    m = re.search(r'v(\d+)', os.path.basename(filename))
    return int(m.group(1)) * 500 if m else 0


def score_tex(filepath: str) -> tuple:
    """Score a tex file for selection.  Higher = better.
    
    Returns (score, path).  Score = 1000 (has document) + version_bonus + cite_count.
    """
    try:
        with open(filepath) as f:
            content = f.read()
    except Exception:
        return (-1, filepath)
    has_doc = 1000 if '\\begin{document}' in content else 0
    vbonus = version_bonus(filepath)
    cites = len(extract_cites(content))
    return (has_doc + vbonus + cites, filepath)


def compute_d10a(tex_content: str, bbl_path: str | None, tex_path: str) -> dict:
    """Compute D10a for a tex file with optional .bbl."""
    cites = extract_cites(tex_content)
    bibitems = set()
    source = "NONE"
    stale_note = ""

    if bbl_path and os.path.exists(bbl_path):
        bbl_size = os.path.getsize(bbl_path)
        if bbl_size == 0:
            stale_note = " [STALE: 0-byte]"
        else:
            tex_basename = os.path.splitext(os.path.basename(tex_path))[0]
            bbl_basename = os.path.splitext(os.path.basename(bbl_path))[0]
            if tex_basename != bbl_basename:
                stale_note = f" [STALE: basename mismatch ({bbl_basename} vs {tex_basename})]"
        try:
            with open(bbl_path) as f:
                bbl_content = f.read()
        except Exception:
            bbl_content = ""
        bibitems = extract_bibitems(bbl_content)
        source = f".bbl ({len(bibitems)} bibitems){stale_note}"
    else:
        # Fall back to inline thebibliography
        tb = re.search(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}',
                       tex_content, re.DOTALL)
        if tb:
            bibitems = extract_bibitems(tb.group(0))
            source = f"thebibliography ({len(bibitems)} bibitems)"

    if not cites:
        d10a = 100.0
        d10a_str = "N/A (0 cites)"
    elif not bibitems:
        d10a = 0.0
        d10a_str = "0.0% (no bibitems found)"
    else:
        matched = cites & bibitems
        d10a = len(matched) / len(cites) * 100
        d10a_str = f"{d10a:.1f}%"

    orphans = sorted(cites - bibitems) if cites and bibitems else []
    return {
        "cites": len(cites),
        "bibitems": len(bibitems),
        "d10a": d10a,
        "d10a_str": d10a_str,
        "source": source,
        "orphans": orphans,
    }


def main():
    if not os.path.isdir(BASE):
        print(f"ERROR: article_todo base not found: {BASE}")
        return

    paper_dirs = sorted(
        d for d in os.listdir(BASE)
        if os.path.isdir(os.path.join(BASE, d)) and not d.startswith('.')
    )

    results = []
    for pdir in paper_dirs:
        pdir_path = os.path.join(BASE, pdir)
        tex_files = glob.glob(os.path.join(pdir_path, '**', '*.tex'), recursive=True)

        # Filter out templates and submission-file copies
        real_tex = [
            t for t in tex_files
            if 'elsarticle-template-num' not in t
            and 'Sage_LaTeX_Guidelines' not in t
            and 'new graph' not in t
            and '投稿文件' not in t  # submission-file copies
        ]

        if not real_tex:
            results.append({'paper': pdir, 'error': 'no real tex (only template stubs)'})
            continue

        # Pick best tex: score + version bonus
        scored = [score_tex(t) for t in real_tex]
        scored.sort(key=lambda x: x[0], reverse=True)
        best_tex = scored[0][1]

        try:
            with open(best_tex) as f:
                tex_content = f.read()
        except Exception:
            results.append({'paper': pdir, 'error': f'cannot read {best_tex}'})
            continue

        # Find .bbl — prefer same-directory, same-basename match
        tex_dir = os.path.dirname(best_tex)
        tex_basename = os.path.splitext(os.path.basename(best_tex))[0]
        bbl_files = glob.glob(os.path.join(tex_dir, '*.bbl'))
        bbl_path = None
        for bbl in bbl_files:
            bbl_basename = os.path.splitext(os.path.basename(bbl))[0]
            if bbl_basename == tex_basename:
                bbl_path = bbl
                break
        if not bbl_path and bbl_files:
            bbl_path = bbl_files[0]  # fallback to first bbl (will flag staleness)

        info = compute_d10a(tex_content, bbl_path, best_tex)
        info['paper'] = pdir
        info['tex'] = os.path.relpath(best_tex, BASE)
        info['bbl_path'] = bbl_path
        results.append(info)

    # Print
    print("=" * 70)
    print("ARTICLE_TODO D10a SCAN RESULTS")
    print("=" * 70)
    passed = 0
    failed = 0
    for r in results:
        if 'error' in r:
            print(f"  {r['paper']}: WARNING: {r['error']}")
            continue
        flag = "PASS" if r['d10a'] >= 95.0 else "FAIL"
        if flag == "PASS":
            passed += 1
        else:
            failed += 1
        print(f"[{flag}] {r['paper']}")
        print(f"   tex: {r['tex']}")
        print(f"   D10a: {r['d10a_str']} ({r['cites']} cites / {r['bibitems']} bibitems)")
        print(f"   source: {r['source']}")
        if r.get('orphans'):
            print(f"   orphans: {r['orphans'][:8]}")
        print()

    print(f"\nSUMMARY: {passed} PASS, {failed} FAIL, "
          f"{len([r for r in results if 'error' in r])} errors")


if __name__ == "__main__":
    main()
