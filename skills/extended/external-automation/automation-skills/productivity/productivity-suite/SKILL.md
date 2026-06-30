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


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

> 对应原则：P3（人机分层 — 路由器负责路由，原子负责执行）


# Productivity Suite

