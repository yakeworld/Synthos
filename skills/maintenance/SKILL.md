---

name: maintenance
description: Synthos维护 — 认知原子结构完整性验证。
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
