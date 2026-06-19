---

name: creative
related_skills: ["academic-diagram", "architecture-diagram", "ascii-art", "ascii-video", "baoyu-comic", "baoyu-infographic", "claude-design", "comfyui", "excalidraw", "ffmpeg-video-audio-sync", "figure-generation", "humanizer", "manim-video", "p5js", "pixel-art", "popular-web-designs", "pretext", "sketch", "songwriting-and-ai-music", "touchdesigner-mcp"]
description: "创意工具 — 图表、视频、图像、代码生成"
author: Synthos
license: MIT
version: 2.0.0
license: MIT
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 创意工具 — 涵盖图表、视频音频、图像艺术、网页代码生成"

---


## IO_CONTRACT

- **input**: `creative_request: str, style: str, output_format: str` — 创意请求、风格偏好、输出格式
- **output**: `creative_output: dict` — 创意产物（图表/视频/图像/代码）

> 对应原则：P2（机械原子暴露输入输出规范）


# Creative Tools

> 父级技能目录，包含 4 个子类别共 23 个技能。

## 子类别

- `diagrams/` — 图表与可视化（学术图、架构图、信息图、Excalidraw）
- `video-audio/` — 视频与音乐（Manim动画、FFmpeg、AI音乐、ASCII视频）
- `image-art/` — 图像与艺术（素描、像素艺术、漫画、信息图、Claude设计）
- `web-code/` — 网页与代码（p5.js创意编程、网页设计、TouchDesigner、Pretext）
- `tools/` — 创意工具（ComfyUI图像生成、论文转PPT、创意发散）

## 使用方式

直接调用子技能名称即可：`academic-diagram`、`manim-video`、`comfyui`、`p5js` 等。
