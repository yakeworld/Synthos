#!/usr/bin/env python3
"""
Unified Paper Pipeline Audit Scan — v1.0
Produces: outputs/researchaudit/unified-scan-<date>.json

Scans outputs/papers/ and outputs/_knowledge_only/ for:
  - Bib file inventory (count, entries, DOI coverage, suspicious count)
  - Per-paper bib analysis (entries, DOI, coverage, suspicious)
  - Cross-file duplicate keys with inconsistency detection
  - Suspicious entry classification
  - Paper state.json metrics (quality_score, gate_status)

Class of tasks: Paper pipeline integrity auditing, reference health monitoring.
Derived from: 2026-06-29 cron job scan methodology.
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime


def parse_bib_entries(bib_path):
    """Parse a .bib file and return list of entry dicts."""
    if not os.path.isfile(bib_path):
        return []
    
    content = open(bib_path, 'r', encoding='utf-8', errors='replace').read()
    entries = []
    
    # Match @type{key, ...} blocks
    pattern = r'@(article|book|inbook|incollection|inproceedings|misc|phdthesis|proceedings|techreport|unpublished)\s*\{([^,]+),'\n\s*\{(?:.*?)\n.*?^\}'
    
    # Simple entry splitter
    in_entry = False
    current_entry = ''
    brace_count = 0
    entry_type = ''
    entry_key = ''
    
    for line in content.split('\n'):
        if not in_entry:
            m = re.match(r'\s*@(\w+)\s*\{([^,]+),', line, re.IGNORECASE)
            if m:
                in_entry = True
                entry_type = m.group(1).lower()
                entry_key = m.group(2).strip()
                current_entry = line + '\n'
                brace_count = line.count('{') + line.count('[') - line.count('}') - line.count(']')
                if brace_count <= 0:
                    in_entry = False
                    entries.append({
                        'type': entry_type,
                        'key': entry_key,
                        'content': current_entry,
                    })
        else:
            current_entry += line + '\n'
            brace_count += line.count('{') + line.count('[') - line.count('}') - line.count(']')
            if brace_count <= 0:
                in_entry = False
                entries.append({
                    'type': entry_type,
                    'key': entry_key,
                    'content': current_entry,
                })
    
    return entries


def count_dois(entries):
    """Count entries that contain a DOI."""
    doi_count = 0
    for e in entries:
        if 'doi' in e['content'].lower() or 'isbn' not in e['content'].lower() and re.search(r'10\.\d{4,}/', e['content']):
            doi_count += 1
    return doi_count


def classify_suspicious(entries):
    """Classify suspicious entries by type."""
    suspicious = []
    
    for e in entries:
        issues = []
        
        # Check for arXiv without ID
        content_lower = e['content'].lower()
        if 'arxiv' in content_lower or 'arxiv.org' in content_lower:
            if not re.search(r'arxiv\.\d{4}\.\d{4,5}|arXiv:\d{4}\.\d{4,5}', e['content'], re.IGNORECASE):
                issues.append('arXiv preprint without arXiv:ID')
        
        # Check for missing author
        if re.search(r'author\s*=\s*\{\s*\}', e['content'], re.IGNORECASE):
            issues.append('missing author field')
        
        # Check for URL in year field
        year_m = re.search(r'\byear\s*=\s*\{([^}]+)\}', e['content'])
        if year_m:
            year_val = year_m.group(1).strip()
            if re.match(r'https?://', year_val):
                issues.append(f'URL in year field: {year_val}')
        
        # Check for non-standard publisher names in author
        for keyword in ['CASIA', 'MMU', 'UCI', 'arXiv', 'Google Scholar', 'Wiley', 'Springer', 'IEEE']:
            if re.search(rf'author\s*=\s*\{(?:\s*{keyword}\s*,\s*)*{keyword}\s*\}}', e['content'], re.IGNORECASE):
                if 'missing author field' not in issues:
                    issues.append(f'institution listed as author: {keyword}')
        
        if issues:
            suspicious.append({
                'key': e['key'],
                'type': issues,
            })
    
    return suspicious


def find_cross_file_duplicates(all_entries):
    """Find keys that appear in multiple paper directories."""
    key_locations = defaultdict(list)
    
    for paper, entries in all_entries.items():
        for e in entries:
            key_locations[e['key']].append({
                'paper': paper,
                'file': e.get('file', ''),
                'content': e.get('content', ''),
            })
    
    duplicates = {}
    for key, locations in key_locations.items():
        papers = set(loc['paper'] for loc in locations)
        if len(papers) > 1:
            duplicates[key] = locations
    
    return duplicates


def check_cross_file_inconsistencies(duplicates):
    """Check cross-file duplicates for title/year inconsistencies."""
    results = {}
    
    for key, locations in duplicates.items():
        papers = set(loc['paper'] for loc in locations)
        if len(papers) <= 1:
            continue
        
        titles = []
        years = []
        for loc in locations:
            title_m = re.search(r'title\s*=\s*\{([^}]+)\}', loc['content'], re.IGNORECASE)
            year_m = re.search(r'\byear\s*=\s*\{([^}]+)\}', loc['content'], re.IGNORECASE)
            if title_m:
                titles.append(title_m.group(1).strip())
            if year_m:
                years.append(year_m.group(1).strip())
        
        issues = []
        if titles and len(set(titles)) > 1:
            issues.append(f'titles: {titles}')
        if years and len(set(years)) > 1:
            issues.append(f'years: {years}')
        
        if issues:
            results[key] = {
                'locations': [f"{l['paper']}/{l['file']}" for l in locations],
                'inconsistencies': issues,
            }
    
    return results


def scan_papers(paper_root):
    """Scan all paper directories for bib files and state."""
    results = []
    all_entries = {}
    
    if not os.path.isdir(paper_root):
        return results, all_entries
    
    for name in sorted(os.listdir(paper_root)):
        paper_dir = os.path.join(paper_root, name)
        if not os.path.isdir(paper_dir):
            continue
        
        # Find all .bib files in this paper
        bib_files = []
        for root, dirs, files in os.walk(paper_dir):
            for f in files:
                if f.endswith('.bib'):
                    bib_files.append(os.path.relpath(os.path.join(root, f), paper_root))
        
        if not bib_files:
            continue
        
        paper_results = []
        total_entries = 0
        total_doi = 0
        total_suspicious = 0
        
        for rel_path in bib_files:
            full_path = os.path.join(paper_dir, rel_path)
            entries = parse_bib_entries(full_path)
            dois = count_dois(entries)
            suspicious = classify_suspicious(entries)
            
            entry_count = len(entries)
            doi_coverage = round(dois / entry_count * 100, 1) if entry_count > 0 else 0
            
            paper_results.append({
                'paper': name,
                'file': rel_path,
                'entries': entry_count,
                'doi_count': dois,
                'doi_coverage': doi_coverage,
                'suspicious_count': len(suspicious),
            })
            
            total_entries += entry_count
            total_doi += dois
            total_suspicious += len(suspicious)
            
            all_entries.setdefault(name, []).extend([
                {**e, 'file': rel_path} for e in entries
            ])
        
        if paper_results:
            results.append({
                'paper_name': name,
                'total_entries': total_entries,
                'total_doi': total_doi,
                'overall_coverage': round(total_doi / total_entries * 100, 1) if total_entries > 0 else 0,
                'suspicious_count': total_suspicious,
                'bib_files': paper_results,
            })
    
    return results, all_entries


def scan_state_json(paper_root):
    """Scan state.json files for quality metrics."""
    state_data = {}
    
    if not os.path.isdir(paper_root):
        return state_data
    
    for name in sorted(os.listdir(paper_root)):
        state_file = os.path.join(paper_root, name, 'state.json')
        if not os.path.isfile(state_file):
            continue
        try:
            d = json.load(open(state_file))
            state_data[name] = {
                'quality_score': d.get('quality_score', 'N/A'),
                'gate_status': d.get('gate_status', 'N/A'),
            }
        except:
            pass
    
    return state_data


def main():
    paper_root = sys.argv[1] if len(sys.argv) > 1 else '/media/yakeworld/sda2/Synthos/outputs/papers'
    
    bib_results, all_entries = scan_papers(paper_root)
    state_data = scan_state_json(paper_root)
    duplicates = find_cross_file_duplicates(all_entries)
    inconsistencies = check_cross_file_inconsistencies(duplicates)
    
    total_bib_files = sum(len(r['bib_files']) for r in bib_results)
    total_entries = sum(r['total_entries'] for r in bib_results)
    total_doi = sum(r['total_doi'] for r in bib_results)
    total_suspicious = sum(r['suspicious_count'] for r in bib_results)
    overall_doi = round(total_doi / total_entries * 100, 1) if total_entries > 0 else 0
    
    report = {
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'paper_root': paper_root,
        'summary': {
            'total_bib_files': total_bib_files,
            'total_entries': total_entries,
            'total_with_doi': total_doi,
            'overall_doi_coverage': overall_doi,
            'total_suspicious_entries': total_suspicious,
        },
        'papers': sum([r['bib_files'] for r in bib_results], []),
        'state_data': state_data,
        'cross_file_duplicates': inconsistencies,
        'cross_file_duplicate_count': len(duplicates),
    }
    
    out_dir = os.path.join(paper_root.rsplit('/', 1)[0], 'researchaudit')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'unified-scan-{datetime.now().strftime("%Y-%m-%d")}.json')
    
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Bib files: {total_bib_files} | Entries: {total_entries} | DOI: {overall_doi}% | Suspicious: {total_suspicious} | Cross-dupe keys: {len(duplicates)}")
    print(f"Scan complete: {out_path}")
    
    return report


if __name__ == '__main__':
    main()
