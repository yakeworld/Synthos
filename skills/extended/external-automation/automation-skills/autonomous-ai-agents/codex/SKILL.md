---

name: codex
description: "Delegate coding to OpenAI Codex CLI — 主力编码代理。覆盖多节点profile配置、无PTY执行、Cron集成、多模型并行。"
version: 1.1.0
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
|---------|------|------|------|
| 默认(无-p) | 100.82.27.51:8000 | qwen3.6-35b-nvfp4 | 主力节点 |
| -p amax | 100.82.27.51:8000 | Qwen3.6-35B-A3B-GPTQ-Int4 | AMAX 备用 |
| -p hermes | 100.125.10.93:8000 | qwen3.6-35b-nvfp4 | Hermes 节点 |
| -p fallback | 100.100.252.99:8000 | qwen3.6-35b-nvfp4 | 第三备用 |

Profile 文件位于 `~/.codex/<name>.config.toml`。每个文件独立配置 model、model_provider、base_url、wire_api。

### 使用方式

```bash
# 主力节点（默认）
codex exec "task description" --yolo

# 备用节点并行
codex -p hermes exec "task description" --yolo
codex -p amax exec "task description" --yolo
codex -p fallback exec "task description" --yolo
```

### 并行任务策略

不同任务分配到不同 profile 节点，实现多节点并行负载：

```bash
# Task 1 → 主力节点
codex exec "task A" --yolo

# Task 2 → hermes 节点（后台）
codex -p hermes exec "task B" --yolo &

# Task 3 → amax 节点（后台）
codex -p amax exec "task C" --yolo &

# 等待全部完成
wait
```

## Key Flags

| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed but auto-approves file changes in workspace |
| `--yolo` | No sandbox, no approvals (fastest, most dangerous) |
| `-p <profile>` | Load specific config profile |
| `-c key=value` | Override a config value (CLI-only) |
| `--strict-config` | Error on unrecognized config fields |

## One-Shot Tasks (interactive PTY mode)

```bash
# 主力节点（默认）
terminal(command="codex exec 'Add dark mode toggle' --yolo", workdir="~/project", pty=true)

# 备用节点并行
terminal(command="codex -p hermes exec 'Refactor auth' --yolo", workdir="~/project", background=true, pty=true)
terminal(command="codex -p amax exec 'Fix login' --yolo", workdir="~/project", background=true, pty=true)

# Monitor
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
```

For scratch work (Codex needs a git repo):
```bash
terminal(command="cd $(mktemp -d) && git init && codex exec 'Build snake game' --yolo", pty=true)
```

## Background Mode (Long Tasks)

```bash
terminal(command="codex exec --full-auto 'Refactor auth' --yolo", workdir="~/project", background=true, pty=true)

# 备用节点并行
terminal(command="codex -p amax exec --yolo 'Fix issue #42'", workdir="~/project", background=true, pty=true)

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")
process(action="wait", session_id="<id>", timeout=300)
```

**注意：** 长任务或批量任务优先使用 `--yolo` 模式 + `background=true`，并分配到不同 profile 实现多节点并行。

## PR Reviews

```bash
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main", pty=true)
```

## Batch PR Reviews with Parallel Worktrees

```bash
# Create worktrees
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/project")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/project")

# Launch Codex in each (parallel, different profiles)
terminal(command="codex --yolo exec 'Fix issue #78: <description>. Commit when done.'", workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex -p hermes --yolo exec 'Fix issue #99: <description>. Commit when done.'", workdir="/tmp/issue-99", background=true, pty=true)

# Monitor
process(action="list")

# After completion, push and create PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78", pty=true)
terminal(command="cd /tmp/issue-99 && git push -u origin fix/issue-99", pty=true)

# Cleanup
terminal(command="git worktree remove /tmp/issue-78", workdir="~/project")
```

## Cron Integration — Script Pattern

Codex `exec` works in no-agent cron scripts when prompt is passed as CLI argument (no PTY needed):

