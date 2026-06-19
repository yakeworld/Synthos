---
name: python-docx
description: "创建/读取/编辑.docx — python-docx: 表格/字体/页面设置。"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

---






## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）


# Python Docx

创建/读取/编辑.docx — python-docx: 表格/字体/页面设置。

## 新增参考
- `references/bci-proposal-generation-patterns.md` — BCI平台建设方案生成规范：术语修正（已完稿技术成果/硕士生导师/删除无差异项）、设备表格三列无空列、刷新率≥90Hz、预算表5列结构。适用于政策对接类docx生成。
