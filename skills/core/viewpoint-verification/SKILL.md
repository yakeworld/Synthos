---


name: viewpoint-verification
description: "Directory index for viewpoint-verification: viewpoint-verification"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "hypothesis: str, context: dict -> verification_report: dict (score, evidence, counter_evidence, confidence)"
    atom_type: skill
    priority: P1
    related_skills: []
---





# Viewpoint Verification

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考
## IO_CONTRACT

- **input**: `hypothesis: str, context: dict` — 任务描述、参数配置
- **output**: `verification_report: dict (score, evidence, counter_evidence, confidence)` — 执行结果

> 对应原则：P2（机械原子暴露输入输出规范）
