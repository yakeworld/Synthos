# Bib Integrity Audit — Session Log 2026-06-12

## Key Findings
- 8 papers scanned, 394 total entries, 83% DOI coverage
- 60 DOIs supplemented (9 known, 51 via OpenAlex)
- 6 suspicious items detected (Kaggle publishers, URL-as-year fields)
- 56 cross-file duplicate keys found (mostly same-paper redundant copies)
- 8 DOI gaps remaining requiring manual lookup

## Technique Updates Applied

### 1. Cross-file dedup: same-paper grouping
The original `bib-audit.py` flagged all cross-file duplicate keys. Session revealed that same-paper copies (e.g., `reference4.bib` in root dir and `latexnew/reference4.bib`) are redundant copies of the same references, NOT inconsistent entries.
- **Fix**: `dedup_cross_files()` in `bib-audit-v2.py` groups files by paper first, only flags cross-paper duplicates as true inconsistencies.
- **Skill patch**: Added "Cross-file dedup: same-paper copies are NOT inconsistent" to SKILL.md pitfalls.

### 2. Paper root discovery
- `outputs/papers/` contains only report markdown files — NOT a paper root
- Actual papers are under `/home/yakeworld/桌面/article_todo/`
- The original `bib-audit.py` has a hardcoded static `PAPER_BIBS` mapping that becomes stale
- `bib-audit-v2.py` is the improved version with better reporting and grouping

### 3. Deduplicated script
- Removed duplicate entry key `daugman-off-axis-correction` from `PAPER_BIBS` in original script
- Added warning comments about static mapping staleness

### 4. Enhanced report output (v2)
- Same-paper duplicates now grouped in "跨文件重复条目" section without flagging as inconsistent
- Priority ordering: P0 (dataset issues) > P0 (DOI coverage) > P1 (suspicious) > P2 (missing DOI) > P2 (dedup)
- Deduplicated suspicious items (same paper/key/issue counted once)

## Known Issues (Not Fixed)
- `bib-audit.py` original still has stale static mapping — should be deprecated in favor of v2
- No dynamic paper discovery mechanism yet (would need to scan `桌面/article_todo/` root)
- OpenAlex API lookup has no retry or rate-limiting for bulk lookups
