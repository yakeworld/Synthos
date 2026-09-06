#!/bin/bash
# Synthos 一键安装脚本
#
# 用法:
#   本地安装:    ./install.sh [--repo-dir /path/to/Synthos]
#   远程安装:    git clone --depth 1 --branch <TAG> https://github.com/yakeworld/Synthos.git /tmp/Synthos && /tmp/Synthos/install.sh
#
# 设计原则:
#   - 零硬编码路径: 仓库位置从脚本真实位置推导, 或 --repo-dir 显式指定
#   - 默认装用户目录 (~/.local/bin), 不碰 /usr/local, 不需要 sudo
#   - 修改 Hermes 配置前备份, 原子写入
#   - --dry-run 只显示将要做什么, 不写任何文件
#   - 基于固定 tag 安装 (见上方用法), 不默认跟踪不断变化的 main

set -euo pipefail

# ---------- 参数解析 ----------
REPO_DIR=""
DRY_RUN=0
SKIP_HERMES=0

while [ $# -gt 0 ]; do
  case "$1" in
    --repo-dir)   REPO_DIR="${2:?--repo-dir 需要路径参数}"; shift 2 ;;
    --dry-run)    DRY_RUN=1; shift ;;
    --skip-hermes) SKIP_HERMES=1; shift ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//' | sed -n '2,20p'; exit 0 ;;
    *) echo "未知参数: $1 (见 --help)" >&2; exit 2 ;;
  esac
done

# ---------- 定位仓库根 ----------
# 本地运行: 脚本在 <repo>/install.sh, 父目录即仓库根
# 若推导结果无 SKILL.md, 则要求显式 --repo-dir (curl|bash 场景下 $0 不可靠)
if [ -z "$REPO_DIR" ]; then
  REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
fi
if [ ! -f "$REPO_DIR/SKILL.md" ]; then
  echo "❌ 无法在 $REPO_DIR 找到 SKILL.md" >&2
  echo "   请用 --repo-dir 指定仓库根目录" >&2
  exit 1
fi
REPO_DIR="$(cd "$REPO_DIR" && pwd)"

# 校验关键子目录
[ -d "$REPO_DIR/skills/core" ] || { echo "❌ $REPO_DIR/skills/core 不存在, 不是完整 Synthos 仓库" >&2; exit 1; }

# 安装目标 (用户目录, 无 sudo)
BIN_DIR="${SYNTHOS_BIN_DIR:-$HOME/.local/bin}"
HERMES_CONFIG="${HOME}/.hermes/config.yaml"

if [ "$DRY_RUN" = 1 ]; then
  echo "🧪 [dry-run] 仓库: $REPO_DIR"
  echo "   将安装 CLI:  $BIN_DIR/synthos"
  [ "$SKIP_HERMES" = 0 ] && [ -f "$HERMES_CONFIG" ] && \
    echo "   将修改配置: $HERMES_CONFIG (先备份到 ${HERMES_CONFIG}.bak-$(date +%Y%m%d%H%M%S))"
  [ -f "$REPO_DIR/philosophy/SOUL.md" ] && \
    echo "   将链接 SOUL: ${HOME}/.hermes/SOUL.md (已有则备份)"
  exit 0
fi

# ---------- 前置检查 ----------
python3 --version >/dev/null 2>&1 || { echo "❌ 需要 python3" >&2; exit 1; }

# ---------- 1. 安装 synthos CLI (用户目录) ----------
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/synthos" <<CLI
#!/bin/bash
# Synthos CLI — 仓库: $REPO_DIR
REPO="$REPO_DIR"
cmd="\${1:-help}"; shift || true
case "\$cmd" in
  skills)    ls "\$REPO/skills/core" ;;
  run)       echo "加载 core/task-router 技能后由 Agent 执行: \$*" ;;
  status)    echo "repo: \$REPO"; ls "\$REPO/skills/core/" | head -5 ;;
  *)         head -20 "\$REPO/README.md" 2>/dev/null || echo "usage: synthos {skills|run|status|help}" ;;
esac
CLI
chmod +x "$BIN_DIR/synthos"
echo "✅ synthos CLI → $BIN_DIR/synthos"
case ":$PATH:" in *":$BIN_DIR:"*) ;; *) echo "   ⚠️  $BIN_DIR 不在 PATH, 请添加: export PATH=\"$BIN_DIR:\$PATH\"" ;; esac

