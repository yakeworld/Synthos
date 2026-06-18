---

name: gaming
description: 游戏服务器 — Minecraft模组服务器、宝可梦模拟器。
version: 1.0.0
triggers:
  - 需要执行gaming下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 游戏服务器 — Minecraft模组服务器、宝可梦模拟器。"
    signature: 'gaming -> sub-skills: [minecraft-modpack-server, pokemon-player]'
    related_skills: ["minecraft-modpack-server", "pokemon-player"]

---

## IO_CONTRACT

- **input**: `game_type: str, mode: str` — 用户请求描述、上下文信息
- **output**: `game_state: dict — 游戏状态`

> 对应原则：P2（机械原子暴露输入输出规范）

> 对应原则：P2（机械原子暴露输入输出规范）



# gaming

> 父级技能目录，包含 2 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `minecraft-modpack-server`
- `pokemon-player`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='minecraft-modpack-server')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
