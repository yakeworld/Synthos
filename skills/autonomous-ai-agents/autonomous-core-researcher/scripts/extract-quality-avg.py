#!/usr/bin/env python3
"""
Extract confirmed average quality score from quality-report.md or QUALITY.md.
Handles multi-section quality reports (Layer B → Cron Revision → Layer A Confirmation).

Usage:
  python3 extract-quality-avg.py <path-to-quality-report.md>
  python3 extract-quality-avg.py /path/to/papers/ --scan
  python3 extract-quality-avg.py /path/to/papers/ --scan --min 0.75 --max 0.84
  python3 extract-quality-avg.py /path/to/papers/ --scan --tier t2
"""

import re
import os
import sys

QUALITY_FILENAMES = ["quality-report.md", "QUALITY.md"]

# Confidence levels for weighted score selection
CONFIDENCE_CALIBRATED = 5  # "Calibrated score = Layer A: 0.853"
CONFIDENCE_CONFIRMED = 4   # "Layer A Confirmation" section average
CONFIDENCE_ESTIMATED = 3   # "Estimated Average: ~0.853"
CONFIDENCE_PROVISIONAL = 2 # "Provisional Assessment" or "Cron Revision" table
CONFIDENCE_INITIAL = 1     # Initial Layer B review


def extract_all_scores(content: str):
    """Extract ALL scores from a quality report, returning list of (score, confidence, context).

    Confidence levels let callers pick the most reliable score.
    """
    scores = []

    # 1. Calibrated scores (highest priority) — e.g. "Calibrated score = Layer A: 0.853"
    for m in re.finditer(
        r'(?:校准|Calibrated)\s*(?:平均|avg|score|分)?[^0-9]*?([0-9]\.[0-9]{2,3})',
        content, re.IGNORECASE):
        val = float(m.group(1))
        if 0.0 <= val <= 1.0:
            scores.append((val, CONFIDENCE_CALIBRATED, "calibrated"))

    # 2. "Layer A Confirmation" sections — look for "Confirmed" headers with Average rows
    confirmed_sections = re.split(r'###+\s*Layer A Confirmation', content, re.IGNORECASE)
    for i, section in enumerate(confirmed_sections[1:], 1):  # skip pre-confirmation content
        for m in re.finditer(r'\*\*平均\*\*\s*\|\s*\*\*([0-9.~]+)\*\*', section):
            val = float(m.group(1).replace('~', ''))
            if 0.0 <= val <= 1.0:
                scores.append((val, CONFIDENCE_CONFIRMED, f"confirmed_section_{i}"))
        for m in re.finditer(r'\*\*Average\*\*\s*\|\s*\*\*([0-9.~]+)\*\*', section):
            val = float(m.group(1).replace('~', ''))
            if 0.0 <= val <= 1.0:
                scores.append((val, CONFIDENCE_CONFIRMED, f"confirmed_section_{i}"))

    # 3. "Estimated Average" in Cron Revision sections
    for m in re.finditer(
        r'(?:Estimated|Projected)\s*Average[^0-9]*?([0-9]~?[0-9]\.[0-9]{2,3})',
        content, re.IGNORECASE):
        val = float(m.group(1).replace('~', ''))
        if 0.0 <= val <= 1.0:
            scores.append((val, CONFIDENCE_ESTIMATED, "estimated"))

    # 4. "Provisional" assessment averages
    for m in re.finditer(
        r'Provisional.*?Average[^0-9]*?([0-9]\.[0-9]{2,3})',
        content, re.IGNORECASE):
        val = float(m.group(1))
        if 0.0 <= val <= 1.0:
            scores.append((val, CONFIDENCE_PROVISIONAL, "provisional"))

    # 5. Average rows in ALL tables (take the LAST one for each section context)
    #    We need to handle multi-table QRs carefully.
    #    Split by top-level headers to find table positions.
    sections = re.split(r'\n(?=###|## )', content)
    for section in sections:
        avgs = []
        for m in re.finditer(r'\|\s*\*\*(?:平均|Average)\*\*\s*\|\s*\*\*([0-9.~]+)\*\*', section):
            val_str = m.group(1).replace('~', '')
            try:
                val = float(val_str)
                if 0.0 <= val <= 1.0:
                    avgs.append(val)
            except ValueError:
                pass
        if avgs:
            # Take the LAST average in each section (most recent revision)
            scores.append((avgs[-1], CONFIDENCE_PROVISIONAL, "section_avg"))

    # 6. Fallback: simple "Average: 0.XX" or "avg=0.XX" lines
    for m in re.finditer(
        r'\b(?:Avg|Average|avg)\b[^0-9]*?([0-9]\.[0-9]{2,3})',
        content, re.IGNORECASE):
        val = float(m.group(1))
        if 0.0 <= val <= 1.0:
            scores.append((val, CONFIDENCE_INITIAL, "simple_avg"))

    return scores


