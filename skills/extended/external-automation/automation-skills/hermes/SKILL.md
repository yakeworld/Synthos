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

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



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
