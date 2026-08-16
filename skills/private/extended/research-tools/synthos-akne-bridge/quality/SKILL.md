---
name: quality
description: 1. 确认输入参数完整
signature: 'quality -> synthos-akne-bridge: synthetic skill for quality'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: 1. 确认输入参数完整
    signature: 'quality -> synthos-akne-bridge: synthetic skill for quality'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
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
category: research-tools
signature: "quality -> research-tools: 质量保障 — 伪证验证、黄金测试。"
description: 质量保障 — 伪证验证、黄金测试。
author: Synthos
license: MIT
version: 1.0.0
triggers:
  - 需要执行quality下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 质量保障 — 伪证验证、黄金测试。"
    signature: 'quality -> sub-skills: [falsification-validation, golden-test-methodology]'
    related_skills: ["falsification-validation", "golden-test-methodology"]

## IO_CONTRACT

- **input**: `skill_path: str` — 用户请求描述、上下文信息
- **output**: `quality_report: dict — 质量报告`

> 对应原则：P2（机械原子暴露输入输出规范）

# quality

> 父级技能目录，包含 2 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `falsification-validation`
- `golden-test-methodology`

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

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

```
skill_view(name='falsification-validation')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。

# Quality---

> (P032 去重: 以下为合并前第二份中的 1 行独有内容, 保留以防丢失)
# Quality
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[QUAL-001]** 输入参数/文件/路径不完整或无效 → 必须执行输入验证并拒绝执行
- **[QUAL-002]** 中间步骤/转换/计算过程 → 必须验证其正确性以确保过程合规
- **[QUAL-003]** 输出格式/内容不符合预期契约 → 必须执行输出验证以符合 IO_CONTRACT
- **[QUAL-004]** 遇到空输入、极大值或异常场景 → 必须执行边界验证以处理极端情况
- **[QUAL-005]** 操作失败或出现错误 → 必须提供包含上下文和恢复建议的明确错误信息
- **[QUAL-006]** 参数类型、范围或格式校验 → 必须严格执行输入约束规则
- **[QUAL-007]** 返回值结构、编码或命名不一致 → 必须严格执行输出约束规则
- **[QUAL-008]** 涉及未验证代码或内部状态暴露 → 必须拒绝执行或隔离以遵守安全约束