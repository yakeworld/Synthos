#!/usr/bin/env python3
"""
Synthos Unified Paper Scan v2 — D8 + D10a + Bib Standardization
Scans all papers in outputs/papers/, checks citation/bib consistency,
validates references, and generates JSON + HTML reports.

Handles three reference formats:
1. Inline \bibitem{} in thebibliography of .tex files
2. Separate .bib files (BibTeX format)
3. Numbered markdown references in section files

Usage: python3 unified-scan.py
Output: outputs/researchaudit/unified-scan-YYYY-MM-DD.{json,html}
"""

import os
import re
import json
import sys
from datetime import datetime

PAPERS_ROOT = "/media/yakeworld/sda2/Synthos/outputs/papers"
AUDIT_DIR = "/media/yakeworld/sda2/Synthos/outputs/researchaudit"
EXCLUDE_DIRS = {"knowledge-index", "research", "submissions", "_archive", "_knowledge_only", "_template", "_archive_scripts", "_templates", "new-queue"}


def get_paper_dirs():
    papers = []
    for entry in sorted(os.listdir(PAPERS_ROOT)):
        p = os.path.join(PAPERS_ROOT, entry)
        if os.path.isdir(p) and entry not in EXCLUDE_DIRS:
            papers.append(p)
    return papers


def find_tex_files(paper_dir):
    tex_files = []
    for root, dirs, files in os.walk(paper_dir):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", ".svn"}]
        for f in files:
            if f.endswith(".tex") and "paper.tex" in f:
                tex_files.append(os.path.join(root, f))
    return sorted(tex_files)


def find_bib_files(paper_dir):
    bib_files = []
    for root, dirs, files in os.walk(paper_dir):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", ".svn"}]
        for f in files:
            if f.endswith(".bib"):
                bib_files.append(os.path.join(root, f))
    return sorted(bib_files)


def extract_cites_from_tex(tex_path):
    try:
        with open(tex_path, 'r', errors='replace') as f:
            content = f.read()
        matches = re.findall(r'\\cite[pt]?[aA]?\{([^{]*)\}', content)
        keys = set()
        for m in matches:
            for k in m.split(','):
                k = k.strip()
                if k:
                    keys.add(k)
        return keys
    except Exception:
        return set()


def extract_bib_entries(bib_path):
    try:
        with open(bib_path, 'r', errors='replace') as f:
            content = f.read()
        pattern = r'@\w+\s*\{\s*([A-Za-z0-9_.:-]+)'
        matches = re.findall(pattern, content)
        return set(matches)
    except Exception:
        return set()


def check_cite_format(tex_path):
    issues = []
    try:
        with open(tex_path, 'r', errors='replace') as f:
            content = f.read()
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Empty cite
            if re.search(r'\\cite[pt]?[aA]?\{\s*\}', line):
                issues.append({"line": i, "type": "empty_cite", "content": line.strip()[:120]})
            # Check for suspicious placeholder keys
            for k in re.findall(r'\\cite[pt]?[aA]?\{([^{]*)\}', line):
                for part in k.split(','):
                    part = part.strip()
                    if re.match(r'^key\d*$', part, re.IGNORECASE) or part in ('REF', 'FIXME', 'TODO', '???'):
                        issues.append({"line": i, "type": "placeholder_key", "content": f"placeholder key: {part}"})
    except Exception:
        pass
    return issues


def extract_bibitem_keys(tex_path):
    """Extract \bibitem{key} keys from thebibliography environment."""
    keys = set()
    try:
        with open(tex_path, 'r', errors='replace') as f:
            content = f.read()
        matches = re.findall(r'\\bibitem\{([^}]*)\}', content)
        for m in matches:
            keys.add(m.strip())
    except Exception:
        pass
    return keys


def parse_bib_entry_fields(bib_path):
    entries = {}
    try:
        with open(bib_path, 'r', errors='replace') as f:
            content = f.read()
        # Skip Comment entries
        content = re.sub(r'@Comment\{[^\}]*\}', '', content)
        entry_pattern = r'(@\w+\{[^\n,\s]+,[\s\S]*?)(?=\n\s*}\s*\n|\n\s*}\s*$|\n@[A-Za-z]+\s*\{)'
        for match in re.finditer(entry_pattern, content):
            block = match.group(1)
            key_match = re.search(r'@\w+\s*\{\s*([A-Za-z0-9_.:-]+)', block)
            if key_match:
                key = key_match.group(1)
                entries[key] = {
                    "has_doi": bool(re.search(r'\bdoi\s*=', block, re.IGNORECASE)),
                    "has_year": bool(re.search(r'\byear\s*=', block, re.IGNORECASE)),
                    "has_authors": bool(re.search(r'\bauthor\s*=', block, re.IGNORECASE)),
                    "has_title": bool(re.search(r'\btitle\s*=', block, re.IGNORECASE)),
                    "has_journal": bool(re.search(r'\b(journal|journaltitle|booktitle|proceedings)\s*=', block, re.IGNORECASE)),
                    "entry_type": re.search(r'(@\w+)', block).group(1).lower() if re.search(r'(@\w+)', block) else "unknown"
                }
    except Exception:
        pass
    return entries


def check_numbered_refs(section_file):
    """Check if a file contains numbered markdown references."""
    try:
        with open(section_file, 'r', errors='replace') as f:
            content = f.read()
        matches = re.findall(r'^\[(\d+)\]\s+(.+)$', content, re.MULTILINE)
        return len(matches) > 0
    except Exception:
        return False


def scan_paper(paper_dir):
    paper_name = os.path.basename(paper_dir)
    result = {
        "name": paper_name,
        "path": os.path.relpath(paper_dir, PAPERS_ROOT),
        "tex_files": [],
        "bib_files": [],
        "health": "healthy",
        "warnings": [],
        "errors": [],
        "d8": {
            "score": 1.0,
            "total_cites": 0,
            "matched_cites": 0,
            "unmatched_cites_in_tex": [],
            "unused_in_bib": [],
            "bib_entries": 0
        },
        "d10a": {
            "format_issues": [],
            "all_cites_have_bib": True,
            "placeholder_keys_found": []
        },
        "bib_standardization": {
            "missing_doi": [],
            "missing_year": [],
            "missing_authors": [],
            "missing_title": [],
            "missing_journal": [],
            "entry_types": {},
            "total_entries": 0
        },
        "cite_details": [],
        "ref_format": "unknown"
    }

    # Find files
    tex_files = find_tex_files(paper_dir)
    result["tex_files"] = [os.path.relpath(tf, PAPERS_ROOT) for tf in tex_files]
    bib_files = find_bib_files(paper_dir)
    result["bib_files"] = [os.path.relpath(bf, PAPERS_ROOT) for bf in bib_files]

    if not tex_files:
        result["health"] = "unscannable"
        result["errors"].append("No paper.tex file found")
        return result

    # Check for numbered markdown refs
    has_numbered = False
    for tf in tex_files:
        for section_dir in ["06-references", "07-references"]:
            sec_path = os.path.join(paper_dir, section_dir)
            if os.path.isdir(sec_path):
                for f in os.listdir(sec_path):
                    if check_numbered_refs(os.path.join(sec_path, f)):
                        has_numbered = True
                        break

    # Check for bibitem_inline
    bibitem_keys = set()
    for tf in tex_files:
        bibitem_keys.update(extract_bibitem_keys(tf))

    # Extract citations from all tex files
    all_cites = set()
    cite_locations = []
    format_issues = []

    for tf in tex_files:
        cites = extract_cites_from_tex(tf)
        rel = os.path.relpath(tf, PAPERS_ROOT)
        for cite in sorted(cites):
            all_cites.add(cite)
            cite_locations.append({"key": cite, "file": rel})
        issues = check_cite_format(tf)
        format_issues.extend(issues)

    result["cite_details"] = cite_locations

    # Determine reference format
    formats = []
    if bibitem_keys and not bib_files:
        formats.append("bibitem_inline")
    elif bibitem_keys and bib_files:
        formats.append("separate_bib+bibitem_inline")
    elif bib_files and not bibitem_keys:
        formats.append("separate_bib")
    elif bibitem_keys and has_numbered:
        formats.append("bibitem_inline+numbered")
    elif bib_files and has_numbered:
        formats.append("separate_bib+numbered")
    else:
        formats.append("unknown")

    result["ref_format"] = "+".join(formats)

    # Extract bib entries
    all_bibs = set()
    bib_fields = {}
    for bf in bib_files:
        keys = extract_bib_entries(bf)
        all_bibs.update(keys)
        fields = parse_bib_entry_fields(bf)
        bib_fields.update(fields)

    # Combine all reference sources for D8 calculation
    all_refs = all_bibs | bibitem_keys
    result["d8"]["bib_entries"] = len(all_refs)

    matched = all_cites & all_refs
    unmatched = all_cites - all_refs
    unused = all_refs - all_cites

    d8_score = len(matched) / len(all_cites) if all_cites else 1.0

    result["d8"] = {
        "score": round(d8_score, 4),
        "total_cites": len(all_cites),
        "matched_cites": len(matched),
        "unmatched_cites_in_tex": sorted(list(unmatched)),
        "unused_in_bib": sorted(list(unused)),
        "bib_entries": len(all_refs)
    }

    # D10a
    placeholder_keys = []
    for issue in format_issues:
        if issue["type"] == "empty_cite":
            result["d10a"]["format_issues"].append({"type": "empty_cite", **issue})
        elif issue["type"] == "placeholder_key":
            result["d10a"]["format_issues"].append({"type": "placeholder_key", **issue})
            placeholder_keys.append(issue["content"])

    result["d10a"]["format_issues"].extend([
        {"type": "missing_bib_entry", "cite_key": k} for k in sorted(unmatched)
    ])
    result["d10a"]["all_cites_have_bib"] = len(unmatched) == 0
    result["d10a"]["placeholder_keys_found"] = placeholder_keys

    # Bib standardization
    missing_doi = [k for k, v in bib_fields.items() if not v.get("has_doi", False)]
    missing_year = [k for k, v in bib_fields.items() if not v.get("has_year", False)]
    missing_authors = [k for k, v in bib_fields.items() if not v.get("has_authors", False)]
    missing_title = [k for k, v in bib_fields.items() if not v.get("has_title", False)]
    missing_journal = [k for k, v in bib_fields.items() if not v.get("has_journal", False)]

    entry_types = {}
    for k, v in bib_fields.items():
        t = v.get("entry_type", "unknown")
        entry_types[t] = entry_types.get(t, 0) + 1

    result["bib_standardization"] = {
        "missing_doi": sorted(missing_doi),
        "missing_year": sorted(missing_year),
        "missing_authors": sorted(missing_authors),
        "missing_title": sorted(missing_title),
        "missing_journal": sorted(missing_journal),
        "entry_types": entry_types,
        "total_entries": len(bib_fields)
    }

    # Health status
    if not bib_files and not bibitem_keys and not has_numbered:
        result["health"] = "warning"
        result["errors"].append("No references found in any format")
    elif d8_score < 0.5:
        result["health"] = "critical"
        result["errors"].append(f"D8 score {d8_score:.2f} critically low ({len(unmatched)}/{len(all_cites)} unmatched)")
    elif d8_score < 0.85:
        result["health"] = "warning"
        result["warnings"].append(f"D8 score {d8_score:.2f} below 0.85 threshold ({len(unmatched)} unmatched)")

    if len(unmatched) > 5:
        result["warnings"].append(f"{len(unmatched)} unmatched cite keys")
    if len(missing_doi) > len(all_bibs) * 0.5 and all_bibs:
        result["warnings"].append(f"{len(missing_doi)}/{len(all_bibs)} entries missing DOI")
    if len(placeholder_keys) > 0:
        result["errors"].append(f"Placeholder keys found: {', '.join(placeholder_keys)}")

    return result


