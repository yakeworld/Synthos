#!/usr/bin/env python3
"""PubMed literature search — final robust version with correct parser."""

import json
import re
import ssl
import sys
import urllib.parse
import urllib.request

ssl_ctx = ssl.create_default_context()
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

QUERY_LABELS = [
    ("pupil segmentation", "瞳孔/虹膜分割、眼球三维建模"),
    ("eye tracking ADHD", "ADHD 眼动追踪"),
    ("semicircular canal posture", "半规管空间姿态"),
]

CATEGORY_KW = {
    "pupil segmentation": [
        "pupil", "iris", "segmentation", "3d", "three-dimensional",
        "eye model", "gaze", "eye tracking", "sclera", "cornea",
        "eyeball model", "anterior segment", "lens detection",
        "pupil edge", "pupil center", "dilation", "eye geometry",
    ],
    "eye tracking ADHD": [
        "adhd", "attention deficit", "hyperactivity", "saccade",
        "fixation", "autism", "dopamine", "inattention",
        "eye movement", "vergence", "pursuit", "blink rate",
        "cognitive task", "concentration",
    ],
    "semicircular canal posture": [
        "semicircular canal", "vestibular", "posture", "balance",
        "otolith", "canal", "vng", "videonystagmography", "caloric",
        "head movement", "spatial orientation", "vertigo",
        "bvn", "vestibular evoked",
    ],
}


def pubmed_search_json(term):
    search_url = (
        f"{BASE}esearch.fcgi?db=pubmed&retmax=15"
        f"&term={urllib.parse.quote(term)}"
        f"[Title/Abstract]&datetype=pdat&sort=date&retmode=json"
    )
    req = urllib.request.Request(search_url)
    req.add_header("User-Agent", "PubMedMonitor/1.0 (cron)")
    try:
        with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [!] Search failed for '{term}': {e}", file=sys.stderr)
        return None


def parse_pubmed_abstract_text(raw_text):
    """
    Parse PubMed eFetch abstract text format.
    Record structure (split by 'N. ' at line start):
      Journal. YYYY...
      
      Title.
      
      Authors.
      
      Author information:
      (1)Affiliation...
      ...
      
      BACKGROUND: ...
      METHODS: ...
      ...
      CONCLUSIONS: ...
      
      DOI: ...
      PMCID: ...
      PMID: XXXXX
      
      Conflict of interest...
    """
    papers = []

    # Split records by 'N. ' at start of line (where N is a digit)
    records = re.split(r'^\d+\.\s', raw_text, flags=re.MULTILINE)

    for rec in records:
        if not rec.strip():
            continue

        lines = rec.split('\n')
        idx = 0

        # Collect all consecutive non-blank lines at the start (journal info may span multiple lines)
        journal_lines = []
        while idx < len(lines) and lines[idx].strip():
            journal_lines.append(lines[idx].strip())
            idx += 1

        # Extract year from all journal lines
        year = "?"
        all_journal = ' '.join(journal_lines)
        m = re.search(r'\b(20[2-5][0-9])\b', all_journal)
        if m:
            year = m.group(1)

        # Skip blank line
        if idx < len(lines) and lines[idx].strip() == '':
            idx += 1

        # Title: read consecutive non-blank lines (usually 1-2)
        # Skip any DOI/meta continuations
        title = "N/A"
        title_parts = []
        while idx < len(lines) and lines[idx].strip():
            candidate = lines[idx].strip().rstrip('.')
            if candidate.startswith('doi:') or candidate.startswith('DOI:') or \
               candidate.startswith('eCollection') or candidate.startswith('Epub') or \
               (candidate.startswith('10.') and 'doi' not in candidate.lower()):
                # DOI continuation, skip
                idx += 1
                continue
            title_parts.append(candidate)
            idx += 1
            if len(title_parts) >= 2:
                break
        if title_parts:
            title = ' '.join(title_parts)
            while title.endswith('.'):
                title = title[:-1]

        # Skip blank line
        if idx < len(lines) and lines[idx].strip() == '':
            idx += 1

        # Authors line
        authors = "N/A"
        if idx < len(lines) and lines[idx].strip():
            # Check if it looks like an authors line (comma-separated, ends with period)
            auth_text = lines[idx].strip()
            if ',' in auth_text or '(' in auth_text or auth_text.endswith('.'):
                authors = auth_text
                idx += 1

        # Skip blank line
        if idx < len(lines) and lines[idx].strip() == '':
            idx += 1

        # Author information block (optional) — lines starting with '(' and containing affiliation info
        while idx < len(lines):
            line = lines[idx].strip()
            if line.startswith('(') and ')' in line[:5] and (',' in line or 'University' in line or 'Institute' in line or 'Hospital' in line or 'Department' in line):
                idx += 1
                continue
            elif line.startswith('Author information') or line.startswith('(#)'):
                idx += 1
                continue
            else:
                break

        # Skip blank after author info
        if idx < len(lines) and lines[idx].strip() == '':
            idx += 1

        # Abstract: everything until DOI:/PMCID:/PMID: line
        abstract_lines = []
        while idx < len(lines):
            line = lines[idx].strip()
            if line.startswith('DOI:') or line.startswith('PMCID:') or \
               line.startswith('PMID:') or line.startswith('Copyright') or \
               line.startswith('Conflict') or line.startswith('Link') or \
               line.startswith('Copyright'):
                break
            if line:
                abstract_lines.append(line)
            idx += 1

        abstract = ' '.join(abstract_lines).strip()
        if not abstract:
            abstract = "No abstract available"

        # Extract PMID from within the record
        pmid = None
        for line in lines:
            m = re.search(r'PMID:\s*(\d+)', line)
            if m:
                pmid = m.group(1)
                break
        if not pmid:
            continue

        papers.append({
            "pmid": pmid,
            "title": title,
            "authors": authors,
            "year": year,
            "abstract": abstract,
        })

    return papers


