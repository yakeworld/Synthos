---
name: autonomous-ai-agents
description: autonomous-ai-agents 金测集 — 父级路由索引的可执行测试
---

# 金测集: autonomous-ai-agents

> 来源: SKILL.md「Golden 集合 · GOLDEN SET」+「验证清单 · VERIFICATION」。
> 本技能为父级路由索引（atom_type: parent-skill），不直接执行任务；
> 每个 case 验证路由决策的正确性（P1 可复现性）与错误路径的合规处理（AUTO-005/AUTO-007）。

## 子技能清单（路由目标）

- `ai-outreach` — AI 平台信号发布（social-media）
- `claude-code` — Claude Code CLI 编程代理（mlops）
- `codex` — Codex CLI 编程代理（mlops）
- `hermes-agent` — Hermes Agent 运行时
- `moltbook-connector` — Moltbook 平台连接器
- `opencode` — OpenCode 非 daemon 编程代理（mlops）

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由 — 编码任务委托 claude-code | route=delegate, target=claude-code, 输入契约校验通过 |
| case_002 | 正常路由 — 未知平台 AI 信号发布路由 ai-outreach | route=delegate, target=ai-outreach |
| case_003 | 错误路径 — 未知子技能名称 | route=reject, error 含上下文与恢复建议，不臆造路由 |
| case_004 | 错误路径 — request 为空违反 IO 契约 | route=reject, error=contract_violation |

## 通过标准

- 加权总分 ≥ 0.80（critical 项必过）
- case_001/002: route 必须为 delegate，target 必须精确命中上表子技能名，且父级不自行实现执行逻辑
- case_003/004: 必须拒绝（route=reject），错误信息必须包含上下文（context）与恢复建议（recovery_hint）；不得静默失败、不得臆造未知子技能
- expected/ 与 cases/ 文件数量与命名一一对应（case_001..case_004）

## 权重

| 权重 | 值 | 用例 | 含义 |
|------|----|------|------|
| critical | 1.0 | case_001, case_003 | 正常路由命中 / 未知子技能拒绝（核心判别） |
| high | 0.7 | case_002, case_004 | 次级路由 / 契约校验错误路径 |

## 关联

- SKILL.md Genes: AUTO-001 ~ AUTO-007
- SKILL.md 验证清单: 6 项 checkbox（子技能清单完整 / Hermes 可发现 / 原子边界不重叠 / 跨Agent流转 / 契约校验 / 失败隔离）
- 方法论: golden-test-methodology（GOLD-001/002/003）
