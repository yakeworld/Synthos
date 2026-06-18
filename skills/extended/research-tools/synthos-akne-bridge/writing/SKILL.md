---

name: writing
description: 写作辅助 — 引用完整性修复、LaTeX输出、政治提案、标准论文结构。
version: 1.0.0
triggers:
  - 需要执行writing下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 写作辅助 — 引用完整性修复、LaTeX输出、政治提案、标准论文结构。"
    signature: 'writing -> sub-skills: [citation-integrity-fix, latex-output, political-proposal]'
    related_skills: ["citation-integrity-fix", "latex-output", "political-proposal", "sci-paper-standard-structure"]

---

## IO_CONTRACT

- **input**: `request: str, context: dict` — 用户请求描述、上下文信息
- **output**: `result: dict — 技能执行结果（结构因技能而异）`

> 对应原则：P2（机械原子暴露输入输出规范）



# writing

> 父级技能目录，包含 4 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `citation-integrity-fix`
- `latex-output`
- `political-proposal`
- `sci-paper-standard-structure`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='citation-integrity-fix')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
