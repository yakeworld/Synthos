# EVIDENCE_SCHEMA.md — knowledge-extraction

> 对应原则：P0

## 证据链节点类型

| source_type | 何时产生 |
|------------|---------|
| `doi` | 每个 KnowledgeItem 生成一个节点，引用论文DOI |
| `atom_output` | 论文无DOI时的降级方案，引用 raw_papers 索引 |

## 节点结构

```json
{"source_type": "doi", "source_ref": "<DOI>", "fetch_time": "<ISO>", "note": "Extracted from abstract"}
```

## 传递规则

本原子的 evidence_chain 是追加型：不删除上游节点，仅追加本原子的新节点。每个 KnowledgeItem 的 findings 可追溯到具体 DOI。
