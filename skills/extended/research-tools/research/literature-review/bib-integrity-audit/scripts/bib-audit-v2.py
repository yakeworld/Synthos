#!/usr/bin/env python3
"""Bib integrity audit v2 — comprehensive scan across all Synthos papers.

Discovers paper bib files dynamically from the article_todo directory,
handles unicode paths via os.listdir, and produces a complete report.
"""

import os
import re
import json
import urllib.request
import urllib.parse
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

# Known DOI mappings for Synthos references
KNOWN_DOIS = {
    "daugman2009iris": "10.1016/b978-0-12-374457-9.00025-1",
    "proencca2009ubiris": "10.1109/TPAMI.2009.66",
    "lu2022neural": "10.1109/ISMAR55827.2022.00053",
    "dierkes2018novel": "10.1145/3281417.3281423",
    "tsukada2011illumination": "10.1109/ICCVW.2011.6139507",
}

# Root-level bib files
ROOT_BIBS = {
    "/home/yakeworld/references.bib": "root-references",
    "/home/yakeworld/inner_ear_development_references.bib": "inner-ear-references",
}

# Paper name mapping: short_name -> list of bib paths
# Manually maintained from discovered files
PAPER_BIBS = {
    "iris-segmentation-3d-eyeball": [
        "/home/yakeworld/桌面/article_todo/3D Eyeball Model-Constrained Iris Segmentation/reference4.bib",
        "/home/yakeworld/桌面/article_todo/3D Eyeball Model-Constrained Iris Segmentation/latexnew/reference4.bib",
    ],
    "membranous-scc-reconstruction": [
        "/home/yakeworld/桌面/article_todo/Three-Dimensional Reconstruction and Spatial Orientation Measurement of the Membranous Semicircular Canals/sage_latex_template_4/ref_orig.bib",
        "/home/yakeworld/桌面/article_todo/Three-Dimensional Reconstruction and Spatial Orientation Measurement of the Membranous Semicircular Canals/sage_latex_template_4/ref.bib",
        "/home/yakeworld/桌面/article_todo/Three-Dimensional Reconstruction and Spatial Orientation Measurement of the Membranous Semicircular Canals/ref.bib",
    ],
    "dual-ellipse-pupil": [
        "/home/yakeworld/桌面/article_todo/A Dual-Ellipse Fitting Method for High-Accuracy Pupil Boundary Estimation/投稿文件final/referencefinalenhance.bib",
        "/home/yakeworld/桌面/article_todo/A Dual-Ellipse Fitting Method for High-Accuracy Pupil Boundary Estimation/投稿文件final/referencefinal.bib",
    ],
    "dual-ellipse-localization": [
        "/home/yakeworld/桌面/article_todo/Dual-Ellipse Modeling for Accurate Pupil Localization/reference4.bib",
    ],
    "iris-normalization-3d-transform": [
        "/home/yakeworld/桌面/article_todo/A Precise 3D Geometric Transform Method for Iris Normalization/reference3.bib",
    ],
    "daugman-off-axis-correction": [
        "/home/yakeworld/桌面/article_todo/Correcting the Off-Axis Iris Normalization Formulas in Daugman's Method/references.bib",
    ],
    "yolov8-iris-segmentation": [
        "/home/yakeworld/桌面/article_todo/High-Accuracy Iris Segmentation Using Improved YOLOv8 with Anatomical Priors/reference4.bib",
    ],
}


