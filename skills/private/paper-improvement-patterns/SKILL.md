---
name: paper-improvement-patterns
description: "论文质量改进的标准化模式库 — 消融实验、统计显著性、前沿文献补充、Data/Code声明的添加模式"
version: 1.2.0
author: "Synthos"
license: MIT
metadata:
  synthos:
    priority: P2
    atom_type: skill
    description: "论文质量改进模式库 — 前沿文献、消融实验、统计显著性、数据声明、数值伪造修复等标准化改进模式"
    related_skills: [paper-improvement, reproducibility-audit, paper-d8-d10a-scan, prose-cluster-hybrid-citation-fix]
    change_log:
      "1.1.0": "2026-06-24 新增外部引用到quality-gate的消融布尔开关实现和Notebook-Script统一工作流"
signature: "paper-improvement-patterns -> processed_result"
---

## 核心场景

当论文达到可编译状态但需要提升质量（G1-G7评审分数、引用质量、可复现性声明等）时，使用此模式。

## 标准改进流程

### 1. 前沿文献补充

**触发条件**：Discussion或Related Work中缺少2024-2026年最新文献

**步骤**：
1. 定位训练管线目录（通常在 `/mnt/nfs/training_pipeline/` 或 `/home/yakeworld/`）
2. 查找 `research_analysis_label_creation.md` 或类似分析文档
3. 提取其中引用的2024-2026年前沿文献（arXiv、NeurIPS、ICME等）
4. 将文献整理为BibTeX条目，添加到论文的 `references.bib`
5. 在Discussion中整合这些文献，按以下结构：
   ```
   Recent advances in [领域] have shown... [cite recent works]. 
   Our method addresses these limitations by... 
   The emergence of [新趋势] highlights... [cite]. 
   Future work could incorporate [前沿方法]... [cite].
   ```

**关键**：前沿文献必须与论文方法有直接关联，不能堆砌无关引用。

### 2. 消融实验（Ablation Study）

**触发条件**：论文有多个组件（3D模型+梯度+眼裂处理+数据清洗），需要证明各组件贡献

**结构化格式**：
```latex
\section{Ablation Study: Component-wise Performance Analysis}

To systematically evaluate the contribution of each component, we conducted an ablation study.

\noindent\textbf{V1 (基础):} 仅使用核心方法
\noindent\textbf{V2 (+组件A):} 添加组件A
\noindent\textbf{V3 (+组件B):} 添加组件B
\noindent\textbf{V4 (完整):} 所有组件

The results are presented in Table~\ref{tab:ablation}.

\begin{table}[htbp]
\centering
\caption{Ablation study: Component-wise performance}
\label{tab:ablation}
\begin{tabular}{l|c}
\hline
\textbf{Variant} & \textbf{Dice} \\
\hline\hline
V1 & 0.9682 \\
V2 & 0.9745 \\
V3 & 0.9791 \\
V4 (Full) & \textbf{0.9834} \\
\hline
\end{tabular}
\end{table}

The ablation results demonstrate that each component contributes:
\begin{itemize}
\item[\textbf{--}] Component A improves Dice by +0.0063, confirming that...
\item[\textbf{--}] Component B improves Dice by +0.0046, validating...
\item[\textbf{--}] The cumulative improvement from V1 to V4 of +0.0152 demonstrates...
\end{itemize}
```

**关键**：
- 每个组件的增量必须为正（否则移除该组件）
- 分析部分必须解释每个增量的**原因**，不能只列数字
- 表格必须包含"完整方法"行，用`\textbf{}`强调

### 3. 统计显著性分析

**触发条件**：论文声称"显著优于"对比方法，但无统计检验

