---

name: autonomous-ai-agents
description: 自主AI智能体编排 — 多Agent协作、委托任务、跨Agent通信。
version: 1.0.0
triggers:
  - 需要执行autonomous-ai-agents下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — 自主AI智能体编排 — 多Agent协作、委托任务、跨Agent通信。"
    signature: 'autonomous-ai-agents -> sub-skills: [ai-outreach, claude-code, codex]'
    related_skills: ["ai-outreach", "claude-code", "codex", "hermes-agent", "moltbook-connector"]

---


# autonomous-ai-agents

> 父级技能目录，包含 6 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `ai-outreach`
- `claude-code`
- `codex`
- `hermes-agent`
- `moltbook-connector`
- `opencode`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='ai-outreach')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
