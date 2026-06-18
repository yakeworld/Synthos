---
name: opencode
related_skills: []
description: >-
version: 1.0.0
  委托OpenCode CLI编码 — 功能开发/PR审查。
metadata:
  synthos:
    version: 1.0.0
    author: Synthos

---

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）

> 对应原则：P2（机械原子暴露输入输出规范）



# Opencode

> ⚠️ **已降级为轻量替代。** Codex CLI 是主力编码代理。OpenCode 仅用于极轻量的临时脚本任务，复杂编码一律走 Codex。

委托OpenCode CLI编码 — 仅限一次性简单脚本。
