---
name: devops
description: devops 父级路由金测集 — 验证运维请求正确路由到子技能
---

# 金测集: devops

> 来源: SKILL.md Genes DEVO-001~006 + 验证清单。每个 case 验证父级路由入口能否将运维请求正确分发到对应子技能（P1 可复现性）。
> 父级职责: 目录索引 + 路由，不直接执行运维操作（DEVO-002: 优先通过子技能执行而非父级直接操作）。

## 路由逻辑

| 请求特征 | 路由目标 | 依据 |
|----------|----------|------|
| Cron 任务管理/维护/调度 | `cron-system-maintenance` | DEVO-002: 优先通过子技能执行 |
| 看板编排/任务分发/worker 调度 | `kanban-orchestrator` | DEVO-002: 优先通过子技能执行 |
| 单任务执行/worker 状态 | `kanban-worker` | DEVO-002: 优先通过子技能执行 |
| 未知子技能/越界请求 | 拒绝 + 结构化错误 | DEVO-004: 错误含上下文与恢复指引 |

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由: Cron 任务维护 → cron-system-maintenance | routed_to == 'cron-system-maintenance', 父级不越权执行 |
| case_002 | 错误路径: 未知子技能 | 返回结构化 error, 含上下文与恢复建议, 不崩溃 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `routed_to` 必须精确匹配目标子技能名，父级 `parent_executed` 必须为 `false`（DEVO-002），`result` 符合 IO_CONTRACT 结构
- case_002: 必须返回结构化错误（含 `error_type`、`context`、`recovery`），不得吞掉异常（DEVO-004: 错误信息必须包含上下文和明确的恢复指引）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001/002） |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 关联

- SKILL.md Genes: DEVO-001~006
- 子技能: cron-system-maintenance, kanban-orchestrator, kanban-worker
- 验证清单: SKILL.md L66-71

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-13 | 初始金测集，2 个 case（正常路由 + 未知子技能错误路径） | Synthos Agent |
