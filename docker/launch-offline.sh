#!/bin/bash
# Hermes + OpenCode — Offline Portable Launcher (Linux/macOS)
# Pre-downloaded offline version. NO internet connection needed.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

DATA_DIR="$SCRIPT_DIR/data"
CACHE_DIR="$SCRIPT_DIR/.cache"
RUNTIME_DIR="$CACHE_DIR/runtimes"
SRC_DIR="$SCRIPT_DIR/src"
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

if [ "$OS" = "darwin" ]; then
    RUNTIME_DIR="$RUNTIME_DIR/macos-${ARCH}"
else
    RUNTIME_DIR="$RUNTIME_DIR/linux-${ARCH}"
fi

SRC_DIR="$SRC_DIR/hermes-agent"
mkdir -p "$DATA_DIR" "$SRC_DIR"

# Environment isolation
VIRTUAL_ENV="$RUNTIME_DIR/venv"
export PATH="$VIRTUAL_ENV/bin:$RUNTIME_DIR/python/bin:$RUNTIME_DIR/node/bin:$RUNTIME_DIR/bin:$PATH"
export PYTHONNOUSERSITE=1
export PYTHONHOME=
export PYTHONPATH=
export UV_NO_CONFIG=1
export UV_PYTHON="$RUNTIME_DIR/python/bin/python3"
export HERMES_HOME="$DATA_DIR"

# Fix pyvenv.cfg
if [ -f "$VIRTUAL_ENV/pyvenv.cfg" ]; then
    PYTHON_VERSION=$("$RUNTIME_DIR/python/bin/python3" --version 2>&1 | awk '{print $2}')
    echo "home = $RUNTIME_DIR/python/bin" > "$VIRTUAL_ENV/pyvenv.cfg"
    echo "include-system-site-packages = false" >> "$VIRTUAL_ENV/pyvenv.cfg"
    echo "version = $PYTHON_VERSION" >> "$VIRTUAL_ENV/pyvenv.cfg"
fi

# Verify
if [ ! -f "$RUNTIME_DIR/python/bin/python3" ]; then
    echo "[ERROR] Python not found. Extract offline package correctly."
    exit 1
fi

# Launch
if [ -n "$1" ]; then
    cd "$SRC_DIR"
    exec python3 -c "from hermes_cli.main import main; main()" "$@"
else
    clear
    echo ""
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║  Hermes + OpenCode — Offline Portable║"
    echo "  ╚═══════════════════════════════════════╝"
    echo ""
    echo "   [1] Start Chat (Hermes Agent)"
    echo "   [2] Start OpenCode CLI"
    echo "   [3] System Info"
    echo "   [0] Exit"
    echo ""
    read -r -p "Choose [0-3]: " choice

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
            echo "=== System Info ==="
            echo "Root:   $SCRIPT_DIR"
            echo "Runtime: $RUNTIME_DIR"
            echo "Source: $SRC_DIR"
            python3 --version
            node --version
            hermes --version
            du -sh "$SCRIPT_DIR"
            ;;
        0|*)
            exit 0
            ;;
    esac
fi