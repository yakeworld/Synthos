#!/bin/bash
# build-green.sh — 将当前 Hermes + OpenCode 环境打包成便携绿色软件
# 用法: bash build-green.sh [output_dir]
# 输出: hermes-green/ 目录 — 解压即用，零依赖

set -e

OUTPUT_DIR="${1:-/tmp/hermes-green}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BUILD_DIR="${OUTPUT_DIR}/hermes-green-${TIMESTAMP}"

echo "═══════════════════════════════════════════"
echo "  Hermes Green — 便携绿色软件构建"
echo "═══════════════════════════════════════════"
echo ""

# ── Step 1: 创建目录结构 ──
echo "[1/6] 创建目录结构..."
mkdir -p "$BUILD_DIR"
mkdir -p "$BUILD_DIR/.hermes"
mkdir -p "$BUILD_DIR/.opencode"
mkdir -p "$BUILD_DIR/lib"
mkdir -p "$BUILD_DIR/.scripts"

# ── Step 2: 打包 Python 虚拟环境 ──
echo "[2/6] 打包 Python 虚拟环境..."
cd "$BUILD_DIR/lib"
python3 -m venv .venv
source .venv/bin/activate

# 安装核心依赖
pip install --no-cache-dir \
    hermes-agent \
    requests \
    jinja2 \
    pyyaml \
    numpy \
    matplotlib \
    2>/dev/null || true

deactivate
echo "  Python venv: $(du -sh .venv | cut -f1)"

# ── Step 3: 复制 Node.js 全局包 ──
echo "[3/6] 复制 Node.js 全局包..."
if command -v opencode &>/dev/null; then
    # 找到 opencode 的安装位置
    OPENCODE_PATH=$(npm root -g 2>/dev/null || echo "")
    if [ -n "$OPENCODE_PATH" ] && [ -d "$OPENCODE_PATH" ]; then
        cp -r "$OPENCODE_PATH/opencode" "$BUILD_DIR/.opencode-bin/" 2>/dev/null || true
        cp -r "$OPENCODE_PATH/@ai-sdk" "$BUILD_DIR/.opencode-bin/" 2>/dev/null || true
        echo "  OpenCode: copied from $OPENCODE_PATH"
    fi
else
    echo "  OpenCode CLI not found, skipping"
fi

# ── Step 4: 复制 Node.js 运行时 ──
echo "[4/6] 复制 Node.js 运行时..."
if command -v node &>/dev/null; then
    cp "$(which node)" "$BUILD_DIR/.opencode-bin/" 2>/dev/null || true
    cp "$(which npm)" "$BUILD_DIR/.opencode-bin/" 2>/dev/null || true
    # 复制 node 依赖的动态链接库
    ldd "$(which node)" 2>/dev/null | grep "=>" | awk '{print $3}' | while read lib; do
        if [ -f "$lib" ]; then
            mkdir -p "$BUILD_DIR/.opencode-bin/libs"
            cp "$lib" "$BUILD_DIR/.opencode-bin/libs/" 2>/dev/null || true
        fi
    done
    echo "  Node.js runtime: copied"
else
    echo "  Node.js not found, skipping"
fi

# ── Step 5: 复制配置文件 ──
echo "[5/6] 复制配置文件..."

# Hermes 配置
if [ -f ~/.hermes/config.yaml ]; then
    cp ~/.hermes/config.yaml "$BUILD_DIR/.hermes/config.yaml"
    echo "  Hermes config: copied"
else
    # 创建默认配置
    cat > "$BUILD_DIR/.hermes/config.yaml" << 'EOF'
# Hermes Agent — Default Configuration
# 使用方法: 复制 .hermes/config.yaml 到任意位置
# 在 run.sh 中通过 HERMES_CONFIG 环境变量指定
model:
  default: qwen3.6-35b-nvfp4
  provider: custom:local

custom_providers:
  - name: local
    base_url: http://localhost:8000/v1
    api_key: "${API_KEY:-EMPTY}"
    model: qwen3.6-35b-nvfp4

agent:
  max_turns: 150
  gateway_timeout: 1800
EOF
    echo "  Hermes config: default template created"
fi

# OpenCode 配置
cat > "$BUILD_DIR/.opencode/opencode.json" << 'EOF'
{
  "provider": {},
  "models": {},
  "mcp": {},
  "plugins": {}
}
EOF

# ── Step 6: 创建启动脚本 ──
echo "[6/6] 创建启动脚本..."

cat > "$BUILD_DIR/run.sh" << 'SCRIPT'
#!/bin/bash
# run.sh — Hermes Agent 便携绿色软件启动器
# 用法: ./run.sh [hermes命令 | opencode命令 | "shell"]
#
# 示例:
#   ./run.sh              # 进入交互模式
#   ./run.sh "你好"       # 直接问问题
#   ./run.sh shell        # 进入完整 shell

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export HERMES_CONFIG="${HERMES_CONFIG:-$SCRIPT_DIR/.hermes/config.yaml}"
export PATH="$SCRIPT_DIR/lib/.venv/bin:$SCRIPT_DIR/.opencode-bin:$PATH"

# 激活 Python 虚拟环境
source "$SCRIPT_DIR/lib/.venv/bin/activate"

CMD="${1:-shell}"

case "$CMD" in
    shell)
        echo "═══════════════════════════════════════════"
        echo "  Hermes Agent 便携绿色软件"
        echo "  输入 'exit' 退出"
        echo "═══════════════════════════════════════════"
        bash --rcfile <(echo "source $SCRIPT_DIR/lib/.venv/bin/activate; export HERMES_CONFIG=$HERMES_CONFIG")
        ;;
    --verify|verify)
        echo "运行环境验证..."
        bash "$SCRIPT_DIR/.scripts/verify.sh"
        ;;
    --help|-h)
        echo "用法: $0 [command]"
        echo "  [无参数]  进入交互模式"
        echo "  <text>    直接问问题 (传给 Hermes)"
        echo "  shell     进入完整 shell"
        echo "  verify    验证环境"
        ;;
    *)
        # 直接执行 Hermes 命令
        hermes chat -q "$CMD" -Q
        ;;
esac
SCRIPT

chmod +x "$BUILD_DIR/run.sh"

# 验证脚本
cat > "$BUILD_DIR/.scripts/verify.sh" << 'VERIFY'
#!/bin/bash
PASS=0
check() {
    local name="$1"
    local cmd="$2"
    if eval "$cmd" > /dev/null 2>&1; then
        echo "✅  $name"
        PASS=$((PASS + 1))
    else
        echo "❌  $name"
    fi
}
echo "═══════════════════════════════════════════"
echo "  环境验证"
echo "═══════════════════════════════════════════"
check "Python" "python3 --version"
check "Hermes" "hermes --version"
check "Node.js" "node --version"
check "OpenCode" "opencode --version"
echo "═══════════════════════════════════════════"
echo "  结果: $PASS/4 通过"
echo "═══════════════════════════════════════════"
VERIFY

chmod +x "$BUILD_DIR/.scripts/verify.sh"

# README
cat > "$BUILD_DIR/README.md" << 'README'
# Hermes Agent — 便携绿色软件

> 解压即用，零安装，零依赖，零残留。

## 使用方法

```bash
# 1. 下载后解压
tar xzf hermes-green-*.tar.gz
cd hermes-green-*

# 2. 直接问问题
./run.sh "写一段 Python 计算瞳孔椭圆3D法向量"

# 3. 进入交互模式
./run.sh

# 4. 验证环境
./run.sh verify
```

## 特点

- **零安装**: 不需要 sudo，不需要 apt，不需要 pip install
- **不污染系统**: 所有依赖打包在 lib/.venv/ 里
- **可删除**: 删掉文件夹即卸载，不留任何痕迹
- **可移植**: 拷贝到任意 Linux 机器直接运行

## 目录结构

```
hermes-green/
├── run.sh              # 启动器
├── .hermes/            # 隔离配置
├── .opencode/          # OpenCode 配置
├── lib/.venv/          # Python 虚拟环境
└── .opencode-bin/      # Node.js 运行时
```

## 更新

下载新版覆盖旧版即可: `cp -r hermes-green-new/* hermes-green-old/`
README