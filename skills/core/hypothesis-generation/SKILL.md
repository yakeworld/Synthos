---


name: hypothesis-generation
description: "Directory index for hypothesis-generation: hypothesis-generation"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "knowledge_base: dict, gap_analysis: dict -> hypotheses: list[Hypothesis] (statement, rationale, testability, priority)"
    atom_type: skill
    priority: P1
    related_skills: []
---




# Hypothesis Generation

## IO_CONTRACT

- **input**: `research_gap: str, domain_knowledge: str, constraints: dict` — 研究空白、领域知识、约束条件
- **output**: `hypotheses: list[Hypothesis]` — 可检验假设列表（statement, falsifiability_test, supporting_evidence, counter_evidence）

> 对应原则：P2（机械原子暴露输入输出规范）

> 对应原则：P2 机械原子暴露输入输出规范

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。
This skill has been compressed. Full content is available in references/.
