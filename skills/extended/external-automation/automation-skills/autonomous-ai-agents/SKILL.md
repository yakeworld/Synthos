---
name: autonomous-ai-agents
description: autonomous-ai-agents
version: 1.0.0
category: automation
signature: 'autonomous-ai-agents -> automation: 自主AI智能体编排 — 多Agent协作、委托任务、跨Agent通信。'
author: Synthos
license: MIT
triggers:
- 需要执行autonomous-ai-agents下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: 父级技能 — 自主AI智能体编排 — 多Agent协作、委托任务、跨Agent通信。
    signature: 'autonomous-ai-agents -> sub-skills: [ai-outreach, claude-code, codex]'
    related_skills:
    - ai-outreach
    - claude-code
    - codex
    - hermes-agent
    - moltbook-connector
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

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

# autonomous-ai-agents

> 父级技能目录，包含 6 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `ai-outreach`
- `claude-code`
- `codex`
- `hermes-agent`
- `moltbook-connector`
- `opencode`

## 使用方式

直接调用子技能名称即可：

## 验证清单 · VERIFICATION

- [ ] 本目录已列出全部 6 个子技能（ai-outreach、claude-code、codex、hermes-agent、moltbook-connector、opencode），无遗漏
- [ ] 每个子技能可通过 Hermes 技能加载机制被发现并以 `skill_view(name=...)` 直接加载，无需显式配置
- [ ] 父级 SKILL.md 仅作为路由/目录索引，未自行实现与子技能重叠的执行逻辑（原子边界不重叠）
- [ ] 复杂任务已按多 Agent 协作委托给对应子技能，跨 Agent 间的信息（输入/上下文/结果）在子技能间有效流转
- [ ] 调用子技能前已按 IO 契约校验输入参数（类型/范围/格式），不符合契约的请求被拒绝
- [ ] 子技能执行失败时返回含上下文与恢复建议的错误信息，父级据此隔离或降级，不向下游传播未验证状态

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
skill_view(name='ai-outreach')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。

# Autonomous Ai Agents

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[AUTO-015]** 当需要执行复杂自动化任务时 → 采用多Agent协作模式，通过委托任务实现分工与并行处理
- **[AUTO-016]** 当涉及多个智能体交互时 → 建立跨Agent通信机制，确保信息在子技能间有效流转
- **[AUTO-017]** 当调用子技能时 → 利用Hermes技能加载机制自动发现并直接调用子技能名称，无需显式配置
- **[AUTO-018]** 当执行核心操作前 → 严格校验输入参数的类型、范围及格式，确保符合IO契约规范
- **[AUTO-019]** 当处理异常或失败场景时 → 提供包含上下文和恢复建议的明确错误信息，并执行隔离或拒绝操作
- **[AUTO-020]** 当验证技能执行结果时 → 基于Golden集合（标准输入/预期输出/预期错误）进行单一真理来源的精确匹配或格式校验
- **[AUTO-007]** 当执行安全敏感操作时 → 拒绝执行未验证的任意代码，并严格保护内部状态不对外暴露
