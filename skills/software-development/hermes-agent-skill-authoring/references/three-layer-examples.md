# Three-Layer Skill Structure — Reference Examples

This file documents proven three-layer (原理层·文言 + 方法层·白话 + 命令层·English) implementations from the Synthos ecosystem.

## Example 1: OS-Level Skill (总纲式)

**File**: `Synthos/SKILL.md` (v1.2.0)

Structure:
```
原理层·文言 ← FIRST (theory first)
├── 总纲 (system manifesto, 3 sentences)
├── 认知原子论 (6 atoms as 4-char table)
├── 思维八维论 (8 dimensions with usage descriptions)
├── 进化之道 (evolution philosophy, 3 sentences)
└── 质量之规 (quality gates, 3 sentences)
---
方法层·白话
├── 触发条件
├── Agent4S层级映射表
├── 6原子DAG编排
│   └── 任务复杂度→最短原子链
├── 外部吸收流程
├── 进化引擎触发
└── 当前度量
---
命令层·English
├── Quick Start (code blocks)
├── Directory Structure (tree)
└── Absorbed External Skills (table)
```

**Key pattern**: 总纲式 — 1 paragraph manifesto + N subsection essays, each with a table.

## Example 2: Meta-Skill (格言式 + 吸收记录)

**File**: `skills/evolution/SKILL.md` (v2.11)

Structure:
```
原理层·文言
├── 核心理念 (格言式: 6 pairs of 白话/文言/义)
└── 吸收之道 (4-sentence essay + absorption record table)
---
方法层·白话
├── 两种触发模式
├── 状态机图
├── 11步概要
└── 工作目录
---
命令层·English
├── Trigger (code block)
├── Key Tool References (table)
└── Related References (table)
```

## Example 3: Domain Skill (论文式)

**File**: `skills/patent-disclosure/SKILL.md` (v1.8.5-synthos-2)

Structure:
```
原理层·文言
├── 专利本源论 (essay: 三性为纲)
├── 交底书体要 (essay: 三事贯通如鼎之三足)
├── 查新原道 (essay: 先官后民)
├── 迭代变通 (essay: 旧稿不覆，新篇另出)
└── 脱敏守正 (essay: 抽象为通用语)
---
方法层·白话
├── 总纲 (workflow table)
├── 触发条件
├── 核心约束 (5 rules)
└── 工具安装
---
命令层·English
├── Directory Structure
├── Key Command Patterns
└── Step Execution Order
```

## Example 4: Workflow Skill (格言式 + PaperSpine吸收)

**File**: `skills/paper-workflow/SKILL.md` (v1.0.0 + PaperSpine)

Currently does NOT have 原理层·文言 yet (pending update).
Demonstrates: structured step-by-step 方法层 + PaperSpine absorption integration.
