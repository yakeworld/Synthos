#!/bin/bash
# Codex CLI with vLLM backend — 一键启动脚本
# 用法:
#   ./codex-vllm.sh "写一个函数读取眼动CSV并可视化"
#   echo "description" | ./codex-vllm.sh
#
# 自动加载环境变量、跳过git检查和hook确认。

set -e

# ── 加载环境 ────────────────────────────────────────
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# vLLM 本地无需认证，但 Codex 要求 env_key 存在
export VLLM_API_KEY="${VLLM_API_KEY:-EMPTY}"

# ── 默认参数 ────────────────────────────────────────
EXTRA_ARGS="--skip-git-repo-check --disable hooks -c sandbox.mode=danger-full-access"

if [ $# -ge 1 ]; then
    exec codex exec $EXTRA_ARGS "$@"
else
    exec codex exec $EXTRA_ARGS
fi
