---
name: research-ideation
description: 研究创意发散与认知引擎（RIF+CCF）。三层架构：Layer 1（10操作框架）→ 产出研究方向候选； Layer 2（8认知引擎）→
version: 1.0.0
  产出认知洞察；Layer 3（组合协议）→ 编排执行流程。 将研究问题转化为多维度创意方向和认知洞察。先发散后收敛，多角度扫描领域机会。
license: MIT
allowed-tools: Read Write
dependencies:
- knowledge-acquisition
- association-discovery
metadata:
  synthos_atom_type: cognitive
  synthos_version: 2.1.0
  synthos_skill_md_hash: research-ideation-v2.1.0
  synthos_model_tested_on: '2026-05-10T00:00:00Z'
  synthos_author: Synthos
  synthos_absorbed_from: Synthos internal (research ideation methodology)
  synthos_absorbed_date: '2026-05-10'
  synthos_io_contract_ref: references/IO_CONTRACT.md
  synthos_asserted_compliance: P1
  synthos_data_access_level: raw
  synthos_depends_on: knowledge-acquisition, association-discovery
  synthos:
    author: Synthos
    signature: 'research_question: str -> research_candidates: list[ResearchCandidate],
      cognitive_insights: list[CognitiveInsight]'
    related_skills:
    - academic-paper-completion
    - adhd-eye-tracking-review
    - arxiv
    - biorxiv
    - blogwatcher
    version: 2.1.0
    tags:
    - research-ideation
    - brainstorming
    - cognitive-engine
    - research-direction
    - exploration

---



## 原理层·文言

### 构思之道

> 问从何来，思由何起？不见其问，焉有其答。
> 四源而后有问：政策导向、临床困境、技术碰撞、学科交叉。
> 十框架操作为体，八引擎认知为用，六协议组合为变。
> 发散而后收敛，收敛而后凝练，凝练而后验证。
> 思维若僵，反向求之。不见出路，问其反面。

## 方法层·白话

**研究创意发散与认知引擎** — 创意生成的起点。四源（政策/临床/技术/交叉）是灵感之泉，10框架是发散之器，8引擎是收敛之力。

## 触发条件

加载此技能当用户：需要多维度创意发散、从不同角度探索方向、思维卡住需突破、系统扫描领域机会。

**不适用**：已有明确方向 → 用hypothesis-generation；需要文献检索 → knowledge-acquisition；需要关联分析 → association-discovery。

## 验证清单

- [ ] 输入：清晰的研究问题描述
- [ ] 输出包含与用户预设方向相反的创意方向（反谄媚）
- [ ] top-5创意来自≥3个不同框架

---

## 三层架构

```
输入问题 → Layer 3: 集成流程(Diverge→Converge→Refine→Validate)
                ├── Layer 1: 10操作框架 → 研究方向候选
                └── Layer 2: 8认知引擎 → 认知洞察
         → 输出：创意候选 + 认知视角 + 组合分析
```

| Layer | 内容 | 产出 |
|:------|:-----|:-----|
| L1 操作层 | 10种结构化创意框架 | 具体研究方向列表 |
| L2 引擎层 | 8种底层认知操作模式 | 认知洞察、新维度 |
| L3 组合层 | 6种预定义组合协议 + 集成流程 | 编排执行方案 |

---

## Layer 1: 10操作框架

| # | 框架 | 核心操作 | 一句话示例 |
|:-:|:-----|:---------|:-----------|
| F1 | Problem-First vs Solution-First 切换 | 从问题出发 vs 从方案出发 | "能否用客观生物标记物替代主观量表？" |
| F2 | Abstraction Ladder 抽象阶梯 | 沿具体↔抽象上下移动 | ADHD眼动异常 → 注意力-运动耦合机制 |
| F3 | Tension Hunting 张力狩猎 | 寻找领域内矛盾/悖论/异常值 | "为什么模型预测A但观察到B？" |
| F4 | Cross-Pollination 交叉授粉 | 跨领域迁移概念/方法 | 生态学多样性指数 → 精神症状谱宽度 |
| F5 | What Changed 变化探测 | 关注技术/环境/人群/政策变化 | "新技术能否回答旧问题？" |
| F6 | Failure Analysis 失败分析 | 从失败和不一致中挖方向 | 效应量小→是否忽略了调节变量？ |
| F7 | Simplicity Test 简洁性检验 | 追问更简单解释/更少前提 | 多症状是否共享一个核心缺陷？ |
| F8 | Stakeholder Rotation 利益旋转 | 换视角（患者/医生/政策/研究者） | 患者的"生活质量"vs医生的"诊断准确" |
| F9 | Composition/Decomposition 组合分解 | 拆分组件后重新组合 | 空间×时间×功能维度新组合 |
| F10 | Explain-It Test 解释检验 | 向不同听众解释发现盲点 | 外行→动机；跨学科→方法；专家→反证 |

