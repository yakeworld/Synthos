---
name: opencode
description: "Delegate coding to OpenCode CLI (features, PR review)."
signature: "task: str, context: dict -> result: str"
related_skills: [ai-outreach, autonomous-core-researcher, claude-code, codex, hermes-agent]
allowed-tools: [terminal, file]
version: 1.3.0
author: Hermes Agent + Synthos
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, OpenCode, Autonomous, Refactoring, Code-Review]
    related_skills: [claude-code, codex, hermes-agent]
---

# OpenCode CLI

Use [OpenCode](https://opencode.ai) as an autonomous coding worker orchestrated by Hermes terminal/process tools. OpenCode is a provider-agnostic, open-source AI coding agent with a TUI and CLI.

## When to Use

**ALL task execution goes through OpenCode.** Hermes only plans, reviews, and gates. This is the core behavioral rule:

| Hermes does | OpenCode does |
|:------------|:--------------|
| Reasoning, planning, architecture decisions | All code/script writing |
| Quality gating, review, verification | Batch file operations |
| Tool/API orchestration (NotebookLM, cron, etc.) | Data processing, conversion |
| User-facing explanation, strategy | Multi-file refactoring |
| Single-step terminal commands (git, mkdir, grep) | Anything requiring iteration |

Exceptions (Hermes does directly):
- 1-2 line patches
- Architecture/design decisions
- Single git commands, file reads
- Config edits (config.yaml, .gitignore)
- Tool invocations (cronjob, memory, fact_store, skill operations)

## When to Use

- User explicitly asks to use OpenCode
- You want an external coding agent to implement/refactor/review code
- You need long-running coding sessions with progress checks
- You want parallel task execution in isolated workdirs/worktrees
- Repetitive/mechanical work that would require writing a Python script
- Batch file operations, data conversion, multi-file code changes

## When NOT to Use (do it yourself)

- 1-2 line patches / single `read_file` / architecture decisions
- Reasoning-heavy analysis that needs your full context
- Single-step terminal commands

## Multi-Provider Configuration

OpenCode supports multiple local/remote models via `~/.config/opencode/opencode.json`:

```json
{
  "provider": {
    "hermes": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Hermes vLLM",
      "options": { "baseURL": "http://100.100.252.99:8000/v1", "apiKey": "EMPTY" },
      "models": {
        "qwen3.6-35b-nvfp4": {
          "name": "Qwen3.6 35B",
          "limit": { "context": 65536, "output": 8000 },
          "tools": true, "maxOutputTokens": 8000, "supportsToolCalling": true
        }
      }
    },
    "amax-fallback": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "AMAX Fallback",
      "options": { "baseURL": "http://100.82.27.51:8000/v1", "apiKey": "EMPTY" },
      "models": { "qwen3.6-35b-nvfp4": { ... same schema ... } }
    }
  },
  "model": "hermes/qwen3.6-35b-nvfp4"
}
```

Select model with `--model`:
```bash
opencode run '任务1' --model hermes/qwen3.6-35b-nvfp4           # 主节点
opencode run '任务2' --model amax-fallback/qwen3.6-35b-nvfp4     # 备选节点
```

## Synthos Skill Absorption

OpenCode auto-loads Synthos standards from `.opencode/rules.md` when launched from the Synthos repo root. It can also read `skills/` directory directly.

**验证吸收成功**：
```bash
opencode run '读取 skills/quality/dual-quality-check-v2/SKILL.md，总结D8-D10标准'
# → 应返回正确阈值（≥30篇，≥0.80覆盖率，引用匹配）

- OpenCode installed: `npm i -g opencode-ai@latest` or `brew install anomalyco/tap/opencode`
- Auth configured: `opencode auth login` or set provider env vars (OPENROUTER_API_KEY, etc.)
- Verify: `opencode auth list` should show at least one provider
- Git repository for code tasks (recommended)
- `pty=true` for interactive TUI sessions

## Binary Resolution (Important)

Shell environments may resolve different OpenCode binaries. If behavior differs between your terminal and Hermes, check:

```
terminal(command="which -a opencode")
terminal(command="opencode --version")
```

If needed, pin an explicit binary path:

```
terminal(command="$HOME/.opencode/bin/opencode run '...'", workdir="~/project", pty=true)
```

## One-Shot Tasks

Use `opencode run` for bounded, non-interactive tasks:

```
terminal(command="opencode run 'Add retry logic to API calls and update tests'", workdir="~/project")
```

Attach context files with `-f`:

```
terminal(command="opencode run 'Review this config for security issues' -f config.yaml -f .env.example", workdir="~/project")
```

Show model thinking with `--thinking`:

```
terminal(command="opencode run 'Debug why tests fail in CI' --thinking", workdir="~/project")
```

Force a specific model:

```
terminal(command="opencode run 'Refactor auth module' --model openrouter/anthropic/claude-sonnet-4", workdir="~/project")
```

## Interactive Sessions (Background)

For iterative work requiring multiple exchanges, start the TUI in background:

```
terminal(command="opencode", workdir="~/project", background=true, pty=true)
# Returns session_id

# Send a prompt
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow and add tests")

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Send follow-up input
process(action="submit", session_id="<id>", data="Now add error handling for token expiry")

# Exit cleanly — Ctrl+C
process(action="write", session_id="<id>", data="\x03")
# Or just kill the process
process(action="kill", session_id="<id>")
```

**Important:** Do NOT use `/exit` — it is not a valid OpenCode command and will open an agent selector dialog instead. Use Ctrl+C (`\x03`) or `process(action="kill")` to exit.

### TUI Keybindings

| Key | Action |
|-----|--------|
| `Enter` | Submit message (press twice if needed) |
| `Tab` | Switch between agents (build/plan) |
| `Ctrl+P` | Open command palette |
| `Ctrl+X L` | Switch session |
| `Ctrl+X M` | Switch model |
| `Ctrl+X N` | New session |
| `Ctrl+X E` | Open editor |
| `Ctrl+C` | Exit OpenCode |

### Resuming Sessions

After exiting, OpenCode prints a session ID. Resume with:

```
terminal(command="opencode -c", workdir="~/project", background=true, pty=true)  # Continue last session
terminal(command="opencode -s ses_abc123", workdir="~/project", background=true, pty=true)  # Specific session
```

## Common Flags

| Flag | Use |
|------|-----|
| `run 'prompt'` | One-shot execution and exit |
| `--continue` / `-c` | Continue the last OpenCode session |
| `--session <id>` / `-s` | Continue a specific session |
| `--agent <name>` | Choose OpenCode agent (build or plan) |
| `--model provider/model` | Force specific model |
| `--format json` | Machine-readable output/events |
| `--file <path>` / `-f` | Attach file(s) to the message |
| `--thinking` | Show model thinking blocks |
| `--variant <level>` | Reasoning effort (high, max, minimal) |
| `--title <name>` | Name the session |
| `--attach <url>` | Connect to a running opencode server |

## Procedure

1. Verify tool readiness:
   - `terminal(command="opencode --version")`
   - `terminal(command="opencode auth list")`
2. For bounded tasks, use `opencode run '...'` (no pty needed).
3. For iterative tasks, start `opencode` with `background=true, pty=true`.
4. Monitor long tasks with `process(action="poll"|"log")`.
5. If OpenCode asks for input, respond via `process(action="submit", ...)`.
6. Exit with `process(action="write", data="\x03")` or `process(action="kill")`.
7. Summarize file changes, test results, and next steps back to user.

## PR Review Workflow

OpenCode has a built-in PR command:

```
terminal(command="opencode pr 42", workdir="~/project", pty=true)
```

Or review in a temporary clone for isolation:

```
terminal(command="REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && opencode run 'Review this PR vs main. Report bugs, security risks, test gaps, and style issues.' -f $(git diff origin/main --name-only | head -20 | tr '\n' ' ')", pty=true)
```

## Parallel Work Pattern

Use separate workdirs/worktrees to avoid collisions:

```
terminal(command="opencode run 'Fix issue #101 and commit'", workdir="/tmp/issue-101", background=true, pty=true)
terminal(command="opencode run 'Add parser regression tests and commit'", workdir="/tmp/issue-102", background=true, pty=true)
process(action="list")
```

## Session & Cost Management

List past sessions:

```
terminal(command="opencode session list")
```

Check token usage and costs:

```
terminal(command="opencode stats")
terminal(command="opencode stats --days 7 --models anthropic/claude-sonnet-4")
```

## External Agent Sync

**OpenCode auto-loads**: OpenCode reads `.opencode/rules.md` when launched from a project root. This is the primary mechanism for syncing Synthos standards.

**AGENTS.md**: In the Synthos repo root, points other AI agents to `.opencode/rules.md`.

## Cron + no_agent=true Bridge Pattern

For long-running autonomous tasks (research, paper enhancement, monitoring), use the **cron + no_agent=true + script → opencode run** pattern:

```
hermes cron (triggers hourly)
  └→ no_agent=true (zero LLM cost for scheduling)
      └→ shell script (quick checks: terminal state, scope, etc.)
          ├─ terminal state → exit silently (zero cost)
          └─ work needed → opencode run 'prompt' (local model)
```

### Implementation Template

```
~/.hermes/scripts/<task-name>.sh:
  #!/bin/bash
  # no_agent=true — execution via opencode run
  
  # Step 1: Quick state check (bash/Python, zero LLM cost)
  python3 -c "import json; t=json.load(open('tracker.json')); print(t.get('phase',''))"
  if [ "$phase" = "terminal" ]; then
    echo "Terminal state — skip"
    exit 0
  fi
  
  # Step 2: Delegate to OpenCode
  cd /project/root
  opencode run 'Self-contained prompt describing the task'
```

### Cron Job Setup

```bash
# Create 
hermes cron create '0 * * * *' --name "task-name" --script "task-name.sh" --no-agent

# Requirements
# 1. The script file at ~/.hermes/scripts/<name>.sh (chmod +x)
# 2. no_agent=true (Hermes doesn't process, just triggers script execution)
# 3. The script handles all logic — including skipping when nothing to do
```

### Advantages
- **Zero LLM cost** for no-op cycles (bash check exits before opencode)
- **Local model execution** (cheaper than deepseek API)
- **Hermes context preserved** (agent not occupied by cron loop)
- **Parallel safe** (background=true doesn't interfere with user conversation)

### Real-World Example
`autonomous-core-researcher.sh` — checks agent-tracker.json phase, 
if terminal state → increment counter, exit; 
if work needed → `opencode run '...'` with NotebookLM interaction protocol.
# OpenCode inherits all Synthos standards automatically:
terminal(command="opencode run '实现批量下载功能'", workdir="/media/yakeworld/sda2/Synthos")
# → 自动遵守：命名{dir}-v{N}.pdf / D8≥30篇 / PDF三级验证 / 凭据环境变量
```

**Synthos标准已写入 `.opencode/rules.md`：**
1. 论文命名规范（`{dir}-v{N}.pdf`）
2. D1-D10 十维质量门
3. PDF下载三级验证
4. 参考文献管线流程
5. 凭据管理（环境变量，不硬编码）
6. 进化日志格式
7. 项目目录结构
8. Synthos哲学（文言八句）

**外部agent同步机制：** `AGENTS.md` 在仓库根目录，指向 `.opencode/rules.md`。其他AI agent clone仓库后通过 AGENTS.md 发现标准。

## Pitfalls

- Interactive `opencode` (TUI) sessions require `pty=true`. The `opencode run` command does NOT need pty.
- `/exit` is NOT a valid command — it opens an agent selector. Use Ctrl+C to exit the TUI.
- PATH mismatch can select the wrong OpenCode binary/model config.
- If OpenCode appears stuck, inspect logs before killing:
  - `process(action="log", session_id="<id>")`
- Avoid sharing one working directory across parallel OpenCode sessions.
- Enter may need to be pressed twice to submit in the TUI (once to finalize text, once to send).

## Verification

Smoke test:

```
terminal(command="opencode run 'Respond with exactly: OPENCODE_SMOKE_OK'")
```

Success criteria:
- Output includes `OPENCODE_SMOKE_OK`
- Command exits without provider/model errors
- For code tasks: expected files changed and tests pass

## Rules

1. Prefer `opencode run` for one-shot automation — it's simpler and doesn't need pty.
2. Use interactive background mode only when iteration is needed.
3. Always scope OpenCode sessions to a single repo/workdir.
4. For long tasks, provide progress updates from `process` logs.
5. Report concrete outcomes (files changed, tests, remaining risks).
6. Exit interactive sessions with Ctrl+C or kill, never `/exit`.
