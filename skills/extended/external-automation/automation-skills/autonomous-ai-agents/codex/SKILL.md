---
name: codex
description: Delegate coding to OpenAI Codex CLI (features, PRs).
version: 1.0.0
allowed-tools:
- terminal
- file
- web
license: MIT
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
    version: 1.0.0

---

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

> 对应原则：P2（机械原子暴露输入输出规范）




# Codex CLI

Delegate coding tasks to [Codex](https://github.com/openai/codex) via the Hermes terminal. Codex is OpenAI's autonomous coding agent CLI.

## 合成记忆 · 合成记忆

**Codex CLI 是 Synthos 的主力编码代理。** 所有编码任务（功能开发、重构、PR审查、批量issue修复）优先走 Codex。

## When to use

- Building features (⚡ 默认选择)
- Refactoring
- PR reviews
- Batch issue fixing
- 复杂编码任务（多文件、多步骤、需自主规划）

OpenCode 仅用于极轻量的一键脚本，复杂任务一律走 Codex。

Requires the codex CLI and a git repository.

## 多模型多节点 Profile

Codex CLI 支持多 profile 切换不同 vLLM 节点和模型：

| Profile | 节点 | 模型 | 用途 |
|---------|------|------|------|
| 默认(无-p) | 100.82.27.51:8000 | qwen3.6-35b-nvfp4 | 主力节点 |
| -p amax | 100.82.27.51:8000 | Qwen3.6-35B-A3B-GPTQ-Int4 | AMAX 备用 |
| -p hermes | 100.125.10.93:8000 | qwen3.6-35b-nvfp4 | Hermes 节点 |
| -p fallback | 100.100.252.99:8000 | qwen3.6-35b-nvfp4 | 第三备用 |

**使用方式：**
```
# 主力（默认）
codex exec "task description" --yolo

# 备用节点
codex -p amax exec "task description" --yolo
codex -p hermes exec "task description" --yolo
codex -p fallback exec "task description" --yolo
```

**并行任务策略：** 不同任务分配到不同 profile 节点，实现多节点并行负载。

## Prerequisites

- Codex installed: `npm install -g @openai/codex`
- **Must run inside a git repository** — Codex refuses to run outside one
- Use `pty=true` in terminal calls — Codex is an interactive terminal app

## One-Shot Tasks

```
# 主力节点（默认）
terminal(command="codex exec 'Add dark mode toggle to settings' --yolo", workdir="~/project", pty=true)

# 备用节点并行
terminal(command="codex -p hermes exec 'Refactor auth module' --yolo", workdir="~/project", background=true, pty=true)
terminal(command="codex -p amax exec 'Fix login bug' --yolo", workdir="~/project", background=true, pty=true)
```

For scratch work (Codex needs a git repo):
```
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python' --yolo", pty=true)
```

## Background Mode (Long Tasks)

```
# Start in background with PTY (主力节点)
terminal(command="codex exec --full-auto 'Refactor the auth module' --yolo", workdir="~/project", background=true, pty=true)

# 备用节点并行
terminal(command="codex -p amax exec --yolo 'Fix issue #42' --yolo", workdir="~/project", background=true, pty=true)
# Returns session_id

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
```

**注意：** 长任务或批量任务优先使用 `--yolo` 模式 + `background=true`，并分配到不同 profile 实现多节点并行。

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |

## PR Reviews

Clone to a temp directory for safe review:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Parallel Issue Fixing with Worktrees

```
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'")

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Batch PR Reviews

```
# Fetch all PR refs
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/project")

# Review multiple PRs in parallel
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86'", workdir="~/project", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87'", workdir="~/project", background=true, pty=true)

# Post results
terminal(command="gh pr comment 86 --body '<review>'", workdir="~/project")
```

## Rules

1. **Always use `pty=true`** — Codex is an interactive terminal app and hangs without a PTY
2. **Git repo required** — Codex won't run outside a git directory. Use `mktemp -d && git init` for scratch
3. **Use `--yolo`** — No sandbox, no approvals (fastest). For building use `--full-auto` for auto-approve within sandbox
4. **Multi-node parallel** — 复杂/批量任务分配到不同 profile 节点并行执行（-p amax / -p hermes / -p fallback）
5. **Background for long tasks** — use `background=true` and monitor with `process` tool
6. **Don't interfere** — monitor with `poll`/`log`, be patient with long-running tasks
7. **Parallel is fine** — run multiple Codex processes at once with different profiles

## Multi-Node Load Balancing Strategy

```bash
# Task 1 → 主力节点
codex exec "task A" --yolo -w /path/to/project

# Task 2 → hermes 节点
codex -p hermes exec "task B" --yolo -w /path/to/project

# Task 3 → amax 节点
codex -p amax exec "task C" --yolo -w /path/to/project

# Monitor all in parallel
process(action="list")
```
