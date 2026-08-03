#!/usr/bin/env python3
"""从 .bak 备份文件恢复正确的参考文献到 06-references/references.bib

.bak 文件包含 bib-recovery pipeline 恢复的原始引用数据，
使用 tex 文件中的 cite key 命名，因此可以直接使用。
"""
import json, os, re, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS_DIR = os.path.join(BASE_DIR, 'outputs', 'papers')

BIB_RE = r'^@\w+\{([^,]+)'

def extract_clean_entries(content):
    """Extract clean @article entries from potentially messy .bak content."""
    entries = {}
    # Split by @article or @ or @comment
    for m in re.finditer(r'(@\w+)\{([^,]+)', content):
        entry_type = m.group(1)
        key = m.group(2).strip()
        if not key or key.startswith('%'):
            continue
        
        # Find the closing brace for this entry
        start = m.start()
        depth = 0
        end = start
        for i, c in enumerate(content[start:], start):
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        
        # Check if this looks like a real bib entry (has title/author/year)
        block = content[start:end]
        has_title = 'title' in block.lower()
        has_author = 'author' in block.lower()
        has_year = 'year' in block.lower()
        
        if has_title or has_author or has_year:
            entries[key] = block
    
    return entries

def main():
    fixed = 0
    skipped = 0
    no_bak = 0
    
    for item in sorted(os.listdir(PAPERS_DIR)):
        full = os.path.join(PAPERS_DIR, item)
        if not os.path.isdir(full):
            continue
        
        tex_path = os.path.join(full, '01-manuscript', 'paper.tex')
        if not os.path.exists(tex_path):
            continue
        
        # Get tex cite keys
        tex = open(tex_path).read()
        cites = set()
        for m in re.findall(r'\\cite[^{]*{([^}]+)}', tex):
            for k in m.split(','):
                k = k.strip()
                if k:
                    cites.add(k)
        if not cites:
            continue
        
        # Check for .bak files in 06-references/
        bak_path = os.path.join(full, '06-references', 'references.bib.bak')
        if os.path.exists(bak_path):
            with open(bak_path) as f:
                bak_content = f.read()
            
            bak_entries = extract_clean_entries(bak_content)
            
            # Find entries that match tex cite keys
            matching = {}
            for key, entry in bak_entries.items():
                # Match by key name (case-insensitive) or by key containing cite key
                for cite in cites:
                    if key.lower() == cite.lower() or cite in key.lower():
                        matching[key] = entry
                        break
                if key in matching:
                    continue
            
            if matching:
                # Write matching entries as 06-references/references.bib
                target = os.path.join(full, '06-references', 'references.bib')
                os.makedirs(os.path.dirname(target), exist_ok=True)
                
                with open(target, 'w') as f:
                    f.write(f'% Consolidated references for {item}\n')
                    f.write(f'% Restored from .bak backup\n')
                    f.write(f'% Matching {len(matching)} of {len(cites)} tex cite keys\n\n')
                    
                    written = 0
                    for key, entry in matching.items():
                        f.write(f'{entry}\n\n')
                        written += 1
                    
                    # Add remaining tex cite keys as comments (need manual fix)
                    remaining = cites - set(matching.keys())
                    if remaining:
                        f.write(f'% MISSING REFERENCES (need manual fix):\n')
                        for k in sorted(remaining):
                            f.write(f'% {k}\n')
                    
                    fixed += 1
                    print(f"  {item}: restored {written} from .bak ({len(remaining)} missing)")
                continue
            
            print(f"  {item}: .bak found but no matching entries")
            skipped += 1
        else:
            no_bak += 1
    
    print(f"\nPhase 2.5 Complete:")
    print(f"  Restored from .bak: {fixed}")
    print(f"  Skipped (no match): {skipped}")
    print(f"  No .bak file: {no_bak}")

if __name__ == '__main__':
    main()
