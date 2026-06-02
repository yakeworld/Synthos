---
name: sci-paper-standard-structure
description: "Standard IMRaD (Introduction, Methods, Results, Discussion, Conclusion) SCI paper architecture. Philosophical grounding: CARS + Toulmin + Pyramid + Hourglass. Theory-first, technology-second."
version: 2.0.0
author: Synthos + 临床科研设计与论文写作(2026-05-20)
license: MIT
priority: P1
execution_rule: "Load before ARG atom. Each section driven by its theory model. Verify all required elements before saving."
references:
  section-requirements.md: "Per-section content requirements, word counts, and common pitfalls"
  template-example.md: "Complete LaTeX IMRaD template"
  template-synthos-meta-paper.md: "Complete Synthos meta-paper template (30K chars, 5 sections, T1 target)"
  latex-compilation.md: "Full pdflatex x2 + bibtex compilation"
  fstring-pitfalls.md: "Python f-string LaTeX gotchas"
  comparative-gap-analysis.md: "Systematic paper improvement method"
  prewriting-gap-analysis.md: "Research asset → paper planning"
  source-to-methods-extraction.md: "From NotebookLM to Methods section"
---

---

## 原理层·文言

> 「夫人之立言，因字而生句，积句而为章，积章而成篇。」
> 「物有本末，事有终始，知所先后，则近道矣。」文有常格，序不可乱。
> 引言设问，方法答之，结果证之，讨论释之。首尾相顾，逻辑贯之。
> CARS开篇，金字塔立论，沙漏收束。# IMRaD 标准论文架构（理论驱动版）

## 哲学层（Philosophy Layer）

### IMRaD 为何是五章？

IMRaD 结构不是任意约定的，而是由科学发现的内在认知逻辑决定：

```
科学发现过程                    IMRaD论文结构
─────────────────              ──────────────
为什么研究这个问题？    →        Introduction
怎么研究的？            →        Methods
发现了什么？            →        Results
这意味着什么？          →        Discussion
所以呢？                →        Conclusion
```

每一章对应一个认知问题，不增不减。违反此结构的论文（如将Related Work独立成章、将Limitations独立成节）必然导致认知逻辑断裂。

## 理论层（Theory Layer）

### 每章的驱动理论

```
论文全文（沙漏模型）
 宽 │
    ├── Introduction    → CARS模型（Move1→Move2→Move3）
 窄 │        │
    ├── Methods         → 精确到可复现
 窄 │        │
    ├── Results         → 图尔敏Grounds（实述不论）
    │        │
 宽 │    ├── Discussion      → 图尔敏模型（六要素完整）
    └── Conclusion     → 金字塔原理（塔尖重申）
```

### CARS模型（Introduction专用）

```
Move1: 建立领地
  ├── 宣称中心性：该主题为何重要
  ├── 主题概括：领域知识现状
  └── 回顾研究：前人工作

Move2: 建立壁龛
  ├── 反驳主张 / 指出空白 / 提出问题 / 延续传统
  └── 必须连续：从Move1的回顾自然过渡到Move2的空白

Move3: 占据壁龛
  ├── 概述目的/宣告本研究
  ├── 宣告主要发现（可选）
  └── 指明论文结构（可选）
```

### 图尔敏模型（Discussion专用）

```
Claim(主张)                 ← 子节开头句
  ↑ 被 Warrant(保证) 连接
Grounds/Data(根据/数据)     ← 来自Results的引用
  ↑ 被 Backing(支撑) 加固
Qualifier(限定)             ← 审慎限定词
Rebuttal(反驳)              ← Limitations编号≥3条
```

### 金字塔原理（Abstract+Conclusion专用）

```
塔尖: 核心结论（1句话）
  │
  ├── 论点1: 关键支撑
  ├── 论点2: 关键支撑      ← 神奇数字3-4
  └── 论点3: 关键支撑
        │
塔基: 具体数据/事实/案例
```

## 五章定式（技术层）

### 1. Introduction（CARS模型驱动）

| 元素 | 位置 | CARS对应 |
|:-----|:-----|:---------|
| 背景 | 开头1-2段 | Move1: 宣称中心性+主题概括 |
| Related Work | 中间3-6段，按主题分组 | Move1→Move2: 回顾→指出空白 |
| Gap声明 | Gap段 | Move2: 建立壁龛 |
| 贡献声明（编号列表） | 最后一段 | Move3: 占据壁龛 |
| 对比表 | 紧接贡献声明后 | Move3: 可视化定位 |

### 2. Methods（沙漏模型最窄处）

不含评估内容。每个组件详细到可复现。含形式化定义。架构图作为Backing（可视化证据）。

### 3. Results（图尔敏Grounds）

**铁律：实述不论** — 只呈现数据，不解释数据。解释归Discussion的Claim+Warrant。结果表是Grounds的核心载体。

### 4. Discussion（图尔敏模型完整驱动）

每个论点必须包含：Claim(主张)→Grounds(根据)→Warrant(保证)→Backing(支撑)→Qualifier(限定)→Rebuttal(反驳)。

Limitations独立子节，编号≥3条——这是图尔敏Rebuttal要素的显式呈现。

### 5. Conclusion（金字塔原理驱动）

结论先行。贡献总结(塔尖)+3个关键论点(中层)+具体数据(塔基)。Code Availability作为学术诚信的Backing。

## 编译验证

```bash
pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex
```

验证：所有引用可解析、无Undefined warning、PDF≥5页、Overfull hbox尽量少。

## 陷阱

1. **改写时退化参考文献格式**：原版有`\textit{}`/`\url{}`/`vol.~pp.~`的，不允许替换为简写。
2. **Figure必须用矢量图**：不接受verbatim图替代True figures。架构图用TikZ/PDF。
3. **引用格式碎片化**：同一论文内所有bibitem格式必须一致。
5. **CARS Move1→Move2缺乏连贯性**：Related Work最后一段必须自然过渡到Gap，不能突然转折。

## 系统描述论文的结构

当描述一个自建系统（AI Agent / 认知架构 / 软件框架）时，标准IMRaD需要调整为5节系统论文结构。
详见 `references/system-description-paper-structure.md`。关键不同：
- Methods分裂为 Architecture（系统是什么）和 Evolution（系统怎么进化）
- Results 必须包含内部指标 + 外部定量对比（N, ±SD, p<0.05）
- Discussion 增加"论文自证"节——"本文本身就是系统产出的"
5. **Discussion缺少Rebuttal**：没有Limitations子节的Discussion是不完整的图尔敏论证。
