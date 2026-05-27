#!/bin/bash
# ============================================================
#  Batch Runner — Round 2 Deep Optimization
#  串行模式，取队首一个项目，用 R2 脚本（10篇文献+深度LaTeX）
# ============================================================
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
set +e

OUTDIR="/media/yakeworld/sda2/Synthos/outputs/papers"
QUEUE="$OUTDIR/QUEUE.md"
LOG="$OUTDIR/BATCH_LOG.md"
SCRIPT="/media/yakeworld/sda2/Synthos/scripts/enhance-notebook-r2.sh"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "$TIMESTAMP — Batch runner R2 started"

# Parse queue, take 1st
ITEM=$(python3 << 'PYEOF'
import re
with open('/media/yakeworld/sda2/Synthos/outputs/papers/QUEUE.md') as f:
    text = f.read()

in_queue = False
for line in text.split('\n'):
    if line.strip().startswith('## Phase') or line.strip().startswith('|'):
        # Check if we're in the table area
        pass
    if line.strip().startswith('## Phase'):
        # Check for table rows within Phase sections
        pass

# Simpler: scan for table rows with backtick IDs
for line in text.split('\n'):
    if line.startswith('|') and '`' in line and not line.startswith('|:'):
        # Ensure it's in Phase section (has a number column)
        parts = [p.strip() for p in line.split('|')]
        for i, p in enumerate(parts):
            if '`' in p and len(parts) >= i + 4:
                item_id = p.strip('`')
                query = parts[i + 2].strip()
                project = parts[i + 3].strip()
                print(f"{item_id}|{query}|{project}")
                exit(0)
PYEOF
)

if [ -z "$ITEM" ]; then
  echo "ℹ️  Queue empty — nothing to do"
  # Check if shall we stop the cron
  exit 0
fi

NID=$(echo "$ITEM" | cut -d'|' -f1)
QUERY=$(echo "$ITEM" | cut -d'|' -f2)
PROJ=$(echo "$ITEM" | cut -d'|' -f3)

echo "R2 Processing: $PROJ ($NID)"
echo "Query: $QUERY"

# Run R2 script
bash "$SCRIPT" "$NID" "$QUERY" "$PROJ"

# Check result
PDF="$OUTDIR/$PROJ/paper.pdf"
if [ -f "$PDF" ]; then
    SIZE=$(du -h "$PDF" 2>/dev/null | cut -f1)
    RESULT="✅ $PROJ(${SIZE}) (R2)"
    FAIL=0
else
    RESULT="❌ $PROJ (R2)"
    FAIL=1
fi

# Log
[ ! -f "$LOG" ] && echo "# Batch Run Log\n\n| # | Time | Result | Fail |\n|:-:|:----|:------|:----:|" > "$LOG"
BATCH=$(($(grep -c '^|' "$LOG" 2>/dev/null) + 1))
echo "| $BATCH | $(date '+%Y-%m-%d %H:%M:%S') | $RESULT | $FAIL |" >> "$LOG"

echo "📝 Logged batch $BATCH"
echo "✅ Done: $RESULT"
exit $FAIL
