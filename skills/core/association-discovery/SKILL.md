---


name: association-discovery
description: "Directory index for association-discovery: association-discovery"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "knowledge_base: dict, query: str -> associations: list[Association] (type, strength, confidence, source)"
    atom_type: skill
    priority: P1
    related_skills: []
---




# Association Discovery

## IO_CONTRACT

- **input**: `knowledge_items: list[KnowledgeItem]` — 待分析的知识项集合
- **output**: `relationships: list[Relationship]` — 知识关系列表（source, target, type, strength, evidence）

> 对应原则：P2（机械原子暴露输入输出规范）

> 对应原则：P2 机械原子暴露输入输出规范

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。
This skill has been compressed. Full content is available in references/.
