---
name: skill-authoring
description: Synthos技能格式规范与编写标准。兼容Agent Skills(agentskills.io)标准。定义主/子skill层级分离、三语策略(文言+白话+英文)、长度规范、frontmatter schema。加载此skill作为所有SKILL.md创建/维护的唯一规范参考。
license: MIT
compatibility: Requires file system access to Synthos skills directory
metadata:
  synthos:
    version: 2.6.0
    author: Synthos
    priority: P0
    atom_type: meta
    related_skills: [quality-gate, project-experience-distillation]
    signature: "query: str -> skill_spec: dict"
---

# Synthos Skill Authoring Standard

## 核心原则（文言）

| 白话 | 文言 | 义 |
|:-----|:-----|:----|
| 层级分离 | **层分则明** | 技能平铺→AI无法精确选技能 |
| 单源——每段知识只存在一处 | **源一不二** | 同一段命令不写三次 |
| 主skill=地图，不做事 | **主为图，不为事** | 只告诉AI为什么做+先做什么+什么情况加载哪个子skill |
| 原理文言+方法白话+命令英文 | **三层三语** | 原理层用文言(四字格言), 方法层白话, 命令层英文 |
| 压缩原则 | **存精去冗** | SKILL.md保持<8K, 详细内容移references/ |

## 兼容 Agent Skills 标准

完全兼容 https://agentskills.io 标准。Synthos 特有字段放在 `metadata.synthos`。

### 目录结构

```
skill-name/
├── SKILL.md          # 必需
├── scripts/          # 可执行脚本
├── references/       # 参考文档/案例
├── assets/           # 模板/资源
└── templates/        # 启动模板
```

### Frontmatter Schema

```yaml
# Agent Skills 标准字段（顶层）
name: my-skill              # 必需. 小写+连字符, 1-64字符
description: "..."          # 必需. 1-1024字符
license: MIT                # 推荐
compatibility: "..."        # 可选
metadata:                   # 可选
  synthos:
    version: 1.0.0          # 语义化版本
    author: Synthos
    priority: P2            # P0元技能/P1编排器/P2子skill/P3工具
    related_skills: [name]
```

| 字段 | 必须 | 标准 | 约束 |
|:-----|:----:|:-----|:-----|
| `name` | ✅ | Agent Skills | 小写+连字符, 1-64字符 |
| `description` | ✅ | Agent Skills | 1-1024字符 |
| `metadata.synthos.*` | 推荐 | Synthos | 所有扩展字段在此命名空间 |

### Body 顺序

1. **原理层·文言**（最先）— 核心理念
2. **方法层·白话** — 步骤化流程
3. **命令层·英文** — 精确命令/代码

## 压缩规范

SKILL.md ≤8K。超标时压缩策略：

| 原始 | 目标 |
|:-----|:-----|
| 长篇原理 | 文言表格(40-60%) |
| 完整命令列表 | 快速参考表 → references/ |
| 全部陷阱 | 关键陷阱节 → references/ |
| 长流程 | 伪代码 → references/ |

**铁律**：压缩后 `skill_view()` 验证。keep frontmatter intact, only truncate body.

## 三层文言密度

| 层 | 数量 | 范围 | 文言深度 |
|:---|:----:|:-----|:---------|
| 甲·哲学 | ~15 | 认知原子 + meta + infra | 全文言+经典 |
| 乙·方法 | ~25 | writing/quality/research | 短文言一句 |
| 丙·工具 | ~80 | productivity/github/media | 不写文言 |

## 层级分离

```
Layer 0: 元技能 (P0) — evolution, quality-gate, skill-authoring
Layer 1: 主技能(编排器) — 4-6K, 核心原理+工作流地图
Layer 2: 子技能(原子方法) — 2-4K, 触发条件+方法+验证
Layer 3: 参考文件 — 不限, references/
```

## 维护陷阱

| # | 陷阱 | 正确做法 |
|:-:|:-----|:---------|
| 1 | 累积patch导致文档退化 | 重复≥2次 → write_file重写 |
| 2 | 轻易创建新skill | 先检查能否吸收到已有 |
| 3 | 建完不验证 | 每次edit/patch后 skill_view() |
| 4 | 跨skill引用文件重复 | 共享引用放 skills/shared/references/ |
| 5 | 顶层字段污染 | 非标准字段放 metadata.synthos |
| 6 | head -c截断破坏frontmatter | 压缩时保留完整frontmatter, 只截body |
