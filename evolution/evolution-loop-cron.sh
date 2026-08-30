#!/bin/bash
# Synthos 自动化进化循环 — cron 脚本
#
# [DEPRECATED cycle 272] 本脚本是 v2 旧链路 (check_skill 结构扫描)。
# 现行唯一度量层 = skills/private/extended/meta/evolution/scripts/diagnose.py (v4, 8-dim)
# 结构扫描 = skills/private/extended/meta/evolution/scripts/evolution-loop.py
# 定时进化 = hermes cron synthos-self-evolution (05:00)
# 保留本脚本仅供手动对比 v2/v4 口径, 不再注册 cron。
# 注意: evolution-loop.py 的退出码 = 分数信号 (0=优秀, 1=合格, 2=不合格),
# 不是错误信号 — 不能用 set -e, 否则第一个 phase 就中止全脚本 (2026-08-31 修复)
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"
LOG_DIR="outputs/cron-archive/evolution-logs"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/evolution-${TIMESTAMP}.log"
exec > "$LOG_FILE" 2>&1
echo "=== Synthos 进化循环开始 ==="
echo "时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""
echo "--- Phase 1: 扫描核心技能 ---"
python3 evolution-loop.py --scan --subset core --cycle 0 2>&1
echo ""
echo "--- Phase 2: 扫描扩展技能 ---"
python3 evolution-loop.py --scan --subset extended --cycle 0 2>&1
echo ""
echo "--- Phase 3: 扫描私人技能 ---"
python3 evolution-loop.py --scan --subset private --cycle 0 2>&1
echo ""
echo "--- Phase 4: 汇总 ---"
python3 -c "
import json
with open('evolution-state.json') as f:
    state = json.load(f)
dims = state.get('dimensions', {})
print(f'整体分数: {state.get(\"overall_score\", 0)}')
print(f'结构质量: {dims.get(\"structural\", 0)}')
print(f'覆盖率:   {dims.get(\"coverage\", 0)}')
print(f'宪法对齐: {dims.get(\"constitutional\", 0)}')
"
echo ""
echo "=== 进化循环完成 ==="
echo "日志: $LOG_FILE"
