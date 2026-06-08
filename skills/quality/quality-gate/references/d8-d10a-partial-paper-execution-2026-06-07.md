# D8/D10a/DOI Scan: PARTIAL Papers Execution Record — 2026-06-07

## Context

PARTIAL papers (55) have state.json or step files but lack complete pipeline artifacts. This session scanned all 55.

## Key Finding: The ".bib is missing" Failure Mode

**54/55 (98%) PARTIAL papers have NO references.bib file at all.**

Their structure is:
```
paper-name/
├── paper.tex (root level, ~5-8KB)
├── qc-d8-refs.md (quality check)
├── quality-report.md (or multiple versions)
├── notebooklm-sources.json (Layer B results)
├── qc-layer-b.md (Layer B output)
├── state.json or step_*.md (some have both, some have neither)
├── .bbl, .aux, .log, .out (some have compiled output)
└── NO references.bib
```

These papers have step files and quality reports but the `.bib` source was never created or was deleted. The `.bbl` compiled output exists for only 4 of the 54 papers.

### Why this matters

Unlike PIPELINE papers (which have tex+bib but may have orphans/zombies) or COMPLETE papers (which have everything), PARTIAL papers with missing bib require **generating** references.bib from scratch, not just cleaning it.

## Execution Pattern

For each PARTIAL paper:

1. **Locate files**: Check root + 01-manuscript/ for .tex, root + 06-references/ + 01-manuscript/ for .bib
2. **Extract citations**: Parse `\cite{}` from primary tex (prefer 01-manuscript/ over root)
3. **Parse bib**: If .bib exists, parse entries and DOI coverage
4. **Calculate D8/D10a**: Intersection of cited keys and bib keys
5. **Handle missing bib**: If no .bib, D8=0, all cited keys are orphans, note in report
6. **Create quality report**: Write 07-quality/quality-report.md with full context

## Result Summary

| Metric | Value |
|--------|-------|
| Total PARTIAL papers | 55 |
| Has .tex AND .bib | 1 (dual-ellipse-fitting) |
| Has .tex, NO .bib | 54 |
| Has state.json | 18 |
| Has step files | 30 |
| Has .bbl | 4 |
| Has Layer B | varies |
| Passed D8/D10a/DOI | 0 |
| Needs improvement | 1 (dual-ellipse-fitting) |
| Failed (no bib) | 54 |

## Reusable Script Location

The batch scan script was written to `/home/yakeworld/process_partial_batch.py` during this session. It can be adapted for future PARTIAL batch scans. Key functions:
- `scan_paper(paper_name)` — full D8/D10a/DOI scan
- `create_quality_report(paper_name, result)` — generates 07-quality/quality-report.md
- Handles multi-tex and multi-bib environments

## Contrast with PIPELINE and COMPLETE

| Category | .tex | .bib | state.json | Typical D8 | Typical Fix |
|----------|------|------|------------|------------|-------------|
| COMPLETE | ✅ | ✅ | ✅ | 30+ | DOI fixes, minor cleanup |
| PIPELINE | ✅ | ✅ | ❌ | 0-33 | Cleanup orphans/zombies |
| PARTIAL | ✅ | ❌ | sometimes | 0 | **Generate bib from scratch** |
| EMPTY | ❌ | ❌ | ❌ | 0 | Full pipeline required |
