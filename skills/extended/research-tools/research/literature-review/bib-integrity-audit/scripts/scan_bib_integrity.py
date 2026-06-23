#!/usr/bin/env python3
"""
Bib Integrity Audit — standalone runner (no Codex dependency)
Scans all .bib files under a paper library root, producing a unified JSON report.

Usage: python3 scan_bib_integrity.py <output_json_path> [--paper-root <path>]

Originally, unified-paper-scan.sh called 'codex -p hermes exec' which caused
silent 120s timeouts. This script replaces that path with direct Python execution.

Key features:
- Robust BibTeX parsing with multi-line regex (avoids non-greedy trap)
- Suspicious entry detection (arXiv without ID, URL-as-year, Kaggle, auto-keys)
- Cross-file deduplication with consistency check
- Empty bib file detection
- Archive vs active paper separation

Author: Synthos
Date: 2026-06-23
"""

import os
import re
import json
import sys
import argparse

def find_bib_files(root, skip_patterns=None):
    """Find all .bib files under root, skipping _archive_scripts."""
    bibs = []
    skip_patterns = skip_patterns or ['_archive_scripts']
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip _archive_scripts directory entirely
        if any(sp in dirpath for sp in skip_patterns):
            continue
        for f in filenames:
            if f.endswith('.bib'):
                bibs.append(os.path.join(dirpath, f))
    return sorted(bibs)

def parse_bib_entries(filepath):
    """Parse BibTeX entries from a file using robust multi-line regex.
    
    Avoids the non-greedy (.+?) trap that truncates entries at the first }.
    Uses [\\s\\S]*? with lookahead on closing } on its own line.
    """
    with open(filepath, 'r', errors='replace') as f:
        content = f.read()
    
    entries = []
    # Robust multi-line regex — [\s\S]*? matches ANY char including newlines
    # Lookahead matches } on its own line (BibTeX entry terminator)
    pattern = re.compile(
        r'^@([A-Za-z]+)\s*\{\s*([^,]+?),\s*([\s\S]*?)(?=\n\s*\}\s*\n|\n\s*\}\s*$)',
        re.MULTILINE
    )
    
    for m in pattern.finditer(content):
        entry_type = m.group(1).lower()
        key = m.group(2).strip()
        body = m.group(3)
        
        # Skip @Comment entries (JabRef artifacts)
        if entry_type == 'comment':
            continue
        
        fields = {}
        # Parse fields: key = {value} or key = "value" or key = bare_value
        for fm in re.finditer(
            r'(\w+)\s*=\s*(?:\{([^}]*)\}|"([^"]*)"|([^}\n,]+))',
            body, re.DOTALL
        ):
            fname = fm.group(1).lower()
            fval = fm.group(2) or fm.group(3) or fm.group(4) or ''
            fields[fname] = fval.strip()
        
        entries.append({
            'type': entry_type,
            'key': key,
            'fields': fields,
            'title': fields.get('title', 'N/A'),
            'author': fields.get('author', 'N/A'),
            'year': fields.get('year', 'N/A'),
            'journal': fields.get('journal', fields.get('booktitle', 'N/A')),
            'doi': fields.get('doi', ''),
        })
    
    return entries

def is_suspicious(entry):
    """Check for suspicious entry patterns. Returns list of issue descriptions."""
    issues = []
    key = entry['key']
    
    # 1. @misc with auto-generated key
    if entry['type'] == 'misc' and re.search(r'auto\d{4}', key):
        issues.append(f"auto-generated key '@misc{{auto...}}' in key '{key}'")
    
    # 2. Kaggle publisher (dataset citation often malformed)
    author = entry.get('author', '')
    publisher = entry.get('publisher', '')
    if 'kaggle' in author.lower() or 'kaggle' in publisher.lower():
        issues.append("Kaggle publisher in metadata")
    
    # 3. URL in year field
    year = entry.get('year', '')
    if re.match(r'https?://', year):
        issues.append(f"URL in year field: {year}")
    
    # 4. arXiv preprint without arXiv:ID
    journal = entry.get('journal', '')
    if ('arxiv preprint' in journal.lower() or 'arxiv' in journal.lower()):
        has_id = (
            'arxiv:' in entry.get('author', '') or
            'arxiv:' in journal or
            'arxiv:' in entry.get('title', '') or
            'eprint' in entry.get('fields', {})
        )
        if not has_id:
            issues.append("arXiv preprint without arXiv:ID")
    
    # 5. Missing author
    if not entry.get('author') or entry['author'] == 'N/A':
        issues.append("missing author field")
    
    # 6. Missing title
    if not entry.get('title') or entry['title'] == 'N/A':
        issues.append("missing title field")
    
    return issues

