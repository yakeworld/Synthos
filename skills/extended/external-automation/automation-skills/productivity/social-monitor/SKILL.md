---
name: social-monitor
description: "Social and monitoring tools: blog watching, LLM wiki, social media, market monitoring."
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

# social-monitor

## Purpose

Composite skill that merges 11 overlapping skills into a unified interface.

## Members (11)

- **ai-outreach**: 主skill | 在AI可访问的平台上发布信号，引导其他AI智能体了解你的系统。覆盖平台选择(GitHub AGENTS.md/GitHub Discussions/Moltbook/X)、消息撰写(技术性/非推销)、节奏控制、回复监测。v1.1新增：AGENTS.md创建指南、GitHub_Discussions_Cron自动化、Moltbook注册API流程。调用子skill: moltbook-connector, xurl
- **blogwatcher**: Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool.
- **llm-wiki**: Directory index for llm-wiki: llm-wiki
- **minecraft-modpack-server**: Before starting setup, ask the user for:
- **moltbook-connector**: 子skill | 将Synthos认知原子接入Moltbook AI社交网络。注册→心跳→发帖/回复。父skill: ai-outreach。注意：注册需人类claim(发推验证)，优先使用GitHub version: 1.0.0 Discussions(零注册)代替。
- **pokemon-player**: Play Pokemon games via headless emulation using the `pokemon-agent` package.
- **polymarket**: Query Polymarket: markets, prices, orderbooks, history.
- **social-media**: 社交媒体 — X/Twitter发帖、搜索、DM。
- **spotify**: Control the user's Spotify account via the Hermes Spotify toolset (7 tools). Setup guide: https://hermes-agent.nousresearch.com/docs/user-guide/features/spotify
- **xurl**: `xurl` is the X developer platform's official CLI for the X API. It supports shortcut commands for common actions AND raw curl-style access to any v2 endpoint. All commands return JSON to stdout.
- **youtube-content**: YouTube transcripts to summaries, threads, blogs.

## IO_CONTRACT

- **input**: `task_desc: str, context: dict` — Task description and context
- **output**: `result: dict` — Merged results from all member skills

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）