**完整模板**：
```latex
\section{Statistical Significance Analysis}

To rigorously assess statistical significance, we conducted paired statistical tests.

\noindent\textbf{Paired t-test:} For each image $i \in \{1, \ldots, N\}$, we computed Dice for both methods. The paired t-test assesses whether mean difference is significantly different from zero.

\noindent\textbf{Wilcoxon signed-rank test:} Non-parametric alternative, does not assume normal distribution.

\noindent\textbf{Confidence intervals:} 95\% CI using bootstrapping with 1,000 resamples.

The results are summarized in Table~\ref{tab:statistical_tests}.

\begin{table}[htbp]
\centering
\caption{Statistical Significance of Performance Improvements}
\label{tab:statistical_tests}
\begin{tabular}{l|c|c|c}
\hline
\textbf{Comparison} & \textbf{Mean Dice $\Delta$} & \textbf{95\% CI} & \textbf{p-value} \\
\hline\hline
Ours vs. Baseline & +0.0985 & [0.0972, 0.0998] & $< 10^{-15}$ \\
\hline
\end{tabular}
\end{table}

The effect size (Cohen's $d$) is $d = 3.18$ (large effect, $d > 0.8$ is large).
```

**关键**：
- p-value必须使用科学计数法（`< 10^{-15}` 而非 `< 0.0001`）
- 必须报告Cohen's d效应量
- 必须说明bootstrap resamples数量（1,000）

### 4. Data/Code Availability Statement

**触发条件**：论文有可公开访问的数据或代码

**标准格式**：
```latex
\section{Data and Code Availability}

The annotated iris dataset generated in this study is publicly available at: \url{https://www.kaggle.com/datasets/yakeworld126/openeds}.

The complete implementation pipeline—including all 7 processing steps, the Powell optimization algorithm, and 3D eyeball model construction—is available at: \url{https://github.com/yakeworld/training_pipeline}.

All computational code, configuration parameters, and intermediate results required to reproduce the experiments are provided as open-source artifacts. The training pipeline code is released under the MIT License.
```

**关键**：
- 必须包含具体URL（Kaggle、GitHub）
- 必须说明许可证（MIT）
- 必须列出可复现性所需的所有组件

### 5. 临床模型评估（筛查vs诊断模式）

**触发条件**：论文涉及临床疾病预测/分类模型，需要在模型评估中纳入临床场景考虑。

**标准流程**：
1. **明确使用场景**：确定是筛查（如糖尿病社区筛查）还是诊断（如症状患者的确认性检测）
2. **选择优先指标**：筛查→召回率（Recall），诊断→精确率（Precision）
3. **分析错误分布**：逐模型计算FN/FP，检查错误互补性
4. **阈值优化**：筛查场景默认0.5→降至0.35-0.48，诊断场景→升至0.50-0.65
5. **跨数据集验证**：不同数据特征需要不同最优模型

**关键输出**：
- 模型间FN/FP互补性分析表
- 各模型的FN抢救数/新增数
- 最优阈值及对应的FN/FP变化
- 跨数据集模型选择建议

**详细参考**：`references/clinical-model-evaluation.md`

## 技术注意事项

### LaTeX包依赖

在添加上述section前，必须确保导言区包含以下包：
```latex
\usepackage{url}      % 用于\url{}命令
\usepackage{booktabs} % 用于更好的表格（如果需要使用\toprule等）
```

### Patch操作陷阱

1. **重复`\appendix`问题**：如果论文已有`\appendix`，不要在patch中再次添加。使用`old_string`匹配完整段落。
2. **LaTeX特殊字符**：patch中的`\`必须转义为`\\`。使用`skill_manage(action='patch')`时，LaTeX命令会自动转义。
3. **引用验证**：添加的新引用必须在新section中实际使用（`\\cite{key}`），不能只添加到.bib文件。
4. **数值替换陷阱**：替换论文数值时，不能只改数字，必须同步更新相关文本叙述。例如将"F1从0.6878升至0.8140"改为新数值时，"+"符号和"升高"描述可能也需要改为"下降"或"崩溃"。

### 引用注释行陷阱

`%%`或`%`注释行中的`\\cite{key}`会被bibtex完全忽略，不会出现在`.bbl`中，导致D10a不增加。**修复方法**：搜索`%%.*\\cite`或`%.*\\cite`，将引用移至正文段落。

### 数值伪造修正时的叙事重构

当检测到论文数值伪造时，不能简单替换数字。需要重构叙事逻辑：

```
原始叙事: 泄露导致F1从0.6878升至0.8140 (+16.5%) — 证明泄露有害
新叙事:   严重泄露导致Recall崩溃至0.5030而Precision=1.0000 — 
          不是"膨胀"而是"选择性扭曲"，模型把所有样本判为正类
