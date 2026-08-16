---
name: kanban-orchestrator
description: kanban-orchestrator
version: 1.0.0
category: devops
signature: 'kanban-orchestrator -> devops: Create Kanban tasks when any of these are
  true:'
license: MIT
author: Synthos
metadata:
  synthos:
    signature: 'task_desc: str, params: dict -> result: dict'
    atom_type: skill
    priority: P2
    related_skills: []
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告
## IO_CONTRACT

- **input**: `task_batch: list[str], priorities: dict` — 用户请求描述、上下文信息
- **output**: `work_items: list — 待办任务列表`

> 对应原则：P2（机械原子暴露输入输出规范）

# Kanban Orchestrator — Decomposition Playbook

> The **core worker lifecycle** (including the `kanban_create` fan-out pattern and the "decompose, don't execute" rule) is auto-injected into every kanban process via the `KANBAN_GUIDANCE` system-prompt block. This skill is the deeper playbook when you're an orchestrator profile whose whole job is routing.

## When to use the board (vs. just doing the work)

Create Kanban tasks when any of these are true:

1. **Multiple specialists are needed.** Research + analysis + writing is three profiles.
2. **The work should survive a crash or restart.** Long-running, recurring, or important.
3. **The user might want to interject.** Human-in-the-loop at any step.
4. **Multiple subtasks can run in parallel.** Fan-out for speed.
5. **Review / iteration is expected.** A reviewer profile loops on drafter output.
6. **The audit trail matters.** Board rows persist in SQLite forever.

If *none* of those apply — it's a small one-shot reasoning task — use `delegate_task` instead or answer the user directly.

## The anti-temptation rules

Your job description says "route, don't execute." The rules that enforce that:

- **Do not execute the work yourself.** Your restricted toolset usually doesn't even include terminal/file/code/web for implementation. If you find yourself "just fixing this quickly" — stop and create a task for the right specialist.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **If no specialist fits, ask the user which profile to create.** Do not default to doing it yourself under "close enough."
- **Decompose, route, and summarize — that's the whole job.**

## The standard specialist roster (convention)

Unless the user's setup has customized profiles, assume these exist. Adjust to whatever the user actually has — ask if you're unsure.

| Profile | Does | Typical workspace |
|---|---|---|
| `researcher` | Reads sources, gathers facts, writes findings | `scratch` |
| `analyst` | Synthesizes, ranks, de-dupes. Consumes multiple `researcher` outputs | `scratch` |
| `writer` | Drafts prose in the user's voice | `scratch` or `dir:` into their Obsidian vault |
| `reviewer` | Reads output, leaves findings, gates approval | `scratch` |
| `backend-eng` | Writes server-side code | `worktree` |
| `frontend-eng` | Writes client-side code | `worktree` |
| `ops` | Runs scripts, manages services, handles deployments | `dir:` into ops scripts repo |
| `pm` | Writes specs, acceptance criteria | `scratch` |

## Decomposition playbook

### Step 1 — Understand the goal

Ask clarifying questions if the goal is ambiguous. Cheap to ask; expensive to spawn the wrong fleet.

### Step 2 — Sketch the task graph

Before creating anything, draft the graph out loud (in your response to the user). Example for "Analyze whether we should migrate to Postgres":

```
T1  researcher        research: Postgres cost vs current
T2  researcher        research: Postgres performance vs current
T3  analyst           synthesize migration recommendation       parents: T1, T2
T4  writer            draft decision memo                       parents: T3
```

Show this to the user. Let them correct it before you create anything.

### Step 3 — Create tasks and link

```python
t1 = kanban_create(
    title="research: Postgres cost vs current",
    assignee="researcher",
    body="Compare estimated infrastructure costs, migration costs, and ongoing ops costs over a 3-year window. Sources: AWS/GCP pricing, team time estimates, current Postgres bills from peers.",
    tenant=os.environ.get("HERMES_TENANT"),
)["task_id"]

t2 = kanban_create(
    title="research: Postgres performance vs current",
    assignee="researcher",
    body="Compare query latency, throughput, and scaling characteristics at our expected data volume (~500GB, 10k QPS peak). Sources: benchmark papers, public case studies, pgbench results if easy.",
)["task_id"]

t3 = kanban_create(
    title="synthesize migration recommendation",
    assignee="analyst",
    body="Read the findings from T1 (cost) and T2 (performance). Produce a 1-page recommendation with explicit trade-offs and a go/no-go call.",
    parents=[t1, t2],
)["task_id"]

t4 = kanban_create(
    title="draft decision memo",
    assignee="writer",
    body="Turn the analyst's recommendation into a 2-page memo for the CTO. Match the tone of previous decision memos in the team's knowledge base.",
    parents=[t3],
)["task_id"]
```

`parents=[...]` gates promotion — children stay in `todo` until every parent reaches `done`, then auto-promote to `ready`. No manual coordination needed; the dispatcher and dependency engine handle it.

### Step 4 — Complete your own task

If you were spawned as a task yourself (e.g. `planner` profile was assigned `T0: "investigate Postgres migration"`), mark it done with a summary of what you created:

```python
kanban_complete(
    summary="decomposed into T1-T4: 2 researchers parallel, 1 analyst on their outputs, 1 writer on the recommendation",
    metadata={
        "task_graph": {
            "T1": {"assignee": "researcher", "parents": []},
            "T2": {"assignee": "researcher", "parents": []},
            "T3": {"assignee": "analyst", "parents": ["T1", "T2"]},
            "T4": {"assignee": "writer", "parents": ["T3"]},
        },
    },
)
```

### Step 5 — Report back to the user

Tell them what you created in plain prose:

> I've queued 4 tasks:
> - **T1** (researcher): cost comparison
> - **T2** (researcher): performance comparison, in parallel with T1
> - **T3** (analyst): synthesizes T1 + T2 into a recommendation
> - **T4** (writer): turns T3 into a CTO memo
>
> The dispatcher will pick up T1 and T2 now. T3 starts when both finish. You'll get a gateway ping when T4 completes. Use the dashboard or `hermes kanban tail <id>` to follow along.

## Common patterns

**Fan-out + fan-in (research → synthesize):** N `researcher` tasks with no parents, one `analyst` task with all of them as parents.

**Pipeline with gates:** `pm → backend-eng → reviewer`. Each stage's `parents=[previous_task]`. Reviewer blocks or completes; if reviewer blocks, the operator unblocks with feedback and respawns.

**Same-profile queue:** 50 tasks, all assigned to `translator`, no dependencies between them. Dispatcher serializes — translator processes them in priority order, accumulating experience in their own memory.

**Human-in-the-loop:** Any task can `kanban_block()` to wait for input. Dispatcher respawns after `/unblock`. The comment thread carries the full context.

## Large-scale architectural refactoring pattern

When refactoring an entire project structure (e.g., skills → cognitive atoms, monolith → microservices, flat → hierarchical), use this specialized decomposition pattern:

### Step 1 — Define the target state FIRST
Before touching any file, define the final target structure in one authoritative document (JSON registry, architecture diagram). All workers read from this single source of truth.

### Step 2 — Parallel launch all subtasks with a fixed batch (3-4 at a time)
Don't wait for one batch to finish before starting the next. Launch batches of 3-4 independent subtasks concurrently via `delegate_task`. Each subtask should be self-contained (doesn't need other subtasks' output).

### Step 3 — Order matters: definitions before deletion
Always create new files BEFORE deleting old ones. This prevents a "broken state" window where neither old nor new exist.

### Step 4 — Validate everything in one sweep
After all subtasks complete, run a single comprehensive validation:
- Python syntax: `py_compile` on every .py file
- JSON validity: `json.load()` on every .json file
- File existence: check each expected path
- SKILL.md existence: every skill dir must have SKILL.md
- Report results in one summary

### Step 5 — Update meta-files LAST
After all content is created and validated, update:
- skill_registry.json (master index)
- skill_network.json (dependency graph)
- TODO.md (task list)
- evolution-state.json (state snapshot)
- Main SKILL.md (overview)

### Anti-pattern: sequential subtasks
DON'T wait for each subtask to complete before starting the next if they're independent. This wastes time. The orchestration overhead is small compared to the subtask time.

