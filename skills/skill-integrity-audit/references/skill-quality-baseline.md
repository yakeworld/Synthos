# Skill Quality Baseline — 2026-06-12

> Audit 143 SKILL.md files baseline. Compare against on future audits.

## Key Data

| Quality Dimension | Value | Pct |
|---|---|---|
| BOUNDARY.md | 8/143 | 6% |
| IO_CONTRACT.md | 8/143 | 6% |
| EVIDENCE_SCHEMA.md | 8/143 | 6% |
| CHANGE_LOG.md | 8/143 | 6% |
| Complete golden test | 8/143 | 6% |
| SKILL.md >=2KB | 91/143 | 64% |
| Chinese content (class-level) | 17/37 | 46% |
| Has references/ | 102/143 | 71% |
| Full frontmatter | 14/143 | 10% |

## Priority Fixes

### P0: Cron script bugs (FIXED)
- qc_batch_scan.py: r['d8_count'] -> r.get('d8_count')
- synthos-papers-to-gdrive.sh: removed rclone check, direct rclone sync

### P1: quality-gate structure files (quality-gate is P0 core gate)
- Add BOUNDARY.md, IO_CONTRACT.md, EVIDENCE_SCHEMA.md, CHANGE_LOG.md

### P2: Chinese content in class-level skills
- 20/37 class-level skills lack Chinese, violating Synthos identity

### P3: Golden test coverage
- Target >=70%, currently 6%. Prioritize: high-usage -> newly absorbed -> core atoms