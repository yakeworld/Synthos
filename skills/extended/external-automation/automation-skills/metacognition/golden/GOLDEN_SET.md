---
name: metacognition
description: metacognition 父级路由金测集 — 验证子技能路由决策的正确性
---

# 金测集: metacognition

> 来源: SKILL.md Genes META-001~006 + 验证清单。每个 case 验证父级路由入口能否将请求正确分发到子技能（P1 可复现性）。
> 父级职责: 目录索引 + 路由，不承载业务逻辑。

## 路由逻辑

| 请求特征 | 路由目标 | 依据 |
|----------|----------|------|
| 涉及自主执行阈值/置信度决策 | `autonomous-execution-threshold` | META-006: Hermes 机制发现子技能 |
| 涉及记忆优化/清理/压缩 | `memory-optimization-system` | META-006: Hermes 机制发现子技能 |
| 未知子技能/越界请求 | 拒绝 + 错误信息 | META-002: 错误含上下文与恢复指引 |

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由: 自主执行阈值 | routed_to == 'autonomous-execution-threshold', 父级不直接执行 |
| case_002 | 错误路径: 未知子技能 | 返回 error, 含上下文与恢复建议, 不崩溃 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `routed_to` 必须精确匹配目标子技能名，父级 `executed` 必须为 `false`
- case_002: 必须返回结构化错误（含 `error_type`、`context`、`recovery`），不得静默失败或崩溃

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001/002） |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 关联

- SKILL.md Genes: META-001~006
- 子技能: autonomous-execution-threshold, memory-optimization-system
- 验证清单: SKILL.md L63-68

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-13 | 初始金测集，2 个 case（正常路由 + 错误路径） | Synthos Agent |
