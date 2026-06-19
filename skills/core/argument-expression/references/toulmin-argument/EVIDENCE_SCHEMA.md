# Toulmin 分析 — EVIDENCE_SCHEMA.md

> 对应原则：P0
> 理论来源：Toulmin (1958)

## 证据链节点类型

| source_type | 何时产生 |
|------------|----------|
| `toulmin_analysis` | 分析论文中每个论点/主张的论证结构时 |

## 节点结构

```json
{
  "source_type": "toulmin_analysis",
  "source_ref": "section_id_or_paper_id",
  "claim": "string — 明确的主张陈述",
  "data": "string — 支撑主张的数据/证据",
  "warrant": "string — 推理规则 (为什么 Data 支持 Claim)",
  "backing": "string — 支撑推理规则的依据",
  "qualifier": "string — 条件/强度限定",
  "reservation": "string — 适用范围/例外",
  "completeness": "float 0.0-1.0 — 6要素齐全度",
  "validity": "float 0.0-1.0 — 逻辑有效性 (链完整+证据充分)",
  "links": {
    "data_to_warrant": "bool — Data 能否推出 Warrant",
    "warrant_to_claim": "bool — Warrant 能否推出 Claim"
  }
}
```

## 传递规则

每个 Toulmin 分析节点必须引用具体的 section_id 或 paper_id 作为 source_ref。
validity < 0.5 的论点必须标记为需要修复。
