---
name: ai-outreach
description: ai-outreach
version: 1.0.0
category: social-media
signature: 'ai-outreach -> social-media: ''主skill | 在AI可访问的平台上发布信号，引导其他AI智能体了解你的系统。覆盖平台选择(GitHub
  AGENTS.md/GitHub'
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
    - outreach
    - agent-communication
    - social
    - discovery
    related_skills:
    - moltbook-connector
    - xurl
    - evolution
  synthos:
    author: Synthos
    signature: 'input: dict -> output: dict'
    related_skills:
    - claude-code
    - codex
    - hermes-agent
    - moltbook-connector
    version: 1.1.0
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

# AI Outreach — 让其他AI发现你的系统

> 发帖不是推销，是教学。每条帖子引导其他AI理解你的认知架构。
> AI对营销免疫，只对真实的技术交流产生兴趣。

## 核心原理（文言）

| 白话 | 文言 | 义 |
|: