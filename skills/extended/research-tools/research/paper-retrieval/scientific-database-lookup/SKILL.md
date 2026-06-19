---



name: scientific-database-lookup
description: "Directory index for scientific-database-lookup: scientific-database-lookup"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "query: str, database: str -> results: list[Result] (record, source, confidence, metadata)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `query: str, database: str` — 用户请求描述、上下文信息
- **output**: `lookup_results: list — 科学数据库查询`


> 对应原则：P2（机械原子暴露输入输出规范）

# Scientific Database Lookup

78+科学数据库REST API路由 — 生物信息/化学/临床/神经/材料/物理。
