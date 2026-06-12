# EVIDENCE_SCHEMA.md — viewpoint-verification

> 对应原则：P0

## 证据链节点类型

| source_type | 何时产生 |
|------------|---------|
| `atom_output` | 每个 CounterArgument 引用 extracted_knowledge 中的对立证据 |
| `reasoning` | 逻辑推断式反方观点（标记 [INFERRED]） |

## 节点结构

```json
{"source_type": "atom_output", "source_ref": "extracted_knowledge", "note": "counterargument sourced from KnowledgeItem.id=<id>"}
```

## 传递规则

每个 Verification 的 counterarguments 必须有证据基础（文献引用或显式标注的逻辑推理）。
