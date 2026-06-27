# Multi-Tex Version Drift Detection

## Problem

A paper directory contains multiple `.tex` files with different citation keys. When a quality review or D10a scan targets one version while the queue record is based on another, the D10a score drops dramatically even though the paper's references are actually healthy.

## Real Case: HCS-3WT (2026-06-26)

- `hcs3wt-breast-cancer.tex` (current): 29 unique cite keys
- `hcs3wt-breast-cancer-improved.tex` (older): 23 unique cite keys
- 6 cite keys in current version have no bib entries
- 9 bib entries in current version are not cited (were cited in older version)
- Queue record: D10a=100% (30/30) — based on an earlier version
- Current scan: D10a=79.3% (23/29)

Root cause: During revision, some old cite keys were replaced with new ones, but the new keys were never added to `references.bib`.

## Detection Script

```python
#!/usr/bin/env python3
"""Detect multi-tex version drift in a paper directory."""
import re, os, sys

def extract_cite_keys(tex_path):
    """Extract all unique cite keys from a .tex file."""
    with open(tex_path) as f:
        content = f.read()
    cites = re.findall(r'\\(?:cite|citep|citet)\{([^}]+)\}', content)
    keys = set()
    for c in cites:
        for k in c.split(','):
            k = k.strip()
            if k and k not in ('<label>',):
                keys.add(k)
    return keys

def check_tex_drift(paper_dir):
    """Check for citation key drift across .tex versions."""
    manuscript_dir = os.path.join(paper_dir, '01-manuscript')
    if not os.path.isdir(manuscript_dir):
        manuscript_dir = paper_dir
    
    tex_files = [f for f in os.listdir(manuscript_dir) if f.endswith('.tex')]
    
    if len(tex_files) <= 1:
        print("Single .tex file — no drift possible.")
        return
    
    versions = {}
    for tf in tex_files:
        versions[tf] = extract_cite_keys(os.path.join(manuscript_dir, tf))
    
    all_keys = set()
    for keys in versions.values():
        all_keys.update(keys)
    
    print(f"Found {len(tex_files)} .tex versions:")
    for tf, keys in sorted(versions.items()):
        print(f"  {tf}: {len(keys)} unique cite keys")
    
    print(f"\nAll unique keys across all versions: {len(all_keys)}")
    
    for key in sorted(all_keys):
        in_versions = [tf for tf, k in versions.items() if key in k]
        if len(in_versions) < len(tex_files):
            missing_from = [tf for tf in tex_files if tf not in in_versions]
            print(f"  {key}: in {in_versions}, missing from {missing_from}")
    
    bib_path = os.path.join(manuscript_dir, 'references.bib')
    if os.path.exists(bib_path):
        with open(bib_path) as f:
            bib_content = f.read()
        bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib_content))
        
        print(f"\nBib entries: {len(bib_keys)}")
        for tf, keys in sorted(versions.items()):
            not_in_bib = keys - bib_keys
            if not_in_bib:
                print(f"  {tf}: {len(not_in_bib)} keys NOT in bib: {sorted(not_in_bib)}")

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else input("Paper directory: ")
    check_tex_drift(path)
```

## Prevention

1. **When editing `.tex`**: Always add corresponding entries to `references.bib` BEFORE replacing a cite key.
2. **Clean up**: Delete old `.tex` versions after finalizing. Keep only the canonical manuscript.
3. **Document**: Add a comment at the top of the final `.tex` file noting the expected cite count.
4. **CI check**: Run this script during quality reviews whenever a paper directory has >1 `.tex` file.

## Integration with D10a Scan

When running `scripts/d10a-targeted-scan.py` on a paper:
1. First check if the directory has >1 `.tex` file
2. If yes, run this multi-tex drift check
3. Only compute D10a on the version confirmed as the current manuscript
4. If the queue record's D10a differs from the current version's D10a, flag for manual review