def pick_best_score(scores):
    """Pick the best score: highest confidence, most recent among ties."""
    if not scores:
        return None, "no_score"
    
    # Highest confidence first, then highest score (conservative pick within ties)
    scores.sort(key=lambda x: (-x[1], -x[0]))
    best = scores[0]
    return best[0], best[2]


def extract_avg(content: str) -> float | None:
    """Extract the most reliable average score from a quality report."""
    scores = extract_all_scores(content)
    score, _ = pick_best_score(scores)
    return score


def tier_of(score: float) -> str:
    if score >= 0.85:
        return "T1"
    elif score >= 0.80:
        return "T2"
    elif score >= 0.75:
        return "T3"
    else:
        return "T4"


def scan_papers(papers_dir: str, min_score: float = None, max_score: float = None,
                tier_filter: str = None):
    """Scan all paper directories and report quality averages."""
    results = []
    for d in sorted(os.listdir(papers_dir)):
        paper_dir = os.path.join(papers_dir, d)
        if not os.path.isdir(paper_dir) or d.startswith('.'):
            continue
        
        avg = None
        source = "no_report"
        found = False
        for fname in QUALITY_FILENAMES:
            path = os.path.join(paper_dir, fname)
            if os.path.exists(path):
                found = True
                with open(path, errors='replace') as f:
                    content = f.read()
                scores = extract_all_scores(content)
                avg, source = pick_best_score(scores)
                break
        
        if not found:
            results.append((d, None, "NO_REPORT", "N/A"))
        elif avg is None:
            results.append((d, None, "PARSE_FAILED", "N/A"))
        else:
            results.append((d, avg, source, tier_of(avg)))
    
    # Filter
    for name, score, source, tier in results:
        if score is not None:
            if min_score is not None and score < min_score:
                continue
            if max_score is not None and score > max_score:
                continue
            if tier_filter is not None and tier.upper() != tier_filter.upper():
                continue
            print(f"{name}: avg={score:.3f} [{tier}] ({source})")
        else:
            if min_score is None and max_score is None and tier_filter is None:
                print(f"{name}: {source}")
    
    # Summary
    scored = [(n, s, t) for n, s, _, t in results if s is not None]
    if scored:
        print(f"\n--- Summary ---")
        print(f"Total papers: {len(results)}")
        print(f"With score:   {len(scored)}")
        if len(scored) > 1:
            print(f"Range:        {min(s for _, s, _ in scored):.3f} - {max(s for _, s, _ in scored):.3f}")
        t1 = sum(1 for _, s, _ in scored if s >= 0.85)
        t2 = sum(1 for _, s, _ in scored if 0.80 <= s < 0.85)
        t3 = sum(1 for _, s, _ in scored if 0.75 <= s < 0.80)
        t4 = sum(1 for _, s, _ in scored if s < 0.75)
        print(f"T1 (>=0.85):  {t1}")
        print(f"T2 (0.80-):   {t2}")
        print(f"T3 (0.75-):   {t3}")
        print(f"T4 (<0.75):   {t4}")
        print(f"Failed:       {sum(1 for _, s, _ in results if s is None)}")


if __name__ == '__main__':
    args = sys.argv[1:]
    
    if not args:
        print(__doc__)
        sys.exit(1)
    
    if '--scan' in args:
        args.remove('--scan')
        papers_dir = args[0] if args and not args[0].startswith('--') else '.'
        min_score = None
        max_score = None
        tier_filter = None
        
        i = 0
        while i < len(args):
            a = args[i]
            if a == '--min' and i + 1 < len(args):
                min_score = float(args[i + 1])
                i += 2
            elif a == '--max' and i + 1 < len(args):
                max_score = float(args[i + 1])
                i += 2
            elif a == '--tier' and i + 1 < len(args):
                tier_filter = args[i + 1]
                i += 2
            else:
                i += 1
        
        scan_papers(papers_dir, min_score=min_score, max_score=max_score,
                    tier_filter=tier_filter)
    else:
        path = args[0]
        if not os.path.exists(path):
            print(f"File not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path, errors='replace') as f:
            content = f.read()
        avg = extract_avg(content)
        if avg is not None:
            print(f"{avg:.3f}")
        else:
            print("N/A")
