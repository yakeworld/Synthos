# OpenCode 工具集与 Hermes Agent 对应表

> 2026-05-28 实战验证。cron→opencode bridge 模式下，脚本 prompt 必须使用 OpenCode 原生工具名。

## 核心差异

| Hermes Agent 工具 | OpenCode 等价 | 备注 |
|:-----------------|:-------------|:------|
| `skill_view(name)` | `Read <path>/SKILL.md` | OpenCode 无 Skill 加载协议，直接读文件 |
| `skill_loader(name)` | `skill()` 加载 opencode manifest | 仅加载 synthos manifest，非单个 SKILL.md |
| `notebooklm list` | `bash: notebooklm list` | notebooklm 是 CLI 程序，非 MCP 工具 |
| `web_search(query)` | `websearch: <query>` | 等价 |
| `terminal(cmd)` | `bash: <command>` | 等价 |
| `session_search(q)` | 无直接等价 | 用 `grep` 或 `Read` 替代 |
| `memory()` | 无直接等价 | 用 `Read outputs/agent-tracker.json` |
| `delegate_task()` | `task(category, prompt)` | 命名不同，功能类似 |

## OpenCode 可用工具清单（2026-05-28 验证）

```
bash:       ✅ 可用 — 所有 shell 命令
Read:       ✅ 可用 — 读文件
websearch:  ✅ 可用 — 网络搜索
task():     ✅ 可用 — 委托子任务
skill():    ✅ 可用 — 仅加载 opencode 的 skill manifest
codesearch: ✅ 可用 — 代码搜索
```

## 不存在于 OpenCode 的工具

```
skill_view ❌ — 用 Read 替代
skill_loader ❌ — 不存在
notebooklm MCP ❌ — 用 bash: notebooklm 替代
memory() ❌ — 用 Read agent-tracker.json
fact_store ❌ — 不存在
cronjob ❌ — 不存在（cron 调度由外部 hermes 完成）
```

## Prompt 编写规则

给 OpenCode 的 prompt 必须在 **第一段** 声明可用工具，例如：

```
## Available Tools
- **`bash: <command>`** — Run shell commands (use for: notebooklm, python3, paper-manager, git)
- **`Read <path>`** — Read file content (use for: SKILL.md, agent-tracker.json, quality reports)
- **`websearch: <query>`** — Search the internet
- **`task(category, prompt)`** — Delegate subtasks (use for: analysis, writing, deep reasoning)

NOT available: `skill_view`, `skill_loader` — use `Read` instead.
```

不声明的话，OpenCode 会花费 20-40 次工具调用去探索哪些工具可用。
