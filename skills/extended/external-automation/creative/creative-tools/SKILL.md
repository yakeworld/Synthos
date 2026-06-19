---
name: creative-tools
description: "Creative tools suite: images, diagrams, comics, videos, music, designs, presentations."
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    atom_type: composite
    priority: P1
    signature: "task_desc: str, context: dict -> result: dict"
    related_skills: []

---

# creative-tools

## Purpose

Composite skill that merges 25 overlapping skills into a unified interface.

## Members (25)

- **ascii-art**: Multiple tools for different ASCII art needs. All tools are local CLI programs or free REST APIs — no API keys required.
- **ascii-video**: Use when users request: ASCII video, text art video, terminal-style video, character art animation, retro text visualization, audio visualizer in ASCII, converting video to ASCII art, matrix-style effects, or any animated ASCII output.
- **baoyu-comic**: Adapted from [baoyu-comic](https://github.com/JimLiu/baoyu-skills) for Hermes Agent's tool ecosystem.
- **baoyu-infographic**: Adapted from [baoyu-infographic](https://github.com/JimLiu/baoyu-skills) for Hermes Agent's tool ecosystem.
- **claude-design**: Use this skill when the user asks for design work that would normally fit Claude Design, but the agent is running in a CLI/API environment instead of the hosted Claude Design web UI.
- **competition-video-production**: Directory index for competition-video-production: competition-video-production
- **creative**: 直接调用子技能名称即可：`academic-diagram`、`manim-video`、`comfyui`、`p5js` 等。
- **creative-ideation**: Use when the user says 'I want to build something', 'give me a project idea', 'I'm bored', 'what should I make', 'inspire me', or any variant of 'I have tools but no direction'. Works for code, art, hardware, writing, tools, and anything that can be made.
- **design-md**: DESIGN.md is Google's open spec (Apache-2.0, `google-labs-code/design.md`) for
- **ffmpeg-video-audio-sync**: Debug and fix FFmpeg video-audio synchronization issues including duration
- **figure-generation**: 科研图表创建：Figure契约方法论——结论Claim→证据层级→面板映射→出口契约→审核。 支持Nature语义色板（蓝主-绿正-红基+中性色），16种排版模式。兼容所有SCI/会议图表场景。
- **heartmula**: HeartMuLa is a family of open-source music foundation models (Apache-2.0) that generates music conditioned on lyrics and tags, with multilingual support. Generates full songs from lyrics + tags. Comparable to Suno for open-source. Includes:
- **humanizer**: Identify and remove signs of AI-generated text to make writing sound natural and human. Based on Wikipedia's "Signs of AI writing" guide (maintained by WikiProject AI Cleanup), derived from observations of thousands of AI-generated text instances.
- **manim-video**: Directory index for manim-video: manim-video
- **p5js**: Use when users request: p5.js sketches, creative coding, generative art, interactive visualizations, canvas animations, browser-based visual art, data viz, shader effects, or any p5.js project.
- **pil-image-generation**: Python Pillow生成科技风格图像。无matplotlib依赖，适合封面/卡片/原子图。
- **pixel-art**: Convert any image into retro pixel art, then optionally animate it into a short
- **popular-web-designs**: 54 real-world design systems ready for use when generating HTML/CSS. Each template captures a
- **powerpoint**: 创建/读取/编辑.pptx — python-pptx: 幻灯片/表格/模板。 覆盖环境陷阱（sandbox venv无包→系统Python）、复杂表格、 多页模板化PPTX生成。关联 skill: nature-paper2ppt。
- **pretext**: [`@chenglou/pretext`](https://github.com/chenglou/pretext) is a 15KB zero-dependency TypeScript library by Cheng Lou (React core, ReasonML, Midjourney) for **DOM-free multiline text measurement and layout**. It does one thing: given `(text, font, width)`, return the line breaks, per-line widths, per-grapheme positions, and total height — all via canvas measurement, no reflow.
- **sketch**: Use this skill when the user wants to **see a design direction before committing** to one — exploring a UI/UX idea as disposable HTML mockups. The point is to generate 2-3 interactive variants so the user can compare visual directions side-by-side, not to produce shippable code.
- **smart-home**: 智能家居 — Philips Hue灯光控制。
- **songsee**: Generate spectrograms and multi-panel audio feature visualizations from audio files.
- **songwriting-and-ai-music**: Everything here is a GUIDELINE, not a rule. Art breaks rules on purpose.
- **touchdesigner-mcp**: 1. **NEVER guess parameter names.** Call `td_get_par_info` for the op type FIRST. Your training data is wrong for TD 2025.32.

## IO_CONTRACT

- **input**: `task_desc: str, context: dict` — Task description and context
- **output**: `result: dict` — Merged results from all member skills

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）