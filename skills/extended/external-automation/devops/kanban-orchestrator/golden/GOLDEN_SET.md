---
name: kanban-orchestrator
description: kanban-orchestrator 金测集 — Kanban 任务分解与路由的可执行测试（基于 kanban_* 工具）
---

# 金测集: kanban-orchestrator

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (KANB-001~006)。
> 本技能是 Kanban 编排者：将用户目标分解为任务图（Task Graph），经用户确认后
> 用 `kanban_create` 建卡并建依赖链，严格"只路由不执行"。
> IO_CONTRACT: input `task_batch: list[str], priorities: dict` → output `work_items: list`。
> 每个 case 验证一条真实可执行的操作契约（P1 可复现性）；错误路径必须返回结构化
> Golden Error（含 context + ≥2 条恢复建议），禁止仅返回通用错误。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：多专家协作目标 → 展示任务图 → 确认后建卡（fan-out+fan-in） | 创建前先向用户展示任务图草案并获确认（KANB-004）；每个具体任务 `kanban_create` 并分配给对应专家，编排者不自行执行（KANB-002）；`parents=[...]` 建依赖链（KANB-005）；`HERMES_TENANT` 已设置时每次 `kanban_create` 均传 `tenant` |
| case_002 | 错误：目标模糊 → 先澄清，不建卡 | 命中 KANB-003 → 拒绝创建任何任务；返回结构化 Golden Error（context + ≥2 recovery）；不产生"错误的任务舰队" |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: `work_items` 中每个条目都有 `assignee`（标准专家角色名）且编排者自身未执行
  任何子任务内容（KANB-002）；任务图草案 `task_graph` 先于创建动作出现并经用户确认
  （KANB-004）；有依赖的子任务必须带 `parents` 且父任务 ID 指向本批已创建的真实
  `task_id`（KANB-005）；`HERMES_TENANT` 已设置时所有建卡调用带 `tenant`（验证清单第4项）
- case_002: 必须命中 KANB-003（目标模糊/歧义）→ 拒绝建卡；`work_items` 为空；错误结构
  必须同时含 `context`（请求回声 + 歧义点 + 待澄清问题列表）与 ≥2 条可操作 `recovery`

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_002） |
| high | 0.7 | 重要但不致命（扩展用例） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: work_items / 任务图 / 错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 正常路径 `work_items` 非空，每项含 `title` / `assignee` / `task_id`（非虚构，来自
  `kanban_create` 返回值），有依赖者含 `parents`
- 正常路径必须记录 `task_graph_confirmed: true`（先展示后创建，KANB-004）
- 正常路径 `executed_by_orchestrator: false`（只路由不执行，KANB-002）
- 错误路径 `work_items` 为空且必须同时含 `context` 与 `recovery` 两个字段

## 关联

- SKILL.md Genes: KANB-001~006
- SKILL.md 验证清单: 6 项（任务图先确认 / 全部建卡分配 / parents 依赖链 / tenant 传递 / 重构分批 / 统一验证扫描）
- 关联技能: kanban-worker, devops
