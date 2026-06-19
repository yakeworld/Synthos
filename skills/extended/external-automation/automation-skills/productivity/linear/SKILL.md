---



name: linear
description: "Directory index for linear: linear"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "project_id: str, status: str -> tasks: list[Task] (id, title, assignee, due_date, priority, status)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# Linear

Linear项目管理 — issues/projects/teams via GraphQL。

详细内容请加载对应 references/ 目录下的参考文件。
