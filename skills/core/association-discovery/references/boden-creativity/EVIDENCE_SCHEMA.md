# Boden 创造力分类 — EVIDENCE_SCHEMA.md

> 对应原则：P0
> 理论来源：Boden (1991)

## 节点结构

```json
{
  "source_type": "boden_creativity_classification",
  "source_ref": "gap_id_or_hypothesis_id",
  "creativity_type": "combinatorial|exploratory|transformational",
  "novelty_score": "float 0.0-5.0",
  "justification": "string — 为什么是此类型",
  "elements": {
    "known_elements": ["string — 组成元素是否已知"],
    "new_combination": "bool",
    "space_expanded": "bool",
    "constraints_changed": "bool"
  },
  "journal_target": "string — 建议期刊级别",
  "novelty_risk": "string — 过度宣称检测"
}
```

## 传递规则

- 必须引用 gap_id 或 hypothesis_id
- novelty_score 与 creativity_type 必须一致
- 声称 transformational 时需要额外 justification (防止过度宣称)