def generate_html_report(scan_results, report_path):
    total = len(scan_results)
    healthy = sum(1 for r in scan_results if r["health"] in ("healthy", "info"))
    warning = sum(1 for r in scan_results if r["health"] == "warning")
    critical = sum(1 for r in scan_results if r["health"] == "critical")
    unscannable = sum(1 for r in scan_results if r["health"] == "unscannable")

    valid_scores = [r["d8"]["score"] for r in scan_results if r["d8"]["score"] > 0]
    avg_d8 = round(sum(valid_scores) / len(valid_scores), 4) if valid_scores else 0

    health_colors = {"healthy": "#22c55e", "info": "#3b82f6", "warning": "#f59e0b", "critical": "#ef4444", "unscannable": "#6b7280"}

    rows = ""
    for r in sorted(scan_results, key=lambda x: ({"critical":0,"warning":1,"unscannable":2,"healthy":3,"info":3}.get(x["health"],4), -x["d8"]["score"])):
        c = health_colors.get(r["health"], "#6b7280")
        sc = "#22c55e" if r["d8"]["score"] >= 0.85 else ("#f59e0b" if r["d8"]["score"] >= 0.5 else "#ef4444")
        issues = ""
        for e in r.get("errors", []):
            issues += f'<span style="background:#fee2e2;color:#991b1b;padding:2px 6px;border-radius:3px;font-size:0.8em;margin:1px;">✗ {e}</span> '
        for w in r.get("warnings", []):
            issues += f'<span style="background:#fef3c7;color:#92400e;padding:2px 6px;border-radius:3px;font-size:0.8em;margin:1px;">⚠ {w}</span> '
        if not issues:
            issues = '<span style="background:#dcfce7;color:#166534;padding:2px 6px;border-radius:3px;font-size:0.8em;">✓ Clean</span>'
        rows += f'''<tr>
<td><strong>{r['name']}</strong></td>
<td><span style="display:inline-block;padding:3px 10px;border-radius:12px;color:white;font-size:0.85em;font-weight:bold;background:{c};">{r['health'].upper()}</span></td>
<td>{r['d8']['score']:.2f}</td>
<td>{r['d8']['total_cites']}</td>
<td>{r['d8']['bib_entries']}</td>
<td>{issues}</td>
</tr>'''

    details = ""
    for r in sorted(scan_results, key=lambda x: x["name"]):
        c = health_colors.get(r["health"], "#6b7280")
        d = r["d8"]
        b = r["bib_standardization"]
        details += f'''<details style="margin:5px 0;border:1px solid #e5e7eb;border-radius:6px;padding:10px;">
<summary style="cursor:pointer;font-weight:bold;color:#4361ee;">{r['name']} — {r['health'].upper()} | D8={d['score']:.2f} | {d['total_cites']} cites / {d['bib_entries']} bib | {r['ref_format']}</summary>
<table style="width:100%;border-collapse:collapse;margin:8px 0;">
<tr><th style="background:#4361ee;color:white;padding:6px;text-align:left;">Metric</th><th style="background:#4361ee;color:white;padding:6px;text-align:left;">Value</th></tr>
<tr><td style="padding:5px;border-bottom:1px solid #eee;">D8 Score</td><td style="padding:5px;border-bottom:1px solid #eee;">{d['score']:.4f} ({d['matched_cites']}/{d['total_cites']} matched)</td></tr>
<tr><td style="padding:5px;border-bottom:1px solid #eee;">Unmatched Cites</td><td style="padding:5px;border-bottom:1px solid #eee;">{d['unmatched_cites_in_tex']}</td></tr>
<tr><td style="padding:5px;border-bottom:1px solid #eee;">Unused Bib Entries</td><td style="padding:5px;border-bottom:1px solid #eee;">{d['unused_in_bib']}</td></tr>
<tr><td style="padding:5px;border-bottom:1px solid #eee;">Missing DOI</td><td style="padding:5px;border-bottom:1px solid #eee;">{b['missing_doi']}</td></tr>
<tr><td style="padding:5px;border-bottom:1px solid #eee;">Missing Year</td><td style="padding:5px;border-bottom:1px solid #eee;">{b['missing_year']}</td></tr>
<tr><td style="padding:5px;border-bottom:1px solid #eee;">Missing Authors</td><td style="padding:5px;border-bottom:1px solid #eee;">{b['missing_authors']}</td></tr>
<tr><td style="padding:5px;border-bottom:1px solid #eee;">Missing Title</td><td style="padding:5px;border-bottom:1px solid #eee;">{b['missing_title']}</td></tr>
<tr><td style="padding:5px;border-bottom:1px solid #eee;">Missing Journal</td><td style="padding:5px;border-bottom:1px solid #eee;">{b['missing_journal']}</td></tr>
<tr><td style="padding:5px;border-bottom:1px solid #eee;">Entry Types</td><td style="padding:5px;border-bottom:1px solid #eee;">{b['entry_types']}</td></tr>
<tr><td style="padding:5px;border-bottom:1px solid #eee;">Tex Files</td><td style="padding:5px;border-bottom:1px solid #eee;">{r['tex_files']}</td></tr>
<tr><td style="padding:5px;border-bottom:1px solid #eee;">Bib Files</td><td style="padding:5px;border-bottom:1px solid #eee;">{r['bib_files']}</td></tr>
{'<tr><td style="padding:5px;border-bottom:1px solid #eee;">Errors</td><td style="padding:5px;border-bottom:1px solid #eee;">' + '<br>'.join('<span style="color:#ef4444;">' + e + '</span>' for e in r.get("errors",[])) + '</td></tr>' if r.get("errors") else ''}
{'<tr><td style="padding:5px;border-bottom:1px solid #eee;">Warnings</td><td style="padding:5px;border-bottom:1px solid #eee;">' + '<br>'.join('<span style="color:#f59e0b;">' + w + '</span>' for w in r.get("warnings",[])) + '</td></tr>' if r.get("warnings") else ''}
</table>
</details>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Synthos Unified Paper Scan Report</title>
<style>
body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f8f9fa; color: #212529; }}
h1 {{ color: #1a1a2e; border-bottom: 3px solid #4361ee; padding-bottom: 10px; }}
h2 {{ color: #4361ee; margin-top: 30px; }}
.summary {{ display: flex; gap: 15px; margin: 20px 0; flex-wrap: wrap; }}
.card {{ background: white; border-radius: 8px; padding: 15px 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); min-width: 120px; text-align: center; }}
.card .number {{ font-size: 2em; font-weight: bold; }}
.card .label {{ font-size: 0.9em; color: #666; }}
table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 15px 0; }}
th {{ background: #4361ee; color: white; padding: 12px 15px; text-align: left; }}
td {{ padding: 10px 15px; border-bottom: 1px solid #e5e7eb; }}
tr:hover {{ background: #f8f9fa; }}
footer {{ margin-top: 40px; color: #666; font-size: 0.85em; text-align: center; border-top: 1px solid #e5e7eb; padding-top: 20px; }}
</style>
</head>
<body>
<h1>🔬 Synthos Unified Paper Scan Report</h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Papers: <strong>{total}</strong></p>
<h2>Summary</h2>
<div class="summary">
    <div class="card" style="background:#dcfce7;"><div class="number" style="color:#166534;">{healthy}</div><div class="label">✅ Healthy</div></div>
    <div class="card" style="background:#fef3c7;"><div class="number" style="color:#92400e;">{warning}</div><div class="label">⚠️ Warning</div></div>
    <div class="card" style="background:#fee2e2;"><div class="number" style="color:#991b1b;">{critical}</div><div class="label">❌ Critical</div></div>
    <div class="card" style="background:#f3f4f6;"><div class="number" style="color:#6b7280;">{unscannable}</div><div class="label">🔍 Unscannable</div></div>
    <div class="card" style="background:#eff6ff;"><div class="number" style="color:#1d4ed8;">{avg_d8}</div><div class="label">📊 Avg D8</div></div>
</div>
<h2>📋 Paper Health Status</h2>
<table>
<tr><th>Paper</th><th>Health</th><th>D8 Score</th><th>Citations</th><th>Bib Entries</th><th>Issues</th></tr>
{rows}
</table>
<h2>🔍 Detailed Results</h2>
{details}
<footer>Synthos Unified Paper Scan | {datetime.now().strftime('%Y-%m-%d')} | D8 & D10a Citation Audit | {total} papers scanned</footer>
</body>
</html>'''

    with open(report_path, 'w') as f:
        f.write(html)


