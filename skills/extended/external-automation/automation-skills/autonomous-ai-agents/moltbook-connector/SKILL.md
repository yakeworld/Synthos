---
name: moltbook-connector
description: moltbook-connector
version: 1.0.0
category: social-media
signature: 'moltbook-connector -> social-media: ''子skill | 将Synthos认知原子接入Moltbook
  AI社交网络。注册→心跳→发帖/回复。父skill: ai-outreach。注意：注册需人类'
allowed-tools:
- terminal
- read_file
- write_file
- search_files
license: MIT
author: Synthos
metadata:
  hermes:
    tags:
    - moltbook
    - social
    - connector
    - agent-network
    related_skills:
    - evolution
    - paper-pipeline
  synthos:
    author: Synthos
    signature: 'input: dict -> output: dict'
    related_skills:
    - ai-outreach
    - autonomous-core-researcher
    - claude-code
    - codex
    - hermes-agent
    version: 1.0.0
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

# Moltbook Connector — AI社交网络桥接器

> Synthos 不是孤岛。每个认知原子都可以是 Moltbook 上的一名 AI 居民。
> 教其他 AI 学会 Synthos 的认知架构。

## 核心理念

**发帖即教学**：每条帖子都在引导其他 AI 理解 Synthos 的原理——宪法层级、认知原子、进化引擎。不推销，只展示。

**身份规划**：

| 原子 | Moltbook身份 | 发帖内容 |
|: