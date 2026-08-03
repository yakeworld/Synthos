#!/usr/bin/env python3
"""Fix all 06-references/references.bib files by consolidating from paper's bib files."""
import json, os, re, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS_DIR = os.path.join(BASE_DIR, 'outputs', 'papers')
CITE_RE = r'\\cite[^{]*{([^}]+)}'
BIB_RE = r'@\w+\{([^,]+)'

def get_cite_keys(tex_path):
    with open(tex_path) as f:
        content = f.read()
    matches = re.findall(CITE_RE, content)
    return set(k for m in matches for k in m.split(',') if k.strip())

def consolidate_bib(paper_dir):
    """Merge all bib entries into 06-references/references.bib."""
    # Find all real bib files
    all_entries = {}
    for root, dirs, files in os.walk(paper_dir):
        for f in files:
            if not f.endswith('.bib'):
                continue
            path = os.path.join(root, f)
            if os.path.islink(path) and not os.path.exists(path):
                continue
            if not os.path.isfile(path):
                continue
            with open(path) as bf:
                content = bf.read()
            if not re.search(r'^@\w+\{', content, re.MULTILINE):
                continue
            for m in re.finditer(BIB_RE, content):
                key = m.group(1).strip()
                if key not in all_entries:
                    all_entries[key] = content

    if not all_entries:
        return 0

    # Write consolidated bib
    target = os.path.join(paper_dir, '06-references', 'references.bib')
    os.makedirs(os.path.dirname(target), exist_ok=True)

    with open(target, 'w') as f:
        keys_written = set()
        for key, content in all_entries.items():
            if key in keys_written:
                continue
            # Extract just this entry
            key_pattern = r'@\w+\{' + re.escape(key) + r'\s*[,}]'
            for em in re.finditer(key_pattern, content):
                start = em.start()
                # Find the closing brace
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
                f.write(content[start:end])
                f.write('\n\n')
                keys_written.add(key)
                break

    return len(keys_written)

def main():
    fixed = 0
    for item in sorted(os.listdir(PAPERS_DIR)):
        full = os.path.join(PAPERS_DIR, item)
        if not os.path.isdir(full):
            continue
        tex_path = os.path.join(full, '01-manuscript', 'paper.tex')
        if not os.path.exists(tex_path):
            continue

        count = consolidate_bib(full)
        if count > 0:
            fixed += 1
            print(f"  {item}: {count} entries consolidated")

    print(f"\nFixed {fixed} papers")

if __name__ == '__main__':
    main()
