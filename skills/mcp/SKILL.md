---

name: mcp
description: MCP集成 — 模型上下文协议服务器配置与工具注册。
triggers:
  - 需要执行mcp下的子技能
metadata:
  synthos:
    priority: P2
    atom_type: parent-skill
    description: "父级技能 — MCP集成 — 模型上下文协议服务器配置与工具注册。"
    signature: 'mcp -> sub-skills: [mcp-ecosystem-guide, native-mcp]'
    related_skills: ["mcp-ecosystem-guide", "native-mcp"]
---

# mcp

> 父级技能目录，包含 2 个子技能。
> 子技能通过Hermes技能加载机制自动发现，无需显式调用。

## 子技能

- `mcp-ecosystem-guide`
- `native-mcp`

## 使用方式

直接调用子技能名称即可：

```
skill_view(name='mcp-ecosystem-guide')  # 加载第一个子技能
```

父级SKILL.md仅作为目录索引，实际执行由子技能完成。
