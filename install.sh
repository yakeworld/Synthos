#!/bin/bash
# Synthos 一键安装脚本
# 用法: curl -sL https://github.com/yakeworld/Synthos/raw/main/install.sh | bash

set -e

SYNTHOS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "📦 安装 Synthos 到 $SYNTHOS_DIR"

# 1. 安装 literature CLI
echo "🔧 安装 literature CLI..."
cat > /usr/local/bin/literature << 'SCRIPT'
#!/bin/bash
LIT="/media/yakeworld/sda2/Synthos/skills/extended/research-tools/research/literature/scripts/literature.py"
exec python3 "$LIT" "$@"
SCRIPT
chmod +x /usr/local/bin/literature

# 2. 配置 Hermes external_dirs
echo "🔗 配置 Hermes 技能路径..."
HERMES_CONFIG="${HOME}/.hermes/config.yaml"
if [ -f "$HERMES_CONFIG" ]; then
    # 添加 external_dirs 指向 Synthos skills
    python3 -c "
import yaml
cfg = yaml.safe_load(open('$HERMES_CONFIG'))
if 'skills' not in cfg: cfg['skills'] = {}
if 'external_dirs' not in cfg['skills']: cfg['skills']['external_dirs'] = []
if '$SYNTHOS_DIR/skills' not in cfg['skills']['external_dirs']:
    cfg['skills']['external_dirs'].append('$SYNTHOS_DIR/skills')
yaml.dump(cfg, open('$HERMES_CONFIG', 'w'))
"
fi

# 3. Symlink SOUL.md
echo "📜 链接 SOUL.md..."
if [ -f "$SYNTHOS_DIR/philosophy/SOUL.md" ]; then
    ln -sf "$SYNTHOS_DIR/philosophy/SOUL.md" "${HOME}/.hermes/SOUL.md"
fi

# 4. 创建凭据模板
echo "🔑 创建凭据模板..."
if [ ! -f "${HOME}/.secrets" ]; then
    cat > "${HOME}/.secrets.template" << 'TEMPLATE'
# Synthos 凭据
export SEMANTIC_SCHOLAR_API_KEY="your_key_here"
export S2_FALLBACK_KEY="s2k-your_fallback_key"
export MEDDATA_USERNAME="your_username"
export MEDDATA_PASSWORD="your_password"
TEMPLATE
    echo "  凭据模板: ~/.secrets.template"
fi

# 5. 验证
echo ""
echo "✅ Synthos 安装完成"
echo ""
echo "验证:"
which literature && echo "  literature CLI: ✅"
ls "$SYNTHOS_DIR/skills/core/" | head -5 && echo "  core skills: ✅"
ls "${HOME}/.hermes/SOUL.md" 2>/dev/null && echo "  SOUL.md: ✅"
echo ""
echo "下一步:"
echo "  1. 编辑 ~/.secrets 填入 API key"
echo "  2. literature search 'test' --sources crossref --max 1"
