---
name: training-pipeline-principles
related_skills: []
description: >-
version: 1.0.0
  多阶段训练管线抽象原则 — teacher→distillation→student→hybrid→fine-tune。
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



# Training Pipeline Principles

多阶段训练管线抽象原则 — teacher→distillation→student→hybrid→fine-tune。
