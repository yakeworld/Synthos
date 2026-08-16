---
name: smart-home
description: smart-home
version: 1.0.0
category: devops
signature: 'smart-home -> devops: 智能家居 — Philips Hue灯光控制。'
related_skills:
- openhue
author: Synthos
license: MIT
triggers:
- 需要执行smart-home下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: 父级技能 — 智能家居 — Philips Hue灯光控制。
    signature: 'smart-home -> sub-skills: [openhue]'
    related_skills:
    - openhue
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

# smart-home

> 父级技能目录，包含 1 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `openhue`

## 使用方式

直接调用子技能名称即可：

## 验证清单 · VERIFICATION

- [ ] 子技能 `openhue` 是否可被 Hermes 自动发现并以 `skill_view(name='openhue')` 加载
- [ ] Hue Bridge 是否与执行终端处于同一局域网，且已完成按钮配对
- [ ] 子技能目录 `openhue/` 下引用的脚本/资源文件是否真实存在
- [ ] 返回的 `result: dict` 结构是否符合 `IO_CONTRACT` 声明
- [ ] 本父级 SKILL.md 是否仅作为目录索引，未与 `openhue` 子技能功能重叠

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
skill_view(name='openhue')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。

# Smart Home

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[SMAR-001]** 输入参数不完整或无效 → 立即执行输入验证并拒绝执行，确保参数类型、范围、格式符合约束
- **[SMAR-002]** 执行核心操作前 → 确认输入参数完整且符合 IO_CONTRACT 规范，避免无效调用
- **[SMAR-003]** 执行过程中 → 对中间步骤、转换及计算进行过程验证，确保逻辑正确性
- **[SMAR-004]** 生成输出结果时 → 严格校验输出格式、内容、编码及命名，确保符合预期契约
- **[SMAR-005]** 遇到空输入、极大值或异常场景 → 执行边界验证，确保系统具备处理极端情况的鲁棒性
- **[SMAR-006]** 操作失败或异常发生时 → 提供包含上下文信息和恢复建议的明确错误指引，便于快速定位与修复
- **[SMAR-007]** 涉及代码执行或状态暴露时 → 遵循安全约束，拒绝执行未验证的任意代码且不暴露内部状态
