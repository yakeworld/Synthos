---
name: kanban-worker
description: kanban-worker
version: 1.0.0
category: devops
signature: 'kanban-worker -> devops: Your workspace kind determines how you should
  behave inside `$HERMES_KANBAN_WORK'
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

- **input**: `task_list: list[Task], board_state: dict` — 任务描述、参数配置
- **output**: `updated_board: dict — 执行结果`

> 对应原则：P2（机械原子暴露输入输出规范）

## Workspace handling

Your workspace kind determines how you should behave inside `$HERMES_KANBAN_WORKSPACE`:

| Kind | What it is | How to work |
|