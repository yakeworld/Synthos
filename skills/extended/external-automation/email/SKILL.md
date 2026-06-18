---

name: email
description: 电子邮件管理 — Himalaya CLI邮件收发、搜索。
version: 1.0.0
triggers:
  - 需要执行email下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 电子邮件管理 — Himalaya CLI邮件收发、搜索。"
    signature: 'email -> sub-skills: [himalaya]'
    related_skills: ["himalaya"]

---

## IO_CONTRACT

- **input**: `email_action: str, email_account: str` — 用户请求描述、上下文信息
- **output**: `result: dict — 邮件操作结果`

> 对应原则：P2（机械原子暴露输入输出规范）



# email

> 父级技能目录，包含 1 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `himalaya`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='himalaya')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
