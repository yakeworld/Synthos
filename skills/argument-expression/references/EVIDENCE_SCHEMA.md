# EVIDENCE_SCHEMA.md — argument-expression

> 对应原则：P0

## 证据链节点类型

| source_type | 何时产生 |
|------------|---------|
| `atom_output` | 每个 Argument 的 evidence 引用 extracted_knowledge 或 raw_papers |
| `doi` | 参考文献引用 |

## 节点结构

```json
{"source_type": "atom_output", "source_ref": "extracted_knowledge", "note": "ref=<KnowledgeItem.id>"}
```

## 传递规则

每个 Argument.claim 必须有至少一个 evidence 节点支持。
