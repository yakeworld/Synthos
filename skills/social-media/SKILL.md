---

name: social-media
description: 社交媒体 — X/Twitter发帖、搜索、DM。
triggers:
  - 需要执行social-media下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 社交媒体 — X/Twitter发帖、搜索、DM。"
    signature: 'social-media -> sub-skills: [xurl]'
    related_skills: ["xurl"]
---

# social-media

> 父级技能目录，包含 1 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `xurl`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='xurl')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
