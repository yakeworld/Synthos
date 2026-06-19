---



name: architecture-diagram
description: "Directory index for architecture-diagram: architecture-diagram"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "system: str, views: list[str] -> architecture_diagram: dict (components, relationships, tech_stack)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `system: str, components: list` — 用户请求描述、上下文信息
- **output**: `diagram_spec: dict — 系统架构图规范`

> 对应原则：P2（机械原子暴露输入输出规范）



# Architecture Diagram

暗色SVG架构/云/基础设施图 — HTML格式。
