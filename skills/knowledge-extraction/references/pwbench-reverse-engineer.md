# PW-Bench 逆向工程方法论（知识提取的补充模式）

**来源**: PaperOrchestra (Song et al., 2026, arXiv:2604.05018, §3 / App. F.2)
**吸收类型**: P1 — 提取模式增强（注入 knowledge-extraction 原子）
**原理**: 从已发表的论文 PDF 逆向重构其研究设计（Idea + Experimental Log），形成 benchmark case

---

## 动机

knowledge-extraction 原子当前的提取模式专注于**从抽象提取结构化知识**（方法/发现/局限/证据等级）。PW-Bench 的逆向工程提供了**补充模式**：从已发表的论文中重建**研究设计** (Idea) 和**原始实验数据** (Experimental Log)，而非仅提取整理后的知识。

这两种模式的关系：

```
传统提取:  论文 → 结构化摘要（方法/发现/结论）
逆向工程: 论文 → (Idea, Experimental Log) → 可用于重建论文
互补性:   提取→知识消费；逆向工程→知识再生产
```

## 三种逆向工程模式

### 模式 1: Sparse Idea（稀疏想法）

> 用第一人称将来时："我们将探索..."
> 禁止引用、URL、作者名
> 不允许包含实验结果
> 避免 LaTeX 数学，用语言描述功能

从论文中提取**高层概念**（不包含任何实现的细节），适合：

- **输入**: 论文全文（去除实验部分）
- **输出**: `idea_sparse.md`，四个部分：
  1. Problem Statement — 问题陈述
  2. Core Hypothesis — 核心假设
  3. Proposed Methodology (high-level) — 方法学概述
  4. Expected Contribution — 预期贡献
- **用例**: 评估管线应对模糊输入的能力

### 模式 2: Dense Idea（密集想法）

> 用第一人称将来时，但保留数学公式
> 定义所有使用的变量
> 包含具体的架构选择和维度
> 不允许实验结果

从论文中提取**详细技术方案**，适合：

- **输入**: 论文全文（去除实验部分）
- **输出**: `idea_dense.md`，四个部分（同上，但更详细）：
  1. Problem Statement — 包含正式定义
  2. Core Hypothesis — 更精确的数学表述
  3. Proposed Methodology — 架构细节、损失函数、训练策略
  4. Expected Contribution — 预期性能指标
- **用例**: 评估管线处理完整技术规范的能力

### 模式 3: Experimental Log（实验日志）

> 用过去时："我们运行了..."
> 去除所有图表编号引用
> 将表格分解为原始数值数据
> 图表发现记录为事实性观察
> 匿名化作者

从论文中提取**原始实验数据**，适合：

- **输入**: 论文全文（仅实验部分）
- **输出**: `experimental_log.md`，三部分：
  1. Setup — 实验设置
  2. Raw Numeric Data — 原始数值数据
  3. Qualitative Observations — 定性观察
- **用例**: 对照 ground truth 验证生成论文的数据精确性

## 在 knowledge-extraction 中的使用

在原有 5 步提取过程的基础上，增加一个**可选的补充模式**：

**触发条件**：
- 用户明确要求"从这篇论文重构研究设计"
- 用户想建立 benchmark case
- 用户想对比不同管线生成同篇论文的能力

**过程**（在标准提取之后）：
```
Step 6 (可选): PW-Bench 逆向工程
  6a. 判断用户意图是否匹配
  6b. 若匹配，选择模式（Sparse / Dense / Experimental Log / 全部）
  6c. 执行逆向工程，输出到 outputs/bench/<paper_id>/
  6d. 在 field_summary 中添加 reverse_engineering 字段
```

**注意**: 此模式是**可选增强**，不改变 knowledge-extraction 的核心 I/O 契约。当不触发时，原子的行为与原版完全一致。

---

**变更**: 2026-05-14 — 从 PaperOrchestra/PaperWritingBench 吸收，v1.0
