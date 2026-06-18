---

name: hermes
description: Hermes Agent管理 — Cron生命周期、配置、工具管理。
version: 1.0.0
triggers:
  - 需要执行hermes下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — Hermes Agent管理 — Cron生命周期、配置、工具管理。"
    signature: 'hermes -> sub-skills: [hermes-scheduler]'
    related_skills: ["hermes-scheduler"]

---


# hermes

> 父级技能目录，包含 1 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `hermes-scheduler`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='hermes-scheduler')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
