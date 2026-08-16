---
name: media
description: media
version: 1.0.0
category: creative
signature: 'media -> creative: 媒体内容 — GIF搜索、音乐生成、音谱分析、Spotify控制。'
author: Synthos
license: MIT
triggers:
- 需要执行media下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: 父级技能 — 媒体内容 — GIF搜索、音乐生成、音谱分析、Spotify控制。
    signature: 'media -> sub-skills: [gif-search, heartmula, songsee]'
    related_skills:
    - gif-search
    - heartmula
    - songsee
    - spotify
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

# media

> 父级技能目录，包含 4 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `gif-search`
- `heartmula`
- `songsee`
- `spotify`

## 使用方式

直接调用子技能名称即可：

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

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
skill_view(name='gif-search')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。

# Media

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[MEDI-001]** 用户请求涉及媒体内容（GIF/音乐/音谱/Spotify） → 识别为父级技能，通过 Hermes 机制自动发现并路由至对应子技能
- **[MEDI-002]** 执行核心操作前 → 必须确认输入参数（request/context）完整且符合 IO_CONTRACT 规范
- **[MEDI-003]** 处理输入数据时 → 严格校验参数类型、范围及格式，拒绝未验证的任意代码执行
- **[MEDI-004]** 生成输出结果时 → 确保返回值结构、编码及命名与契约一致，并验证内容符合预期
- **[MEDI-005]** 遇到空输入、极大值或异常场景 → 执行边界验证，确保系统具备明确的错误信息和恢复指引
- **[MEDI-006]** 技能执行过程中 → 遵循“可执行、可记录、可复现”原则，对中间步骤和最终结果进行全链路验证
