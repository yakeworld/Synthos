# Meta-分析方法 — EVIDENCE_SCHEMA.md

> 对应原则：P0
> 理论来源：PRISMA 2020; Cochrane Handbook

## 节点结构

```json
{
  "source_type": "meta_analysis_check",
  "source_ref": "review_paper_id",
  "prisma": {
    "flow_diagram_present": "bool",
    "databases_searched": ["string"],
    "records_identified": "int",
    "duplicates_removed": "int",
    "records_screened": "int",
    "full_text_assessed": "int",
    "studies_included": "int"
  },
  "quality_assessment": {
    "tool_used": "RoB2|ROBINS-I|NOS|QUADAS2|CASP|none",
    "assessors_count": "int (≥2 expected)",
    "individual_scores": ["float"],
    "mean_quality": "float"
  },
  "meta_analysis": {
    "model_type": "fixed|random|none",
    "heterogeneity": {
      "Q_statistic": "float",
      "Q_p_value": "float",
      "I_squared": "float",
      "tau_squared": "float"
    },
    "effect_size": "float",
    "confidence_interval": ["float", "float"],
    "forest_plot_present": "bool"
  },
  "bias_assessment": {
    "funnel_plot_present": "bool",
    "eggers_test": "float",
    "beggs_test": "float",
    "fail_safe_n": "int",
    "publication_bias": "absent|possible|likely"
  },
  "sensitivity_analysis": {
    "performed": "bool",
    "methods": ["string"],
    "results_stable": "bool"
  },
  "overall_score": "float 0.0-1.0",
  "verdict": "PASS|REVISE|REJECT"
}
```

## 传递规则

- PRISMA 流程图必须 present
- 检索数据库 ≥ 3
- 质量评估 assessors ≥ 2
