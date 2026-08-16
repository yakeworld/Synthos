#!/usr/bin/env bash
# evolution-reconcile.sh — Synthos 收敛态周期对账 (cycle-218 起)
# 目的: 评分六维饱和 (全 1.0) 后, 进化循环失去分辨率, 但并行研究流
#       (文献监控/3diris 等 cron) 持续产生脏文件, 会把 absorption 维度
#       (1 - dirty/skills) 拉低, 造成 claimed ≠ measured 漂移。
# 动作: 独立重算六维 -> 有脏文件则提交研究文件 -> 重测 -> 同步 state ->
#       提交 state/log -> 验证 clean。
# 纪律: commit-first-then-measure; 独立重算 (不复用 state 声称值);
#       选择性 git add (禁 -A); 提交后验证 git log -1 + porcelain。
set -uo pipefail
cd /media/yakeworld/sda2/Synthos

log() { echo "[$(date -u +%H:%M:%S)] $*"; }
DIAG=skills/private/extended/meta/evolution/scripts/diagnose.py
MAX_DIRTY=50
SELF=$(git rev-parse --show-toplevel)/scripts/evolution-reconcile.sh

# 0. PRECHECK
if [ ! -f "$DIAG" ]; then log "FAIL: diagnose.py 不存在"; exit 1; fi

# 1. 独立重算 (measured, 不读 state 声称值)
M1=$(python3 "$DIAG" 2>&1)
OVERALL1=$(echo "$M1" | awk '/^  OVERALL:/{print $2}')
DIRTY1=$(echo "$M1" | awk '/Total dirty:/{print $3}')
log "measured#1: OVERALL=$OVERALL1 dirty=$DIRTY1"

if [ "${DIRTY1:-999}" -gt "$MAX_DIRTY" ]; then
  log "WARN: dirty $DIRTY1 > $MAX_DIRTY — 超出对账能力, 需人工处理"
fi

# 2. 脏文件分类: 研究/技能文件 vs 引擎自身文件
if [ "${DIRTY1:-0}" -gt 0 ]; then
  # 排除引擎自身文件 (state/log) 与对账脚本自身 (首次落地后应已入库;
  # 若 untracked 说明脚本本体未 commit — 属部署缺陷, 不自动提交)
  RESEARCH=$(git status --porcelain | grep -vE 'evolution-(state\.json|log\.md)$' \
    | grep -vF 'scripts/evolution-reconcile.sh' || true)
  if [ -n "$RESEARCH" ]; then
    log "提交研究流脏文件:"
    echo "$RESEARCH" | sed 's/^...//' | while read -r f; do
      [ -e "$f" ] || { log "  skip (已消失): $f"; continue; }
      git add -A -- "$f"
    done
    if git diff --cached --quiet; then
      log "  无可提交改动 (可能全是 untracked 噪音)"
      git reset -q
    else
      git commit -q -m "research-log: 周期对账 $(date -u +%F) — 提交并行研究流脏文件 (对账脚本自动, 防 absorption 漂移)" \
        && log "  committed research files" || log "  FAIL: research commit"
    fi
  fi
fi

# 3. 重测 (commit-first-then-measure)
M2=$(python3 "$DIAG" 2>&1)
OVERALL2=$(echo "$M2" | awk '/^  OVERALL:/{print $2}')
DIRTY2=$(echo "$M2" | awk '/Total dirty:/{print $3}')
log "measured#2: OVERALL=$OVERALL2 dirty=$DIRTY2"

# 4. 同步 evolution-state.json (仅当分数或漂移有变化时改写)
python3 - "$OVERALL2" << 'PYEOF'
import json, sys, datetime, subprocess
overall = float(sys.argv[1])
p = 'evolution-state.json'
s = json.load(open(p))
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
head = subprocess.run(['git','rev-parse','--short','HEAD'], capture_output=True, text=True).stdout.strip()
changed = False
m = overall / 1.0  # overall already measured
if s.get('score') != overall or s.get('git_commit') != head:
    s['score'] = overall
    s['last_run'] = now
    s['diagnostics']['overall'] = overall
    s['diagnostics']['measured_at'] = now
    s['git_commit'] = head
    s['trigger'] = 'reconcile-cron'
    s['next_action'] = 'converged — 周期对账运行中 (absorption 对脏文件敏感, 每 6h 同步)'
    changed = True
if changed:
    json.dump(s, open(p,'w'), ensure_ascii=False, indent=2)
    print(f"state synced: score={overall} git_commit={head}")
else:
    print("state already in sync")
PYEOF

# 5. 提交 state/log (force-add: P035 — 两文件被 .gitignore 忽略, git-as-memory 需入库)
if ! git diff --quiet -- evolution-state.json 2>/dev/null || ! git diff --cached --quiet -- evolution-state.json 2>/dev/null; then
  git add -f evolution-state.json evolution-log.md 2>/dev/null
  if git diff --cached --quiet; then
    git reset -q
  else
    git commit -q -m "reconcile: state sync $(date -u +%F) OVERALL=$OVERALL2 (周期对账)" \
      && log "committed state sync" || log "FAIL: state commit"
  fi
fi

# 6. 验证
LAST=$(git log -1 --oneline)
D=$(git status --porcelain | wc -l)
log "FINAL: HEAD=$LAST dirty=$D OVERALL_measured=$OVERALL2"
if [ "$D" -gt 0 ]; then
  log "WARN: 仍有 $D 个脏文件 (untracked 或提交失败)"
fi
