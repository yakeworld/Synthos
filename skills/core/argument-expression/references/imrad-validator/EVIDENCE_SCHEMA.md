# IMRaD 结构验证 — EVIDENCE_SCHEMA.md

> 对应原则：P0
> 理论来源：ICMJE; IMRaD 标准

## 节点结构

```json
{
  "source_type": "imrad_structure_check",
  "source_ref": "paper_id_or_manuscript_id",
  "paper_type": "empirical|system|methodology|review|other",
  "sections": {
    "introduction": {
      "present": "bool",
      "elements": {
        "background": "bool",
        "gap": "bool",
        "purpose": "bool",
        "contributions": "bool"
      },
      "cars_moves": ["Move1", "Move2", "Move3"],
      "issues": ["string"]
    },
    "methods": {
      "present": "bool",
      "elements": {
        "design": "bool",
        "materials": "bool",
        "procedure": "bool",
        "measurement": "bool",
        "statistics": "bool",
        "ethics": "bool"
      },
      "issues": ["string"]
    },
    "results": {
      "present": "bool",
      "elements": {
        "primary_findings": "bool",
        "secondary_findings": "bool",
        "statistics": "bool",
        "tables_figs": "int"
      },
      "issues": ["string"]
    },
    "discussion": {
      "present": "bool",
      "elements": {
        "summary": "bool",
        "literature_comparison": "bool",
        "mechanism": "bool",
        "limitations": "int (≥3)",
        "implications": "bool",
        "future_work": "bool"
      },
      "issues": ["string"]
    }
  },
  "system_paper_additional": {
    "architecture_present": "bool",
    "evolution_mechanisms_present": "bool",
    "philosophy_engineering_mapping": "bool"
  },
  "overall_score": "float 0.0-1.0",
  "verdict": "PASS|REVISE|REJECT",
  "failures": ["string"],
  "warnings": ["string"]
}
```

## 评分规则

- 每个元素 present=true 计 1 分
- overall_score = 有效元素分 / 总必需元素分
- 系统论文额外检查 architecture/evolution/映射
- verdict: PASS (≥0.80, ≤1 WARN) | REVISE (0.60-0.79) | REJECT
