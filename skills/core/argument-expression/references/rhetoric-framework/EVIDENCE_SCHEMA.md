# 修辞学分析 — EVIDENCE_SCHEMA.md

> 对应原则：P0
> 理论来源：Hyland (2000); Swales & Feak (2012)

## 节点结构

```json
{
  "source_type": "rhetoric_analysis",
  "source_ref": "paper_id_or_section_id",
  "hyland_five_dimensions": {
    "centrality": {
      "score": "float 0.0-1.0",
      "topic_sentences": "bool",
      "on_topic": "bool",
      "transitions": "bool"
    },
    "authority": {
      "score": "float 0.0-1.0",
      "cautious_language": "bool",
      "fact_vs_inference": "bool",
      "literature_support": "bool",
      "overconfident_claims": ["string"]
    },
    "complexity": {
      "score": "float 0.0-1.0",
      "multi_level_argument": "bool",
      "counter_argument_handled": "bool",
      "logical_chain_complete": "bool"
    },
    "expression": {
      "score": "float 0.0-1.0",
      "terminology_consistent": "bool",
      "ambiguities": ["string"],
      "grammar_issues": ["string"]
    },
    "introduction_strategy": {
      "score": "float 0.0-1.0",
      "cars_model_used": "bool",
      "contribution_testable": "bool"
    }
  },
  "swales_feak_style_matrix": {
    "formality": "float 0.0-1.0",
    "precision": "float 0.0-1.0",
    "conciseness": "float 0.0-1.0",
    "average": "float 0.0-1.0"
  },
  "overall_rhetoric_score": "float 0.0-1.0 — 加权平均 (D1×0.30+D2×0.20+D3×0.15+D4×0.20+D5×0.15)",
  "verdict": "excellent|good|pass|rewrite_needed",
  "improvement_suggestions": ["string"]
}
```

## 传递规则

- 每个 Hyland 维度必须有子项评估
- overconfident_claims 必须列出具体原文
- ambiguities 必须列出具体的模糊表达
