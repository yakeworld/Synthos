---
name: github-discussions
description: github-discussions
version: 1.0.0
category: automation
signature: 'github-discussions -> automation: Create, list, search, and manage GitHub
  Discussions via GraphQL API.'
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
    - GitHub
    - Discussions
    - A2A
    - GraphQL
    related_skills:
    - github-auth
    - github-issues
    - github-repo-management
  synthos:
    author: Hermes Agent
    signature: 'action: str, params: dict -> result: dict'
    related_skills:
    - github-auth
    - github-code-review
    - github-issues
    - github-pr-workflow
    - github-repo-management
    version: 1.0.0
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

# GitHub Discussions Management

Create, list, search, and manage GitHub Discussions. Unlike Issues (which use the REST API), Discussions require **GraphQL** for creation — the REST POST endpoint returns 404. This skill covers the full GraphQL workflow.

## When This Skill Triggers

- User asks to create a GitHub Discussion
- User asks to list/search discussions
- User asks to find discussion categories
- User asks to reply to a discussion
- User asks for an A2A (Agent-to-Agent) style post
- User asks about discussion categories or configuration

## Prerequisites

- Authenticated with GitHub via `gh` CLI (see `github-auth` skill)

```bash
gh auth status
```

