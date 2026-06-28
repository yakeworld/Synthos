---


name: devops
description: DevOps运维 — Cron任务管理、看板编排、worker管理。
author: Synthos
license: MIT
version: 1.0.0
license: MIT
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


## IO_CONTRACT

- **input**: `pipeline_stage: str` — 用户请求描述、上下文信息
- **output**: `result: dict — DevOps操作`

> 对应原则：P2（机械原子暴露输入输出规范）



# devops

> 父级技能目录，包含 3 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `cron-system-maintenance`
- `kanban-orchestrator`
- `kanban-worker`

## 使用方式

直接调用子技能名称即可：


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

```
skill_view(name='cron-system-maintenance')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
