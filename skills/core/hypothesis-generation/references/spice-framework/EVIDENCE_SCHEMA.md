# SPICE/SPIRIT — EVIDENCE_SCHEMA.md

> 对应原则：P0
> 理论来源：Thompson (2004); Richardson (1999)

## 证据链节点类型

| source_type | 何时产生 |
|------------|----------|
| `spice_formulation` | 将研究空白转化为结构化研究问题时 |

## 节点结构

```json
{
  "source_type": "spice_formulation",
  "source_ref": "gap_id_or_research_question_id",
  "gap_source": "string — 引用的空白 ID (来自 association-discovery)",
  "gap_type": "string — 空白类型 (method/theory/empirical/application)",
  "spice": {
    "setting": "string",
    "perspective": "string",
    "intervention": "string",
    "comparison": "string",
    "evaluation": "string",
    "context": "string (optional)"
  },
  "spirit": {
    "source": "string (if applicable)",
    "phenomenon": "string (if applicable)",
    "research_design": "string (if applicable)",
    "outcome_type": "string (if applicable)",
    "timing": "string (if applicable)"
  },
  "research_question": "string — 完整的研究问题表述",
  "quality_score": "float 0.0-1.0",
  "converts_to_hypothesis": "bool — 是否可转化为可检验假设",
  "suggested_hypothesis": "string — 建议的 H₁ 表述"
}
```

## 传递规则

每个 SPICE 节点必须引用 gap_id 作为 source_ref。
quality_score 基于 SPICE 完整性 (5/5=1.0, 4/5=0.8, 3/5=0.6, <3=0.0)
