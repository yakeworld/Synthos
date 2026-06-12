# EVIDENCE_SCHEMA.md — hypothesis-generation

> 对应原则：P0

## 证据链节点类型

| source_type | 何时产生 |
|------------|---------|
| `atom_output` | 每个 Hypothesis 引用 upstream research_gaps 或 associations |

## 节点结构

```json
{"source_type": "atom_output", "source_ref": "research_gaps", "note": "gap_id=<id>"}
```

## 传递规则

每个 Hypothesis 的 rationale 必须引用具体的 gap 或 association 作为证据基础。
