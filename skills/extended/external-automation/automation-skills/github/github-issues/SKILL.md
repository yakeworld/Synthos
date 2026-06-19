---



name: github-issues
description: "Skill: github-issues"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "repo: str, filter: dict -> issues: list[Issue] (title, labels, assignee, priority)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# Github Issues

创建/分类/标记/分配GitHub issues — gh或REST API。
