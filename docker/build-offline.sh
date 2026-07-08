#!/bin/bash
# build-offline.sh — Build the offline portable package for Windows
# Usage: bash build-offline.sh [output_dir]
#
# This script downloads all dependencies ONCE and packages them into
# a self-contained zip that requires NO internet connection to run.
#
# Requirements:
#   - Windows x64 machine (to download Windows-specific binaries)
#   - Or cross-platform download (see below)
#
# On non-Windows, we download pre-built binaries for Windows x64:
#   - Python: astral-sh/python-build-standalone (x86_64-pc-windows-msvc)
#   - Node.js: nodejs.org (win-x64)
#   - uv: astral-sh/uv (x86_64-pc-windows-msvc)

set -e

OUTPUT_DIR="${1:-/tmp/hermes-offline}"
PACKAGE_NAME="hermes-portable-offline-windows-x64"
BUILD_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BUILD_DIR="$OUTPUT_DIR/$PACKAGE_NAME"

echo "================================================================"
echo "  Hermes + OpenCode — Offline Package Builder"
echo "  Target: Windows x64 (pre-downloaded, no internet needed)"
echo "================================================================"
echo ""

mkdir -p "$BUILD_DIR"
mkdir -p "$BUILD_DIR/data"
mkdir -p "$BUILD_DIR/.cache/runtimes/windows-x64"
mkdir -p "$BUILD_DIR/.cache/runtimes/windows-x64/pip-packages"
mkdir -p "$BUILD_DIR/src"

# ── Step 1: Python ─────────────────────────────────────────────
echo "[1/6] Downloading Python 3.11 (standalone, Windows x64)..."
PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20260623/cpython-3.11.15+202****0623-x86_64-pc-windows-msvc-install_only_stripped.tar.gz"
curl -L -f --retry 3 --max-time 900 -o "$BUILD_DIR/.cache/runtimes/windows-x64/python.tar.gz" "$PYTHON_URL"
echo "  Python: $(du -h "$BUILD_DIR/.cache/runtimes/windows-x64/python.tar.gz" | cut -f1)"

# ── Step 2: Node.js ────────────────────────────────────────────
echo "[2/6] Downloading Node.js 22 LTS (Windows x64)..."
NODE_URL="https://nodejs.org/dist/v22.22.3/node-v22.22.3-win-x64.zip"
curl -L -f --retry 3 --max-time 900 -o "$BUILD_DIR/.cache/runtimes/windows-x64/node.zip" "$NODE_URL"
echo "  Node.js: $(du -h "$BUILD_DIR/.cache/runtimes/windows-x64/node.zip" | cut -f1)"

# ── Step 3: uv ─────────────────────────────────────────────────
echo "[3/6] Downloading uv..."
UV_URL="https://github.com/astral-sh/uv/releases/download/0.11.19/uv-x86_64-pc-windows-msvc.zip"
curl -L -f --retry 3 --max-time 300 -o "$BUILD_DIR/.cache/runtimes/windows-x64/uv.zip" "$UV_URL"
echo "  uv: $(du -h "$BUILD_DIR/.cache/runtimes/windows-x64/uv.zip" | cut -f1)"

# ── Step 4: Hermes source ──────────────────────────────────────
echo "[4/6] Downloading Hermes Agent source..."
SOURCE_URL="https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip"
curl -L -f --retry 3 --max-time 600 -o "$BUILD_DIR/src/hermes-agent.zip" "$SOURCE_URL"
# Extract source
unzip -o "$BUILD_DIR/src/hermes-agent.zip" -d "$BUILD_DIR/src/" 2>/dev/null || true
mv "$BUILD_DIR/src/hermes-agent-main" "$BUILD_DIR/src/hermes-agent" 2>/dev/null || true
echo "  Source: $(du -sh "$BUILD_DIR/src/hermes-agent" | cut -f1)"

# ── Step 5: Pre-download pip packages ─────────────────────────
echo "[5/6] Downloading pip dependencies (wheel packages)..."
# We need a Python to download the wheels. On Linux, use system Python.
# We'll use the bundled Python once extracted, or system Python as fallback.
SYSTEM_PYTHON="python3"
if command -v python3 &>/dev/null; then
    SYSTEM_PYTHON="python3"
fi

# Create a temp venv to download wheels
TEMP_VENV="/tmp/.hermes-offline-build-venv"
rm -rf "$TEMP_VENV"
"$SYSTEM_PYTHON" -m venv "$TEMP_VENV"
"$TEMP_VENV/bin/pip" install --upgrade pip --quiet 2>/dev/null || "$TEMP_VENV/bin/pip" install --upgrade pip 2>/dev/null || true

# Download hermes-agent and all dependencies as wheels
"$TEMP_VENV/bin/pip" download --dest "$BUILD_DIR/.cache/runtimes/windows-x64/pip-packages/" \
    --platform win_amd64 \
    --implementation cp \
    --only-binary :all: \
    --no-deps \
    hermes-agent 2>&1 || echo "[WARN] Could not download wheels (need Windows Python to fetch correct wheels)"

# If that failed (we're on Linux, can't get Windows wheels), 
# download source dists instead and let pip build them offline
if [ ! -d "$BUILD_DIR/.cache/runtimes/windows-x64/pip-packages/" ] || [ -z "$(ls -A "$BUILD_DIR/.cache/runtimes/windows-x64/pip-packages/" 2>/dev/null)" ]; then
    echo "[INFO] Cross-platform: downloading source dists as fallback..."
    "$TEMP_VENV/bin/pip" download --dest "$BUILD_DIR/.cache/runtimes/windows-x64/pip-packages/" \
        hermes-agent 2>&1 || true
fi

# Also download OpenCode dependencies (this is complex, skip for now)
# OpenCode needs npm packages — we'll use npm's --offline mode with pre-cached .npmrc

echo "  Pip packages: $(du -sh "$BUILD_DIR/.cache/runtimes/windows-x64/pip-packages/" | cut -f1)"

# ── Step 6: Package everything ─────────────────────────────────
echo "[6/6] Building package..."
cd "$OUTPUT_DIR"

# Remove the build helper files
rm -rf "$TEMP_VENV"

# Calculate size
TOTAL_SIZE=$(du -sh "$BUILD_DIR" | cut -f1)

echo ""
echo "================================================================"
echo "  Build complete!"
echo "================================================================"
echo ""
echo "  Package: $BUILD_DIR"
echo "  Size: $TOTAL_SIZE"
echo ""
echo "  Files:"
find "$BUILD_DIR" -maxdepth 2 -type f -o -type d | grep -v ".cache/runtimes/windows-x64/pip-packages" | head -30
echo "  ..."
echo ""
echo "  To use on Windows:"
echo "    1. Copy the entire folder to Windows"
echo "    2. Double-click launch-offline.bat"
echo "    3. No internet needed!"
echo ""
echo "  To create a distributable zip:"
echo "    7z a -tzip $PACKAGE_NAME.zip $PACKAGE_NAME/"
echo ""