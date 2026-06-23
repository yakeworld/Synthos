#!/usr/bin/env python3
"""
Synthos Unified Paper Scan - D8 + D10a + Bib Standardization
"""

import os, re, json, urllib.request, urllib.parse, urllib.error
from datetime import datetime
from pathlib import Path
from html import escape

PAPERS_ROOT = Path("/media/yakeworld/sda2/Synthos/outputs/papers")
AUDIT_DIR = Path("/media/yakeworld/sda2/Synthos/outputs/researchaudit")
CROSSREF_URL = "https://api.crossref.org/works/"
CROSSREF_MAIL = "synthos-audit@localhost"


def _http_get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Synthos/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _crossref_lookup(title, authors=None, year=None, journal=None):
    params = []
    if title:
        params.append("query.bibtitle=" + urllib.parse.quote(title[:120]))
    if authors:
        a1 = authors[0].replace(" ", "+")
        params.append("query.author=" + a1)
    if year:
        params.append("selected=" + str(year))
    if journal:
        params.append("query.container-title=" + urllib.parse.quote(journal[:80]))
    if not params:
        return None
    url = CROSSREF_URL + "?" + "&".join(params) + "&rows=1&select=DOI,title,author,container-title,published-print"
    data = _http_get(url)
    if data and data.get("status") == "ok" and data["message"].get("items"):
        item = data["message"]["items"][0]
        doi = item.get("DOI")
        score = 1.0
        if title and "title" in item:
            t1 = title.lower().replace(" ", "")
            t2 = item["title"][0].lower().replace(" ", "")
            if t1 in t2 or t2 in t1:
                score += 0.5
            else:
                score -= 0.3
        return {"doi": doi, "score": round(score, 2), "match": item}
    return None


