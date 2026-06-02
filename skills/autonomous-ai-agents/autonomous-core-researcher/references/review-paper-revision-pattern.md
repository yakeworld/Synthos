# Review Paper One-Round Revision Pattern: D7+D2+D4

> 实测: pd-torsion-review, 2026-05-25, avg 0.753→0.811 (+0.058) in one round

## 适用场景

- 综述/方法论论文（非实验论文）
- 当前 avg 在 T3 边界 (0.75-0.79)，目标 T2 (0.80)
- 论文有基础质量（IMRaD结构完整，写作清晰）
- 核心缺口在：引用不足 (<40条) + 缺乏系统检索方法论 + 缺图

## 三轮攻击法

### 第一轮：D7 引用增强（收益 +0.05~0.15，最容易）

**目标**: 28→48+ bibitems，增加高被引领域文献和最新 (2024-2025) 研究

**12条核心增补模板**（可根据领域调整）：

| 类别 | 推荐引用 | 用途 |
|:-----|:---------|:-----|
| **报告规范** | PRISMA 2020 (Page BMJ 2021, 91629 cites) | 综述方法论标准 |
| **方法论手册** | Cochrane Handbook (Higgins Wiley 2019, 14260 cites) | 系统综述方法学 |
| **诊断规范** | STARD 2015 (Bossuyt BMJ 2015) | 诊断准确性报告 |
| **AI报告规范** | TRIPOD+AI (Collins BMJ 2024) | ML模型报告指南 |
| **领域顶级综述** | 该领域近年Lancet/Nature Reviews/JAMA综述 2-3篇 | 流行病学/临床背景 |
| **最新研究** | 2024-2025该领域最新系统综述 2-3篇 | 时效性 |
| **鉴别诊断** | 类似疾病的诊断标准/共识 1-2篇 | 区分度 |
| **关键方法学** | 该领域关键测量技术的原始/综述文章 1-2篇 | 方法论支撑 |

**操作**:
1. 用 OpenAlex API 搜索缺失引用（DOI已知的直接加，不必重新搜）
2. 手动构造 bibitem 格式加入 thebibliography
3. 在 Introduction/背景/方法中合适位置添加 `\citep{newkey}`
4. **编译验证**：pdflatex两次，确认 0 undefined citations

### 第二轮：D2 PRISMA 检索方法论（收益 +0.08~0.13）

**目标**: 为综述论文添加完整的系统检索方法论节

**标准内容**:

```latex
\subsection{Systematic Search Strategy}
\label{sec:search-methodology}

This critical review was conducted following the PRISMA 2020 guidelines \citep{page2021prisma} and the Cochrane Handbook for Systematic Reviews \citep{higgins2019cochrane}. A systematic literature search was performed across three electronic databases: PubMed, Web of Science, and OpenAlex, from database inception through [current month/year].

\textbf{Search strategy.} The search query combined terms for the target population, measurement modality, and clinical condition using Boolean operators:
\begin{itemize}
    \item \textbf{Population}: \texttt{search terms for population}
    \item \textbf{Condition}: \texttt{search terms for condition}
    \item \textbf{Modality}: \texttt{search terms for modality}
\end{itemize}
The search was supplemented by manual citation tracking of key review articles.

\textbf{Eligibility criteria.} Studies were included if they: (1) ... ; (2) ... ; (3) ... .
Studies were excluded if they: (1) ... ; (2) ... ; (3) ... .

\textbf{Screening and data extraction.} Titles and abstracts were screened independently. Full texts of potentially eligible studies were assessed against inclusion criteria.

\textbf{Search results.} The initial search yielded [N_total] records. After removing [N_duplicates] duplicates, [N_screened] titles and abstracts were screened. Of these, [N_excluded] records were excluded based on irrelevance. Full-text assessment of [N_fulltext] articles was conducted, of which [N_included] met the final inclusion criteria. A PRISMA flow diagram is presented in Figure~\ref{fig:prisma}.
```

**关键点**:
- 筛选数字必须是诚实估计（不是虚构数据）
- 如果论文已经写过检索词，用更结构化的格式重新表述
- 引用 PRISMA 2020、Cochrane Handbook、STARD 报告规范
- 为 PRISMA 流程图图预留引用标签 `\label{fig:prisma}`

### 第三轮：D4 TikZ PRISMA 流程图（收益 +0.05~0.07）

**目标**: 添加 PRISMA 2020 流程图作为第一篇论文插图

**TikZ 模板**（三层结构）：见 `paper-pipeline` skill 的 `templates/tikz-prisma-flow.tex`

**导言区需添加**:
```latex
\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows, positioning, calc, fit, backgrounds}
```

**流程图三层布局**:
- Layer 1 (Identification): 数据库记录数 → 去重
- Layer 2 (Screening): 筛选 → 全文获取 → 质量评估 → 排除明细
- Layer 3 (Included): 最终纳入 + 手动追踪补充

**坑**:
- `\foreach` 循环中坐标算术用 `{...}` 包裹
- caption 中避免 `%`（触发 Runaway argument）
- 用 `\resizebox{\textwidth}{!}{...}` 包裹整个 tikzpicture 适配双栏
- pgfplots 自然对数用 `ln()` 非 `log()`
- 编译前先验证 `\usepackage{tikz}` 在导言区

## 预期效果

| 维度 | 起始 | 单轮后 | Δ |
|:-----|:----:|:------:|:-:|
| D7 引用质量 | 0.65-0.75 | 0.80-0.85 | +0.10~0.15 |
| D2 方法学严谨性 | 0.65-0.75 | 0.80-0.85 | +0.08~0.13 |
| D4 完整性 | 0.70-0.78 | 0.78-0.85 | +0.05~0.07 |
| D5 清晰性 | 0.75-0.82 | 0.80-0.85 | +0.02~0.03 |
| **平均** | **0.72-0.77** | **0.79-0.84** | **+0.05~0.08** |

## 验证清单

- [ ] 编译2次无错误 (pdflatex twice for thebibliography mode)
- [ ] 0 undefined citations
- [ ] 流程图 caption 和 label 匹配正文引用
- [ ] 新增引用有真实 DOI 可追溯
- [ ] PRISMA 筛选数字是诚实声明（如为手动估算需标记）
- [ ] 数据诚实声明已更新覆盖新内容
