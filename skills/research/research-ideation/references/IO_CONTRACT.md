# IO_CONTRACT.md — research-ideation

## 输入契约 (Input Contract)

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `problem_statement` | string | ✅ | 研究问题描述 |
| `context` | string | ❌ | 可选上下文/约束 |
| `upstream_findings` | json | ❌ | 上游原子输出（如GAP空白） |

## 输出契约 (Output Contract)

| 字段 | 类型 | 说明 |
|------|------|------|
| `ideations` | list[IdeationItem] | 研究方向候选列表 |
| `cognitive_insights` | list[CognitiveInsight] | 认知洞察（仅L2激活时） |
| `statistics` | json | 统计数据 |

## IdeationItem Schema

```yaml
id: string
title: string
description: string
framework_sources: list[string]
scores:
  novelty: integer  # 1-5
  feasibility: integer  # 1-5
  impact: integer  # 1-5
  composite: float
risk_flags: list[{type, description}]
```

## CognitiveInsight Schema

```yaml
id: string
framework: string
insight: string
dimension: string
value_assessment:
  novelty: integer  # 1-5
  actionability: integer  # 1-5
```
