---
name: github
description: github 金测集 — 父级路由索引的可执行测试
---

# 金测集: github

> 来源: SKILL.md「Golden 集合 · GOLDEN SET」+「验证清单 · VERIFICATION」。
> 本技能为父级路由索引（atom_type: parent-skill），不直接实现 GitHub 操作；
> 每个 case 验证路由决策的正确性（P1 可复现性）与错误路径的合规处理（GITH-005/GITH-006）。

## 子技能清单（路由目标，7 个）

- `codebase-inspection` — 仓库代码规模/结构分析（mlops）
- `github-auth` — GitHub 认证
- `github-code-review` — PR 代码审查
- `github-discussions` — Discussion 创建/列表/搜索/管理
- `github-issues` — Issue 管理
- `github-pr-workflow` — PR 工作流
- `github-repo-management` — 仓库管理

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常路由 — 仓库代码分析委托 codebase-inspection | route=delegate, target=codebase-inspection, context 含 owner/repo |
| case_002 | 正常路由 — Discussion 管理委托 github-discussions | route=delegate, target=github-discussions |
| case_003 | 错误路径 — 未知子技能名称 | route=reject, error 含上下文与恢复建议，不臆造路由 |
| case_004 | 错误路径 — context 缺失 owner/repo，契约不完整 | route=reject, error=contract_incomplete |

## 通过标准

- 加权总分 ≥ 0.80（critical 项必过）
- case_001/002: route 必须为 delegate，target 必须精确命中上表 7 个子技能之一，context 含必要 owner/repo（验证清单 L70）
- case_003/004: 必须拒绝（route=reject），错误信息必须包含具体上下文与恢复指引（GITH-006）；不得静默失败、不得臆造未知子技能、不得直接执行 GitHub 操作
- expected/ 与 cases/ 文件数量与命名一一对应（case_001..case_004）

## 权重

| 权重 | 值 | 用例 | 含义 |
|------|----|------|------|
| critical | 1.0 | case_001, case_003 | 正常路由命中 / 未知子技能拒绝（核心判别） |
| high | 0.7 | case_002, case_004 | 次级路由 / 契约完整性错误路径 |

## 关联

- SKILL.md Genes: GITH-001 ~ GITH-007
- SKILL.md 验证清单: 5 项 checkbox（7子技能可路由 / IO契约 / 父级仅索引 / Hermes自动发现 / 状态变更安全）
- 方法论: golden-test-methodology（GOLD-001/002/003）
