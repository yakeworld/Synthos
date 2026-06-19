# 实验设计检查 — EVIDENCE_SCHEMA.md

> 对应原则：P0, P1
> 理论来源：CONSORT; STROBE; CASP; COREQ; PICOS

## 证据链节点类型

| source_type | 何时产生 |
|------------|----------|
| `experimental_design_check` | 检查任何实验/研究设计的方法学质量时 |

## 节点结构

```json
{
  "source_type": "experimental_design_check",
  "source_ref": "paper_id_or_protocol_id",
  "study_type": "RCT|observational|simulation|qualitative|diagnostic|meta|other",
  "pikos": {
    "population": "string",
    "intervention": "string",
    "comparison": "string",
    "outcome": "string",
    "study_design": "string"
  },
  "dimensions": {
    "sample_design": {
      "score": "float 0.0-1.0",
      "passed": "bool",
      "issues": ["string"]
    },
    "randomization_blinding": {
      "score": "float 0.0-1.0",
      "passed": "bool",
      "issues": ["string"]
    },
    "control_design": {
      "score": "float 0.0-1.0",
      "passed": "bool",
      "issues": ["string"]
    },
    "variable_definition": {
      "score": "float 0.0-1.0",
      "passed": "bool",
      "issues": ["string"]
    },
    "data_analysis": {
      "score": "float 0.0-1.0",
      "passed": "bool",
      "issues": ["string"]
    }
  },
  "reporting_checklist": {
    "framework": "CONSORT|STROBE|COREQ|STARD|PRISMA|none",
    "items_checked": "int",
    "items_passed": "int",
    "compliance": "float"
  },
  "overall_score": "float 0.0-1.0 — 加权平均 (D1×0.25+D2×0.20+D3×0.15+D4×0.20+D5×0.20)",
  "verdict": "PASS|REVISE|REJECT",
  "failures": ["string — 直接FAIL的项"],
  "warnings": ["string — 建议修改的项"],
  "required_actions": ["string — 必须修复的具体项"]
}
```

## 评分规则

- overall_score: 加权平均，权重见 EXPERIMENTAL-DESIGN.md
- verdict: PASS (≥0.80, ≤1 WARN) | REVISE (0.60-0.79) | REJECT (<0.60 或有 FAIL)
- 每个 dimension 的 issues 列表必须具体 (如 "no power analysis for sample size n=24")
