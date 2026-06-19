# 可重复性检查 — EVIDENCE_SCHEMA.md

> 对应原则：P0, P1
> 理论来源：Ioannidis (2005); Open Science Framework

## 节点结构

```json
{
  "source_type": "reproducibility_check",
  "source_ref": "paper_id",
  "data_availability": {
    "public": "bool",
    "platform": "string (GitHub|Figshare|Zenodo|OSF|None)",
    "access": "open|restricted|request",
    "doi": "string or null"
  },
  "code_availability": {
    "public": "bool",
    "repository": "string",
    "version": "string (commit hash)",
    "environment": "string (Docker|conda|requirements)",
    "example_data": "bool"
  },
  "preregistration": {
    "registered": "bool",
    "platform": "string (OSF|AsPredicted|ClinicalTrials|None)",
    "id": "string or null",
    "exempt": "bool — 回溯性/案例/方法论可豁免"
  },
  "reporting_checklist_compliance": {
    "framework": "CONSORT|STROBE|COREQ|STROBE-Sim|STARD|PRISMA|none",
    "items_passed": "int",
    "total_items": "int",
    "compliance_rate": "float"
  },
  "effect_size_reported": {
    "has_effect_size": "bool",
    "has_ci_95": "bool",
    "has_p_value": "bool",
    "effect_size_type": "string (Cohens_d|OR|RR|HR|r|none)"
  },
  "negative_results_reported": {
    "all_outcomes_reported": "bool",
    "unexpected_findings_reported": "bool",
    "selective_reporting": "bool"
  },
  "ioannidis_risk_signals": {
    "small_sample": "bool",
    "no_preregistration": "bool",
    "multiple_outcomes": "bool",
    "p_hacking_risk": "bool",
    "conflict_of_interest": "bool",
    "low_consensus_field": "bool",
    "hot_field": "bool",
    "total_signals": "int"
  },
  "reproducibility_score": "float 0.0-1.0",
  "verdict": "HIGHLY_REPRODUCIBLE|MODERATELY_REPRODUCIBLE|LOW_REPRODUCIBILITY",
  "recommended_actions": ["string"]
}
```

## 传递规则

- 每个可用性声明必须有可验证链接
- 预注册必须可查询
- Ioannidis 风险信号用于标记需要独立验证的研究
