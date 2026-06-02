#!/usr/bin/env python3
"""Silent Citation Trap Scanner — pre-compilation citation health check.

Detects two classes of silent citation failure that compile successfully
with 0 errors but produce [?] for specific references:

Trap A — Accented bibitem/cite keys (e.g. \\cite{Abràmoff2018}):
  LaTeX truncates the key at the accent character. PDF generates, pages
  count is correct, log shows 'moff2018 undefined on input'.

Trap B — Double-backslash bibitem keys (e.g. \\\\\\bibitem{Chen2025}):
  LaTeX silently ignores the doubled control sequence. The entry counts
  in D8 scans but never resolves. Log shows '[?]' for that ref.

Usage:
  python3 silent_trap_scanner.py paper.tex             # Scan a single .tex file
  python3 silent_trap_scanner.py --dir outputs/papers/ # Scan entire directory
  python3 silent_trap_scanner.py paper.tex --verbose   # Show source lines
  python3 silent_trap_scanner.py paper.tex --fix       # Auto-fix both traps

Exit codes:
  0 — No traps found
  1 — Traps detected (or fix applied)
  2 — File not found / parse error
"""

import re
import sys
import os
import shutil

def scan_tex(filepath, verbose=False):
    """Scan a .tex file for silent citation traps.
    
    Returns dict with trap counts and details.
    """
    tex = open(filepath, 'r', errors='replace').read()
    
    # Filter comment lines
    lines = tex.split('\n')
    active_lines = [l for l in lines if not l.strip().startswith('%')]
    active = '\n'.join(active_lines)
    
    result = {
        'file': filepath,
        'accented_keys': [],
        'accented_cites': [],
        'double_bs_bibitems': [],
        'has_bibtex_mode': None,
        'has_thebibliography': None,
    }
    
    # Detection Mode: Thebibliography vs BibTeX
    result['has_thebibliography'] = '\\begin{thebibliography}' in active
    result['has_bibtex_mode'] = '\\bibliography{' in active
    
    # Trap A: Accented bibitem keys (in thebibliography mode)
    if result['has_thebibliography']:
        bibitem_keys = set(re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', active))
        for k in sorted(bibitem_keys):
            if re.search(r'[àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþ]', k, re.IGNORECASE):
                result['accented_keys'].append(k)
    
    # Trap B: Double-backslash bibitem keys (in thebibliography mode)
    if result['has_thebibliography']:
        dbl_keys = re.findall(r'\\\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', active)
        result['double_bs_bibitems'] = dbl_keys
    
    # Trap A: Also check \\cite{} keys for accents (applies to all modes)
    for m in re.finditer(r'\\cite[tp]?\s*\{([^}]+)\}', active):
        for k in m.group(1).split(','):
            k = k.strip()
            if re.search(r'[àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþ]', k, re.IGNORECASE):
                if k not in result['accented_cites']:
                    result['accented_cites'].append(k)
    
    # Verbose: show line numbers
    if verbose:
        for i, line in enumerate(lines, 1):
            if not line.strip().startswith('%'):
                for k in result['accented_keys']:
                    if k in line:
                        print(f"  L{i}: {line.strip()[:120]}")
                for k in result['double_bs_bibitems']:
                    if k in line:
                        print(f"  L{i}: {line.strip()[:120]}")
    
    return result


def scan_directory(root_dir, verbose=False):
    """Scan all .tex files in a directory tree."""
    results = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip background, _todo, scripts directories
        skip_dirs = {'09-background', '_todo', '_archive_scripts', 'scripts'}
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        
        for f in sorted(filenames):
            if f.endswith('.tex') and not f.startswith('.'):
                fp = os.path.join(dirpath, f)
                try:
                    res = scan_tex(fp, verbose=verbose)
                    if res['accented_keys'] or res['double_bs_bibitems'] or res['accented_cites']:
                        paper = os.path.basename(os.path.dirname(fp))
                        results[f"{paper}/{f}"] = res
                except Exception as e:
                    print(f"  ERROR {fp}: {e}", file=sys.stderr)
    return results


def fix_traps(filepath, dry_run=True):
    """Auto-fix detected traps in-place.
    
    Fixes:
      - Double-backslash bibitem: \\\\\\bibitem{key} → \\\\bibitem{key}
      - Accented bibitem keys: \\\\bibitem{Zéboulon2023} → \\\\bibitem{Zeboulon2023}
      - Also fixes corresponding \\\\cite{...} references
    
    Creates .bak backup before modifying.
    """
    tex = open(filepath, 'r', errors='replace').read()
    original = tex
    fixes = []
    
    # Fix Trap B: Double-backslash bibitem
    dbl_keys = re.findall(r'\\\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', tex)
    for key in dbl_keys:
        old = f'\\\\bibitem{{{key}}}'
        # Also handle bibitem with optional arg
        old_alt = None
        for m in re.finditer(r'\\\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', tex):
            if m.group(1) == key:
                old_alt = m.group(0)
                break
        if old in tex:
            tex = tex.replace(old, f'\\bibitem{{{key}}}')
            fixes.append(f"FIXED double-bs bibitem: {key}")
        elif old_alt:
            new = old_alt.replace('\\\\bibitem', '\\bibitem')
            tex = tex.replace(old_alt, new)
            fixes.append(f"FIXED double-bs bibitem (with opt arg): {key}")
    
    # Fix Trap A: Accented bibitem keys + cite keys
    accent_map = str.maketrans({
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a', 'æ': 'ae',
        'ç': 'c',
        'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
        'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
        'ð': 'd', 'ñ': 'n',
        'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o', 'ø': 'o',
        'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
        'ý': 'y', 'þ': 'th',
        'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A', 'Æ': 'AE',
        'Ç': 'C',
        'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
        'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O', 'Ø': 'O',
        'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
        'Ý': 'Y',
    })
    
    # Find all accented keys in bibitems
    lines = tex.split('\n')
    for i, line in enumerate(lines):
        for m in re.finditer(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', line):
            key = m.group(1)
            if re.search(r'[àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþ]', key, re.IGNORECASE):
                ascii_key = key.translate(accent_map)
                # Fix this specific bibitem
                old_line = line
                new_line = line.replace(f'{{{key}}}', f'{{{ascii_key}}}')
                if new_line != old_line:
                    lines[i] = new_line
                    fixes.append(f"FIXED accented bibitem: {key} → {ascii_key}")
    
    # Fix accented cite keys in the entire tex
    tex = '\n'.join(lines)
    cite_patterns = [
        (r'\\cite\{([^}]+)\}', '\\cite'),
        (r'\\citep\{([^}]+)\}', '\\citep'),
        (r'\\citet\{([^}]+)\}', '\\citet'),
        (r'\\citealt\{([^}]+)\}', '\\citealt'),
    ]
    for pattern, cmd_name in cite_patterns:
        for m in re.finditer(pattern, tex):
            keys_str = m.group(1)
            keys = [k.strip() for k in keys_str.split(',')]
            new_keys = []
            for k in keys:
                if re.search(r'[àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþ]', k, re.IGNORECASE):
                    ascii_k = k.translate(accent_map)
                    fixes.append(f"FIXED accented cite: {k} → {ascii_k}")
                    new_keys.append(ascii_k)
                else:
                    new_keys.append(k)
            if any(nk != ok for nk, ok in zip(new_keys, keys)):
                old_str = f'{cmd_name}{{{keys_str}}}'
                new_str = f'{cmd_name}{{{", ".join(new_keys)}}}'
                tex = tex.replace(old_str, new_str)
    
    if dry_run:
        return fixes, False
    
    if fixes:
        # Backup
        shutil.copy2(filepath, filepath + '.bak')
        with open(filepath, 'w') as f:
            f.write(tex)
        return fixes, True
    return fixes, False


def print_report(result, verbose=False):
    """Pretty-print scanning results."""
    traps = sum([
        len(result['accented_keys']),
        len(result['double_bs_bibitems']),
        len(result['accented_cites']),
    ])
    
    paper = os.path.basename(os.path.dirname(result['file']))
    fname = os.path.basename(result['file'])
    label = f"{paper}/{fname}" if paper and paper != fname.replace('.tex', '') else fname
    
    if traps == 0:
        print(f"  ✅ {label} — clean")
        return
        
    print(f"  ⚠️  {label} — {traps} trap(s) detected")
    
    if result['accented_keys']:
        print(f"     Trap A (accented bibitem keys): {', '.join(result['accented_keys'])}")
    if result['accented_cites']:
        unique = [k for k in result['accented_cites'] if k not in result['accented_keys']]
        if unique:
            print(f"     Trap A (accented cite keys, non-bibitem): {', '.join(unique)}")
    if result['double_bs_bibitems']:
        print(f"     Trap B (double-backslash bibitems): {', '.join(result['double_bs_bibitems'])}")
    
    print(f"     Mode: thebibliography={result['has_thebibliography']}, bibtex={result['has_bibtex_mode']}")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Silent citation trap scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('target', nargs='?', help='.tex file or directory to scan')
    parser.add_argument('--dir', help='Scan entire paper directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show source lines')
    parser.add_argument('--fix', action='store_true', help='Auto-fix detected traps (creates .bak)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without changing')
    
    args = parser.parse_args()
    
    target = args.target or args.dir
    if not target:
        parser.print_help()
        sys.exit(2)
    
    if os.path.isdir(target):
        results = scan_directory(target, verbose=args.verbose)
        if not results:
            print(f"No traps found in {target}")
            sys.exit(0)
        print(f"\nFound traps in {len(results)} file(s):")
        for path, r in results.items():
            print_report(r, verbose=args.verbose)
        sys.exit(1)
    
    elif os.path.isfile(target):
        if args.fix or args.dry_run:
            fixes, applied = fix_traps(target, dry_run=args.dry_run or not args.fix)
            if fixes:
                mode = "Would fix" if (args.dry_run or not args.fix) else "Fixed"
                for f in fixes:
                    print(f"  {mode}: {f}")
                if applied:
                    print(f"  Backup saved to {target}.bak")
                    print(f"  Run rm -f *.aux *.bbl && pdflatex paper.tex && pdflatex paper.tex to verify")
                sys.exit(1)
            else:
                print("No traps found — nothing to fix")
                sys.exit(0)
        else:
            result = scan_tex(target, verbose=args.verbose)
            print_report(result, verbose=args.verbose)
            if result['accented_keys'] or result['double_bs_bibitems'] or result['accented_cites']:
                sys.exit(1)
            sys.exit(0)
    
    else:
        print(f"Error: {target} not found", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
