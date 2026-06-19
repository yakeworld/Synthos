---


name: metacognition
description: 元认知 — 自主执行阈值、记忆增强、记忆优化系统。
author: Synthos
license: MIT
version: 1.0.0
license: MIT
triggers:
  - 需要执行metacognition下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 元认知 — 自主执行阈值、记忆增强、记忆优化系统。"
    signature: 'metacognition -> sub-skills: [autonomous-execution-threshold, memory-enhancement, memory-optimization-system]'
    related_skills: ["autonomous-execution-threshold", "memory-enhancement", "memory-optimization-system"]


---


## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# metacognition

> 父级技能目录，包含 3 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `autonomous-execution-threshold`
- `memory-enhancement`
- `memory-optimization-system`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='autonomous-execution-threshold')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
