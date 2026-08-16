---
name: devops
description: devops
version: 1.0.0
category: devops
signature: 'devops -> devops: DevOps运维 — Cron任务管理、看板编排、worker管理。'
author: Synthos
license: MIT
triggers:
- 需要执行devops下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: 父级技能 — DevOps运维 — Cron任务管理、看板编排、worker管理。
    signature: 'devops -> sub-skills: [cron-system-maintenance, kanban-orchestrator,
      kanban-worker]'
    related_skills:
    - cron-system-maintenance
    - kanban-orchestrator
    - kanban-worker
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 
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

- [ ] 用户请求正确路由到对应子技能（cron-system-maintenance / kanban-orchestrator / kanban-worker），父级未直接越权执行
- [ ] 子技能通过 Hermes 技能加载机制（如 `skill_view(name='cron-system-maintenance')`）成功发现并加载，无需显式路径
- [ ] 子技能返回的 `result: dict` 符合 IO_CONTRACT 结构，关键字段非空且格式正确
- [ ] 涉及 cron 任务时，修改后已验证调度仍生效（任务列表/下次触发时间符合预期）
- [ ] 失败场景下错误信息包含上下文与恢复指引，未吞掉异常

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

```
skill_view(name='cron-system-maintenance')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。

# Devops

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[DEVO-001]** 执行核心操作前 → 必须确认输入参数完整且符合契约规范
- **[DEVO-002]** 处理用户请求时 → 优先通过子技能（如 cron-system-maintenance）执行而非父级直接操作
- **[DEVO-003]** 验证输出结果时 → 需同时检查格式、内容符合预期及边界异常场景
- **[DEVO-004]** 发生执行失败时 → 错误信息必须包含上下文和明确的恢复指引
- **[DEVO-005]** 执行任意代码或操作前 → 必须经过安全验证，拒绝未验证的任意代码执行
- **[DEVO-006]** 进行技能改进或测试时 → 必须通过 Golden 集合（标准输入/输出/错误）作为单一真理来源进行校验