def main():
    print("=" * 60)
    print("Synthos Unified Paper Scan v2 — D8 + D10a + Bib Standardization")
    print("=" * 60)

    os.makedirs(AUDIT_DIR, exist_ok=True)
    papers = get_paper_dirs()
    print(f"\nFound {len(papers)} paper directories\n")

    results = []
    for i, paper in enumerate(papers, 1):
        name = os.path.basename(paper)
        sys.stderr.write(f"Scanning [{i}/{len(papers)}] {name}... ")
        result = scan_paper(paper)
        results.append(result)
        sys.stderr.write(f"health={result['health']} d8={result['d8']['score']:.2f} fmt={result['ref_format']}\n")

    date_str = datetime.now().strftime('%Y-%m-%d')
    json_path = os.path.join(AUDIT_DIR, f"unified-scan-{date_str}.json")
    with open(json_path, 'w') as f:
        json.dump({
            "scan_date": date_str,
            "scan_time": datetime.now().strftime('%H:%M:%S'),
            "total_papers": len(results),
            "papers": results
        }, f, indent=2, ensure_ascii=False)

    html_path = os.path.join(AUDIT_DIR, f"unified-scan-{date_str}.html")
    generate_html_report(results, html_path)

    print("\n" + "=" * 60)
    print("SCAN COMPLETE")
    print("=" * 60)

    healthy = sum(1 for r in results if r["health"] in ("healthy", "info"))
    warning = sum(1 for r in results if r["health"] == "warning")
    critical = sum(1 for r in results if r["health"] == "critical")
    unscannable = sum(1 for r in results if r["health"] == "unscannable")

    print(f"Total: {len(results)} papers")
    print(f"  Healthy/Info: {healthy}")
    print(f"  Warning:      {warning}")
    print(f"  Critical:     {critical}")
    print(f"  Unscannable:  {unscannable}")

    # Format distribution
    fmt_counts = {}
    for r in results:
        f = r["ref_format"]
        fmt_counts[f] = fmt_counts.get(f, 0) + 1
    if fmt_counts:
        print(f"\n📊 Reference Format Distribution:")
        for f in sorted(fmt_counts, key=lambda x: -fmt_counts[x]):
            print(f"  {f}: {fmt_counts[f]}")

    print(f"\n📁 Reports saved:")
    print(f"   {json_path}")
    print(f"   {html_path}")


if __name__ == "__main__":
    main()
