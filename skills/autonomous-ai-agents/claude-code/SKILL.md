---
name: cla
## 原理层·文言

> 文以验法，技乃所产。Delegate coding to Claude Code CLI — features, PRs, refactoring, review.。
ude-code
description: Delegate coding to Claude Code CLI — features, PRs, refactoring, review.
allowed-tools:
- terminal
- file
license: MIT
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
    signature: 'task: str -> result: dict'
---

# Claude Code Delegation

Delegate software development tasks to Claude Code CLI.

## Setup

```bash
npm install -g @anthropic-ai/claude-code
# or via pip
pip install claude-code-cli
```

## Usage

```bash
# 直接运行（PTY模式）
claude

# 单次任务
claude "Implement feature X in file Y"

# 带上下文
claude --context "Project structure: ..." "Add unit tests for Z"

# PR审查
claude "Review this PR, check for bugs and security issues"

# 后台任务
terminal(command="claude 'Task description'", background=true, pty=true, notify_on_complete=true)
```

## 模式

| 模式 | 场景 | 命令 |
|:-----|:-----|:------|
| REPL | 交互式编码 | `claude` (pty=true) |
| 单次 | 特定任务 | `claude "task"` |
| 审查 | 代码评审 | `claude "review PR"` |
| 批量 | 批量修改 | delegate_task + claude |

## 注意事项

- 需要 `pty=true`（PTY模式），否则挂起
- 长任务用 `background=true + notify_on_complete`
- 确认claude CLI已安装: `which claude`

## Reference

- `references/setup-guide.md` — 安装和配置
- `references/best-practices.md` — 任务拆分和上下文管理
