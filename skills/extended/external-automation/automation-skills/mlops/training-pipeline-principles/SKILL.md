---



name: training-pipeline-principles
description: "Skill: training-pipeline-principles"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "pipeline_type: str, domain: str -> pipeline_spec: dict (stages, optimizers, monitoring, checkpoints)"
    atom_type: skill
    priority: P1
    related_skills: []
---




## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# Training Pipeline Principles

多阶段训练管线抽象原则 — teacher→distillation→student→hybrid→fine-tune。
