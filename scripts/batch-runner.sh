#!/bin/bash
# ============================================================
#  Batch Runner v2.0 — 串行模式 (Cron-safe PATH)
export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"

# ============================================================
#
# 读取 QUEUE.md，取队首一个项目，执行 enhance-notebook.sh，
# 完成后更新队列和日志。
# ============================================================
set +e  # 因子进程可能返回非零，不中断

OUTDIR="/media/yakeworld/sda2/Synthos/outputs/papers"
QUEUE="$OUTDIR/QUEUE.md"
LOG="$OUTDIR/BATCH_LOG.md"
SCRIPT="/media/yakeworld/sda2/Synthos/scripts/enhance-notebook.sh"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "$TIMESTAMP — Batch runner started"

# 解析队列，取第1个
ITEM=$(python3 << 'PYEOF'
import re
with open('/media/yakeworld/sda2/Synthos/outputs/papers/QUEUE.md') as f:
    text = f.read()

in_queue = False
for line in text.split('\n'):
    if line.strip().startswith('## Queue'):
        in_queue = True
        continue
    if in_queue and line.strip().startswith('## ') and 'Queue' not in line:
        break
    if in_queue and line.startswith('|') and '`' in line and not line.startswith('|:'):
        parts = [p.strip() for p in line.split('|')]
        # Find which column has the backtick ID
        id_col = None
        for i, p in enumerate(parts):
            if '`' in p:
                id_col = i
                break
        if id_col is not None and len(parts) >= id_col + 4:
            item_id = parts[id_col].strip('`')
            query = parts[id_col + 2].strip()
            project = parts[id_col + 3].strip()
            print(f"{item_id}|{query}|{project}")
            break
PYEOF
)

if [ -z "$ITEM" ]; then
  echo "ℹ️  Queue is empty — nothing to do"
  exit 0
fi

# 解析
NID=$(echo "$ITEM" | cut -d'|' -f1)
QUERY=$(echo "$ITEM" | cut -d'|' -f2)
PROJ=$(echo "$ITEM" | cut -d'|' -f3)

echo "Processing: $PROJ ($NID)"
echo "Query: $QUERY"

# 运行
bash "$SCRIPT" "$NID" "$QUERY" "$PROJ"
RC=$?

# 检查结果
PDF="$OUTDIR/papers/$PROJ/paper.pdf"
if [ -f "$PDF" ]; then
    SIZE=$(du -h "$PDF" 2>/dev/null | cut -f1)
    RESULT="✅ $PROJ(${SIZE})"
    FAIL=0
else
    RESULT="❌ $PROJ"
    FAIL=1
fi

# 写日志
[ ! -f "$LOG" ] && echo "# Batch Run Log\n\n| # | Time | Result | Fail |\n|:-:|:----|:------|:----:|" > "$LOG"
BATCH=$(($(grep -c '^|' "$LOG" 2>/dev/null)))
echo "| $((BATCH)) | $(date '+%Y-%m-%d %H:%M:%S') | $RESULT | $FAIL |" >> "$LOG"

echo "📝 Logged batch $((BATCH))"
echo "✅ Done: $RESULT"
exit $FAIL
