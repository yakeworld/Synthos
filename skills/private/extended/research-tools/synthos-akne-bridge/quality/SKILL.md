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
category: research-tools
author: Synthos
triggers:
- 需要执行quality下的子技能
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

- [ ] 输入参数 `skill_path` 完整且指向有效路径，空或无效输入已按 QUAL-001 拒绝执行
- [ ] 中间步骤/转换/计算已验证正确性（QUAL-002），过程合规可追溯
- [ ] 输出 `quality_report: dict` 结构与内容符合 IO_CONTRACT 预期（QUAL-003）
- [ ] 边界场景（空输入、极大值、异常输入）已覆盖并处理（QUAL-004）
- [ ] 失败或错误时输出包含上下文与恢复建议的明确错误信息（QUAL-005）
- [ ] 参数类型、范围、格式已校验（QUAL-006），未通过校验即拒绝
- [ ] 返回值结构、编码、命名一致（QUAL-007），未暴露内部状态或执行未验证代码（QUAL-008）
- [ ] 实际执行已路由到子技能（`falsification-validation` / `golden-test-methodology`），父级仅作目录索引

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

# Quality