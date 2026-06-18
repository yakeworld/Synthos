# System-Description Paper Structure (Systems Track)

> 适用于需要描述一个自建系统（AI Agent / 认知架构 / 软件框架）的 SCI 论文。
> 区别于纯方法论论文或实证研究论文，系统论文的核心任务是**证明系统设计本身是有意义的**，
> 而不仅仅是系统产出的某个结果。
>
> 凝练自 2026-05-23 Synthos 论文结构重构实践 + Gemini 评审反馈。

## 五节结构

```
Sec 1: Introduction
  └── 痛点锁定（命令式进化锁死） + 三叉戟假说 + 系统概述

Sec 2: Architecture
  └── 设计原理 + 核心组件 + 哲学→工程映射

Sec 3: Self-Evolution / Mechanisms
  └── 系统如何自我改进 + 进化机制 + 质量门控

Sec 4: Results & Validation
  └── 内部指标（收敛曲线/benchmark） + 外部对比（N±SD p<0.05）

Sec 5: Discussion & Conclusion
  └── 核心洞察 + 论文自证 + Limitations + 结论
```

## 每节详解

### Sec 1: Introduction

| 要素 | 位置 | 作用 |
|:-----|:-----|:-----|
| 行业痛点（Imperative Lock-in） | 首段 | 不是罗列缺点，而是指出**一个不可逾越的架构局限** |
| 三叉戟假说 H₁/H₂/H₃ | 次段 | 为本系统设计提供**可证伪的学术靶子**。H₁ 是系统采用的方法，H₂ 和 H₃ 是被证伪的竞争路线 |
| Related Work（按主题分组） | 中间 | 不是简单罗列，而是每个段落结尾说明**为什么现有方案不能解决痛点** |
| 贡献列表（编号） | 末尾 | 3-4 条，每条对应系统的一个设计维度 |

**关键认知**：Introduction 的任务不是"这个系统好"而是"在给定痛点下，系统的设计选择是唯一的逻辑结局"。

### Sec 2: Architecture

不是"讲了什么"而是"为什么这么设计"：

| 子节 | 内容 | 陷阱 |
|:-----|:-----|:-----|
| 设计原理 | 系统的最高层约束（如宪法层级、Entelechy 公理） | 不要写成技术参数列表 |
| 核心组件 | 每个组件的认识论基础 + 功能 + I/O 契约 | 不要针对每个组件写一段——用表格 |
| 哲学→工程映射 | 抽象原则如何落地为具体约束 | 这是系统论文的灵魂——缺失此节则论文沦为技术文档 |

**铁律**：Skills 的特点（三语层级、零 Python、I/O 签名、层级分离、质量门控）必须放在 Architecture 节，**不能**放在 Results 之后。

### Sec 3: Self-Evolution / Mechanisms

如果系统具有自我改进能力，需要单独一节说明：

| 子节 | 内容 |
|:-----|:-----|
| 进化状态机 | 执行的步骤、条件分支、退出条件 |
| 关键机制 | Nudge 熔断、Pareto 多目标优化、主动推理门（如有） |
| 外部吸收管线 | 如何从外部项目吸收能力（L+0—L+3） |
| 质量门控 | 如何防止退化（L1-L4 质量门） |

### Sec 4: Results & Validation

**所有数据集中展示** — 不分隔到多个章节：

| 数据类型 | 示例 |
|:---------|:-----|
| 内部收敛曲线 | 进化轮次 vs 综合分，展示曲线收敛和稳态 |
| Benchmark 通过率 | 原子测试套件全部通过 |
| 能力涌现 | 吸收了 N 个外部项目 + 原生感通过率 |
| **外部定量对比（核心）** | N=50, ±SD, p<0.05 — 与竞争路线的 A/B 实验 |

**铁律**：外部定量对比不可缺失。单有内部指标会被审稿人以 "Self-report bias" 拒绝。
对比必须包含：样本量(N)、标准差(SD)或置信区间(CI)、统计显著性(p)，最好用配对 t 检验。

### Sec 5: Discussion & Conclusion

| 子节 | 内容 |
|:-----|:-----|
| 核心洞察 | "系统论文证明了什么"——从数据中提炼一个高于系统本身的见解 |
| **论文自证（Meta-Verification）** | "本文本身就是通过本系统管线产出的"——这是系统论文独有的杀手锏 |
| Limitations | ≥3 条，必须诚实。每条说明"什么条件下此系统不适用" |
| Conclusion | 塔尖一句 + 3 个关键论点 + 具体数据 |

## 与 IMRaD 的关系

```
标准 IMRaD        系统论文映射
─────────         ────────────
Introduction  →   痛点 + 假说 + RC
Methods       →   Architecture + Evolution
Results       →   Internal + External 数据
Discussion    →   洞察 + 自证 + Limitations
Conclusion    →   总结
```

系统论文的 Methods 自然分裂为 Architecture（系统是什么）和 Evolution（系统怎么生长），
因为它们回答的是两个不同的认知问题。

## 与 CARS / 图尔敏 / 金字塔模型的关系

| 理论 | 在系统论文中的位置 |
|:-----|:------------------|
| CARS Move2 → 三叉戟假说 | Introduction 的 Gap 定位 |
| 图尔敏 Claim → 核心洞察 | Discussion 首段 |
| 图尔敏 Rebuttal → Limitations | Discussion 末段 |
| 金字塔塔尖 → 一句话前提 | Conclusion 首句 |
