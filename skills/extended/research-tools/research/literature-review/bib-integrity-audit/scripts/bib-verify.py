#!/usr/bin/env python3
"""
DOI Verification Script for Bib Files
======================================
Verifies DOI entries via Crossref API, searches for missing DOIs via
Semantic Scholar and Crossref, and generates a comprehensive verification report.

Usage:
    python3 bib-verify.py <bib-file> [--output report.md] [--verbose]

Requirements:
    - requests library
    - Python 3.6+
"""
import re
import sys
import json
import argparse
import time
from collections import defaultdict

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Install with: pip install requests")
    sys.exit(1)


def parse_bib_file(bib_path):
    """Parse a .bib file and extract all entries with their metadata."""
    entries = []
    current_key = None
    current_data = {}

    with open(bib_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for line in content.split('\n'):
        # Match entry start
        match = re.match(r'@(?:[a-zA-Z]+)\{([^,}]+),', line)
        if match:
            if current_key:
                entries.append(current_data)
            current_key = match.group(1).strip()
            current_data = {
                'key': current_key,
                'doi': None,
                'title': None,
                'authors': None,
                'year': None,
                'venue': None,
                'entry_type': re.match(r'@([a-zA-Z]+)', line).group(1)
            }

        # Extract fields
        for field in ['doi', 'title', 'authors', 'year', 'journal', 'booktitle', 'publisher']:
            pattern = rf'{field}\s*=\s*\{{([^}}]+)\}'
            m = re.search(pattern, line)
            if m:
                if field == 'entry_type':
                    continue
                current_data[field] = m.group(1).strip()

    # Don't forget last entry
    if current_key:
        entries.append(current_data)

    return entries


def verify_doi_crossref(doi):
    """Verify a DOI via Crossref API."""
    doi_clean = doi.replace('\\_', '_')
    url = f"https://api.crossref.org/works/{requests.utils.quote(doi_clean, safe=':/')}"
    try:
        resp = requests.get(url, timeout=10, headers={
            'User-Agent': 'synthos-audit/1.0 (yakeworld@wmu.edu.cn)'
        })
        if resp.status_code == 200:
            data = resp.json()
            if 'message' in data:
                msg = data['message']
                title = msg.get('title', ['N/A'])[0]
                authors = ', '.join([
                    a.get('given', '') + ' ' + a.get('family', '')
                    for a in msg.get('author', [])
                ])
                year = str(
                    msg.get('published-print', {}).get('date-parts', [[None]])[0][0]
                ) or 'N/A'
                return {
                    'status': 'verified',
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'publisher': msg.get('publisher', 'N/A'),
                    'type': msg.get('type', 'N/A')
                }
        return {'status': 'failed', 'reason': f'HTTP {resp.status_code}'}
    except Exception as e:
        return {'status': 'error', 'reason': str(e)}


def search_semantic_scholar(title, author=None):
    """Search Semantic Scholar for a paper."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        'query': title[:100],
        'limit': 3,
        'fields': 'title,authors,year,externalIds'
    }
    if author:
        params['query.author'] = author[:50]
    try:
        resp = requests.get(url, timeout=15, params=params, headers={
            'User-Agent': 'synthos-audit/1.0 (yakeworld@wmu.edu.cn)'
        })
        if resp.status_code == 200:
            data = resp.json()
            return data.get('data', [])
        return []
    except Exception as e:
        return []


def search_crossref(title, author=None, year=None):
    """Search Crossref for a paper by title."""
    url = "https://api.crossref.org/works"
    params = {
        'query.title': title[:100],
        'rows': 3,
        'mailto': 'yakeworld@wmu.edu.cn'
    }
    if author:
        params['query.author'] = author[:50]
    if year:
        params['from-pub-date'] = year
        params['to-pub-date'] = year
    try:
        resp = requests.get(url, timeout=10, params=params)
        if resp.status_code == 200:
            return resp.json()['message'].get('items', [])
        return []
    except Exception as e:
        return []


def classify_entry(entry):
    """Classify an entry to determine if it should have a DOI."""
    if entry['doi']:
        return 'has_doi'

    # Check if it's an arXiv preprint
    if 'arXiv' in str(entry.get('journal', '')) or 'arXiv' in str(entry.get('title', '')):
        return 'arxiv_preprint'

    # Check if it's a dataset
    journal = str(entry.get('journal', '')).lower()
    title = str(entry.get('title', '')).lower()
    publisher = str(entry.get('publisher', '')).lower()
    if any(x in journal + title + publisher for x in [
        'dataset', 'database', 'kaggle', 'casia', 'ubiris', 'openeds'
    ]):
        return 'dataset'

    # Check if it's a preprint
    if 'preprint' in str(entry.get('journal', '')).lower():
        return 'preprint'

    # Default: should have DOI
    return 'should_have_doi'


def generate_report(entries, results, verbose=False):
    """Generate a markdown verification report."""
    total = len(entries)
    with_doi = sum(1 for e in entries if e['doi'])
    without_doi = total - with_doi

    # Categorize results
    verified = sum(1 for r in results if r.get('status') == 'verified')
    failed = sum(1 for r in results if r.get('status') in ['failed', 'error'])
    not_checked = [r for r in results if r.get('status') is None]

    # Categorize missing DOIs
    arxiv_entries = []
    dataset_entries = []
    should_have_doi = []

    for e in entries:
        if not e['doi']:
            entry_type = classify_entry(e)
            if entry_type == 'arxiv_preprint':
                arxiv_entries.append(e)
            elif entry_type == 'dataset':
                dataset_entries.append(e)
            else:
                should_have_doi.append(e)

    report = []
    report.append("# DOI Verification Report")
    report.append("")
    report.append("## Summary")
    report.append(f"- Total entries: {total}")
    report.append(f"- With DOI: {with_doi} ({100.0 * with_doi / total:.1f}%)")
    report.append(f"- Without DOI: {without_doi} ({100.0 * without_doi / total:.1f}%)")
    report.append(f"- Verified via Crossref: {verified}")
    report.append(f"- Verification failed: {failed}")
    report.append("")

    if should_have_doi:
        report.append("## Entries That Should Have DOI")
        for e in should_have_doi:
            report.append(f"- **{e['key']}**: {e.get('title', 'N/A')}")
        report.append("")

    if arxiv_entries:
        report.append("## arXiv Preprints (No DOI Expected)")
        for e in arxiv_entries:
            report.append(f"- **{e['key']}**: {e.get('title', 'N/A')}")
        report.append("")

    if dataset_entries:
        report.append("## Datasets (No DOI Expected)")
        for e in dataset_entries:
            report.append(f"- **{e['key']}**: {e.get('title', 'N/A')}")
        report.append("")

    if results:
        report.append("## Verification Details")
        for r in results:
            if r.get('key') and r.get('status') in ['verified', 'failed', 'error']:
                status_icon = {'verified': '✅', 'failed': '❌', 'error': '⚠️'}.get(r['status'], '?')
                report.append(f"- {status_icon} **{r['key']}**: {r.get('status', 'N/A')}")
                if verbose and r.get('reason'):
                    report.append(f"  - Reason: {r['reason']}")
        report.append("")

    return '\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description='Verify DOI entries in a BibTeX file')
    parser.add_argument('bib_file', help='Path to the .bib file')
    parser.add_argument('--output', '-o', help='Output file path (default: stdout)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    args = parser.parse_args()

    entries = parse_bib_file(args.bib_file)
    results = []

    print(f"Parsed {len(entries)} entries from {args.bib_file}")

    # Verify entries with DOI
    for entry in entries:
        if entry['doi']:
            result = verify_doi_crossref(entry['doi'])
            result['key'] = entry['key']
            results.append(result)
            if args.verbose:
                status = {'verified': '✅', 'failed': '❌', 'error': '⚠️'}.get(result.get('status', ''), '?')
                print(f"  {status} {entry['key']}: {result.get('status', 'N/A')}")
            time.sleep(0.1)  # Rate limiting

    # Generate report
    report = generate_report(entries, results, args.verbose)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\nReport written to {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()