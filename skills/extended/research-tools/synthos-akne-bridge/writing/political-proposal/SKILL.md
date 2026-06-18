---
name: political-proposal
description: >-
  参政议政提案全流程(民进/政协/人大) — 三段式: 基本情况→问题→对策。
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
---

## IO_CONTRACT

- **input**: `topic: str, scope: str` — 用户请求描述、上下文信息
- **output**: `proposal: dict — 政治提案`

> 对应原则：P2（机械原子暴露输入输出规范）


# Political Proposal

参政议政提案全流程(民进/政协/人大) — 三段式: 基本情况→问题→对策。

## 触发条件

加载此技能当用户需要撰写/修改/审核提案（民进/政协/人大等参政议政渠道）。

**前置扫描**：如果提案涉及新兴技术/产业方向（如脑机接口、人工智能、生物医药等），应先加载 `emerging-field-landscape-scan` 完成政策背景扫描，再进入提案写作流程。

详细内容请加载对应 references/ 目录下的参考文件。
