---
name: productivity-suite
description: "Productivity suite: email, notes, tasks, spreadsheets, docs, calendars, meetings."
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

# productivity-suite

## Purpose

Composite skill that merges 14 overlapping skills into a unified interface.

## Members (14)

- **airtable**: Directory index for airtable: airtable
- **apple-notes**: Use `memo` to manage Apple Notes directly from the terminal. Notes sync across all Apple devices via iCloud.
- **apple-reminders**: Use `remindctl` to manage Apple Reminders directly from the terminal. Tasks sync across all Apple devices via iCloud.
- **email**: 电子邮件管理 — Himalaya CLI邮件收发、搜索。
- **google-workspace**: Directory index for google-workspace: google-workspace
- **himalaya**: Himalaya is a CLI email client that lets you manage emails from the terminal using IMAP, SMTP, Notmuch, or Sendmail backends.
- **imessage**: Use `imsg` to read and send iMessage/SMS via macOS Messages.app.
- **jupyter-live-kernel**: Iterative Python via live Jupyter kernel (hamelnb).
- **linear**: Directory index for linear: linear
- **macos-computer-use**: You have a `computer_use` tool that drives the Mac in the **background**.
- **notebooklm-cli**: 子skill | NotebookLM CLI全功能指南 — Q&A知识提取、内容生成(报告/视频/音频/信息图/幻灯片)、文献检索。响应paper-pipeline的P1阶段调用。
- **notion**: Notion API via curl: pages, databases, blocks, search.
- **obsidian**: Read, search, create, and edit notes in the Obsidian vault.
- **teams-meeting-pipeline**: Operate the Teams meeting summary pipeline via Hermes CLI — summarize

## IO_CONTRACT

- **input**: `task_desc: str, context: dict` — Task description and context
- **output**: `result: dict` — Merged results from all member skills

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）