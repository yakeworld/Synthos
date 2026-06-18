#!/usr/bin/env python3
"""D8/D10a Citation Health Scan for Synthos paper library (v2 - fixed bib resolution).

Key rules:
- Only scan primary paper.tex: prefer 01-manuscript/paper.tex, fallback to root paper.tex
- Each paper should use its OWN .bib file, NOT the shared references.bib at top level
- Shared bib is excluded from individual paper scans unless no local bib exists
- D8 = number of bib entries in the paper's own bib
- D10a = % of cite keys found in the paper's own bib
"""

import os, re, glob
from pathlib import Path

PAPERS_DIR = "/media/yakeworld/sda2/Synthos/outputs/papers"
SHARED_BIB = os.path.join(PAPERS_DIR, "references.bib")

def extract_cite_keys(tex_path):
    """Extract all citation keys from LaTeX file."""
    keys = set()
    try:
        with open(tex_path, 'r', errors='ignore') as f:
            content = f.read()
        patterns = [
            r'\\cite[pt]?\{([^}]+)\}',
            r'\\nocite\{([^}]+)\}',
            r'\\fullcite\{([^}]+)\}',
        ]
        for pat in patterns:
            for m in re.finditer(pat, content):
                inner = m.group(1)
                for key in inner.split(','):
                    k = key.strip()
                    if k:
                        keys.add(k)
    except Exception as e:
        print(f"  Error reading {tex_path}: {e}")
    return keys

def extract_bib_keys(bib_path):
    """Extract all bibliographic keys from .bib file."""
    keys = set()
    try:
        with open(bib_path, 'r', errors='ignore') as f:
            content = f.read()
        for m in re.finditer(r'^@\w+\{([^,}]+)', content, re.MULTILINE):
            raw = m.group(1).strip()
            for k in raw.split(','):
                k = k.strip()
                if k:
                    keys.add(k)
    except Exception as e:
        print(f"  Error reading {bib_path}: {e}")
    return keys

def find_primary_tex(paper_dir):
    """Find the primary paper.tex for a paper directory.
    Prefer 01-manuscript/paper.tex, fallback to root paper.tex."""
    tex01 = os.path.join(paper_dir, "01-manuscript", "paper.tex")
    tex_root = os.path.join(paper_dir, "paper.tex")
    if os.path.exists(tex01):
        return tex01
    if os.path.exists(tex_root):
        return tex_root
    return None

def find_paper_bib(paper_dir, exclude_shared=True):
    """Find the paper's own .bib file.
    Priority: 06-references/references.bib > root references.bib > any .bib at root.
    Exclude the shared top-level references.bib."""
    parent = Path(paper_dir)
    
    # Priority 1: 06-references/references.bib
    bib = parent / "06-references" / "references.bib"
    if bib.exists():
        return str(bib)
    
    # Priority 2: root references.bib (at paper dir level)
    bib = parent / "references.bib"
    if bib.exists():
        abs_path = str(bib.resolve())
        if exclude_shared and abs_path == str(Path(SHARED_BIB).resolve()):
            return None  # Skip shared bib
        return str(bib)
    
    # Priority 3: any .bib at paper dir level (not shared)
    for f in sorted(parent.glob("*.bib")):
        abs_path = str(f.resolve())
        if exclude_shared and abs_path == str(Path(SHARED_BIB).resolve()):
            continue
        return str(f)
    
    # Fallback: shared bib only if no local found
    if not exclude_shared and os.path.exists(SHARED_BIB):
        return SHARED_BIB
    
    return None

def find_bbl_file(paper_dir):
    """Find .bbl compilation output in the paper's root directory."""
    parent = Path(paper_dir)
    for f in parent.glob("*.bbl"):
        return str(f)
    return None

def is_bib_match(cite_key, bib_key):
    """Check if a citation key matches a bib entry key."""
    if cite_key == bib_key:
        return True
    if cite_key in bib_key or bib_key in cite_key:
        return True
    a = cite_key.replace('_', '-').replace(' ', '-')
    b = bib_key.replace('_', '-').replace(' ', '-')
    if a == b:
        return True
    return False

def get_paper_name(paper_dir):
    """Get the relative path of the paper directory under PAPERS_DIR."""
    return os.path.relpath(paper_dir, PAPERS_DIR)

