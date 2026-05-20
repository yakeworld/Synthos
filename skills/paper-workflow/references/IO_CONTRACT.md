# IO_CONTRACT.md — paper-workflow

> 对应原则：P0, P3
> 原子类型：workflow

## 输入

| 字段 | 类型 | 来源 | 必填 | 说明 |
|:----|:----|:----|:----|:-----|
| `hypotheses` | list[Hypothesis] | hypothesis-generation | 否 | 若为空，本工作流先运行HYP |
| `raw_papers` | list[Paper] | knowledge-acquisition | 否 | 用于框架中的引用支撑 |
| `mode` | string | 用户或路由器 | 否 | "default" (模式A) 或 "explore" (模式C) |
| `user_goal` | string | 用户 | 否 | 用户的研究目标描述 |

## 输出

| 字段 | 类型 | 说明 |
|:----|:----|:------|
| `paper_framework` | PaperFramework | 结构化的论文框架（含6个核心要素） |
| `human_decision` | HumanDecision | 人类确认记录（追溯用） |
| `final_paper` | assembled_output | ARG+VER 输出的最终论文 |

## PaperFramework Schema

```yaml
paper_framework:
  title: string
  research_gap:
    description: string
    gap_type: "methodology_gap|contradiction|unanswered_question|obsolete"
    supporting_refs: [string]
    significance: "P0|P1|P2|P3"
  hypothesis:
    claim: string
    prediction: string
    falsification: string
    supporting_evidence: [string]
  technical_approach:
    method: string
    dataset: string
    variables: [string]
    analysis_plan: string
  experiment_design:
    design_type: string
    population: string
    sample_size: string
    primary_outcome: string
    secondary_outcomes: [string]
  expected_results:
    primary_finding: string
    effect_size_estimate: string
    alternative_outcomes: [string]
  key_conclusions:
    main_claim: string
    significance: string
    limitations: [string]
    next_steps: [string]
```

## HumanDecision Schema

```yaml
human_decision:
  mode_used: "default|explore"
  selected_variant_id: string|null
  user_feedback: string
  modifications: [string]  # 用户要求的修改
  confirmed_at: timestamp
```
