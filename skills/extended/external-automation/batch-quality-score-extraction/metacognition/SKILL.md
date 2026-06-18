---

name: metacognition
description: 元认知 — 自主执行阈值、记忆增强、记忆优化系统。
version: 1.0.0
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