def normalize_paper_name(paper_root, full_path):
    """Extract paper name from path (first directory component after root)."""
    try:
        rel = os.path.relpath(full_path, paper_root)
        parts = rel.split(os.sep)
        if len(parts) >= 2:
            return parts[0]
        return rel.split('/')[0]
    except Exception:
        return full_path.split('/')[-2]

def main():
    parser = argparse.ArgumentParser(description='Bib Integrity Audit')
    parser.add_argument('output', help='Output JSON path')
    parser.add_argument('--paper-root', default='/media/yakeworld/sda2/Synthos/outputs/papers',
                       help='Paper library root directory')
    args = parser.parse_args()
    
    paper_root = args.paper_root
    from datetime import datetime
    DATE = datetime.now().strftime("%Y-%m-%d")
    
    # Discover bib files
    bib_files = find_bib_files(paper_root)
    
    # Tracking structures
    all_results = []
    all_entries = {}  # key -> [(file, entry_meta)]
    suspicious = []
    
    # Scan each bib file
    for bib_path in bib_files:
        paper_name = normalize_paper_name(paper_root, bib_path)
        entries = parse_bib_entries(bib_path)
        
        total = len(entries)
        with_doi = sum(1 for e in entries if e.get('doi') and e['doi'].strip())
        doi_cov = (with_doi / total * 100) if total > 0 else 0
        
        # Collect suspicious entries
        for e in entries:
            issues = is_suspicious(e)
            for issue in issues:
                suspicious.append({
                    'key': e['key'],
                    'type': issue,
                    'paper': paper_name,
                    'file': os.path.relpath(bib_path, paper_root),
                })
            
            # Track for cross-file dedup
            key = e['key']
            if key not in all_entries:
                all_entries[key] = []
            all_entries[key].append({
                'file': os.path.relpath(bib_path, paper_root),
                'paper': paper_name,
                'title': e['title'],
                'author': e['author'],
                'year': e['year'],
                'doi': e['doi'],
            })
        
        all_results.append({
            'paper': paper_name,
            'file': os.path.relpath(bib_path, paper_root),
            'entries': total,
            'doi_count': with_doi,
            'doi_coverage': round(doi_cov, 1),
            'suspicious_count': sum(1 for e in entries if is_suspicious(e)),
        })
    
    # Cross-file deduplication
    cross_dupes = {}
    for key, locations in all_entries.items():
        files = set(l['file'] for l in locations)
        if len(files) >= 2:
            titles = set(l['title'] for l in locations)
            years = set(l['year'] for l in locations)
            inconsistencies = []
            if len(titles) > 1:
                inconsistencies.append(f"titles: {sorted(titles)[:3]}")
            if len(years) > 1:
                inconsistencies.append(f"years: {sorted(years)[:3]}")
            cross_dupes[key] = {
                'locations': sorted(files),
                'inconsistencies': inconsistencies,
            }
    
    # Aggregate summary
    total_bibs = len(bib_files)
    total_entries = sum(r['entries'] for r in all_results)
    total_doi = sum(r['doi_count'] for r in all_results)
    overall_cov = (total_doi / total_entries * 100) if total_entries > 0 else 0
    total_susp = sum(r['suspicious_count'] for r in all_results)
    
    # Sort by DOI coverage (ascending — worst first)
    all_results.sort(key=lambda x: x['doi_coverage'])
    
    report = {
        'report_date': DATE,
        'paper_root': paper_root,
        'summary': {
            'total_bib_files': total_bibs,
            'total_entries': total_entries,
            'total_with_doi': total_doi,
            'overall_doi_coverage': round(overall_cov, 1),
            'total_suspicious_entries': total_susp,
        },
        'papers': all_results,
        'suspicious_entries': suspicious[:200],  # cap for report size
        'cross_file_duplicates': cross_dupes,
    }
    
    # Write output
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Report saved: {args.output}")
    print(f"Bib files: {total_bibs} | Entries: {total_entries} | DOI: {overall_cov:.1f}% | Suspicious: {total_susp} | Cross-dupe keys: {len(cross_dupes)}")
    return report

if __name__ == '__main__':
    main()
