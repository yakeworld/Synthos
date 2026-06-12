# Cron Health Check 2026-06-12

**11 cron jobs. 3 errors fixed.**

## Errors Found and Fixed

| Job ID | Name | Error | Fix |
|--------|------|-------|-----|
| 7e137e0e36d6 | qc-batch-scan | Python SyntaxError: f-string with multiline + CJK chars → unterminated string literal | Extracted variables, replaced ✓/✗ with pass/fail |
| f33ce777b4ba | synthos-papers-to-gdrive | Script timed out after 120s — rclone output too frequent | --quiet + --stats 5s + --bwlimit 10M |
| ff134d00da00 | autonomous-core-researcher | RuntimeError: Request timed out — amax unreachable | Added pre-flight connectivity check in prompt |

## vLLM Node Status

| Node | URL | Response | Status |
|------|-----|----------|--------|
| amax (primary) | 100.100.252.99:8000 | 10ms | Healthy |
| amax-fallback | 100.82.27.51:8000 | 13ms | Healthy |

## Provider Distribution (After Fix)

**amax (primary) — 3 tasks:** autonomous-core-researcher (every 30m), synthos-evolution-full (daily 3am), synthos-github-discussion (monthly)

**amax-fallback (secondary) — 5 tasks:** synthos-evolution-probe (every 6h), papers-daily-scan (every 6h), literature-monitor (daily), bib-standardization (daily), daily-papers-report (daily)

**Script (no_agent) — 3 tasks:** gpu-heartbeat (every 30m), synthos-papers-to-gdrive (every 6h), qc-batch-scan (every 360m)

## Key Patterns

1. **False positive rate**: 75% of grep Error matches are false positives. Use grep FAILED or timed out instead.
2. **f-string CJK pitfall**: f-strings with newline + CJK characters cause SyntaxError. Replace with ASCII pass/fail.
3. **Provider isolation**: cron tasks cannot have automatic failover between providers — must explicitly assign per task.