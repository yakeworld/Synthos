#!/usr/bin/env bash
# gen-dsh-flat.sh — 从 Synthos 嵌套技能目录生成 dsh 一层展平视图(symlink)
# 用法: ./gen-dsh-flat.sh [源技能目录] [展平输出目录]
# 默认: 源=/media/yakeworld/sda2/Synthos/skills  输出=~/.dsh/skills-flat
# 原理: dsh 的 skill-filesystem 只认 <root>/<name>/SKILL.md(一层),
#        Synthos 源是 <root>/<category>/<skill>/SKILL.md(嵌套)。
#        本脚本用 symlink 把每个技能目录展平到单层根,零修改真相源。
# 幂等: 每次运行删除重建展平根,可从真相源随时再生成。
set -euo pipefail

SRC="${1:-/media/yakeworld/sda2/Synthos/skills}"
DST="${2:-$HOME/.dsh/skills-flat}"

[ -d "$SRC" ] || { echo "ERROR: 源目录不存在: $SRC" >&2; exit 1; }

echo "源: $SRC"
echo "展平根: $DST"

rm -rf "$DST"
mkdir -p "$DST"

declare -A seen
conflicts=""
linked=0
skipped=0

while IFS= read -r f; do
  d=$(dirname "$f")
  n=$(basename "$d")
  if [[ -n "${seen[$n]:-}" ]]; then
    conflicts+=" $n(${seen[$n]}|$d)"
    skipped=$((skipped+1))
    continue
  fi
  seen[$n]=$d
  ln -sfn "$d" "$DST/$n"
  linked=$((linked+1))
done < <(find "$SRC" -mindepth 2 -name SKILL.md)

# frontmatter 校验:dsh 要求 name + description 存在,否则该技能被发现时被丢弃
bad=0
for d in "$DST"/*/; do
  n=$(basename "$d")
  [ -f "$d/SKILL.md" ] || continue
  if ! grep -qE '^name:' "$d/SKILL.md" || ! grep -qE '^description:' "$d/SKILL.md"; then
    echo "MISSING-FM: $n"
    bad=$((bad+1))
  fi
done

echo "----------------------------------------"
echo "symlinked=$linked  dup_skipped=$skipped  bad_frontmatter=$bad"
[ -n "$conflicts" ] && echo "CONFLICTS:$conflicts"
echo "总技能: $(ls "$DST" | wc -l)"

# 提示更新 dsh 配置
echo "----------------------------------------"
echo "确认 ~/.dsh/profiles/headless/cordis.patch.yml 的 customSkillDirs 含:"
echo "  - $DST"
echo "验证: dsh --profile headless \"List available skills and count them.\""
