---

name: red-teaming
description: 红队测试 — LLM越狱攻击（Parseltongue、GODMODE、ULTRAPLINIAN）。
triggers:
  - 需要执行red-teaming下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 红队测试 — LLM越狱攻击（Parseltongue、GODMODE、ULTRAPLINIAN）。"
    signature: 'red-teaming -> sub-skills: [godmode]'
    related_skills: ["godmode"]
---

# red-teaming

> 父级技能目录，包含 1 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `godmode`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='godmode')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
