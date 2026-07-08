#!/bin/bash
# verify.sh — 验证 Docker 容器内 Hermes Agent + OpenCode 环境是否就绪
# 在容器内运行: docker run --rm hermes-agent:latest /usr/local/bin/verify.sh

PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    if eval "$cmd" > /dev/null 2>&1; then
        echo "✅  $name"
        PASS=$((PASS + 1))
    else
        echo "❌  $name"
        FAIL=$((FAIL + 1))
    fi
}

echo "═══════════════════════════════════════════"
echo "  Hermes Agent Docker 环境验证"
echo "═══════════════════════════════════════════"
echo ""

check "Python3" "python3 --version"
check "uv" "uv --version"
check "Node.js" "node --version"
check "npm" "npm --version"
check "Hermes Agent" "hermes --version"
check "OpenCode CLI" "opencode --version"
check "Git" "git --version"
check "Hermes config" "test -f ~/.hermes/config.yaml"
check "OpenCode config" "test -f ~/.config/opencode/opencode.json"

echo ""
echo "═══════════════════════════════════════════"
echo "  结果: $PASS/$((PASS+FAIL)) 通过"
if [ $FAIL -eq 0 ]; then
    echo "  ✅ 全部通过 — 环境就绪"
else
    echo "  ⚠️  $FAIL 项未通过"
fi
echo "═══════════════════════════════════════════"