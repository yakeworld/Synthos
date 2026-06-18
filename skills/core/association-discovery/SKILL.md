---
name: association-discovery
description: >-
  识别知识项间关系 — 矛盾/补充/进化/支持/扩展/相似/空白。构建知识图谱。
version: 1.0.0
metadata:
  synthos:
    priority: P0
    atom_type: cognitive-atom
    description: Identify relationships between knowledge items — contradiction/supplement/evolution/support/expansion/similarity/gap.
    signature: "knowledge_items: list[KnowledgeItem] -> relationships: list[Relationship] -> relationships: list[Relationship] (source, target, type, strength, evidence)"
    related_skills: ["knowledge-acquisition", "knowledge-extraction"]
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
