---



name: github-pr-workflow
description: "Skill: github-pr-workflow"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "pr_url: str -> workflow_result: dict (status, checks, merges, deployment)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# Github Pr Workflow

GitHub PR生命周期 — branch→commit→open→CI→merge。
