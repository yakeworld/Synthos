---

name: skill-absorption
related_skills: ["project-experience-distillation"]
description: 双循环进化：内部反思(P0) + 外部吸收(P1)。Cross-project absorption methodology — multi-round cross-project comparison, active project tracking, self-expanding keyword discovery. 动灵驱动吸收(Entelechy-Driven Absorption v4.3).
author: Synthos
license: MIT
version: 4.3
license: MIT
allowed-tools:
- terminal
- file
- web
- search
- delegation
metadata:
  synthos:
    version: 4.3.0
    priority: P1
    signature: 'target: str -> absorption_report: dict'


---



## IO_CONTRACT

- **input**: `target: str` — 待吸收的外部项目/技能标识
- **input**: `source_analysis: dict` — 外部源分析结果（compatibility, transferability, novelty）
- **input**: `keyword_pool: list[str]` — 自扩展关键词池
- **output**: `absorption_report: dict` — 吸收决策报告（decision: absorb/reject/defer, reason, transformed_skills）
- **output**: `project_tracker_update: dict` — 项目追踪数据库更新
- **output**: `keyword_expansion: list[str]` — 新增关键词
> 对应原则：P2（机械原子暴露输入输出规范）
# Skill Absorption Engine v3.0

## 核心原则（文言）

| 原则 | 义 |
|:-----|:----|
| 主动追踪 | 不等待固定周期。每次进化轮次都执行扫描 |
| 看过的项目不丢 | 项目追踪数据库记录所有发现，可随访 |
| 关键词自扩展 | 从项目描述/标签中提取新关键词，持续扩大搜索面 |
| 从自身缺陷发现方向 | 系统诊断结果自动生成新关键词 |
| P2原则 | 核心原子稳定，吸收目标永远是扩展层 |

## 动灵驱动吸收（v4.3.0）

吸收不是补短缺，是选营养。每次吸收前过**动门**：

1. **方向相容吗？** — 核心哲学与 Synthos 7+1 框架相容？
2. **我们能转化吗？** — 能否经三语层级(文言→白话→英文)分解重组？
3. **为什么是这个方向？** — 比另一个方向更有价值吗？

动门未过 → 不吸收。

## 四门流程

```
动门 → 方向相容?能转化?为何是此方向?
  ↓ 通过
L+0 来源标注门 → 标注来源+双循环机制+配置差异
L+1 适配改造门 → 对象化+三语转换+原子化
L+2 五层验证门 → 原理/方法/命令/案例/局限
L+3 独立验证门 → AAA论文评审+五维度评分
```

各门详细协议见 `references/absorption-gates-protocol.md`。

## 五层验证架构

| 层 | 内容 | 验证标准 |
|:---|:-----|:---------|
| 原理层 | 核心思想/哲学（文言提炼） | 与7+1框架相容 |
| 方法层 | 工程步骤（白话） | 可独立执行 |
| 命令层 | 具体命令/代码（英文） | 精确无误 |
| 案例层 | 应用实例 | 覆盖典型场景 |
| 局限层 | 已知约束 | 诚实标注 |

## 【v4.3.1】方法论优先协议

> 用户指令: "吸收思想和理论，技巧，消化吸收，不需要考虑许可"
> 核心: 只看思想/方法论/技巧，许可证不影响方法论吸收决策。

### 五维比较中的许可证处理

原标准中的"许可证"维度(0.10)降级为**纯记录字段**，不扣分、不阻塞吸收决策。

### 可吸收的项目类型

| 项目类型 | 理由 | 注入方式 |
|:---------|:-----|:---------|
| **AGPL-3.0** | AGPL限制代码分发，但方法论可提取 | 流程/架构/设计模式提取 |
| **NOASSERTION** | 无法确认许可 ≠ 不能吸收方法论 | 仅基于五维比较评分 |
| **Chrome扩展/IDE插件** | 架构不可迁移，但方法论可提取 | 流水线/工作流/编排模式提取 |

### 记录要求

所有吸收必须在 `absorption-tracked.json` 记录 `license_note`，标记"仅方法论，无代码"。

### 不可吸收的项目类型

| 项目类型 | 理由 |
|:---------|:-----|
| 与宪法冲突 | 碳硅共生、自进化最高优先、MIT开源 |
| 仅复制代码 | 必须用 Synthos 形态重新表达 |
| 无源代码/文档 | 无法理解核心方法论 |

## 7项适配检查

1. 对象化：从运行时数据→纯声明式skill
2. 三语转换：原理文言/方法白话/命令英文
3. 度量一致：各原子使用统一度量标准
4. 注入方式：平行新原子 vs 扩展现有
5. Phase划分：P0即时/P1近期/P2远期
6. 依存关系：新原子可能依赖已有原子
7. 宪法合规：不违反CONSTITUTION.md

## 搜索源

| 源 | 方法 | 频率 |
|:---|:-----|:-----|
| GitHub Topics | `curl -s "https://api.github.com/search/repositories?q=topic:..."` | 每进化轮次 |
| Hermes Skills | `find skills/ -name 'SKILL.md'` | 每轮 |
| arXiv | `arxiv.search(query, max_results=10)` | 每2轮 |

完整关键词轮转策略见 `references/keyword-rotation.md`。

## 项目追踪

所有发现的项目存储在 `outputs/evolution/absorption-tracked.json`。

状态生命周期：tracking → evaluating → absorbed | deferred → archived

## 吸收报告模板

每次深度吸收后保留吸收报告（见 `references/absorption-report-template.md`）。

## 参考文件

- `references/absorption-gates-protocol.md` — L+0到L+3详细协议
- `references/keyword-rotation.md` — 关键词轮转策略和分类
- `references/absorption-report-template.md` — 吸收报告模板
- `references/multi-project-comparison.md` — 多项目哲学对比矩阵
