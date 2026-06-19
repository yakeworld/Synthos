---
name: patent-disclosure
description: "该技能以Synthos仓库为主版本。Hermes镜像为查找索引，执行时请加载Synthos路径版本。"
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

- **input**: `invention_desc: str, domain: str` — 用户请求描述、上下文信息
- **output**: `disclosure_doc: dict — 专利披露`


> 对应原则：P2（机械原子暴露输入输出规范）
# 专利挖掘与交底书生成

> Synthos原始路径: `/media/yakeworld/sda2/Synthos/skills/patent-disclosure/SKILL.md`
> Hermes镜像路径: `~/.hermes/skills/research/patent-disclosure/SKILL.md`

该技能以Synthos仓库为主版本。Hermes镜像为查找索引，执行时请加载Synthos路径版本。

## 快速入口
```
skill_view(name='patent-disclosure') ——加载Synthos版本
```

## 结构
| Path | Description |
|------|-------------|
| `SKILL.md` | 原理层（文言）+ 方法层（白话）+ 命令层（英文） |
| `prompts/` | 11个分步指令模板 |
| `tools/` | 8个Python扩展脚本（CNIPA查新、Mermaid渲染、文档转换等） |

## 吸收记录
- `references/vor-kappa-patent-background.md` — VOR-Kappa角专利的技术背景与开发陷阱（2026-05-21 完成）