---



name: researcher-portrait
description: "Directory index for researcher-portrait: researcher-portrait"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "researcher_name: str -> portrait: dict (publications, citations, networks, h_index, trajectory)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `researcher_name: str` — 用户请求描述、上下文信息
- **output**: `portrait: dict — 研究者画像`


> 对应原则：P2（机械原子暴露输入输出规范）

# Researcher Portrait

中国研究者学术档案 — 论文/专利/项目结构化画像。
