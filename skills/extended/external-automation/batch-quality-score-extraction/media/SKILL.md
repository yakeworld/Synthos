---

name: media
description: 媒体内容 — GIF搜索、音乐生成、音谱分析、Spotify控制。
version: 1.0.0
triggers:
  - 需要执行media下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 媒体内容 — GIF搜索、音乐生成、音谱分析、Spotify控制。"
    signature: 'media -> sub-skills: [gif-search, heartmula, songsee]'
    related_skills: ["gif-search", "heartmula", "songsee", "spotify"]

---


# media

> 父级技能目录，包含 4 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `gif-search`
- `heartmula`
- `songsee`
- `spotify`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='gif-search')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