def parse_bib_keys(bib_path):
    if not bib_path or not os.path.isfile(bib_path):
        return []
    try:
        with open(bib_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return []
    keys = []
    for m in re.finditer(r'@\w+\{(\w+),', content):
        keys.append(m.group(1))
    return list(set(keys))


def parse_bib_entries(bib_path):
    if not bib_path or not os.path.isfile(bib_path):
        return {}
    try:
        with open(bib_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return {}
    entries = {}
    for m in re.finditer(r'@\w+\{(\w+),\s*(.*?)\n\}', content, re.DOTALL):
        key = m.group(1)
        body = m.group(2)
        fields = {}
        for fm in re.finditer(r'(\w+)\s*=\s*\{([^}]*)\}', body):
            fields[fm.group(1).lower()] = fm.group(2).strip()
        entries[key] = fields
    return entries


def parse_citations(tex_path):
    if not tex_path or not os.path.isfile(tex_path):
        return []
    try:
        with open(tex_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        return []
    keys = []
    # Standard \cite{key} or \cite{key1,key2}
    for m in re.finditer(r'\\cite\{([^}]+)\}', content):
        for k in m.group(1).split(","):
            k = k.strip()
            if k:
                keys.append(k)
    # \citep{key} and \citet{key}
    for m in re.finditer(r'\\cite[p|t]\{([^}]+)\}', content):
        for k in m.group(1).split(","):
            k = k.strip()
            if k:
                keys.append(k)
    return list(dict.fromkeys(keys))


def find_papers(root):
    papers = []
    if not root.exists():
        return papers
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name.startswith("_") or name == "submissions" or name == "research":
            continue
        if not any(entry.iterdir()):
            continue
        papers.append(entry)
    return papers


def find_tex_and_bib(dir_path):
    tex_files = []
    bib_files = []
    for p in dir_path.rglob("*"):
        if p.is_file():
            if p.name == "paper.tex":
                # Skip manuscript subdirectories
                parts = str(p).split(os.sep)
                skip = False
                for part in parts:
                    if part in ("01-manuscript", "02-submission", "09-manuscript", "08-manuscript"):
                        skip = True
                        break
                if not skip:
                    tex_files.append(p)
            if p.name == "references.bib":
                parts = str(p).split(os.sep)
                skip = False
                for part in parts:
                    if part in ("01-manuscript", "07-ref_check", "07-quality", "08-references", "06-references"):
                        skip = True
                        break
                if not skip:
                    bib_files.append(p)

    root_tex = dir_path / "paper.tex"
    if root_tex.is_file():
        tex_files = [root_tex]
    root_bib = dir_path / "references.bib"
    if root_bib.is_file():
        bib_files = [root_bib]

    return tex_files, bib_files


def scan_d8(paper_dir, tex_files, bib_files):
    result = {
        "bib_files_found": [str(f.relative_to(PAPERS_ROOT)) for f in bib_files],
        "tex_files_scanned": [str(f.relative_to(PAPERS_ROOT)) for f in tex_files],
        "all_cite_keys": [],
        "missing_keys": [],
        "unreferenced_keys": [],
        "score": 1.0,
        "citation_count": 0,
        "bib_entry_count": 0,
    }

    all_cite_keys = set()
    all_bib_keys = set()

    for tf in tex_files:
        keys = parse_citations(tf)
        all_cite_keys.update(keys)
        result["all_cite_keys"].extend(keys)

    for bf in bib_files:
        keys = parse_bib_keys(bf)
        all_bib_keys.update(keys)
        result["bib_entry_count"] = len(all_bib_keys)

    result["citation_count"] = len(all_cite_keys)
    missing = all_cite_keys - all_bib_keys
    unreferenced = all_bib_keys - all_cite_keys
    result["missing_keys"] = sorted(missing)
    result["unreferenced_keys"] = sorted(unreferenced)

    if result["citation_count"] > 0:
        result["score"] = round((result["citation_count"] - len(missing)) / result["citation_count"], 4)
    else:
        result["score"] = 0.0

    return result


def scan_d10a(paper_dir, tex_files):
    result = {
        "issues": [],
        "score": 1.0,
        "total_citations": 0,
        "well_formed": 0,
        "mal_formed": 0,
    }

    patterns_found = {
        "standard_cite": 0,
        "citep": 0,
        "citet": 0,
        "multiple_keys": 0,
    }

    for tf in tex_files:
        try:
            with open(tf, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception:
            continue

        line_num = 0
        for line in lines:
            line_num += 1

            # Standard \cite{key} or \cite{key1,key2}
            for m in re.finditer(r'\\cite\{([^}]+)\}', line):
                keys = [k.strip() for k in m.group(1).split(",")]
                patterns_found["standard_cite"] += 1
                if len(keys) > 1:
                    patterns_found["multiple_keys"] += 1
                for k in keys:
                    result["total_citations"] += 1
                    result["well_formed"] += 1

            # \citep{key} and \citet{key}
            for m in re.finditer(r'\\cite([pt])\{([^}]+)\}', line):
                style = m.group(1)
                keys = [k.strip() for k in m.group(2).split(",")]
                if style == "p":
                    patterns_found["citep"] += 1
                else:
                    patterns_found["citet"] += 1
                if len(keys) > 1:
                    patterns_found["multiple_keys"] += 1
                for k in keys:
                    result["total_citations"] += 1
                    result["well_formed"] += 1

    total = result["total_citations"]
    if total > 0:
        result["score"] = round(result["well_formed"] / total, 4)

    styles_used = sum(1 for v in patterns_found.values() if v > 0)
    if styles_used > 2:
        patterns_found["mixed_style"] = True
        result["issues"].append({
            "type": "mixed_style",
            "message": "Multiple citation command styles detected"
        })
        result["score"] = max(0, result["score"] - 0.1)

    if patterns_found["multiple_keys"] > 0:
        result["issues"].append({
            "type": "multiple_keys_per_cite",
            "count": patterns_found["multiple_keys"],
            "message": str(patterns_found["multiple_keys"]) + " multi-key citations found"
        })

    result["patterns_used"] = dict(patterns_found)
    return result


def scan_bib_standard(bib_entries, missing_keys, paper_dir):
    result = {
        "total_entries": len(bib_entries),
        "missing_doi": [],
        "missing_author": [],
        "missing_title": [],
        "missing_year": [],
        "missing_journal": [],
        "crossref_verified": 0,
        "crossref_failed": 0,
        "fake_entries": [],
    }

    for key, fields in bib_entries.items():
        if "doi" not in fields:
            result["missing_doi"].append(key)
        if "author" not in fields:
            result["missing_author"].append(key)
        if "title" not in fields:
            result["missing_title"].append(key)
        if "year" not in fields:
            result["missing_year"].append(key)
        if "journal" not in fields and "journaltitle" not in fields and "booktitle" not in fields:
            result["missing_journal"].append(key)

    verified = 0
    failed = 0
    fake = []

    candidates = []
    for key, fields in bib_entries.items():
        if "title" in fields and "year" in fields:
            candidates.append((key, fields))

    candidates.sort(key=lambda x: 0 if "doi" not in x[1] else 1)
    candidates = candidates[:20]

    for key, fields in candidates:
        year = fields.get("year", "")
        title = fields.get("title", "")
        journal = fields.get("journal", fields.get("journaltitle", ""))
        authors_str = fields.get("author", "")
        authors = [a.strip() for a in authors_str.replace(" and ", ", ").split(",") if a.strip()]

        lookup = _crossref_lookup(title, authors, year, journal)
        if lookup:
            verified += 1
        else:
            failed += 1
            if not fields.get("doi"):
                fake.append({
                    "key": key,
                    "title": title,
                    "year": year,
                    "authors": authors_str,
                })

    result["crossref_verified"] = verified
    result["crossref_failed"] = failed
    result["fake_entries"] = fake[:10]

    return result


def main():
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().isoformat()

    print("[*] Synthos Unified Paper Scan - " + timestamp)
    print("[*] Scanning: " + str(PAPERS_ROOT))

    paper_dirs = find_papers(PAPERS_ROOT)
    for sub in PAPERS_ROOT.rglob("submissions"):
        if sub.is_dir():
            for item in sub.iterdir():
                if item.is_dir():
                    paper_dirs.append(item)

    all_results = {
        "scan_metadata": {
            "timestamp": timestamp,
            "papers_root": str(PAPERS_ROOT),
            "total_papers_scanned": len(paper_dirs),
            "scanner_version": "2.0",
        },
        "papers": [],
        "summary": {},
    }

    total_d8 = 0
    count_d8 = 0
    total_d10a = 0
    count_d10a = 0
    healthy = 0
    degraded = 0
    critical = 0

    for idx, pdir in enumerate(paper_dirs):
        name = pdir.name
        print("  [" + str(idx+1) + "/" + str(len(paper_dirs)) + "] Scanning " + name + "...", end=" ", flush=True)

        tex_files, bib_files = find_tex_and_bib(pdir)
        paper_result = {
            "name": name,
            "path": str(pdir.relative_to(PAPERS_ROOT)),
            "d8": None,
            "d10a": None,
            "bib_standard": None,
            "status": "unknown",
            "health": "unknown",
            "issues": [],
        }

        # D8 scan
        d8_ok = False
        if tex_files and bib_files:
            d8 = scan_d8(pdir, tex_files, bib_files)
            paper_result["d8"] = d8
            total_d8 += d8["score"]
            count_d8 += 1

            if d8["score"] < 0.5:
                paper_result["health"] = "critical"
                paper_result["issues"].append({"type": "d8_critical", "msg": "D8 score " + str(d8["score"]) + ": " + str(len(d8["missing_keys"])) + " missing citations"})
            elif d8["score"] < 0.85:
                paper_result["health"] = "degraded"
                paper_result["issues"].append({"type": "d8_degraded", "msg": "D8 score " + str(d8["score"]) + ": " + str(len(d8["missing_keys"])) + " missing citations"})
            else:
                paper_result["issues"].append({"type": "d8_ok", "msg": "D8 score " + str(d8["score"]) + " - all citations present"})
                d8_ok = True
        elif tex_files and not bib_files:
            first_cites = 0
            if tex_files:
                first_cites = len(parse_citations(tex_files[0]))
            paper_result["d8"] = {"score": 0.0, "missing_keys": ["NO_BIB_FILE"], "citation_count": first_cites, "bib_entry_count": 0}
            paper_result["health"] = "critical"
            paper_result["issues"].append({"type": "d8_critical", "msg": "No references.bib file found"})
        else:
            paper_result["d8"] = {"score": 0.0, "message": "No tex file found"}

        # D10a scan
        if tex_files:
            d10a = scan_d10a(pdir, tex_files)
            paper_result["d10a"] = d10a
            total_d10a += d10a["score"]
            count_d10a += 1

            if d10a["score"] < 0.85:
                if paper_result["health"] not in ("critical",):
                    paper_result["health"] = "degraded"
                for iss in d10a.get("issues", []):
                    paper_result["issues"].append({"type": "d10a", **iss})
            else:
                paper_result["issues"].append({"type": "d10a_ok", "msg": "D10a score " + str(d10a["score"]) + " - citation format consistent"})
        else:
            paper_result["d10a"] = {"score": 0.0, "message": "No tex file found"}

        # Bib standardization
        if bib_files:
            all_bib_entries = {}
            for bf in bib_files:
                entries = parse_bib_entries(bf)
                all_bib_entries.update(entries)

            missing_keys_set = set()
            d8_data = paper_result.get("d8")
            if d8_data:
                missing_keys_set.update(d8_data.get("missing_keys", []))

            bib_std = scan_bib_standard(all_bib_entries, list(missing_keys_set), pdir)
            paper_result["bib_standard"] = bib_std

            if bib_std["fake_entries"]:
                if paper_result["health"] != "critical":
                    paper_result["health"] = "critical"
                paper_result["issues"].append({
                    "type": "bib_fake",
                    "msg": str(len(bib_std["fake_entries"])) + " potentially fake entries detected via Crossref"
                })
            total_entries = max(len(all_bib_entries), 1)
            if len(bib_std["missing_doi"]) > total_entries * 0.3:
                if paper_result["health"] not in ("critical",):
                    paper_result["health"] = "degraded"
                paper_result["issues"].append({
                    "type": "bib_missing_doi",
                    "msg": str(len(bib_std["missing_doi"])) + " entries missing DOI (" + str(round(len(bib_std["missing_doi"])/total_entries*100)) + "%)"
                })

        # Health summary
        if paper_result["health"] == "unknown":
            paper_result["health"] = "no_data"
        if paper_result["health"] == "critical":
            critical += 1
        elif paper_result["health"] == "degraded":
            degraded += 1
        elif paper_result["health"] == "healthy":
            healthy += 1
        # no_data: doesn't count in any category
        if paper_result["health"] not in ("critical", "degraded", "healthy", "no_data"):
            pass

        all_results["papers"].append(paper_result)

    avg_d8 = round(total_d8 / max(count_d8, 1), 4)
    avg_d10a = round(total_d10a / max(count_d10a, 1), 4)

    papers_needing = [p["name"] for p in all_results["papers"] if p["health"] in ("critical", "degraded")]

    all_results["summary"] = {
        "total_papers": len(paper_dirs),
        "papers_with_tex": sum(1 for p in all_results["papers"] if p["d8"] and p["d8"].get("citation_count", 0) > 0),
        "papers_with_bib": sum(1 for p in all_results["papers"] if p["bib_standard"] and "total_entries" in p["bib_standard"]),
        "healthy": healthy,
        "degraded": degraded,
        "critical": critical,
        "no_data": sum(1 for p in all_results["papers"] if p["health"] == "no_data"),
        "avg_d8_score": avg_d8,
        "avg_d10a_score": avg_d10a,
        "papers_needing_attention": papers_needing,
    }

    # Write JSON
    json_path = AUDIT_DIR / ("unified-scan-" + today + ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print("\n  [OK] JSON report: " + str(json_path))

    # Write HTML
    html_path = AUDIT_DIR / ("unified-scan-" + today + ".html")
    write_html_report(all_results, html_path)
    print("  [OK] HTML report: " + str(html_path))

    print("\n" + "=" * 60)
    print("  Summary:")
    print("    Papers scanned:  " + str(len(paper_dirs)))
    print("    Healthy:         " + str(healthy))
    print("    Degraded:        " + str(degraded))
    print("    Critical:        " + str(critical))
    print("    No data:         " + str(sum(1 for p in all_results["papers"] if p["health"] == "no_data")))
    print("    Avg D8 score:    " + str(avg_d8))
    print("    Avg D10a score:  " + str(avg_d10a))
    print("    Papers needing:  " + str(len(papers_needing)))
    print("=" * 60)


def write_html_report(data, path):
    papers = data["papers"]
    summary = data["summary"]
    meta = data["scan_metadata"]

    health_colors = {
        "healthy": "#22c55e",
        "degraded": "#f59e0b",
        "critical": "#ef4444",
        "no_data": "#94a3b8",
    }

    rows = ""
    for p in papers:
        color = health_colors.get(p["health"], "#94a3b8")
        d8 = p.get("d8", {})
        d10 = p.get("d10a", {})
        bib = p.get("bib_standard", {})
        issues_html = ""
        for iss in p.get("issues", [])[:5]:
            t = iss.get("type", "")
            m = escape(str(iss.get("msg", iss.get("message", ""))))
            if "critical" in t:
                issues_html += '<tr><td class="issue-critical">&#x1F534; ' + m + '</td></tr>'
            elif "degraded" in t or "missing" in t or "fake" in t:
                issues_html += '<tr><td class="issue-warn">&#x1F7E1; ' + m + '</td></tr>'
            else:
                issues_html += '<tr><td class="issue-ok">&#x1F7E2; ' + m + '</td></tr>'

        if not issues_html:
            issues_html = '<span style="color:#94a3b8">-</span>'

        rows += """<tr>
  <td><a name="{name}">{name}</a></td>
  <td class="path">{path}</td>
  <td>{d8}</td>
  <td>{cites}</td>
  <td>{d10a}</td>
  <td>{bib}</td>
  <td><span class="health-badge" style="background:{color}">{health}</span></td>
  <td>{issues}</td>
</tr>""".format(
            name=escape(p["name"]),
            path=escape(p.get("path", "")),
            d8=str(d8.get("score", "N/A")),
            cites=str(d8.get("citation_count", "N/A")),
            d10a=str(d10.get("score", "N/A")),
            bib=str(bib.get("total_entries", "N/A")),
            color=color,
            health=escape(p["health"]),
            issues=issues_html
        )

    attention_section = ""
    if not summary["papers_needing_attention"]:
        attention_section = '<p style="color:#22c55e">All papers healthy OK</p>'
    else:
        items = ""
        for n in summary["papers_needing_attention"]:
            items += '<li><strong>' + escape(n) + '</strong></li>'
        attention_section = '<ul class="issue-list">' + items + '</ul>'

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Synthos Unified Paper Scan Report</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background:#0f172a; color:#e2e8f0; padding:2rem; }
  h1 { font-size:1.8rem; margin-bottom:0.5rem; color:#f8fafc; }
  h2 { font-size:1.3rem; margin:2rem 0 1rem; color:#94a3b8; border-bottom:1px solid #334155; padding-bottom:0.5rem; }
  .subtitle { color:#64748b; margin-bottom:2rem; font-size:0.95rem; }
  .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:1rem; margin:1.5rem 0; }
  .stat-card { background:#1e293b; border-radius:0.75rem; padding:1.25rem; text-align:center; border:1px solid #334155; }
  .stat-card .value { font-size:2rem; font-weight:700; color:#38bdf8; }
  .stat-card .label { font-size:0.8rem; color:#94a3b8; margin-top:0.25rem; }
  table { width:100%; border-collapse:collapse; margin:1rem 0; font-size:0.85rem; }
  th { background:#1e293b; padding:0.75rem; text-align:left; color:#94a3b8; font-weight:600; border-bottom:2px solid #334155; position:sticky; top:0; }
  td { padding:0.6rem 0.75rem; border-bottom:1px solid #1e293b; vertical-align:top; }
  tr:hover { background:#1e293b; }
  .health-badge { display:inline-block; padding:0.15rem 0.6rem; border-radius:9999px; font-size:0.75rem; font-weight:600; color:#fff; }
  .path { font-family:monospace; font-size:0.75rem; color:#64748b; }
  .issue-ok { color:#22c55e; }
  .issue-warn { color:#f59e0b; }
  .issue-critical { color:#ef4444; font-weight:600; }
  .summary-section { background:#1e293b; border-radius:0.75rem; padding:1.5rem; border:1px solid #334155; margin:1.5rem 0; }
  .summary-section h3 { color:#38bdf8; margin-bottom:0.75rem; }
  .issue-list { list-style:none; }
  .issue-list li { padding:0.4rem 0; border-bottom:1px solid #0f172a; }
  .footer { margin-top:2rem; color:#475569; font-size:0.75rem; text-align:center; }
  .scroll-table { overflow-x:auto; max-height:80vh; }
</style>
</head>
<body>
<h1>SYNTHOS Unified Paper Scan</h1>
<p class="subtitle">D8 Reference Existence &middot; D10a Citation Format &middot; Bib Standardization &middot; Crossref Validation</p>
<p class="subtitle">Generated: {ts} &middot; {count} papers scanned</p>

<h2>Overview</h2>
<div class="stats">
  <div class="stat-card"><div class="value">{total}</div><div class="label">Total Papers</div></div>
  <div class="stat-card"><div class="value" style="color:#22c55e">{healthy}</div><div class="label">Healthy</div></div>
  <div class="stat-card"><div class="value" style="color:#f59e0b">{degraded}</div><div class="label">Degraded</div></div>
  <div class="stat-card"><div class="value" style="color:#ef4444">{critical}</div><div class="label">Critical</div></div>
  <div class="stat-card"><div class="value">{d8}</div><div class="label">Avg D8 Score</div></div>
  <div class="stat-card"><div class="value">{d10a}</div><div class="label">Avg D10a Score</div></div>
</div>

<h2>All Papers</h2>
<div class="scroll-table">
<table>
<thead>
<tr><th>Name</th><th>Path</th><th>D8</th><th>Cites</th><th>D10a</th><th>Bib</th><th>Health</th><th>Issues</th></tr>
</thead>
<tbody>
{rows}
</tbody>
</table>
</div>

<h2>Papers Needing Attention</h2>
<div class="summary-section">
{attention}
</div>

<h2>Metadata</h2>
<div class="summary-section">
  <table>
    <tr><td style="color:#64748b;padding-right:1rem">Scanner</td><td>v{ver}</td></tr>
    <tr><td style="color:#64748b;padding-right:1rem">Papers with tex</td><td>{wtext}</td></tr>
    <tr><td style="color:#64748b;padding-right:1rem">Papers with bib</td><td>{wtbib}</td></tr>
    <tr><td style="color:#64748b;padding-right:1rem">No data</td><td>{nodata}</td></tr>
  </table>
</div>

<p class="footer">Synthos Unified Scan &middot; {ts} &middot; Powered by CONSTITUTION P0 (Evidence Traceability)</p>
</body>
</html>""".format(
        ts=escape(meta["timestamp"]),
        count=meta["total_papers_scanned"],
        total=summary["total_papers"],
        healthy=summary["healthy"],
        degraded=summary["degraded"],
        critical=summary["critical"],
        d8=str(summary["avg_d8_score"]),
        d10a=str(summary["avg_d10a_score"]),
        rows=rows,
        attention=attention_section,
        ver=meta.get("scanner_version", "2.0"),
        wtext=summary["papers_with_tex"],
        wtbib=summary["papers_with_bib"],
        nodata=summary["no_data"]
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
