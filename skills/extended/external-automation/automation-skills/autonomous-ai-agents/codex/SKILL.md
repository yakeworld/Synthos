---
name: codex
description: codex
version: 1.0.0
category: mlops
signature: 'codex -> mlops: Delegate coding to OpenAI Codex CLI — 主力编码代理。覆盖多节点profile配置、无PTY执行、Cron集成、多模型并行。'
allowed-tools:
- terminal
- file
- web
license: MIT
author: Synthos
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
    - Coding-Agent
    - Codex
    - OpenAI
    - Code-Review
    - Refactoring
    related_skills:
    - claude-code
    - hermes-agent
  synthos:
    author: Hermes Agent
    signature: 'task: str, context: dict -> result: str'
    related_skills:
    - ai-outreach
    - autonomous-core-researcher
    - claude-code
    - hermes-agent
    - moltbook-connector
    version: 1.1.0
    last_updated: 2026-06-19
    update_reason: Multi-node profile architecture + cron script conversion
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

# Codex CLI — 主力编码代理

> ⚡ Codex CLI 是 Synthos 的主力编码代理。所有编码任务优先走 Codex。

## When to use

- Building features (⚡ 默认选择)
- Refactoring
- PR reviews
- Batch issue fixing
- 复杂编码任务（多文件、多步骤、需自主规划）

OpenCode 仅用于极轻量的一键脚本，复杂任务一律走 Codex。

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- **Must run inside a git repository** — Codex refuses to run outside one
- Use `pty=true` in terminal calls for interactive mode
- Config at `~/.codex/config.toml`

## ⚠️ tmux Interaction — 指令与回车必须分开发送

**CRITICAL**: 通过 tmux 与 Codex 交互时，`send-keys` 的指令和 Enter 必须是**两条独立的调用**。

```bash
# ✅ 正确：分两次发送
tmux send-keys -t codex-session "检查代码质量并优化"
sleep 0.5
tmux send-keys -t codex-session Enter

# ❌ 错误：合在一起发送
tmux send-keys -t codex-session "检查代码质量并优化" Enter
# Codex 不会收到回车触发，指令会卡住不响应
```

**根因**：Codex CLI 的 TUI 需要 Enter 键作为独立的 keypress 来触发提交。`send-keys` 在同一调用中一起发送时，Enter 被当作普通字符而非 key event，Codex 不会处理。

**调试信号**：如果 `tmux capture-pane` 看到 `›` 提示符后指令显示但无响应，说明 Enter 没发出去。重新发送 Enter 即可恢复。

## Multi-Node Profile Architecture

Codex CLI 通过 `-p <profile>` 支持多节点并行：

| Profile | 节点 | 模型 | 用途 |
|