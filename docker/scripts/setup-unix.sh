#!/bin/bash
# Hermes + OpenCode — Portable Setup (Linux/macOS)
# Downloads portable Python, Node.js, uv, clones Hermes, creates venv.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$SCRIPT_DIR}"

CACHE_DIR="$ROOT/.cache"
RUNTIME_DIR="$CACHE_DIR/runtimes"
SRC_DIR="$ROOT/src"
DATA_DIR="$ROOT/data"

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

if [ "$OS" = "darwin" ]; then
    RUNTIME_DIR="$RUNTIME_DIR/macos-${ARCH}"
    PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20260623/cpython-3.11.15+202****0623-x86_64-apple-darwin-install_only_stripped.tar.gz"
else
    RUNTIME_DIR="$RUNTIME_DIR/linux-${ARCH}"
    if [ "$ARCH" = "x86_64" ]; then
        PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20260623/cpython-3.11.15+202****0623-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz"
    else
        PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20260623/cpython-3.11.15+202****0623-aarch64-unknown-linux-gnu-install_only_stripped.tar.gz"
    fi
fi

NODE_URL="https://nodejs.org/dist/v22.22.3/node-v22.22.3-${OS}-${ARCH}.tar.gz"
UV_URL="https://github.com/astral-sh/uv/releases/download/0.11.19/uv-${ARCH}-${OS}.zip"
SOURCE_URL="https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip"

mkdir -p "$RUNTIME_DIR" "$SRC_DIR" "$DATA_DIR"

function write_step { echo ""; echo "[SETUP] $1" -ForegroundColor Cyan; }
function write_done { echo "[OK]    $1"; }
function write_warn { echo "[WARN]  $1" -ForegroundColor Yellow; }

# ── Python ───────────────────────────────────────────────────
write_step "Downloading Python 3.11 (standalone)..."
curl -L -f --retry 3 --max-time 900 -o /tmp/python.tar.gz "$PYTHON_URL"
tar -xzf /tmp/python.tar.gz -C "$RUNTIME_DIR"
# Flatten
sub=$(ls -1 "$RUNTIME_DIR" | head -1)
if [ -n "$sub" ] && [ -d "$RUNTIME_DIR/$sub" ]; then
    mv "$RUNTIME_DIR/$sub/"* "$RUNTIME_DIR/"
    rmdir "$RUNTIME_DIR/$sub"
fi
write_done "Python 3.11 ready"

# ── Node.js ──────────────────────────────────────────────────
write_step "Downloading Node.js 22 LTS..."
curl -L -f --retry 3 --max-time 900 -o /tmp/node.tar.gz "$NODE_URL"
tar -xzf /tmp/node.tar.gz -C "$RUNTIME_DIR"
# Flatten
sub=$(ls -1 "$RUNTIME_DIR" | grep "node-v" | head -1)
if [ -n "$sub" ] && [ -d "$RUNTIME_DIR/$sub" ]; then
    mv "$RUNTIME_DIR/$sub/"* "$RUNTIME_DIR/"
    rmdir "$RUNTIME_DIR/$sub"
fi
write_done "Node.js 22 ready"

# ── uv ───────────────────────────────────────────────────────
write_step "Downloading uv..."
curl -L -f --retry 3 --max-time 300 -o /tmp/uv.zip "$UV_URL"
unzip -o /tmp/uv.zip -d "$RUNTIME_DIR" 2>/dev/null || true
chmod +x "$RUNTIME_DIR/uv" 2>/dev/null || true
write_done "uv ready"

# ── venv ─────────────────────────────────────────────────────
write_step "Creating virtual environment..."
VENV_PATH="$RUNTIME_DIR/venv"
rm -rf "$VENV_PATH"
"$RUNTIME_DIR/python/bin/python3" -m venv "$VENV_PATH"
write_done "Virtual environment created"

# ── Install Hermes ───────────────────────────────────────────
write_step "Installing Hermes Agent..."
"$RUNTIME_DIR/venv/bin/pip" install hermes-agent 2>&1
write_done "Hermes Agent installed"

# ── Clone source ─────────────────────────────────────────────
write_step "Cloning Hermes source..."
if [ ! -d "$SRC_DIR" ]; then
    git clone --depth 1 https://github.com/NousResearch/hermes-agent.git "$SRC_DIR" 2>&1 || true
    write_done "Source cloned"
else
    write_done "Source already present"
fi

# ── Config ───────────────────────────────────────────────────
write_step "Creating default configuration..."
if [ ! -f "$DATA_DIR/.env" ]; then
    cat > "$DATA_DIR/.env" << 'EOF'
# Add your API keys below
OPENROUTER_API_KEY=sk-or-...
EOF
fi

if [ ! -f "$DATA_DIR/config.yaml" ]; then
    cat > "$DATA_DIR/config.yaml" << 'EOF'
# Hermes Agent configuration
model:
  default: qwen3.6-35b-nvfp4
  provider: custom:local

custom_providers:
  - name: local
    base_url: http://localhost:8000/v1
    api_key: EMPTY
    model: qwen3.6-35b-nvfp4

agent:
  max_turns: 150
  gateway_timeout: 1800
EOF
fi

# ── Done ─────────────────────────────────────────────────────
touch "$RUNTIME_DIR/ready.flag"

echo ""
echo "============================================================"
echo "  Setup complete! Run ./launch.sh to start."
echo "============================================================"
echo ""
echo "  Next steps:"
echo "    1. Edit data/.env — add your API keys"
echo "    2. Run ./launch.sh"
echo ""
du -sh "$ROOT"