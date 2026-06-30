---


name: quality
description: 质量保障 — 伪证验证、黄金测试、SCI论文质量评审。
author: Synthos
license: MIT
version: 1.0.0
license: MIT
triggers:
  - 需要执行quality下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 质量保障 — 伪证验证、黄金测试、SCI论文质量评审。"
    signature: 'quality -> sub-skills: [falsification-validation, golden-test-methodology, sci-paper-quality-review]'
    related_skills: ["falsification-validation", "golden-test-methodology", "sci-paper-quality-review"]


---


## IO_CONTRACT

- **input**: `skill_path: str` — 用户请求描述、上下文信息
- **output**: `quality_report: dict — 质量报告`

> 对应原则：P2（机械原子暴露输入输出规范）



# quality

> 父级技能目录，包含 3 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `falsification-validation`
- `golden-test-methodology`
- `sci-paper-quality-review`

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



# Quality