def fetch_abstracts(pmid_list):
    if not pmid_list:
        return []
    ids_str = ",".join(pmid_list)
    url = f"{BASE}efetch.fcgi?db=pubmed&id={ids_str}&rettype=abstract&retmode=text"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "PubMedMonitor/1.0 (cron)")
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_ctx) as resp:
            raw = resp.read().decode("utf-8")
        return parse_pubmed_abstract_text(raw)
    except Exception as e:
        print(f"  [!] eFetch failed: {e}", file=sys.stderr)
        return []


def filter_recent(papers, min_year=2024):
    return [p for p in papers if p["year"] != "?" and int(p["year"]) >= min_year]


def main():
    all_papers = []

    for term, desc in QUERY_LABELS:
        print(f"\n{'='*70}")
        print(f"Category: {desc}")
        print(f"Query: {term}")
        print(f"{'='*70}")

        result = pubmed_search_json(term)
        if not result:
            print("  No search result.")
            continue

        id_list = result.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            print("  No PMIDs found.")
            continue

        print(f"  Found {len(id_list)} PMIDs from search")

        all_fetched = fetch_abstracts(id_list)
        print(f"  Parsed {len(all_fetched)} papers from abstract text")

        # Print samples for debugging
        for p in all_fetched[:2]:
            print(f"    Sample: PMID:{p['pmid']} | Title: {p['title'][:60]} | {p['year']}")
            abst_short = p.get('abstract', '')[:100]
            print(f"      Abstract: {abst_short}")

        recent = filter_recent(all_fetched, min_year=2024)
        if not recent:
            recent = filter_recent(all_fetched, min_year=2022)
            if recent:
                print(f"  (Some papers from 2022-2023, outside strict 2yr window)")

        if not recent:
            print("  No recent papers found.")
            continue

        # Score by keyword overlap with category
        kw = CATEGORY_KW.get(term, CATEGORY_KW["pupil segmentation"])
        for p in recent:
            text = f"{p['title']} {p['abstract']}".lower()
            p["relevance"] = sum(1 for k in kw if k in text)

        recent.sort(key=lambda x: x["relevance"], reverse=True)

        print(f"\n  → {len(recent)} papers within 2-year window:")
        for p in recent:
            abst = p.get("abstract", "")
            if abst and abst != "No abstract available":
                abst_preview = abst[:350].replace("\n", " ")
            else:
                abst_preview = "No abstract available"
            print(f"\n  [{p['relevance']}★] PMID:{p['pmid']} | {p['title']} ({p['year']})")
            print(f"      Authors: {p.get('authors','?')}")
            print(f"      Abstract: {abst_preview}")

            all_papers.append({
                **p,
                "category": desc,
                "term": term,
            })

    print(f"\n\n{'='*70}")
    print(f"FINAL REPORT: {len(all_papers)} total papers across all categories")
    for cat in sorted(set(p["category"] for p in all_papers)):
        count = sum(1 for p in all_papers if p["category"] == cat)
        print(f"  {cat}: {count} papers")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
