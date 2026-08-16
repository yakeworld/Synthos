---
name: notebooklm-cli
description: notebooklm-cli
version: 1.0.0
category: productivity
signature: 'notebooklm-cli -> productivity: 子skill | NotebookLM CLI全功能指南 — Q&A知识提取、内容生成(报告/视频/音频/信息图/幻灯片)、文献检索。响应paper-pipel'
related_skills:
- knowledge-extraction
allowed-tools:
- terminal
- file
- web
license: MIT
author: Synthos
metadata:
  synthos:
    version: 3.5.0
    author: Synthos
    signature: 'action: str, params: dict -> result: dict'
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

# NotebookLM CLI — 知识大脑

> **架构定位**: NotebookLM = Synthos 的廉价知识大脑 (Tier 1)。详见 `references/knowledge-brain-architecture.md`。

## 核心原理（文言）

**一问一收，不并投** — 每轮只问一个问题，用答案决定下一个。不一次全抛。

**言不必行** — Q&A输出≠源代码执行结果。

**节点有闸** — Gap门/假设门/方法门/实验门，每节点过闸才前进。

## 快速参考

| 功能 | 命令 | 参考 |
|: