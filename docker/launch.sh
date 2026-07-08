#!/bin/bash
# Hermes + OpenCode — Portable Launcher (Linux/macOS)
# Run: ./launch.sh
# Zero dependencies. All runtimes downloaded into this directory.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

DATA_DIR="$SCRIPT_DIR/data"
CACHE_DIR="$SCRIPT_DIR/.cache"
RUNTIME_DIR="$CACHE_DIR/runtimes"
SRC_DIR="$SCRIPT_DIR/src"
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

if [ "$OS" = "darwin" ]; then
    RUNTIME_DIR="$CACHE_DIR/runtimes/macos-${ARCH}"
else
    RUNTIME_DIR="$CACHE_DIR/runtimes/linux-${ARCH}"
fi

SRC_DIR="$SRC_DIR/hermes-agent"

mkdir -p "$DATA_DIR" "$CACHE_DIR" "$RUNTIME_DIR" "$SRC_DIR"

# ── First-run setup ──────────────────────────────────────────
if [ ! -f "$RUNTIME_DIR/ready.flag" ]; then
    echo ""
    echo "============================================================"
    echo "  Hermes + OpenCode — Portable Setup"
    echo "============================================================"
    echo "  Downloading runtimes for $OS $ARCH..."
    echo "  Total: ~800MB. Please be patient."
    echo "============================================================"
    echo ""
    bash "$SCRIPT_DIR/scripts/setup-unix.sh" "$SCRIPT_DIR"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Setup failed."
        exit 1
    fi
fi

# ── Environment isolation ───────────────────────────────────
VIRTUAL_ENV="$RUNTIME_DIR/venv"
export PATH="$VIRTUAL_ENV/bin:$RUNTIME_DIR/python/bin:$RUNTIME_DIR/node/bin:$RUNTIME_DIR/bin:$PATH"
export PYTHONNOUSERSITE=1
export PYTHONHOME=
export PYTHONPATH=
export UV_NO_CONFIG=1
export UV_PYTHON="$RUNTIME_DIR/python/bin/python3"
export HERMES_HOME="$DATA_DIR"
export PLAYWRIGHT_BROWSERS_PATH="$RUNTIME_DIR/playwright"

# ── Fix pyvenv.cfg ──────────────────────────────────────────
if [ -f "$VIRTUAL_ENV/pyvenv.cfg" ]; then
    PYTHON_VERSION=$("$RUNTIME_DIR/python/bin/python3" --version 2>&1 | awk '{print $2}')
    echo "home = $RUNTIME_DIR/python/bin" > "$VIRTUAL_ENV/pyvenv.cfg"
    echo "include-system-site-packages = false" >> "$VIRTUAL_ENV/pyvenv.cfg"
    echo "version = $PYTHON_VERSION" >> "$VIRTUAL_ENV/pyvenv.cfg"
fi

# ── Launch ──────────────────────────────────────────────────
if [ -n "$1" ]; then
    cd "$SRC_DIR"
    exec python3 -c "from hermes_cli.main import main; main()" "$@"
else
    # Interactive menu
    clear
    echo ""
    echo "  ╔═══════════════════════════════════════════╗"
    echo "  ║  Hermes + OpenCode — Portable Edition     ║"
    echo "  ╚═══════════════════════════════════════════╝"
    echo ""
    echo "   [1] Start Chat (Hermes Agent)"
    echo "   [2] Start OpenCode CLI"
    echo "   [3] Setup API Keys"
    echo "   [4] System Info"
    echo "   [5] Update"
    echo "   [0] Exit"
    echo ""
    read -r -p "Choose [0-5]: " choice

    case "$choice" in
        1)
            cd "$SRC_DIR"
            exec python3 -c "from hermes_cli.main import main; main()"
            ;;
        2)
            cd "$SCRIPT_DIR"
            exec opencode
            ;;
        3)
            echo "Edit $DATA_DIR/.env for API keys"
            echo "Edit $DATA_DIR/config.yaml for models"
            ;;
        4)
            echo "=== System Info ==="
            echo "Root:    $SCRIPT_DIR"
            echo "Data:    $DATA_DIR"
            echo "Runtime: $RUNTIME_DIR"
            echo "Source:  $SRC_DIR"
            echo ""
            python3 --version
            node --version
            hermes --version
            opencode --version
            du -sh "$SCRIPT_DIR"
            ;;
        5)
            echo "Updating..."
            cd "$SRC_DIR"
            git pull 2>/dev/null || git clone --depth 1 https://github.com/NousResearch/hermes-agent.git "$SRC_DIR" 2>/dev/null
            pip install --upgrade hermes-agent 2>&1
            echo "Done!"
            ;;
        0|*)
            exit 0
            ;;
    esac
fi