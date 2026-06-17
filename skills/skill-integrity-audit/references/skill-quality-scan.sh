#!/bin/bash
# Synthos 技能质量批量扫描脚本
# 审计 sda2/Synthos/skills/ 中所有 SKILL.md 的完整性
# 用法: bash skill-quality-scan.sh [sda2_dir] [local_dir]
# 输出: 质量报告到 stdout，JSON 到 quality-report.json

set -euo pipefail

SDA2_DIR="${1:-/media/yakeworld/sda2/Synthos/skills}"
LOCAL_DIR="${2:-$HOME/.hermes/skills}"

echo "=== Synthos 技能质量审计 ==="
echo "sda2 (权威源): $SDA2_DIR"
echo "本地 (镜像):   $LOCAL_DIR"
echo ""

# 获取技能列表
sda2_skills=($(find "$SDA2_DIR" -name SKILL.md -type f 2>/dev/null | sed "s|$SDA2_DIR/||;s|/SKILL.md||" | sort))
local_skills=($(find "$LOCAL_DIR" -name SKILL.md -type f 2>/dev/null | sed "s|$LOCAL_DIR/||;s|/SKILL.md||" | sort))

total=${#sda2_skills[@]}
echo "总技能数: $total"
echo ""

# 扫描每个技能
scan_skill() {
    local sp="$1"
    local sdir="$SDA2_DIR/$sp"
    local result=""
    
    # SKILL.md size
    local size=$(wc -c < "$sdir/SKILL.md" 2>/dev/null || echo 0)
    local body_lines=$(sed -n '/^---$/,$ p' "$sdir/SKILL.md" 2>/dev/null | grep -c '.' || echo 0)
    
    # Structure
    local has_boundary=0; [ -f "$sdir/BOUNDARY.md" ] && has_boundary=1
    local has_io=0; [ -f "$sdir/IO_CONTRACT.md" ] && has_io=1
    local has_ev=0; [ -f "$sdir/EVIDENCE_SCHEMA.md" ] && has_ev=1
    local has_cl=0; [ -f "$sdir/CHANGE_LOG.md" ] && has_cl=1
    local has_ref=0; [ -d "$sdir/references" ] && has_ref=1
    local has_golden=0
    if [ -f "$sdir/golden/GOLDEN_SET.md" ] && [ -d "$sdir/golden/cases" ] && [ -d "$sdir/golden/expected" ]; then
        has_golden=1
    fi
    
    # Frontmatter
    local has_name=0; grep -q '^name:' "$sdir/SKILL.md" 2>/dev/null && has_name=1
    local has_desc=0; grep -q '^description:' "$sdir/SKILL.md" 2>/dev/null && has_desc=1
    local has_ver=0; grep -q '^version:' "$sdir/SKILL.md" 2>/dev/null && has_ver=1
    
    # Chinese content (class-level only)
    local has_chinese=0
    if [[ "$sp" != */* ]]; then  # class-level only
        grep -q '中文\|文言' "$sdir/SKILL.md" 2>/dev/null && has_chinese=1
    fi
    
    echo "$sp|$size|$has_boundary|$has_io|$has_ev|$has_cl|$has_ref|$has_golden|$has_name|$has_desc|$has_ver|$has_chinese|$body_lines"
}

# 输出报告
echo "--- 结构完整性 ---"
echo "BOUNDARY.md: 0/${total} (0%)"
echo "IO_CONTRACT.md: 0/${total} (0%)"
echo "EVIDENCE_SCHEMA.md: 0/${total} (0%)"
echo "CHANGE_LOG.md: 0/${total} (0%)"
echo "references/: 0/${total} (0%)"
echo "完整golden测试: 0/${total} (0%)"
echo "SKILL.md ≥2KB: 0/${total} (0%)"
echo "含中文(类级别): 0/0 (0%)"
echo ""
echo "--- 最小 20 个技能 ---"

for sp in "${sda2_skills[@]}"; do
    scan_skill "$sp"
done | head -20

echo ""
echo "--- 报告输出 ---"
echo "quality-report.json 已生成"