```bash
#!/bin/bash
# my-cron-task.sh
set -euo pipefail
cd /path/to/project

# Use a specific profile, no PTY needed
codex -p hermes exec "## Task description\n\nSteps:\n1. ...\n2. ...\n\nOutput requirements:\n- ...\n" --yolo 2>&1
```

**验证：** 运行 `bash script.sh` 而非 `pty=true`。Codex 在无 PTY 环境下正常执行，输出到 stdout。

### Cron 迁移清单

将 cron agent 任务迁移到 Codex 脚本的步骤：
1. 将 agent 的 prompt 内容提取为 shell 脚本中的 `codex exec` 参数
2. 设置 `script: <filename>` 在 cron job update
3. 脚本用 `#!/bin/bash` + `set -euo pipefail` 开头
4. 用 `cd` 进入正确的工作目录
5. 选择合适 profile（hermes 用于代码任务，amax 用于进化相关）

- Cron 集成 — 脚本模式通过 `bash script.sh` 执行，codex exec prompt 作为命令行参数传递，完全兼容
- 多模型多节点 — 通过 `-p` profile 切换不同 vLLM 节点
- 无 PTY 运行 — `codex exec` 在 cron/脚本环境中无需 PTY

### Cron 脚本模板（内联参考）

```bash
#!/bin/bash
# 复制此模板到 ~/.hermes/scripts/<task>.sh
set -euo pipefail
WORKDIR="/media/yakeworld/sda2/Synthos"
PROFILE="-p hermes"
cd "$WORKDIR"
codex $PROFILE exec "
## [任务名称]

[任务描述]

### 执行步骤
1. [步骤1]
2. [步骤2]

### 输出要求
- [输出格式]
- [输出位置]

## 参考文件

- `references/codexec-npm-removal.md` — npm 卸载旧版 Codex CLI
- `references/opencode-as-codex-fallback.md` — OpenCode 作为 Codex 降级
- `references/codex-vllm-404-troubleshooting.md` — vLLM 404 排查
- `references/codex-process-diagnosis-2026-06-21.md` — 进程诊断
- `references/codex-tmux-troubleshooting.md` — tmux 交互、多节点路由、故障排查
- 只输出关键结果
" --yolo 2>&1
```

## 模型兼容性警告

**Codex CLI 仅支持 OpenAI Responses API (`wire_api = "responses"`)。** 不兼容 Chat Completions API 的供应商（DeepSeek、OpenRouter 等）。

详情见 `references/deepseek-compatibility.md`。

## Pitfalls

1. **Codex needs a git repo** — 在非 git 目录运行会直接失败。用 `cd $(mktemp -d) && git init` 创建临时仓库
2. **PTY required for interactive mode** — `codex`（不带 subcommand）需要 PTY，但 `codex exec` 不需要
3. **Model metadata warning** — `qwen3.6-35b-nvfp4` 可能报 metadata 缺失警告，但不影响运行
4. **Cron scripts run without PTY** — cron 的 no_agent 模式通过 `bash script.sh` 执行，Codex exec 需要 prompt 作为 CLI 参数（非 stdin）
5. **Profile files are independent** — 每个 profile 文件完全独立，不要期望 profile 之间共享配置
6. **--yolo has NO sandbox** — 完全访问文件系统，确保只用于可信任务
7. **Multiple profiles = multiple processes** — 不同 profile 是独立进程，不共享 session/memory
9. **Shell quoting in cron scripts** — Cron 脚本中 prompt 用双引号包裹，内部换行直接写。过长 prompt 注意 shell 命令长度限制（建议 < 4096 字符）
10. **DeepSeek 不兼容 Codex** — Codex `wire_api` 只接受 `responses`（OpenAI Responses API 格式），DeepSeek 仅提供 OpenAI 兼容的 `chat/completions` 端点。尝试将 DeepSeek 接入 Codex 会失败（401 + `/v1/responses` 端点不存在）。解决方案：DeepSeek 通过 cron agent provider 配置或 OpenCode 使用，不要尝试通过 Codex CLI 调用。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
