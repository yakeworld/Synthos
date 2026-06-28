# Cycle 104 Cron Probe Failure — Transcript

## Date
2026-06-20

## Error
```
Script timed out after 120s: /home/yakeworld/.hermes/scripts/synthos-evolution-probe.sh
```

## Root Cause Analysis

### Script content (synthos-evolution-probe.sh)
```bash
#!/bin/bash
set -euo pipefail
cd /media/yakeworld/sda2/Synthos
codex -p amax exec "## Synthos 进化 — PROBE + DRIFT_CHECK (轻量级)
..." --yolo 2>&1
```

### Failure chain
1. Cron triggers the script
2. Script calls `codex -p amax exec "..." --yolo`
3. Codex CLI exits with: `Error: stdin is not a terminal`
4. Exit code is non-zero
5. `set -euo pipefail` causes immediate script exit
6. Cron waits 120s for the process to complete → timeout

### Why `--yolo` doesn't help
Codex CLI is fundamentally an interactive terminal application. The `--yolo` flag modifies its behavior mode but does NOT change its TTY requirement. In cron mode, there is no interactive terminal attached to the process.

## System State at Time of Failure

| Metric | Value |
|--------|-------|
| SKILL.md count (actual) | 209 |
| SKILL.md count (state claims) | 212 |
| Frontmatter name: coverage | 206/209 (98.6%) |
| Signature coverage | 177/209 (84.7%) |
| Registry entries | 20 |
| DAG nodes/edges | 10 / 23 (claimed) |
| Git dirty files | 22 |
| Last evolution commit | cycle-88 |
| Cycles without commit | 89-103 (15 cycles) |

## Anomalies Found (manual probe)

### A. State-Reality Discrepancy
- State claims 212 SKILL.md, actual is 209
- Cycle 103 added 3 SI skills but moved them from root to core/ subdirectory
- Net change should be 0, not +3
- State score: 0.91 EXCELLENT, real score: ~0.735 GOOD

### B. Duplicate Name — `research`
Two redirect stubs both declare `name: research`:
- `skills/extended/external-automation/automation-skills/mlops/research/SKILL.md`
- `skills/extended/research-tools/research/SKILL.md`

### C. Missing Sub-skill — `xhs-content`
Referenced 6 times in `social-media/SKILL.md`, directory does not exist.

### D. DAG Edge Mismatch
- skill_network.json declares 23 edges
- Actual sum of all `downstream` arrays: 14 edges

## Resolution

Probe was executed manually via terminal commands instead of Codex.
Report written to: `/home/yakeworld/.hermes/evolution/cycle-104-probe-report.md`

## Lesson for Future Sessions

**Never use Codex CLI in cron scripts.** The script should be rewritten to use direct terminal commands for all probe operations. The existing `evolution` skill already documents:
- Cycle 85: `execute_code` BLOCKED in cron → use terminal heredoc
- Cycle 104: Codex CLI needs TTY → use direct terminal commands

These are cumulative failures at the same layer: cron-mode tool execution has strict limitations.
