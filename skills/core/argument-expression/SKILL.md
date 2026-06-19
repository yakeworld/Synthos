---


name: argument-expression
description: "Directory index for argument-expression: argument-expression"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "claims: list[Claim], evidence: list[Evidence] -> argument_chain: ArgumentChain (structure, strengths, gaps, counterarguments)"
    atom_type: skill
    priority: P1
    related_skills: []
---




# Argument Expression

## IO_CONTRACT

- **input**: `hypothesis: str, evidence: list[Evidence]` — 待论证的假设及支持证据
- **output**: `argument: str` — 结构化论证（thesis, claims, evidence_chains, literature_support, counterarguments）

> 对应原则：P2（机械原子暴露输入输出规范）

> 对应原则：P2 机械原子暴露输入输出规范

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。
This skill has been compressed. Full content is available in references/.
