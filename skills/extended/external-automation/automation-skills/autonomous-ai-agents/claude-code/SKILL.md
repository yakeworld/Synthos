---

name: claude-code
related_skills: []
description: Delegate coding to Claude Code CLI — features, PRs, refactoring, review.
version: 1.0.0
allowed-tools:
- terminal
- file
license: MIT
author: Synthos
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
    signature: 'task: str -> result: dict'


---


## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



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
## Reference
- `references/setup-guide.md` — 安装和配置
- `references/best-practices.md` — 任务拆分和上下文管理

## 相关技能
- `codex-cli` — Codex CLI 配置与远程部署（主力编码代理，Responses API）
- `opencode` — OpenCode CLI（轻量替代，Chat Completions API）

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
