---


name: knowledge-extraction
description: "Directory index for knowledge-extraction: knowledge-extraction"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "paper_content: str, schema: dict -> structured_knowledge: dict (entities, relations, claims, evidence)"
    atom_type: skill
    priority: P1
    related_skills: []
---





# Knowledge Extraction

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。
This skill has been compressed. Full content is available in references/.

## IO_CONTRACT

- **input**: `paper_text: str, query_focus: str`
- **output**: `extracted: list[KnowledgeExtract]` — 包含 topic, method, dataset, metric, result, confidence, source, quote

> 对应原则：P2（机械原子暴露输入输出规范）
