---



name: github-auth
description: "Skill: github-auth"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "auth_method: str, token: str -> auth_result: dict (status, scope, expiration)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# Github Auth

GitHub认证设置 — HTTPS token, SSH key, gh CLI登录。
