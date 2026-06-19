---


name: social-media
description: 社交媒体 — X/Twitter发帖、搜索、DM。
author: Synthos
license: MIT
version: 1.0.0
license: MIT
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


## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



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
