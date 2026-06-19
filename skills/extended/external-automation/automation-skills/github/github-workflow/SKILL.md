---
name: github-workflow
description: "Complete GitHub workflow: auth, PR review, issue management, repo management, CI/CD, codebase inspection."
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    atom_type: composite
    priority: P1
    signature: "task_desc: str, context: dict -> result: dict"
    related_skills: []

---

# github-workflow

## Purpose

Composite skill that merges 8 overlapping skills into a unified interface.

## Members (8)

- **codebase-inspection**: Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios using `pygount`.
- **github**: GitHub工作流 — PR审查、Issue管理、仓库管理、CI/CD。
- **github-auth**: Skill: github-auth
- **github-code-review**: Skill: github-code-review
- **github-discussions**: Create, list, search, and manage GitHub Discussions via GraphQL API.
- **github-issues**: Skill: github-issues
- **github-pr-workflow**: Skill: github-pr-workflow
- **github-repo-management**: ```bash

## IO_CONTRACT

- **input**: `task_desc: str, context: dict` — Task description and context
- **output**: `result: dict` — Merged results from all member skills

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）