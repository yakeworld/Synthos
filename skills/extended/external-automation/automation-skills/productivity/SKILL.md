---
name: productivity
description: productivity
version: 1.0.0
category: productivity
signature: 'productivity -> productivity: 生产力工具 — 表单自动化、Jupyter、地图、PPT、Notion等。'
author: Synthos
license: MIT
triggers:
- 需要执行productivity下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: 父级技能 — 生产力工具 — 表单自动化、Jupyter、地图、PPT、Notion等。
    signature: 'productivity -> sub-skills: [chinese-form-automation, jupyter-live-kernel,
      maps, markitdown-convert, notebooklm-cli, notion, obsidian, powerpoint, webhook-subscriptions,
      youtube-content]'
    related_skills:
    - chinese-form-automation
    - jupyter-live-kernel
    - maps
    - notebooklm-cli
    - notion
    - powerpoint
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

# productivity

> 父级技能目录，包含 10 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `chinese-form-automation`
- `jupyter-live-kernel`
- `maps`
- `markitdown-convert`
- `notebooklm-cli`
- `notion`
- `obsidian`
- `powerpoint`
- `webhook-subscriptions`
- `youtube-content`

## 使用方式

直接调用子技能名称即可：

## 验证清单 · VERIFICATION

- [ ] 正确路由到对应子技能（chinese-form-automation / jupyter-live-kernel / maps / markitdown-convert / notebooklm-cli / notion / obsidian / powerpoint / webhook-subscriptions / youtube-content）而非在父级硬编码逻辑
- [ ] 接收请求时校验输入参数（request/context）的类型、范围、格式完整性，符合 IO 契约
- [ ] 核心操作参考本目录 scripts/ 或 references/ 资源，中间步骤/转换/计算正确
- [ ] 最终输出格式、内容、编码、命名符合契约并正确保存结果
- [ ] 空输入/极大值/异常场景被边界处理，不崩溃
- [ ] 失败时提供含上下文与明确恢复建议的错误指引；拒绝执行未验证代码、不暴露内部状态

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
skill_view(name='chinese-form-automation')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。

# Productivity

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[PROD-001]** 当需要执行生产力相关任务时 → 通过 Hermes 机制自动发现并直接调用对应的子技能名称，而非在父级技能中硬编码逻辑
- **[PROD-002]** 当接收用户请求时 → 严格校验输入参数（request/context）的类型、范围及格式完整性，确保符合 IO 契约
- **[PROD-003]** 当执行核心操作时 → 参考 scripts/ 或 references/ 目录下的资源，确保中间步骤、转换及计算的正确性
- **[PROD-004]** 当生成最终结果时 → 验证输出格式、内容、编码及命名是否符合预期契约，并保存结果
- **[PROD-005]** 当遇到空输入、极大值或异常场景时 → 执行边界验证，确保系统能处理极端情况并防止崩溃
- **[PROD-006]** 当操作失败时 → 提供包含上下文信息和明确恢复建议的错误指引，而非仅抛出通用错误
- **[PROD-007]** 当涉及代码执行或状态暴露时 → 拒绝执行未验证的任意代码，不暴露内部状态，确保安全性
- **[PROD-008]** 当进行技能迭代或测试时 → 以 Golden 集合（标准输入/预期输出/预期错误）为单一真理来源，确保所有改进通过可复现的测试