def main():
    results = []
    
    # Collect unique paper directories (resolve dedup)
    paper_dirs_seen = set()
    paper_dirs = []
    
    for root, dirs, files in os.walk(PAPERS_DIR):
        if "paper.tex" not in files:
            continue
        
        # Find the primary tex file
        tex01 = os.path.join(root, "01-manuscript", "paper.tex")
        if os.path.exists(tex01):
            # The paper directory is root of the whole paper tree
            paper_dir = os.path.dirname(os.path.dirname(tex01))
        else:
            # Check if there's a 01-manuscript sibling
            parent_dir = os.path.dirname(root)
            tex01_parent = os.path.join(parent_dir, "01-manuscript", "paper.tex")
            if os.path.exists(tex01_parent):
                paper_dir = parent_dir
            else:
                paper_dir = root
        
        if paper_dir in paper_dirs_seen:
            continue
        paper_dirs_seen.add(paper_dir)
        paper_dirs.append(paper_dir)
    
    paper_dirs.sort()
    
    print("📊 论文全库扫描报告")
    print()
    print(f"| 论文 | D8 | D10a | 孤儿 | 僵尸 | 编译 |")
    print(f"|:-----|:--:|:----:|:----:|:----:|:----:|")
    
    problem_papers = []
    total_cites = 0
    total_orphans = 0
    total_zombies = 0
    total_d8 = 0
    
    for paper_dir in paper_dirs:
        base_name = get_paper_name(paper_dir)
        
        # Get primary tex
        tex_path = find_primary_tex(paper_dir)
        if tex_path is None:
            continue
        
        # Get cite keys
        cite_keys = extract_cite_keys(tex_path)
        
        # Find bib file
        bib_file = find_paper_bib(paper_dir, exclude_shared=True)
        
        if bib_file and os.path.exists(bib_file):
            bib_keys = extract_bib_keys(bib_file)
            d8 = len(bib_keys)
            bib_label = os.path.basename(bib_file)
        else:
            bib_keys = set()
            d8 = 0
            bib_label = "NONE"
        
        # Find orphans
        orphans = []
        for ck in sorted(cite_keys):
            matched = False
            for bk in bib_keys:
                if is_bib_match(ck, bk):
                    matched = True
                    break
            if not matched:
                orphans.append(ck)
        
        # Find zombies
        zombies = []
        for bk in sorted(bib_keys):
            matched = False
            for ck in cite_keys:
                if is_bib_match(ck, bk):
                    matched = True
                    break
            if not matched:
                zombies.append(bk)
        
        # D10a
        if len(cite_keys) > 0:
            matched_cites = len(cite_keys) - len(orphans)
            d10a = round((matched_cites / len(cite_keys)) * 100)
        else:
            d10a = 100
        
        # Compiled
        bbl = find_bbl_file(paper_dir)
        compiled = "✅" if bbl else "❌"
        
        total_cites += len(cite_keys)
        total_orphans += len(orphans)
        total_zombies += len(zombies)
        total_d8 += d8
        
        print(f"| {base_name} | {d8} | {d10a}% | {len(orphans)} | {len(zombies)} | {compiled} |")
        
        if d10a < 100 or d8 < 30:
            problem_papers.append({
                'name': base_name,
                'd8': d8,
                'd10a': d10a,
                'orphans': orphans,
                'zombies': zombies,
                'compiled': compiled,
                'cite_count': len(cite_keys),
                'bib_file': bib_label,
            })
    
    print()
    print(f"总计: {len(paper_dirs)}篇, 健康: {len(paper_dirs) - len(problem_papers)}篇, 问题: {len(problem_papers)}篇")
    print(f"总引用数: {total_cites}, 总孤儿: {total_orphans}, 总僵尸: {total_zombies}, 总D8: {total_d8}")
    
    if problem_papers:
        print()
        print("问题论文（D10a<100% 或 D8<30）:")
        for p in sorted(problem_papers, key=lambda x: (x['d10a'], x['d8'])):
            parts = []
            orph_display = ', '.join(p['orphans'][:15])
            if len(p['orphans']) > 15:
                orph_display += f"... (+{len(p['orphans'])-15} more)"
            zomb_display = ', '.join(p['zombies'][:15])
            if len(p['zombies']) > 15:
                zomb_display += f"... (+{len(p['zombies'])-15} more)"
            
            parts.append(f"- {p['name']}")
            parts.append(f"    D8={p['d8']}, D10a={p['d10a']}%, 引用={p['cite_count']}, bib={p['bib_file']}")
            if p['orphans']:
                parts.append(f"    孤儿({len(p['orphans'])}): {orph_display}")
            if p['zombies']:
                parts.append(f"    僵尸({len(p['zombies'])}): {zomb_display}")
            if p['compiled'] == '❌':
                parts.append(f"    ⚠️ 未编译(.bbl缺失)")
            for part in parts:
                print(part)
            print()

if __name__ == "__main__":
    main()
