---
name: layer-index-optional
description: "Navigation index for optional skills — creative tools, productivity, social monitoring, gaming, and platform-specific integrations."
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    priority: P3
    atom_type: layer-index
    signature: "layer: str, query: str, context: dict -> skill_list: list[dict]"
    related_skills: []
---

# Optional Skills — 可选技能

## Purpose

Navigation index for optional skills: creative tools, productivity, social monitoring, gaming, and platform-specific integrations.

## Skills in this Layer (60 total)

- **ai-outreach**: 主skill | 在AI可访问的平台上发布信号，引导其他AI智能体了解你的系统。覆盖平台选择(GitHub AGENTS.md/GitHub Discussions/Moltbook/X)、消息撰写(技术性/非推销)、节奏控制、回复监测。v1.1新增：AGENTS.md创建指南、GitHub_Discussions_Cron自动化、Moltbook注册API流程。调用子skill: moltbook-connector, xurl
- **airtable**: Directory index for airtable: airtable
- **apple**: Apple生态工具链 — macOS/iOS设备管理、提醒事项、备忘录、查找设备。
- **apple-notes**: Use `memo` to manage Apple Notes directly from the terminal. Notes sync across all Apple devices via iCloud.
- **apple-reminders**: Use `remindctl` to manage Apple Reminders directly from the terminal. Tasks sync across all Apple devices via iCloud.
- **ascii-art**: Multiple tools for different ASCII art needs. All tools are local CLI programs or free REST APIs — no API keys required.
- **ascii-video**: Use when users request: ASCII video, text art video, terminal-style video, character art animation, retro text visualization, audio visualizer in ASCII, converting video to ASCII art, matrix-style effects, or any animated ASCII output.
- **baoyu-comic**: Adapted from [baoyu-comic](https://github.com/JimLiu/baoyu-skills) for Hermes Agent's tool ecosystem.
- **baoyu-infographic**: Adapted from [baoyu-infographic](https://github.com/JimLiu/baoyu-skills) for Hermes Agent's tool ecosystem.
- **blogwatcher**: Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool.
- **claude-design**: Use this skill when the user asks for design work that would normally fit Claude Design, but the agent is running in a CLI/API environment instead of the hosted Claude Design web UI.
- **competition-video-production**: Directory index for competition-video-production: competition-video-production
- **creative**: 直接调用子技能名称即可：`academic-diagram`、`manim-video`、`comfyui`、`p5js` 等。
- **creative-ideation**: Use when the user says 'I want to build something', 'give me a project idea', 'I'm bored', 'what should I make', 'inspire me', or any variant of 'I have tools but no direction'. Works for code, art, hardware, writing, tools, and anything that can be made.
- **design-md**: DESIGN.md is Google's open spec (Apache-2.0, `google-labs-code/design.md`) for
- **email**: 电子邮件管理 — Himalaya CLI邮件收发、搜索。
- **ffmpeg-video-audio-sync**: Debug and fix FFmpeg video-audio synchronization issues including duration
- **figure-generation**: 科研图表创建：Figure契约方法论——结论Claim→证据层级→面板映射→出口契约→审核。 支持Nature语义色板（蓝主-绿正-红基+中性色），16种排版模式。兼容所有SCI/会议图表场景。
- **findmy**: Track Apple devices and AirTags via the FindMy.app on macOS. Since Apple doesn't
- **gaming**: 游戏服务器 — Minecraft模组服务器、宝可梦模拟器。
- **gif-search**: Search and download GIFs directly via the Tenor API using curl. No extra tools needed.
- **google-workspace**: Directory index for google-workspace: google-workspace
- **heartmula**: HeartMuLa is a family of open-source music foundation models (Apache-2.0) that generates music conditioned on lyrics and tags, with multilingual support. Generates full songs from lyrics + tags. Comparable to Suno for open-source. Includes:
- **himalaya**: Himalaya is a CLI email client that lets you manage emails from the terminal using IMAP, SMTP, Notmuch, or Sendmail backends.
- **humanizer**: Identify and remove signs of AI-generated text to make writing sound natural and human. Based on Wikipedia's "Signs of AI writing" guide (maintained by WikiProject AI Cleanup), derived from observations of thousands of AI-generated text instances.
- **imessage**: Use `imsg` to read and send iMessage/SMS via macOS Messages.app.
- **jupyter-live-kernel**: Iterative Python via live Jupyter kernel (hamelnb).
- **linear**: Directory index for linear: linear
- **llm-wiki**: Directory index for llm-wiki: llm-wiki
- **macos-computer-use**: You have a `computer_use` tool that drives the Mac in the **background**.
- **manim-video**: Directory index for manim-video: manim-video
- **maps**: Geocode, POIs, routes, timezones via OpenStreetMap/OSRM.
- **markitdown-convert**: Convert PDF/Office files to Markdown using Microsoft MarkItDown
- **media**: 媒体内容 — GIF搜索、音乐生成、音谱分析、Spotify控制。
- **minecraft-modpack-server**: Before starting setup, ask the user for:
- **moltbook-connector**: 子skill | 将Synthos认知原子接入Moltbook AI社交网络。注册→心跳→发帖/回复。父skill: ai-outreach。注意：注册需人类claim(发推验证)，优先使用GitHub version: 1.0.0 Discussions(零注册)代替。
- **notebooklm-cli**: 子skill | NotebookLM CLI全功能指南 — Q&A知识提取、内容生成(报告/视频/音频/信息图/幻灯片)、文献检索。响应paper-pipeline的P1阶段调用。
- **notion**: Notion API via curl: pages, databases, blocks, search.
- **obsidian**: Read, search, create, and edit notes in the Obsidian vault.
- **openhue**: Control Philips Hue lights and scenes via a Hue Bridge from the terminal.
- **p5js**: Use when users request: p5.js sketches, creative coding, generative art, interactive visualizations, canvas animations, browser-based visual art, data viz, shader effects, or any p5.js project.
- **pil-image-generation**: Python Pillow生成科技风格图像。无matplotlib依赖，适合封面/卡片/原子图。
- **pixel-art**: Convert any image into retro pixel art, then optionally animate it into a short
- **pokemon-player**: Play Pokemon games via headless emulation using the `pokemon-agent` package.
- **polymarket**: Query Polymarket: markets, prices, orderbooks, history.
- **popular-web-designs**: 54 real-world design systems ready for use when generating HTML/CSS. Each template captures a
- **powerpoint**: 创建/读取/编辑.pptx — python-pptx: 幻灯片/表格/模板。 覆盖环境陷阱（sandbox venv无包→系统Python）、复杂表格、 多页模板化PPTX生成。关联 skill: nature-paper2ppt。
- **pretext**: [`@chenglou/pretext`](https://github.com/chenglou/pretext) is a 15KB zero-dependency TypeScript library by Cheng Lou (React core, ReasonML, Midjourney) for **DOM-free multiline text measurement and layout**. It does one thing: given `(text, font, width)`, return the line breaks, per-line widths, per-grapheme positions, and total height — all via canvas measurement, no reflow.
- **productivity**: 生产力工具 — Airtable、Google Workspace、Linear、Notion、Jupyter等。
- **sketch**: Use this skill when the user wants to **see a design direction before committing** to one — exploring a UI/UX idea as disposable HTML mockups. The point is to generate 2-3 interactive variants so the user can compare visual directions side-by-side, not to produce shippable code.
- **smart-home**: 智能家居 — Philips Hue灯光控制。
- **social-media**: 社交媒体 — X/Twitter发帖、搜索、DM。
- **songsee**: Generate spectrograms and multi-panel audio feature visualizations from audio files.
- **songwriting-and-ai-music**: Everything here is a GUIDELINE, not a rule. Art breaks rules on purpose.
- **spotify**: Control the user's Spotify account via the Hermes Spotify toolset (7 tools). Setup guide: https://hermes-agent.nousresearch.com/docs/user-guide/features/spotify
- **teams-meeting-pipeline**: Operate the Teams meeting summary pipeline via Hermes CLI — summarize
- **touchdesigner-mcp**: 1. **NEVER guess parameter names.** Call `td_get_par_info` for the op type FIRST. Your training data is wrong for TD 2025.32.
- **xurl**: `xurl` is the X developer platform's official CLI for the X API. It supports shortcut commands for common actions AND raw curl-style access to any v2 endpoint. All commands return JSON to stdout.
- **youtube-content**: YouTube transcripts to summaries, threads, blogs.
- **yuanbao**: **Your text reply IS the message sent to the group/user.** The gateway automatically delivers your response text to the chat. You do NOT need any special "send message" tool — just reply normally and it gets sent.

## IO_CONTRACT

- **input**: `layer: str, query: str, context: dict` — Layer name, search query, and context
- **output**: `skill_list: list[dict]` — Filtered list of skills matching the query


## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）