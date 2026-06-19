# 同行评审模拟 — EVIDENCE_SCHEMA.md

> 对应原则：P0
> 理论来源：Nature/Science review standards

## 节点结构

```json
{
  "source_type": "peer_review_simulation",
  "source_ref": "paper_id",
  "reviewers": {
    "reviewer_A_methodology": {
      "scores": {
        "research_design": "int 0-10",
        "statistical_methods": "int 0-10",
        "sample_size_power": "int 0-10",
        "bias_control": "int 0-10",
        "reproducibility": "int 0-10",
        "ethics_compliance": "int 0-10"
      },
      "average": "float",
      "verdict": "accept_minor|major_revision|reject",
      "comments": "string — 详细评语",
      "must_fix": ["string"],
      "nice_to_have": ["string"]
    },
    "reviewer_B_domain": {
      "scores": {
        "literature_coverage": "int 0-10",
        "positioning": "int 0-10",
        "novelty": "int 0-10",
        "technical_depth": "int 0-10",
        "practical_significance": "int 0-10",
        "writing_quality": "int 0-10"
      },
      "average": "float",
      "verdict": "accept_minor|major_revision|reject",
      "comments": "string",
      "must_fix": ["string"],
      "nice_to_have": ["string"]
    },
    "reviewer_C_statistics": {
      "scores": {
        "statistical_model": "int 0-10",
        "hypothesis_testing": "int 0-10",
        "multiple_comparison": "int 0-10",
        "effect_size": "int 0-10",
        "result_interpretation": "int 0-10",
        "sensitivity_analysis": "int 0-10"
      },
      "average": "float",
      "verdict": "accept|revision_required|reject",
      "comments": "string",
      "must_fix": ["string"],
      "nice_to_have": ["string"]
    }
  },
  "senior_editor": {
    "final_decision": "accept|major_revision|reject",
    "justification": "string",
    "reviewer_disagreement": "bool — 是否出现评审冲突",
    "recommended_journal_tier": "T1|Q1|Q2|Q3|Q4"
  },
  "overall_score": "float 0.0-1.0 — 三位评审平均"
}
```

## 传递规则

- 每个 Reviewer 必须有详细评语 (不能只给分数)
- must_fix 列表合并所有 Reviewer 的必须修改项
- 评审冲突 (差异 > 30) 必须标注并给出仲裁理由
