---


name: maintenance
description: Synthos维护 — 认知原子结构完整性验证。
author: Synthos
license: MIT
version: 1.0.0
license: MIT
triggers:
  - 需要执行maintenance下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — Synthos维护 — 认知原子结构完整性验证。"
    signature: 'maintenance -> sub-skills: [synthos-probe]'
    related_skills: ["synthos-probe"]


---


## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# maintenance

> 父级技能目录，包含 1 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `synthos-probe`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='synthos-probe')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
