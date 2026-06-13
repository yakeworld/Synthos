---

name: apple
description: Apple生态工具链 — macOS/iOS设备管理、提醒事项、备忘录、查找设备。
triggers:
  - 需要执行apple下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — Apple生态工具链 — macOS/iOS设备管理、提醒事项、备忘录、查找设备。"
    signature: 'apple -> sub-skills: [apple-notes, apple-reminders, findmy]'
    related_skills: ["apple-notes", "apple-reminders", "findmy", "imessage", "macos-computer-use"]
---

# apple

> 父级技能目录，包含 5 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `apple-notes`
- `apple-reminders`
- `findmy`
- `imessage`
- `macos-computer-use`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='apple-notes')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