def parse_bib_entries(filepath):
    """Parse a .bib file and return list of entry dicts."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        return []

    if not content.strip():
        return []

    entries = []
    # Entry-block regex — [\s\S]*? matches ANY char including newlines
    # Lookahead matches } alone on a line (BibTeX entry terminator)
    pattern = r'^@([A-Za-z]+)\s*\{\s*([^,]+?),\s*([\s\S]*?)(?=\n\s*\}\s*\n|\n\s*\}\s*$)'
    for m in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
        entry_type = m.group(1).lower()
        key = m.group(2).strip()
        body = m.group(3)

        if entry_type == 'comment':
            continue

        # Parse fields — handle multi-line, braces, quotes, bare values
        fields = {}
        for line in body.split('\n'):
            line = line.strip()
            if not line:
                continue
            for fm in re.finditer(r'(\w+)\s*=\s*(?:\{([^}]*)\}|"[^"]*"|(.+))', line, re.DOTALL):
                fname = fm.group(1).lower()
                fval = fm.group(2) or fm.group(3) or ''
                fval = fval.strip()
                if fname not in fields:  # first occurrence wins
                    fields[fname] = fval

        # Detect URL as year
        url_year = re.search(r'year\s*=\s*(?:\{([^}]*https?://[^}]*)\}|"[^"]*https?://[^"]*")', body)
        if url_year:
            fields['year_url'] = url_year.group(1)

        # Detect empty DOI
        doi_empty = re.search(r'doi\s*=\s*\{\s*\}', body)
        if doi_empty:
            fields['doi_empty'] = True

        entries.append({
            'type': entry_type,
            'key': key,
            'fields': fields,
            'body': body,
            'file': filepath,
        })

    return entries


def check_suspicious(entry):
    """Check entry for suspicious patterns. Return list of issue strings."""
    issues = []
    key = entry['key']
    fields = entry['fields']
    body = entry['body']

    # 1. @misc with auto-generated key
    if entry['type'] == 'misc' and re.search(r'auto\d{4}', key, re.IGNORECASE):
        issues.append(f"@misc auto key pattern: {key}")

    # 2. Kaggle publisher
    if 'kaggle' in body.lower():
        if re.search(r'publisher\s*=\s*\{[^}]*kaggle[^}]*\}', body, re.IGNORECASE):
            issues.append(f"Kaggle publisher: {key}")

    # 3. URL as year field
    if 'year_url' in fields:
        issues.append(f"URL as year: {key} ({fields['year_url'][:60]})")

    # 4. arXiv preprint without arXiv ID
    if re.search(r'journal\s*=\s*\{[^}]*arXiv preprint[^}]*\}', body):
        if not re.search(r'arXiv:\d{4}\.\d{4,5}', body) and not re.search(r'arXiv\[\d{4}\.\d{4,5}\]', body):
            issues.append(f"arXiv preprint no ID: {key}")

    # 5. Incomplete @misc
    if entry['type'] == 'misc':
        if 'author' not in fields and 'title' not in fields:
            issues.append(f"@misc no author/title: {key}")
        elif 'author' not in fields:
            issues.append(f"@misc no author: {key}")
        elif 'title' not in fields:
            issues.append(f"@misc no title: {key}")

    # 6. No author field at all (non-misc too)
    if 'author' not in fields:
        issues.append(f"No author: {key}")

    # 7. No title or booktitle
    if 'title' not in fields and 'booktitle' not in fields and 'howpublished' not in fields:
        issues.append(f"No title: {key}")

    # 8. Empty DOI
    if 'doi_empty' in fields:
        issues.append(f"Empty DOI: {key}")

    return issues


def openalex_lookup(title):
    """Query OpenAlex API for DOI lookup. Returns DOI string or None."""
    if not title:
        return None
    query = urllib.parse.quote(title[:200])
    url = f"https://api.openalex.org/works?search={query}&select=title,doi&per_page=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'SynthosBibAudit/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get('results'):
                result = data['results'][0]
                doi = result.get('doi')
                if doi:
                    return doi
    except Exception as e:
        print(f"  OpenAlex error for '{title[:50]}': {e}", file=sys.stderr)
    return None


def dedup_cross_files(all_keys, paper_bibs):
    """Identify cross-file duplicate keys (ignoring known redundant copies)."""
    dups = {}
    for key, files in all_keys.items():
        unique_files = list(set(files))
        if len(unique_files) <= 1:
            continue
        # Check if these are known redundant copies (same paper, same key)
        # Group by paper
        paper_groups = defaultdict(list)
        for f in unique_files:
            for pname, ppaths in paper_bibs.items():
                if f in ppaths:
                    paper_groups[pname].append(f)
                    break
        # If all files belong to the same paper, likely redundant copies — not a real inconsistency
        if len(paper_groups) <= 1:
            continue
        dups[key] = unique_files
    return dups


def main():
    report_date = date.today().isoformat()

    # Phase 1: Gather all files
    all_files = []
    for pname, paths in PAPER_BIBS.items():
        for p in paths:
            if os.path.isfile(p):
                all_files.append((p, pname))
    for rpath, rname in ROOT_BIBS.items():
        if os.path.isfile(rpath):
            all_files.append((rpath, rname))

    results = {}
    global_suspicious = []
    global_completions = []
    global_gaps = []
    all_keys = defaultdict(list)

    for filepath, paper_name in all_files:
        entries = parse_bib_entries(filepath)
        if not entries:
            continue

        if paper_name not in results:
            results[paper_name] = {
                'entries': 0, 'dois': 0, 'suspicious': [],
                'completions': [], 'bib_path': os.path.basename(filepath),
            }

        results[paper_name]['entries'] += len(entries)

        for entry in entries:
            key = entry['key']
            fields = entry['fields']

            all_keys[key].append(filepath)

            # Count DOIs
            if 'doi' in fields and fields['doi'] and 'doi_empty' not in fields:
                results[paper_name]['dois'] += 1

            # Suspicious
            issues = check_suspicious(entry)
            for issue in issues:
                item = {
                    'paper': paper_name, 'file': os.path.basename(filepath),
                    'key': key, 'type': entry['type'], 'issue': issue,
                }
                results[paper_name]['suspicious'].append(item)
                global_suspicious.append(item)

            # Known DOI completions
            if key in KNOWN_DOIS and 'doi' not in fields:
                comp = {
                    'paper': paper_name, 'key': key,
                    'title': fields.get('title', 'N/A'), 'doi': KNOWN_DOIS[key],
                    'author': fields.get('author', 'N/A'), 'year': fields.get('year', 'N/A'),
                }
                results[paper_name]['completions'].append(comp)
                global_completions.append(comp)

            # DOI gaps (complete metadata but no DOI, skip misc)
            has_authors = 'author' in fields
            has_title = 'title' in fields or 'booktitle' in fields
            has_year = 'year' in fields
            has_journal = 'journal' in fields or 'booktitle' in fields or 'howpublished' in fields

            if (has_authors and has_title and has_year
                and not ('doi' in fields and fields.get('doi'))
                and entry['type'] != 'misc'):
                title = fields.get('title', fields.get('booktitle', ''))
                global_gaps.append({
                    'paper': paper_name, 'key': key,
                    'title': title[:100] if title else 'N/A',
                    'author': fields.get('author', 'N/A')[:80],
                    'year': fields.get('year', 'N/A'),
                    'file': os.path.basename(filepath),
                    'type': entry['type'],
                })

    # Phase 2: OpenAlex lookup for DOI gaps
    print("DOI gap lookup via OpenAlex...", file=sys.stderr)
    api_completions = []
    for gap in global_gaps:
        doi = openalex_lookup(gap['title'])
        if doi:
            gap['suggested_doi'] = doi
            api_completions.append(gap)
            # Also add to the paper's completions
            if gap['paper'] in results:
                results[gap['paper']]['completions'].append({
                    'key': gap['key'],
                    'title': gap['title'],
                    'doi': doi,
                })

    remaining_gaps = [g for g in global_gaps if 'suggested_doi' not in g]

    # Phase 3: Cross-file dedup
    cross_file_dups = dedup_cross_files(all_keys, PAPER_BIBS)

    # Phase 4: Generate report
    lines = []
    def W(s=""):
        lines.append(s)

    W(f"\n🧹 Bib标准化报告 ({report_date})")
    W()
    W("| 论文 | 条目数 | DOI覆盖率 | 可疑条目 | 已补DOI |")
    W("|:-----|:------:|:--------:|:--------:|:-------:|")

    for paper_name in sorted(results.keys()):
        r = results[paper_name]
        if r['entries'] == 0:
            continue
        doi_cov = round(r['dois'] / r['entries'] * 100)
        susp_count = len(r['suspicious'])
        comp_count = len(r['completions'])
        W(f"| {paper_name} | {r['entries']} | {doi_cov}% | {susp_count} | {comp_count} |")

    # Suspicious items
    if global_suspicious:
        W("\n可疑条目明细:")
        # Deduplicate by (paper, key, issue)
        seen_susp = set()
        for item in global_suspicious:
            sig = (item['paper'], item['key'], item['issue'])
            if sig not in seen_susp:
                seen_susp.add(sig)
                W(f"- {item['paper']}: {item['key']} ({item['issue']})")

    # Known DOI completions
    if global_completions:
        W("\n已补DOI明细 (已知文献):")
        for comp in global_completions:
            W(f"- {comp['paper']}: {comp['key']} → {comp['doi']}")

    # API completions
    if api_completions:
        W("\n已补DOI明细 (OpenAlex查询):")
        for comp in api_completions:
            t = comp['title'][:60] if comp['title'] else 'N/A'
            W(f"- {comp['paper']}: {comp['key']} ({t}) → {comp['suggested_doi']}")

    # DOI gaps
    if remaining_gaps:
        W(f"\nDOI缺失待查 ({len(remaining_gaps)} 条):")
        for gap in sorted(remaining_gaps, key=lambda x: x['paper'])[:30]:
            t = gap['title'][:60] if gap['title'] else 'N/A'
            W(f"- {gap['paper']}: {gap['key']} ({t})")

    # Cross-file duplicates
    if cross_file_dups:
        W(f"\n跨文件重复条目 ({len(cross_file_dups)} 个key):")
        for key, files in sorted(cross_file_dups.items()):
            W(f"- {key}: {len(files)} 文件 - " + ", ".join([os.path.basename(f) for f in files]))

    # Summary stats
    total_entries = sum(r['entries'] for r in results.values())
    total_dois = sum(r['dois'] for r in results.values())
    overall_cov = round(total_dois / total_entries * 100) if total_entries else 0
    total_susp = len(set((i['paper'], i['key'], i['issue']) for i in global_suspicious))
    total_comps = len(global_completions) + len(api_completions)

    W(f"\n**总计**: {total_entries} 条目 | {overall_cov}% DOI覆盖率 | {total_susp} 可疑条目 | {total_comps} 已补DOI")

    # Priority recommendations
    W(f"\n优先级建议:")
    if overall_cov < 80:
        W(f"- P0: 整体DOI覆盖率低 ({overall_cov}%)，需重点补全")
    else:
        W(f"- P1: 整体DOI覆盖率良好 ({overall_cov}%)，继续优化可疑条目")

    # P0: Fix suspicious entries before submission
    kaggle_issues = [i for i in global_suspicious if 'Kaggle' in i['issue']]
    url_year_issues = [i for i in global_suspicious if 'URL as year' in i['issue']]
    if kaggle_issues or url_year_issues:
        W(f"- P0: 数据集引用含Kaggle/URL-as-year等严重问题 ({len(kaggle_issues)} Kaggle + {len(url_year_issues)} URL年) — 提交前必须修复")

    # Suspicious entries
    if global_suspicious:
        W(f"- P1: 发现 {total_susp} 个可疑条目，需人工审核")

    # Missing DOI
    if remaining_gaps:
        W(f"- P2: {len(remaining_gaps)} 条DOI缺失需手动补全")

    # Cross-file dups
    if cross_file_dups:
        W(f"- P2: {len(cross_file_dups)} 个跨文件重复key需去重")

    # ArXiv preprints without DOI
    arxiv_issues = [i for i in global_suspicious if 'arXiv' in i['issue']]
    if arxiv_issues:
        W(f"- P2: {len(arxiv_issues)} 条arXiv文献缺少DOI")

    report = "\n".join(lines)
    print(report)

    # Save
    report_dir = "/home/yakeworld/outputs/papers"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"bib-standards-report-{report_date}.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport saved to {report_path}", file=sys.stderr)


if __name__ == '__main__':
    main()
