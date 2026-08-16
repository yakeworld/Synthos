#!/bin/bash
# build-offline.sh — Build the offline portable package for Windows
# Usage: bash build-offline.sh [output_dir]
#
# Downloads all dependencies ONCE and packages them into
# a self-contained zip that requires NO internet connection to run.

set -e

OUTPUT_DIR="${1:-/tmp/hermes-offline}"
PACKAGE_NAME="hermes-portable-offline-windows-x64"
BUILD_DIR="$OUTPUT_DIR/$PACKAGE_NAME"

echo "================================================================"
echo "  Hermes + OpenCode — Offline Package Builder"
echo "================================================================"

mkdir -p "$BUILD_DIR"
mkdir -p "$BUILD_DIR/data"
mkdir -p "$BUILD_DIR/.cache/runtimes/windows-x64"
mkdir -p "$BUILD_DIR/.cache/runtimes/windows-x64/pip-packages"
mkdir -p "$BUILD_DIR/src"

# Step 1: Python (python-build-standalone)
echo "[1/4] Downloading Python 3.11 (standalone, Windows x64)..."
curl -L -f --retry 3 --max-time 900 \
  -o "$BUILD_DIR/.cache/runtimes/windows-x64/python.tar.gz" \
  "https://github.com/astral-sh/python-build-standalone/releases/download/20260623/cpython-3.11.15+202****0623-x86_64-pc-windows-msvc-install_only_stripped.tar.gz"
echo "  Python: $(du -h "$BUILD_DIR/.cache/runtimes/windows-x64/python.tar.gz" | cut -f1)"

# Step 2: Node.js
echo "[2/4] Downloading Node.js 22 LTS (Windows x64)..."
curl -L -f --retry 3 --max-time 900 \
  -o "$BUILD_DIR/.cache/runtimes/windows-x64/node.zip" \
  "https://nodejs.org/dist/v22.22.3/node-v22.22.3-win-x64.zip"
echo "  Node.js: $(du -h "$BUILD_DIR/.cache/runtimes/windows-x64/node.zip" | cut -f1)"

# Step 3: uv
echo "[3/4] Downloading uv..."
curl -L -f --retry 3 --max-time 300 \
  -o "$BUILD_DIR/.cache/runtimes/windows-x64/uv.zip" \
  "https://github.com/astral-sh/uv/releases/download/0.11.19/uv-x86_64-pc-windows-msvc.zip"
echo "  uv: $(du -h "$BUILD_DIR/.cache/runtimes/windows-x64/uv.zip" | cut -f1)"

# Step 4: Hermes source
echo "[4/4] Downloading Hermes Agent source..."
curl -L -f --retry 3 --max-time 600 \
  -o "$BUILD_DIR/src/hermes-agent.zip" \
  "https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip"
unzip -o "$BUILD_DIR/src/hermes-agent.zip" -d "$BUILD_DIR/src/" 2>/dev/null || true
mv "$BUILD_DIR/src/hermes-agent-main" "$BUILD_DIR/src/hermes-agent" 2>/dev/null || true
echo "  Source: $(du -sh "$BUILD_DIR/src/hermes-agent" | cut -f1)"

echo ""
echo "================================================================"
echo "  Build complete!"
echo "  Package: $BUILD_DIR"
echo "  Size: $(du -sh "$BUILD_DIR" | cut -f1)"
echo "  Files:"
find "$BUILD_DIR" -maxdepth 2 -type f | grep -v pip-packages | head -20
echo "================================================================"