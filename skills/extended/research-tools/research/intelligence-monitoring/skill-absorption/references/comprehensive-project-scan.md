# Comprehensive Project Scan Protocol

> 2026-06-03 实战提炼
> 来自: Synthos Phase A/B/C 整理 + ARIS/AI-Scientist 评估过程

## 原理

不是逐项目搜索，而是**全量扫描已收集的数据资产**——文献库、实验数据、论文草稿、已引用外部仓库、可运行脚本——综合评估吸收价值。

## 扫描清单

| # | 扫描目标 | 路径 | 预期产出 |
|:-:|:---------|:-----|:---------|
| 1 | 文献库 | `literature/*/` | 各领域论文数、结构化 bib 引用数 |
| 2 | 实验数据 | `data/*/` | 数据集大小、可用性 |
| 3 | 论文产出 | `outputs/papers/*/` | QC 通过数、方法论验证数据 |
| 4 | 外部 GH 引用 | grep 技能中所有 `github.com/owner/repo` | 已引用但未吸收的项目 |
| 5 | 已有吸收记录 | `evolution/references/absorption-*.md` | 已吸收项目和评分 |
| 6 | 吸收分析 | `skill-absorption/references/*.md` | 已分析但未执行吸收的候选 |
| 7 | 可运行脚本 | `skills/*/scripts/*.py` | 可注入管线的代码示例 |
| 8 | 模板文件 | `skills/*/templates/*` | 可复用的起始模板 |

## 输出格式

每次扫描产出：

1. **吸收潜力汇总表** — 按项目分类，含评分、同步值、已/未吸收
2. **优先级排序** — P0 (立即)、P1 (本周)、P2 (下周)、P3 (参考)
3. **每个P0的简要吸收计划** — 注入目标 skill、预期修改文件数

## 与现有方法论的关系

此协议是 `skill-absorption` 主技能的侦察阶段增强——在 Parallel Reconnaissance (Phase 0) 之前，先做全量资产盘点。
