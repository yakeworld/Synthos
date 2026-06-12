#!/usr/bin/env python3
"""D8/D10a paper library scan — FINAL v7 (fix: %, $...%$ don't trigger comment)."""
import os, re, json, sys
from pathlib import Path

papers_dir = Path("/media/yakeworld/sda2/Synthos/outputs/papers")
results = []

paper_dirs = sorted([d for d in papers_dir.iterdir() if d.is_dir() and not d.name.startswith('_') and d.name != 'lit-reviews'])

def is_comment_line(line):
    """Check if a LaTeX line is a comment.
    - %% or % at start (after optional whitespace) = comment
    - But \\%, $...%$ are NOT comments
    """
    stripped = line.lstrip()
    if not stripped:
        return False
    if stripped.startswith('%%'):
        return True
    if stripped.startswith('%'):
        return True
    return False

# Cite patterns — r'\\cite' = two backslashes in source → one literal backslash in regex
cite_re = re.compile(r'\\cite[sp]?\{([^}]+)\}')
cite_opt_re = re.compile(r'\\cite\[([^\]]*)\]\{([^}]+)\}')
# Bib key: [^\s,;]+? handles hyphens in keys like Norgeot2020MI-CLAIM
bib_key_re = re.compile(r'@(?!Comment)\w+\{[^\s,;]+?,', re.MULTILINE)
bibitem_re = re.compile(r'\\bibitem\{([^}]+)\}')

def find_nearest_bib(pdir, tex_path):
    """Find the best bib file for a tex file. Priority:
    1. 06-references/references.bib (if tex is in 01-manuscript/ or root-level)
    2. <tex_stem>.bib at paper root
    3. references.bib at tex parent directory
    4. enhanced_refs/enhanced.bib
    Only ONE bib file per tex to avoid cross-pollination.
    """
    parent = tex_path.parent
    # For 01-manuscript/ or root-level tex, prefer 06-references/
    if parent.name == '01-manuscript' or parent == pdir:
        p0 = pdir / "06-references" / "references.bib"
        if p0.exists():
            return p0
    p2 = pdir / (tex_path.stem + '.bib')
    if p2.exists():
        return p2
    p3 = parent / 'references.bib'
    if p3.exists():
        return p3
    p5 = pdir / "enhanced_refs" / "enhanced.bib"
    if p5.exists():
        return p5
    return None

def get_main_tex(pdir):
    """Get the primary tex file for this paper. If 01-manuscript/paper.tex exists, use it.
    Otherwise, use root-level paper.tex files only (skip drafts, templates, etc.).
    """
    p = pdir / "01-manuscript" / "paper.tex"
    if p.exists():
        return ("main", p)
    
    # Root-level .tex files only (1 level deep)
    for f in pdir.glob("*.tex"):
        fname = f.name
        skip = ['elsarticle', 'template', 'fig_', 'Sage_', 'manuscript_without_author',
                'todo', 'revision', 'temp', 'article', 'pupil', 'figure', 'fig_',
                'new graph', 'new_graph', 'elsarticle-template', 'cover-letter',
                'declarations', 'supplementary']
        if any(sp in fname for sp in skip):
            continue
        if 'v' in fname and any(c.isdigit() for c in fname.split('v')[-1].split('.')[0]):
            # v1.tex, v2.tex, etc. are draft versions
            continue
        return ("main", f)
    
    return None

for pdir in paper_dirs:
    tex_info = get_main_tex(pdir)
    if not tex_info:
        continue
    
    label, tex_path = tex_info
    name = pdir.name
    
    tex_content = tex_path.read_text(encoding="utf-8", errors="replace")

    # Extract uncommented cite keys
    all_cites = set()
    for line in tex_content.split('\n'):
        if is_comment_line(line):
            continue
        for m in cite_re.finditer(line):
            for key in m.group(1).split(','):
                k = key.strip()
                if k:
                    all_cites.add(k)
        for m in cite_opt_re.finditer(line):
            for key in m.group(2).split(','):
                k = key.strip()
                if k:
                    all_cites.add(k)

    # Find ONE bib file
    bib_keys = set()
    bib_file = find_nearest_bib(pdir, tex_path)
    if bib_file:
        bib_content = bib_file.read_text(encoding="utf-8", errors="replace")
        for k in bib_key_re.findall(bib_content):
            # k = "@Article{key," or "@InProceedings{key," — strip @Type{ prefix
            entry = k.strip()
            idx = entry.find('{')
            if idx >= 0:
                entry = entry[idx+1:]
            idx2 = entry.find(',')
            if idx2 >= 0:
                entry = entry[:idx2]
            bib_keys.add(entry)
        for k in bibitem_re.findall(bib_content):
            bib_keys.add(k.strip())

    # Non-commented \bibitem{} from tex
    tex_bibitems = set()
    for line in tex_content.split('\n'):
        if is_comment_line(line):
            continue
        for k in bibitem_re.findall(line):
            bib_keys.add(k.strip())
            tex_bibitems.add(k.strip())

    # Compute
    d8 = len(bib_keys)
    matched = all_cites & bib_keys
    unmatched = all_cites - bib_keys
    zombies = bib_keys - all_cites

    # D10a: if no \cite but has \bibitem, it's self-referenced (100%)
    if len(all_cites) == 0:
        d10a = 100.0
    else:
        d10a = round((len(matched) / len(all_cites)) * 100, 1)

    bbl_path = pdir / "01-manuscript" / "paper.bbl"
    has_bbl = bbl_path.exists()
    bib_source = "none"
    if bib_file:
        bib_source = bib_file.name
    elif len(tex_bibitems) > 0:
        bib_source = "inline"

    results.append({
        "name": name,
        "d8": d8,
        "d10a": d10a,
        "orphans": sorted(unmatched),
        "zombies": sorted(zombies),
        "has_bbl": has_bbl,
        "total_cites": len(all_cites),
        "matched": len(matched),
        "bib_source": bib_source,
        "tex": str(tex_path.relative_to(papers_dir)),
    })

results.sort(key=lambda x: x["name"])

# Track non-paper directories for audit reporting
non_paper_dirs = []
for pdir in paper_dirs:
    if get_main_tex(pdir) is None:
        non_paper_dirs.append(pdir.name)

# Append summary metadata as the LAST entry (name="__metadata__")
results.append({
    "__metadata__": True,
    "total_directories": len(paper_dirs),
    "papers_scanned": len(results),
    "non_paper_directories": sorted(non_paper_dirs),
    "non_paper_count": len(non_paper_dirs),
})

print(json.dumps(results, indent=2, ensure_ascii=False))