---

## Layer 2: 8认知引擎

| # | 引擎 | 原理来源 | 核心操作 |
|:-:|:-----|:---------|:---------|
| E1 | Bisociation 组合创造 | Koestler《The Act of Creation》 | 两独立框架交叉产生新意义 |
| E2 | Problem Reformulation 问题重构 | 元认知 | 解决问题前先质疑问题本身 |
| E3 | Analogical Reasoning 结构映射 | Gentner SMT(1983) | 关系结构映射，非表面相似 |
| E4 | Constraint Manipulation 约束操作 | Boden《The Creative Mind》 | 放松/收紧/替换/反转约束 |
| E5 | Negation/Inversion 否定反转 | 反直觉 | 问"如果全错，对的会是什么" |
| E6 | Abstraction Laddering 抽象升降 | 认知灵活度 | 上行问"为什么"，下行问"具体如何" |
| E7 | Adjacent Possible 相邻可能 | Kauffman/Johnson | 探索当前知识的一步可达空间 |
| E8 | Janusian/Dialectical 双面辩证 | Rothenberg(1979) / Hegel | 同时持有矛盾，寻找合题 |

---

## Layer 3: 组合协议

### 预定义组合

| 组合 | 目标 | 操作序列 |
|:----|:-----|:---------|
| C1 思维热身 | 激活多维度思考 | E6→E1→E2 → L1全部 |
| C2 瓶颈突破 | 突破认知卡点 | E5→E4→E8 → F6→F3 |
| C3 跨域嫁接 | 引入外域智慧 | E3→E6→E1 → F4 |
| C4 方向扫描 | 系统探测可能方向 | E7→E2→E6 → L1全部 |
| C5 矛盾转化 | 将冲突变机遇 | E8→E5→E7 → F3 |
| C6 约束突破 | 超越资源限制 | E4→E5→E2 → F7→F1 |

### 集成流程

1. **发散**: L2引擎运行→认知洞察 → L1框架触发→创意候选(10-30个) → 交叉标记
2. **收敛**: 去重 → 三轴评分(新颖性/可行性/影响力, 1-5) → 排序(新颖×0.4+影响×0.4+可行×0.2)
3. **检验**: 反谄媚检查 → 框架多样性核验(top-5≥3框架) → 输出格式化

---

## 框架选择指南

| 你的状态 | 推荐路径 |
|:---------|:---------|
| 需要新研究方向 | F2→F3→F5 + E7 |
| 思维卡住 | E5→E4→E2 |
| 需要方法创新 | E3→E1 + F4→F9 |
| 面对学术争议 | E8→E5 + F3 |
| 资源受限 | E4→E5 + F7→F1 |
| 需要系统扫描 | E7→E2→E6 + L1全部 |

---

## 反谄媚防护

1. **强制反方向**: 每个框架至少提出一个与用户预设相反的创意方向
2. **新颖性检查**: L1≥30% novelty≥4, L2≥40% novelty≥4
3. **冲突标记**: 与已知文献冲突必须标记风险
4. **多样性保证**: top-5来自≥3个不同框架

---

## 命令层

- **Signature**: `problem_statement: str, constraints: dict -> research_directions: list[Direction], cognitive_insights: list[Insight]`
- **Allowed tools**: Read, Write
- **Input**: `problem_statement` (required), `constraints` (optional)
- **Output**: `research_directions` (with score + novelty), `cognitive_insights` (with framework type)
- **Do NOT**: perform literature review, formalize hypotheses, write paper sections
