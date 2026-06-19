---

name: quality
description: 质量保障 — 伪证验证、黄金测试、SCI论文质量评审。
version: 1.0.0
triggers:
  - 需要执行quality下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 质量保障 — 伪证验证、黄金测试、SCI论文质量评审。"
    signature: 'quality -> sub-skills: [falsification-validation, golden-test-methodology, sci-paper-quality-review]'
    related_skills: ["falsification-validation", "golden-test-methodology", "sci-paper-quality-review"]

---

## IO_CONTRACT

- **input**: `skill_path: str` — 用户请求描述、上下文信息
- **output**: `quality_report: dict — 质量报告`

> 对应原则：P2（机械原子暴露输入输出规范）



# quality

> 父级技能目录，包含 3 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `falsification-validation`
- `golden-test-methodology`
- `sci-paper-quality-review`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='falsification-validation')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
