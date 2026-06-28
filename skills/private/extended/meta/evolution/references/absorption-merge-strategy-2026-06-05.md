# Absorption Merge Strategy

> 吸收日期: 2026-06-05
> 来源: OpenClaw (376,897⭐, MIT) + Claude Code (130,221⭐, 专有) + autocontext (MIT) + PaperDebugger (AGPL-3.0) + 724-office (MIT)
> 目标: 57个技能整合 + 5个方法论吸收

## 三规则

1. **更完整的保留** — 两个版本对比，内容更多/更详细的那个保留。Synthos的 `blogwatcher` (5391 bytes) vs OpenClaw (1414 bytes) → 保留 Synthos。
2. **更大的合并** — 当一方远大于另一方（>5x差异），将大版本合并到小版本。`node-inspect-debugger`: Synthos 246 bytes → 合并 OpenClaw 3573 bytes → 最终 3781 bytes。
3. **格式归一化** — 所有 SKILL.md 统一为 Synthos 规范：YAML frontmatter → 原理层·文言 → 方法层·白话 → 触发条件 → 验证清单。

## 合并决策表

| 技能 | Synthos 原始大小 | 外部大小 | 决策 | 最终大小 |
|:-----|:----------------:|:-------:|:-----|:--------:|
| blogwatcher | 5391 B | 1414 B | KEEP Synthos | 5391 B |
| notion | 5536 B | 3864 B | KEEP Synthos | 5536 B |
| obsidian | 6081 B | 2939 B | KEEP Synthos | 6081 B |
| node-inspect-debugger | 246 B | 3573 B | MERGE OC→Synthos | 3781 B |
| python-debugpy | 295 B | 2552 B | MERGE OC→Synthos | 2727 B |
| spike | 210 B | 1888 B | MERGE OC→Synthos | 2028 B |

## 归一化模板

```yaml
---
name: <技能名>
description: <一句话描述>
license: MIT
metadata:
  synthos:
    version: 1.1.0
    author: Synthos
    related_skills:
    - <相关技能>
allowed-tools:
- terminal
- read_file
- write_file
- search_files
- task_delegation
---

# <技能名>

> 使用 <技能名> 工具。

## 触发条件

- 需要 <描述> 时

## 方法

[外部内容，保留核心方法论，删除框架特定的代码和工具引用]

## 验证清单

- [ ] 执行前检查
- [ ] 执行后验证
```

## 吸收结果

- Synthos 技能树: 111 → 168 技能
- 保留: 3 (blogwatcher, notion, obsidian)
- 合并: 3 (node-inspect-debugger, python-debugpy, spike)
- 新导入: 51
