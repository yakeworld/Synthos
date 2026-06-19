---



name: academic-diagram
description: "Directory index for academic-diagram: academic-diagram"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "topic: str, diagram_type: str -> diagram_spec: dict (nodes, edges, layout, styling)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `concept: str, relationships: list` — 用户请求描述、上下文信息
- **output**: `diagram_spec: dict — 学术关系图规范`

> 对应原则：P2（机械原子暴露输入输出规范）



# Academic Diagram

Nature/CNS投稿级架构/流程/系统示意图 — TikZ白底高对比色板。

详细内容请加载对应 references/ 目录下的参考文件。
