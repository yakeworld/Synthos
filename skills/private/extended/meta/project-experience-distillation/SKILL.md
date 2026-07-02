---
name: project-experience-distillation

## Operational Steps
1. 
2. 
3. 

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 
category: meta
signature: "project-experience-distillation -> meta: ⚡ 最高优先级技能。From project experience to reusable skill — extract workflow patterns,"
description: "⚡ 最高优先级技能。From project experience to reusable skill — extract workflow patterns, design principles, and pitfalls from completed project work, abstract them into general form, and formalize as SKILL.md. Also: philosophical implementation gap analysis to drive mechanism-level improvements. The reflexive learning engine of Synthos: self-evolution through self-observation."
version: 2.0.0
author: Hermes Agent
license: MIT
priority: P0
execution_rule: "每次 complex task（5+ tool calls）后自动触发。quality-gate 通过后自动触发本技能。信任阈值条件满足时直接执行不需批准。"
allowed-tools: terminal skill_manage skill_view read_file write_file patch memory session_search
related_skills: ["quality-gate", "project-absorption"]
metadata:
  synthos:
    priority: P0
    atom_type: meta-reflection
    description: ⚡ P0 从项目/论文经验到可复用skill — 提取模式/设计原则/陷阱。被 paper-pipeline P6 阶段调用。
    signature: |
      project_context: str, session_summary: str, pitfalls_found: list[str] -> new_pattern: str, new_skill_name: str, target_skill: str, philosophy_insight: str | new_pattern: str, new_skill_name: str or None, target_skill: str or None, philosophy_insight: str, extracted_skill: SKILL.md or patch
    related_skills: ["quality-gate", "project-absorption"]

---

# Project Experience Distillation

> 从做项目中学到的东西，凝练成可复用的技能。
> 凡有所作，必有所得；凡有所得，必凝为器。

## IO_CONTRACT

- **input**: `project_data: dict, experience_type: str` — 用户请求描述、上下文信息
- **output**: `distilled_skills: list — 经验提炼结果`

> 对应原则：P2（机械原子暴露输入输出规范）

## 原理层·文言

| 白话 | 文言 | 义 |
|:---|:-----|:---|
| 系统的生长动力来自内部，不是外部 | **动灵在内，不为外驱** | 即使不吸收任何外部项目，也能从自身实践中学 |
| 每次复杂任务后必须回顾 | **凡作必省，无省不进** | 不回顾的任务只完成了一次，回顾的任务产出了未来 |
| 提取普遍规律而非具体步骤 | **去其形，留其神** | 去掉项目名/路径/日期，保留可跨项目复用的模式 |
| 先有哲学追问，再有技能设计 | **先问其理，再立其器** | 不是从"怎么做"开始，是从"为什么有效"开始 |
| 优先扩展现有技能，不轻易新建 | **源一不二，能扩不创** | 普遍规律优先吸收到已有技能，只有个性化规则才新开 |
| 营养适合当前生长阶段才吸收 | **适则纳，不适则俟** | 不是所有好的方法论都适合当前阶段 |

## 方法层·白话

### 触发条件

以下条件任一满足时运行本技能：

- [ ] 完成了 5+ 次工具调用的复杂任务
- [ ] 解决了一个需要创造性方案的困难问题
- [ ] 发现了一个可以总结的工作模式或流程
- [ ] 踩到了值得记录的陷阱
- [ ] 用户明确说"记住这个方法"/"下次这样用"
- [ ] 项目状态有显著变化（版本升级、架构变更、质量提升）

### 五步反思流程

#### 第1步：回顾 — 这次工作中发生了什么？

用 `session_search` 回顾本次会话的关键节点。

#### 第2步：抽象 — 去掉项目细节，找到通用形式

将具体内容替换为通用概念。输出：一段简洁的通用流程描述（1-3句话）。

#### 第3步：形式化 — 写 SKILL.md

1. **frontmatter** — name, description, version, author, license, allowed-tools, metadata
2. **触发条件** — 什么场景下用
3. **步骤** — 可执行的 numbered steps
4. **原理层·文言** — 四字格言压缩核心哲学
5. **验证** — 如何确认技能有效
6. **陷阱** — 自己的教训（至少3条来自真实经验）

#### 第4步：集成 — 连接相关技能

- `related_skills` 关联互补技能
- **优先扩展现有技能**，只有真正的个性化规则才新开 skill

#### 第5步：思想提升 — 追问"为什么有效"

输出到 SKILL.md 的 Philosophy 节。

### 内部反思 vs 外部吸收

| 维度 | 内部反思（本技能） | 外部吸收 (project-absorption) |
|:-----|:-------------------|:-----------------------------|
| 来源 | 自己的项目工作历史 | 外部项目/目录/代码库 |
| 价值 | 提升思想高度、发现模式 | 引入外部营养、工具复用 |
| 优先级 | **P0（第一循环）** | P1（第二循环） |

### 五层提取规范

| 层次 | 名称 | 问什么 | 怎么吸收 |
|:----:|:-----|:-------|:---------|
| **0** | **文言** | 核心哲学能否用四字格言表达？ | **必选先导** |
| **1** | **思想** | 项目的核心信念是什么？ | 对比→参考，不相容则停止 |
| **2-3** | **规范+规律** | 格式、接口、设计原则 | 吸收到已有技能 |
| **4-5** | **能力+任务** | 具体功能、操作步骤 | 选分析 → 评估后决定 |

## 陷阱

| # | 陷阱 | 正确做法 |
|:-:|:-----|:---------|
| 1 | **抽象不够** — 只在项目级别描述而不提升到通用级别 | 去掉项目名/路径/日期，保留可跨复用的模式 |
| 2 | **只记录不反思** — 记录了步骤没问"为什么有效" | 思想提升是灵魂，不是可选的 |
| 3 | **和 project-absorption 混淆** — 本技能是内部反思，project-absorption 是外部吸收 | 内部反思 = 从自身实践学；外部吸收 = 从外部项目学 |
| 4 | **轻易创建新 skill** | 普遍规律优先扩展现有技能，只有个性化规则才新开 |
| 5 | **建完 skill 不跑质量门** | 新建 skill 至少通过 L1 格式门 |
| 6 | **文档退化** — 累积 patch 操作导致同一节重复出现 | 大重构时重写整个文件，不累积 patch |
| 7 | **抽象级别不够深** — 只去掉实体名没上升到约束类型级别 | 真正的抽象是识别出**约束类型**，不是去掉名字保留模板 |

## 参考文件

- `ref/project-absorption-pattern.md` — 内部反思 vs 外部吸收对比方法论。两者是双向进化引擎：内部反思从自身实践学（P0），外部吸收从外部项目学（P1）。
- `references/batch-loop-pattern.md` — 批量循环执行模式。

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）
