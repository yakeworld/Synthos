---
name: claude-code
description: claude-code
version: 1.0.0
category: mlops
signature: 'claude-code -> mlops: Delegate coding to Claude Code CLI — features, PRs,
  refactoring, review.'
related_skills: []
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


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 

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
|: