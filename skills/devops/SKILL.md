---

name: devops
description: DevOps运维 — Cron任务管理、看板编排、worker管理。
triggers:
  - 需要执行devops下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — DevOps运维 — Cron任务管理、看板编排、worker管理。"
    signature: 'devops -> sub-skills: [cron-system-maintenance, kanban-orchestrator, kanban-worker]'
    related_skills: ["cron-system-maintenance", "kanban-orchestrator", "kanban-worker"]
---

# devops

> 父级技能目录，包含 3 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `cron-system-maintenance`
- `kanban-orchestrator`
- `kanban-worker`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='cron-system-maintenance')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
