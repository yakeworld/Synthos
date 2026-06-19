# Kuhn/Lakatos — EVIDENCE_SCHEMA.md

> 对应原则：P0
> 理论来源：Kuhn (1962); Lakatos (1970)

## 节点结构

```json
{
  "source_type": "kuhn_lakatos_analysis",
  "source_ref": "research_program_or_hypothesis_id",
  "kuhn": {
    "paradigm_consensus": "float 0.0-1.0 — 领域共识度",
    "anomaly_count": "int — 反常现象数量",
    "crisis_severity": "float 0.0-1.0 — 危机严重程度",
    "alternatives_maturity": "float 0.0-1.0 — 替代方案成熟度",
    "classification": "normal_science|paradigm_shift|transitional",
    "justification": "string"
  },
  "lakatos": {
    "hard_core": "string — 核心假设",
    "protective_belt": ["string — 辅助假设列表"],
    "positive_heuristic": "string — 是否预测新现象",
    "negative_heuristic": "string — 保护核心方式",
    "health_score": "float 0.0-1.0 — 研究纲领健康度",
    "program_type": "progressive|mixed|declining"
  },
  "combined_assessment": {
    "novelty_level": "incremental|moderate|transformative",
    "investment_recommendation": "invest|caution|avoid",
    "risk_factors": ["string"]
  }
}
```

## 传递规则

- 必须识别 Hard Core
- health_score 必须基于 4 个维度加权计算
- paradigm_shift 需要额外 justification
