#!/bin/bash
# verify.sh — 验证 Hermes Agent + OpenCode 环境是否就绪
# 用法: bash verify.sh
# 输出: X/Y CHECKS PASSED — 全绿 = 环境就绪

set -e

PASS=0
FAIL=0
TOTAL=10

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
    TOTAL=$((TOTAL + 1))
}

echo "═══════════════════════════════════════════"
echo "  Hermes Agent + OpenCode 环境验证"
echo "═══════════════════════════════════════════"
echo ""

# 1. Python
check "Python 3.12+" "python3 --version | grep -E '3\.(1[2-9]|[2-9][0-9])'"

# 2. uv
check "uv installed" "uv --version"

# 3. Hermes Agent
check "Hermes Agent installed" "hermes --version"

# 4. Hermes config
check "Hermes config exists" "test -f ~/.hermes/config.yaml"

# 5. Hermes chat works
check "Hermes chat responsive" "hermes chat -q 'test' -Q"

# 6. Node.js
check "Node.js installed" "node --version"

# 7. npm
check "npm installed" "npm --version"

# 8. OpenCode
check "OpenCode CLI installed" "opencode --version"

# 9. OpenCode models list
check "OpenCode models accessible" "opencode models --verbose"

# 10. OpenCode config
check "OpenCode config exists" "test -f ~/.config/opencode/opencode.json"

echo ""
echo "═══════════════════════════════════════════"
echo "  结果: $PASS/$TOTAL CHECKS PASSED"

if [ $FAIL -eq 0 ]; then
    echo "  ✅ ALL CHECKS PASSED — 环境就绪！"
else
    echo "  ⚠️  $FAIL项未通过，请检查上方红色 ❌"
fi
echo "═══════════════════════════════════════════"