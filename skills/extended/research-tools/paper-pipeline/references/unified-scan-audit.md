# Unified Paper Pipeline Audit Scan

## Purpose

A comprehensive integrity audit of the paper pipeline's reference system. Goes beyond D10a to produce a multi-dimensional health report covering DOI coverage, cross-file duplicate detection, suspicious entry classification, and state.json metrics.

## Run Command

```bash
cd /media/yakeworld/sda2/Synthos
python3 scripts/unified-scan-audit.py /media/yakeworld/sda2/Synthos/outputs/papers
```

## Output Format

Produces `outputs/researchaudit/unified-scan-YYYY-MM-DD.json` with:

- **summary**: total_bib_files, total_entries, total_with_doi, overall_doi_coverage%, total_suspicious_entries
- **papers**: per-bib-file entries (paper, file, entries, doi_count, doi_coverage, suspicious_count)
- **state_data**: per-paper quality_score and gate_status from state.json
- **cross_file_duplicates**: keys appearing in multiple papers with title/year inconsistencies
- **cross_file_duplicate_count**: total unique keys with cross-file presence

## Interpretation Guide

### Key Metrics

| Metric | Healthy Range | Action if Failing |
|:---|:---|:---|
| DOI coverage | >70% | Review papers with 0% DOI — may be synthetic entries |
| Suspicious count | Low (<50) | Check arXiv-without-ID, missing-author, URL-in-year entries |
| Cross-file dupes with inconsistencies | Low (<10) | Standardize keys; fix title/year mismatches |
| Stale papers (>14 days) | 0-2 | Check if recompile needed or paper is truly complete |

### Common Findings

1. **ref1-ref5 generic keys**: 20+ papers use `ref1`, `ref2`... as bib keys. These create massive cross-file duplicate noise. Fix: replace with author-year format.

2. **Duplicate bib files**: Same paper may have `references.bib` in 01-manuscript/, 06-references/, and root. Check that they're identical; keep one canonical copy.

3. **Zero DOI papers**: Papers like `150-scleral-remodeling-ODE` (20 entries, 0 DOI), `162-corneal-hydration-dynamics-ODE` (26 entries, 0 DOI). These are strong indicators of synthetic/fabricated references — they need D9 verification.

4. **Low score + no bib**: Papers like `104-perilymph-fistula-ODE` (score=55) may be low partly because their references.bib is not in `01-manuscript/` but in a subdirectory like `08-references/`.

5. **State anomaly**: A paper with `quality_score=96` but `steps_completed` has 0 entries (e.g., `187-scleral-remodeling-ODE`) indicates state.json was cleared/overwritten. Check if paper still has all artifacts.

## Session History

- **2026-06-29**: First run. 93 papers scanned, 125 bib files, 2,802 entries, 74.4% DOI coverage, 158 suspicious entries, 524 cross-file dupes. 10 papers below score 60. 1 BLOCKED (crispdm-heart).
