---

name: github
description: GitHub工作流 — PR审查、Issue管理、仓库管理、CI/CD。
triggers:
  - 需要执行github下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — GitHub工作流 — PR审查、Issue管理、仓库管理、CI/CD。"
    signature: 'github -> sub-skills: [codebase-inspection, github-auth, github-code-review]'
    related_skills: ["codebase-inspection", "github-auth", "github-code-review", "github-discussions", "github-issues"]
---

# github

> 父级技能目录，包含 7 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `codebase-inspection`
- `github-auth`
- `github-code-review`
- `github-discussions`
- `github-issues`
- `github-pr-workflow`
- `github-repo-management`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='codebase-inspection')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
