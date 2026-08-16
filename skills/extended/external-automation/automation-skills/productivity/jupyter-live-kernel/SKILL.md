---
name: jupyter-live-kernel
description: jupyter-live-kernel
version: 1.0.0
category: productivity
signature: 'jupyter-live-kernel -> productivity: Iterative Python via live Jupyter
  kernel (hamelnb).'
allowed-tools:
- terminal
- read_file
- write_file
- search_files
license: MIT
author: Synthos
platforms:
- linux
- macos
- windows
metadata:
  hermes:
    tags:
    - jupyter
    - notebook
    - repl
    - data-science
    - exploration
    - iterative
    category: data-science
  synthos:
    author: Hermes Agent
    signature: 'task: str -> notebook_output: dict'
    related_skills:
    - airtable
    - chinese-form-automation
    - google-workspace
    - linear
    - maps
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

# Jupyter Live Kernel (hamelnb)

Gives you a **stateful Python REPL** via a live Jupyter kernel. Variables persist
across executions. Use this instead of `execute_code` when you need to build up
state incrementally, explore APIs, inspect DataFrames, or iterate on complex code.

## When to Use This vs Other Tools

| Tool | Use When |
|