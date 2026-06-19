# 引用链分析 — EVIDENCE_SCHEMA.md

> 对应原则：P0
> 理论来源：Barabási (2016); Garfield (1979)

## 节点结构

```json
{
  "source_type": "citation_chain_analysis",
  "source_ref": "paper_id",
  "forward_citation": {
    "total_citations": "int",
    "annual_citations": "int",
    "core_literature_cited": "bool",
    "citation_sentiment": "positive|mixed|negative",
    "positive_ratio": "float 0.0-1.0"
  },
  "backward_citation": {
    "total_references": "int",
    "key_literature_coverage": "bool",
    "self_citation_ratio": "float 0.0-1.0",
    "seminal_literature": ["string"],
    "core_network_connected": "bool"
  },
  "network_structure": {
    "hub_literature_cited": ["string"],
    "recent_ratio": "float 0.0-1.0 — 近5年占比",
    "classic_ratio": "float 0.0-1.0 — 经典文献占比",
    "core_periphery_connection": "bool"
  },
  "combined_with_citation_functions": {
    "bg_core": "bool",
    "sup_positive": "bool",
    "cmp_mixed": "bool",
    "gap_edges": "bool",
    "meth_method": "bool",
    "obj_hub": "bool"
  },
  "quality_score": "float 0.0-1.0",
  "issues": ["string"]
}
```

## 传递规则

- forward 和 backward 数据必须可验证
- self_citation_ratio 超过 0.3 标记为 FAIL
- 必须连接核心引用网络