# ---------- 2. 配置 Hermes external_dirs (备份 + 原子写) ----------
if [ "$SKIP_HERMES" = 0 ] && [ -f "$HERMES_CONFIG" ]; then
  BACKUP="${HERMES_CONFIG}.bak-$(date +%Y%m%d%H%M%S)"
  cp "$HERMES_CONFIG" "$BACKUP"
  echo "✅ Hermes 配置已备份 → $BACKUP"
  python3 - "$HERMES_CONFIG" "$REPO_DIR/skills" <<'PYEOF'
import sys, os
cfg_path, skills_dir = sys.argv[1], sys.argv[2]
try:
    import yaml
except ImportError:
    sys.exit("❌ 需要 python3-yaml (pip install pyyaml / apt install python3-yaml)")
with open(cfg_path) as f:
    cfg = yaml.safe_load(f) or {}
skills = cfg.setdefault('skills', {})
dirs = skills.setdefault('external_dirs', [])
if skills_dir not in dirs:
    dirs.append(skills_dir)
    tmp = cfg_path + '.tmp'
    with open(tmp, 'w') as f:
        yaml.safe_dump(cfg, f, allow_unicode=True, default_flow_style=False)
    os.replace(tmp, cfg_path)  # 原子替换
    print(f"✅ external_dirs 追加: {skills_dir}")
else:
    print("ℹ️  external_dirs 已包含该路径, 跳过 (重复安装安全)")
PYEOF
elif [ "$SKIP_HERMES" = 0 ]; then
  echo "ℹ️  未找到 $HERMES_CONFIG, 跳过 Hermes 配置 (可稍后手动添加 external_dirs)"
fi

# ---------- 3. SOUL.md 链接 (已有则先备份) ----------
if [ -f "$REPO_DIR/philosophy/SOUL.md" ]; then
  TARGET="${HOME}/.hermes/SOUL.md"
  if [ -L "$TARGET" ] && [ "$(readlink "$TARGET")" = "$REPO_DIR/philosophy/SOUL.md" ]; then
    echo "ℹ️  SOUL.md 已链接, 跳过"
  else
    mkdir -p "${HOME}/.hermes"
    if [ -e "$TARGET" ] && [ ! -L "$TARGET" ]; then
      cp "$TARGET" "${TARGET}.bak-$(date +%Y%m%d%H%M%S)"
      echo "   已有 SOUL.md 已备份"
    fi
    ln -sf "$REPO_DIR/philosophy/SOUL.md" "$TARGET"
    echo "✅ SOUL.md → $TARGET"
  fi
fi

# ---------- 4. 凭据模板 (不覆盖已有) ----------
if [ ! -f "${HOME}/.secrets.template" ]; then
  cat > "${HOME}/.secrets.template" << 'TEMPLATE'
# Synthos 凭据模板 — 复制为 ~/.secrets 并填值, chmod 600 ~/.secrets
# 注意: 禁止把真实 key 提交进任何 git 仓库 (2026-09 历史事故后铁律)
export SEMANTIC_SCHOLAR_API_KEY=""
export PUBSCHOLAR_SALT=""
TEMPLATE
  echo "✅ 凭据模板 → ~/.secrets.template"
fi

# ---------- 5. 外部工具检测 (只提示, 不安装) ----------
for tool in jabkit-rs doi-fetch; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "   ✅ 外部工具: $tool ($(command -v "$tool"))"
  else
    echo "   ℹ️  未找到 $tool (文献检索需要, 按需安装: 见 skills/ 下对应技能文档)"
  fi
done

echo ""
echo "✅ Synthos 安装完成 (仓库: $REPO_DIR)"
echo ""
echo "验证:"
synthos status 2>/dev/null | head -3 || echo "  (synthos CLI 需先刷新 PATH)"
echo ""
echo "下一步:"
echo "  1. cp ~/.secrets.template ~/.secrets && chmod 600 ~/.secrets, 填入 API key"
echo "  2. 在 Hermes 会话中验证: 技能列表应出现 task-router / quality-gate 等 core 技能"
