# EVIDENCE_SCHEMA.md — association-discovery

> 对应原则：P0

## 证据链节点类型

| source_type | 何时产生 |
|------------|---------|
| `atom_output` | 每个 Association 引用 upstream extracted_knowledge 的 KnowledgeItem.id |

## 节点结构

```json
{"source_type": "atom_output", "source_ref": "extracted_knowledge", "note": "引用 KnowledgeItem.id=<item1>, <item2>"}
```

## 传递规则

每个 Association 的 evidence 节点引用参与关联的两个 KnowledgeItem。ResearchGap 的 evidence 节点引用"为什么判定为空白"的具体论文或统计。
