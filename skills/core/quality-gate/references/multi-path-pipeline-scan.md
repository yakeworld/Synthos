# Multi-Path Pipeline Scan Protocol

**Problem**: Paper pipeline state.json files are spread across **three locations** on the filesystem. A cron job that only scans `~/outputs/papers/` will find an empty pipeline (only queue files and bib reports, no actual papers). The authoritative pipeline lives on the external drive at `/media/yakeworld/sda2/Synthos/outputs/papers/`.

## Three Paths

| Path | Contents | Purpose |
|------|----------|---------|
| `~/outputs/papers/` | Queue tracking files, bib-standards reports | Cron output, NOT the pipeline itself |
| `~/桌面/article_todo/` | Actively developed papers | Writing workspace (not in state.json) |
| `/media/yakeworld/sda2/Synthos/outputs/papers/` | **Main pipeline** — 157 papers with state.json | **AUTHORITATIVE** — all quality gates here |

## Scan Script

```bash
#!/bin/bash
# Scan ALL three paths for state.json files
TOTAL=0
for dir in "$HOME/outputs/papers" "$HOME/桌面/article_todo" "/media/yakeworld/sda2/Synthos/outputs/papers"; do
  if [ -d "$dir" ]; then
    COUNT=$(find "$dir" -name "state.json" 2>/dev/null | wc -l)
    echo "$dir: $COUNT state.json files"
    TOTAL=$((TOTAL + COUNT))
  else
    echo "$dir: NOT FOUND"
  fi
done
echo "Total: $TOTAL state.json files across all paths"
```

## Key Rules

1. **Always scan all three paths** — never assume papers are in one location
2. **External drive may not be mounted** — check `/media/yakeworld/sda2/Synthos/` exists before scanning
3. **State.json in `~` is stale** — the paper-queue.json and state.json on sda2 are the authoritative source
4. **`~` queue files are subset** — low_score_papers.txt may list papers that exist on sda2 but not locally

## Detection

If `find ~/outputs/papers -name "state.json"` returns 0, check the external drive. This happened in practice on 2026-06-25 when the cron job scanned only `~/outputs/papers/` and found no papers at all.

## Real-World Case (2026-06-25)

A cron run of quality-gate on 2026-06-25 scanned only `~/Synthos/outputs/papers/` and `~/outputs/papers/`, finding only one paper (`tonic-VOR-PINN`) with no state.json. The actual pipeline (157 papers) was on `/media/yakeworld/sda2/Synthos/outputs/papers/` — an external USB drive mounted at `/media/yakeworld/sda2/`.

The root cause: two separate Synthos repositories:
- `~/Synthos/` — a thin wrapper with just outputs/ and skills/ directories (synced from sda2)
- `/media/yakeworld/sda2/Synthos/` — the actual full pipeline with all paper directories, state.json, paper-queue.json, evolution-state.json

## Related

- `paper-pipeline` SKILL.md — Filesystem Layout section
- `quality-gate` — Cron Job Execution Mode step 2 (updated to multi-path scanning)