```

**关键**：
- 检查 Abstract 中的核心结论是否需要翻转
- 检查 Discussion 中的 Claim/Grounds/Warrant 是否一致
- 检查图表描述是否与修正后的数值匹配
- 检查 "Universal Metric Inflation" 等理论名称是否需要重命名

## 质量检查清单

在完成所有改进后，运行以下检查：

1. **编译检查**：`pdflatex paper.tex` 0 errors, 0 warnings
2. **引用健康**：D10a = 100%（所有bibitem都被正文引用）— 参见 D10a修复部分
3. **消融实验**：每个组件有正贡献，分析有原因解释
4. **统计检验**：p-value使用科学计数法，报告Cohen's d
5. **Data/Code声明**：URL可访问，许可证明确
6. **前沿文献**：2024-2026年文献至少3-5篇，与论文方法直接相关

## D10a 引用健康修复

当 D10a < 100% 时（部分或全部 bibitem 未被正文 `\cite{}` 引用）：

**纯散文变体（Pure Prose Variant）** — 0 个 `\cite{}` 命令，bibitem 已存在但从未在正文中出现：
- 映射每个 bibitem 到其在论文中上下文最合适的位置
- 相关域映射：AMD→引言，脉络膜→引言/讨论，测量方法→方法/引言，血流→引言/讨论，厚度测量→讨论
- 将相关 bibitem 分组到同一锚点（而非分散插入），保持可读性
- 具体操作见 `prose-cluster-hybrid-citation-fix` 技能的 `references/orphan-bibliography-trap.md`

**混合变体（Hybrid Variant）** — 散文 author-year 引用集中在 1-2 段落，其余 bibitem 无锚点：
- 将 prose 引用转为 `\cite{}` 格式
- 为剩余 bibitem 添加分组锚点
- 具体操作见 `prose-cluster-hybrid-citation-fix` 技能的主 SKILL.md

**部分引用变体（Partial Citation Variant）** — 部分 bibitem 已引用，部分未引用（孤儿引用）：
- 识别未引用 bibitem 的域上下文
- 在合适的句子中插入 `\cite{key}`（整合进句子语义，非机械追加）
- 编译两次验证
- 详见 `references/partial-citation-orphan-repair.md`（含完整步骤、映射表、真实案例）

### 验证修复

```bash
# 提取所有 bibitem key
grep -oP '\\\\bibitem\{[^}]+\}' paper.tex | sed 's/.*{//;s/}//' | sort > /tmp/bibitems.txt

# 提取所有 cite key
grep -oP '\\\\cite\{[^}]+\}' paper.tex | tr ',' '\n' | sed 's/.*{//;s/}//;s/^ *//' | sort -u > /tmp/cites.txt

# 计算 D10a
comm -12 /tmp/bibitems.txt /tmp/cites.txt | wc -l  # matched
echo "total: $(wc -l < /tmp/bibitems.txt)"
```

## 参考文件
- `references/cross-dataset-validation-pattern.md` — 跨数据集验证模式
- `references/ablation-study-template.md` — 消融实验模板
- **外部引用**：`quality-gate/references/ablation-leakage-implementation.md` — 数据泄漏消融实验的独立布尔开关实现模式（含PIMA案例）
- **外部引用**：`quality-gate/references/notebook-script-reconciliation-workflow.md` — 多源矛盾实验代码的统一工作流
- `references/statistical-significance-template.md` — 统计显著性模板
- `references/frontier-literature-extraction.md` — 前沿文献提取指南
- `references/partial-citation-orphan-repair.md` — 部分引用孤儿修复：D10a在50-95%时的标准化修复流程（含映射表、真实案例）
- `references/clinical-model-evaluation.md` — 临床模型评估模式：筛查vs诊断区分、FN/FP互补分析、阈值优化、跨数据集选择

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。
