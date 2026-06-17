---

name: creative
description: 创意内容生成 — ASCII艺术、信息图、漫画、动画、PPT、设计原型。
version: 1.0.0
triggers:
  - 需要执行creative下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 创意内容生成 — ASCII艺术、信息图、漫画、动画、PPT、设计原型。"
    signature: 'creative -> sub-skills: [academic-diagram, architecture-diagram, ascii-art]'
    related_skills: ["academic-diagram", "architecture-diagram", "ascii-art", "ascii-video", "baoyu-comic"]

---


# creative

> 父级技能目录，包含 23 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `academic-diagram`
- `architecture-diagram`
- `ascii-art`
- `ascii-video`
- `baoyu-comic`
- `baoyu-infographic`
- `claude-design`
- `comfyui`
- `creative-ideation`
- `design-md`
- `excalidraw`
- `ffmpeg-video-audio-sync`
- `figure-generation`
- `humanizer`
- `manim-video`
- `nature-paper2ppt`
- `p5js`
- `pixel-art`
- `popular-web-designs`
- `pretext`
- `sketch`
- `songwriting-and-ai-music`
- `touchdesigner-mcp`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='academic-diagram')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