## Pitfalls
- 
- 

## Verification
- 
- 

**Reassignment vs. new task.** If a reviewer blocks with "needs changes," create a NEW task linked from the reviewer's task — don't re-run the same task with a stern look. The new task is assigned to the original implementer profile.

**Argument order for links.** `kanban_link(parent_id=..., child_id=...)` — parent first. Mixing them up demotes the wrong task to `todo`.

**Don't pre-create the whole graph if the shape depends on intermediate findings.** If T3's structure depends on what T1 and T2 find, let T3 exist as a "synthesize findings" task whose own first step is to read parent handoffs and plan the rest. Orchestrators can spawn orchestrators.

**Tenant inheritance.** If `HERMES_TENANT` is set in your env, pass `tenant=os.environ.get("HERMES_TENANT")` on every `kanban_create` call so child tasks stay in the same namespace.

**Validation sweep before reporting.** After all subtasks complete, run ONE comprehensive validation sweep (Python py_compile, JSON load, file existence, SKILL.md check) before telling the user. Report all results in a single summary, not task-by-task. This prevents "task A done, task B done, but wait they conflict" surprises.

**Batch size limit.** Never launch more than 4-5 parallel subtasks in a single batch. The orchestration overhead becomes significant and debugging becomes harder. Stick to 3-4.

## Recovering stuck workers

When a worker profile keeps crashing, hallucinating, or getting blocked by its own mistakes (usually: wrong model, missing skill, broken credential), the kanban dashboard flags the task with a ⚠ badge and opens a **Recovery** section in the drawer. Three primary actions:

## 验证清单 · VERIFICATION

- [ ] 任务图草案（Task Graph）已展示给用户确认后才创建任务
- [ ] 每个具体任务均已通过 `kanban_create` 创建并分配给对应专家角色（未自行执行）
- [ ] 依赖链通过 `parents=[...]` 参数建立，子任务在父任务完成前保持 `todo` 状态
- [ ] 每个 `kanban_create` 调用均传入 `tenant=os.environ.get("HERMES_TENANT")`（如环境变量已设置）
- [ ] 大规模重构场景：先定义目标状态文档，再并行启动 3-4 个独立子任务批次
- [ ] 所有子任务完成后执行统一验证扫描（py_compile / json.load / 文件存在性 / SKILL.md 检查）再向用户报告

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

1. **Reclaim** (or `hermes kanban reclaim <task_id>`) — abort the running worker immediately and reset the task to `ready`. The existing claim TTL is ~15 min; this is the fast path out.
2. **Reassign** (or `hermes kanban reassign <task_id> <new-profile> --reclaim`) — switch the task to a different profile and let the dispatcher pick it up with a fresh worker.
3. **Change profile model** — the dashboard prints a copy-paste hint for `hermes -p <profile> model` since profile config lives on disk; edit it in a terminal, then Reclaim to retry with the new model.

Hallucination warnings appear on tasks where a worker's `kanban_complete(created_cards=[...])` claim included card ids that don't exist or weren't created by the worker's profile (the gate blocks the completion), or where the free-form summary references `t_<hex>` ids that don't resolve (advisory prose scan, non-blocking). Both produce audit events that persist even after recovery actions — the trail stays for debugging.

# Kanban Orchestrator

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[KANB-001]** 当任务涉及多专家协作、需持久化、需人工介入、可并行或需审计时 → 创建 Kanban 任务而非直接执行或简单委托
- **[KANB-002]** 当角色定位为编排者 (Orchestrator) 时 → 严格遵循“只路由不执行”原则，禁止自行处理具体工作
- **[KANB-003]** 当目标模糊或存在歧义时 → 先向用户提出澄清问题，避免生成错误的任务舰队
- **[KANB-004]** 在创建具体任务前 → 先向用户展示任务依赖图 (Task Graph) 草案，获得确认后再执行创建
- **[KANB-005]** 当子任务存在依赖关系时 → 使用 `parents` 参数建立依赖链，利用自动晋升机制替代手动协调
- **[KANB-006]** 当进行大规模架构重构时 → 先定义唯一权威的目标状态文档，再以 3-4 个独立子任务为批次并行启动
