---
name: knowledge-extraction
description: >-
version: 1.0.0
  从学术论文元数据和摘要中提取结构化知识 — 返回JSON。
metadata:
  synthos:
    priority: P0
    atom_type: cognitive-atom
    description: Extract structured knowledge from papers, notebooks, or documents.
    signature: "document: str, extraction_mode: str, schema: dict -> knowledge_items: list[KnowledgeItem] -> knowledge_items: list[KnowledgeItem] (finding, method, limitation, relevance, source)"
    related_skills: [association-discovery, hypothesis-generation, knowledge-acquisition]

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
