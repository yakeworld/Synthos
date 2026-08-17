---
name: kanban-worker
description: kanban-worker 金测集 — Kanban 工作区执行与交接的可执行测试（基于 kanban_* 工具）
---

# 金测集: kanban-worker

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (KANB-001~007)。
> 本技能是 Kanban 工作者：在 `$HERMES_KANBAN_WORKSPACE` 内执行分配到的任务，
> 以结构化的 `kanban_complete` / `kanban_block` / `kanban_comment` 交接给下游。
> IO_CONTRACT: input `task_list: list[Task], board_state: dict` → output `updated_board: dict`。
> 每个 case 验证一条真实可执行的操作契约（P1 可复现性）；错误路径必须返回结构化
> Golden Error（含 context + ≥2 条恢复建议），禁止仅返回通用错误。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：代码变更任务完成 → comment 写元数据 + `kanban_block(reason="review-required: ...")` | 启动先 `kanban_show` 确认非 blocked/archived（验证清单1）；代码变更任务不直接 complete 而是 block 并加 `review-required:` 前缀（KANB-003）；结构化元数据（changed_files/tests/decisions）先写入 `kanban_comment` 而非 block（block 只带人类可读 reason） |
| case_002 | 错误：`created_cards` 含虚构 ID → 门禁拒绝 complete，任务保持未终结 | 命中 KANB-005 → `created_cards` 仅可含成功 `kanban_create` 返回的真实 ID；虚构 ID 触发 gate reject，complete 被阻断且事件记入任务事件日志；返回结构化 Golden Error（context + ≥2 recovery） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `updated_board` 中该任务状态为 `blocked` 且 `reason` 以 `review-required: ` 前缀开头
  （KANB-003）；block 前已用 `kanban_comment` 写入含 `changed_files` / `tests_run` /
  `tests_passed` / `decisions` 的结构化 JSON 元数据；`kanban_complete` 未被调用；
  启动时 `kanban_show` 已执行且任务状态非 `blocked`/`archived`
- case_002: 必须命中 KANB-005（虚构 created_cards ID）→ 门禁拒绝 complete；任务状态保持
  未完成（`done: false`）；错误结构必须同时含 `context`（拒绝原因 + 虚构 ID 列表 +
  本 profile 实际创建的 ID 列表）与 ≥2 条可操作 `recovery`

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_002） |
| high | 0.7 | 重要但不致命（扩展用例） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: updated_board / block+comment 交接结构 / 错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 正常路径 `kanban_show_first: true`（启动先查状态）
- 代码变更正常路径：`blocked == true`，`reason` 以 `review-required: ` 开头，
  comment 中元数据含 `changed_files`/`tests_run`/`tests_passed`/`decisions`
- 正常路径 `kanban_complete_called == false`（review-required 场景不 complete）
- 错误路径 `completed == false` 且必须同时含 `context` 与 `recovery` 两个字段

## 关联

- SKILL.md Genes: KANB-001~007
- SKILL.md 验证清单: 6 项（先 kanban_show / worktree 初始化 / 租户前缀 / review-required block / created_cards 真实性 / retry 诊断）
- 关联技能: kanban-orchestrator, devops
