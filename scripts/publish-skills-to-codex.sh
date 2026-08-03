#!/bin/bash
# publish-skills-to-codex.sh — Synthos 技能投影到 codex 加载区
#
# 设计 (2026-08-02 验证):
#   - codex 只扫 ~/.codex/skills/, 深度 ≤3 层全发现, 4-5 层仅 ~31%
#   - codex skills context budget = 2%: 156 技能全加载会超限,
#     超限后所有技能描述被移除 (模型看不到描述=不知道该用哪个技能)
#   - 分层投影: core 常驻, standard 白名单常驻, 其余按需 (不投影)
#   - 投影层用 symlink (零拷贝, 源技能更新即时生效, 相对引用保持)
#   - 绝不复制 — 129/156 技能有 references/scripts 相对引用, 复制会断链
#
# 用法:
#   ./publish-skills-to-codex.sh              # standard (默认): core 8 + 白名单
#   ./publish-skills-to-codex.sh --tier core  # 仅 core 8
#   ./publish-skills-to-codex.sh --tier full  # 全量 156 (会触发 codex budget 超限)
#   ./publish-skills-to-codex.sh --check      # 只报告当前覆盖率
#
# 退出码: 0=OK, 1=未达标 (供 cron 告警)

set -euo pipefail

SYNTHOS_ROOT="/media/yakeworld/sda2/Synthos"
SKILLS_SRC="$SYNTHOS_ROOT/skills"
CODEX_SKILLS="$HOME/.codex/skills"
WHITELIST="$SKILLS_SRC/codex-tier-standard.txt"

# ---- 参数解析 ----
TIER="standard"
MODE="publish"
ARGS=("$@")
for ((i=0; i<${#ARGS[@]}; i++)); do
  case "${ARGS[$i]}" in
    --tier)
      # 取下一个参数作为值
      if [ $((i+1)) -lt ${#ARGS[@]} ]; then
        TIER="${ARGS[$((i+1))]}"
        i=$((i+1))
      else
        echo "错误: --tier 需要值 (core|standard|full)" >&2; exit 2
      fi
      ;;
    --tier=*) TIER="${ARGS[$i]#--tier=}" ;;
    --check) MODE="check" ;;
  esac
done
case "$TIER" in
  core|standard|full) ;;
  *) echo "错误: 未知 tier '$TIER' (可用: core|standard|full)" >&2; exit 2 ;;
esac

# ---- 函数: 统计投影层可达 SKILL.md 数 ----
# 只数投影层直接子目录的 SKILL.md (maxdepth 2 = synthos-xxx/<技能>/SKILL.md)
count_visible() {
  local n=0
  for p in "${PREFIXES[@]:-}"; do
    if [ -d "$CODEX_SKILLS/$p" ]; then
      n=$(( n + $(find -L "$CODEX_SKILLS/$p" -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l) ))
    fi
  done
  echo "$n"
}

# ---- --check 模式: 只报告 ----
if [ "$MODE" = "check" ]; then
  PREFIXES=("synthos-core" "synthos-ext" "synthos-priv")
  VIS=$(count_visible)
  echo "codex 投影技能数: $VIS"
  echo "(目标: core=8, standard≈$(grep -vc '^#\|^$' "$WHITELIST" 2>/dev/null || echo 0)+8, full=156)"
  exit 0
fi

echo "== Synthos 技能投影到 codex (tier=$TIER) =="

# ---- 清理旧投影 ----
for p in synthos-core synthos-ext synthos-priv; do
  if [ -L "$CODEX_SKILLS/$p" ]; then
    rm -f "$CODEX_SKILLS/$p"
  elif [ -d "$CODEX_SKILLS/$p" ]; then
    # 旧版脚本留下的真实目录 (内含本项目 symlink), 清空 symlink 后删目录
    find "$CODEX_SKILLS/$p" -maxdepth 1 -type l -exec rm {} \; 2>/dev/null || true
    rmdir "$CODEX_SKILLS/$p" 2>/dev/null || rm -rf "$CODEX_SKILLS/$p"
  fi
done

# ---- 1. synthos-core: 整目录 symlink (始终投影) ----
ln -s "$SKILLS_SRC/core" "$CODEX_SKILLS/synthos-core"
echo "synthos-core -> skills/core (8 技能)"

# ---- 2. 确定投影集 ----
declare -A PROJ  # name -> 源目录
case "$TIER" in
  core)
    # 只投影 core (已做), ext/priv 不投影
    ;;
  standard)
    # 白名单匹配: 在 extended/private 中找目录名匹配的技能
    while IFS= read -r wl; do
      [ -z "$wl" ] && continue
      # 在源中找匹配的技能目录 (最后一段 = 白名单名)
      while IFS= read -r sd; do
        name=$(basename "$sd")
        [ "$name" = "$wl" ] && PROJ["$name"]="$sd"
      done < <(find "$SKILLS_SRC/extended" "$SKILLS_SRC/private" -name SKILL.md -printf '%h\n' 2>/dev/null | sort -u)
    done < <(grep -v '^#' "$WHITELIST" | grep -v '^$')
    ;;
  full)
    while IFS= read -r sd; do
      name=$(basename "$sd")
      PROJ["$name"]="$sd"
    done < <(find "$SKILLS_SRC/extended" "$SKILLS_SRC/private" -name SKILL.md -printf '%h\n' 2>/dev/null | sort -u)
    ;;
esac

# ---- 3. 投影到 ext/priv 分区 ----
# 按源路径分区: extended → synthos-ext, private → synthos-priv
ext_count=0; priv_count=0
for name in "${!PROJ[@]}"; do
  src="${PROJ[$name]}"
  case "$src" in
    "$SKILLS_SRC/extended"*) TARGET="$CODEX_SKILLS/synthos-ext" ;;
    "$SKILLS_SRC/private"*)  TARGET="$CODEX_SKILLS/synthos-priv" ;;
    *) continue ;;
  esac
  mkdir -p "$TARGET"
  if [ ! -e "$TARGET/$name" ]; then
    ln -s "$src" "$TARGET/$name"
    if [ "$TARGET" = "$CODEX_SKILLS/synthos-ext" ]; then ext_count=$((ext_count+1)); else priv_count=$((priv_count+1)); fi
  fi
done
echo "synthos-ext: $ext_count 技能, synthos-priv: $priv_count 技能"

# ---- 4. 覆盖率报告 ----
PREFIXES=("synthos-core" "synthos-ext" "synthos-priv")
VIS=$(count_visible)
TOTAL=$(find "$SKILLS_SRC" -name SKILL.md | wc -l)
echo ""
echo "== 投影: $VIS 技能 (tier=$TIER, 全量 $TOTAL) =="
if [ "$TIER" = "standard" ]; then
  WLCNT=$(grep -vc '^#\|^$' "$WHITELIST")
  echo "白名单: $WLCNT 条 (core 8 + 白名单匹配 ext/priv)"
fi
echo "✓ 发布完成"
exit 0
