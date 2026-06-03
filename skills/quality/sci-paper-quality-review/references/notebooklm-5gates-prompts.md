# NotebookLM 5门质量系统 — 完整 Prompt 模板

> 每个门 = NotebookLM Q&A 提问 → 评分 → 补救 → 重新评估
> 实战验证于 PIMA CRISP-DM (avg 0.93→0.945) 和 Iris_YOLO (avg 0.89)

---

## 门1: 文献检索质量 (Q1)

### 提问模板

```
请评估论文 '[title]' 的文献检索质量(门1)：

1. 覆盖度(0-1): 是否覆盖了该领域的所有主流方法流派？有无明显遗漏？
2. 时效性(0-1): 是否覆盖了近5年的关键进展？
3. 精准度(0-1): 引用的文献与论文主题的相关度如何？
4. 权威性(0-1): 是否包含了高影响力期刊/会议的文献？

给出每维评分(0-1)。

**【必答】对于评分<0.85的维度，请逐一给出具体的补救方案：**
- 缺失了哪些具体的文献/流派/系统？列出论文标题或DOI
- 应该用什么检索词在哪个数据库(PubMed/Semantic Scholar/OpenAlex)搜索？
- 检索的时间范围和过滤条件建议是什么？
```

### 判定标准

| 维度 | PASS | 补救信号 |
|:-----|:----:|:---------|
| 覆盖度 | ≥0.80 | 缺流派/系统 → 补检索词 |
| 时效性 | ≥0.80 | 缺近3年文献 → 限时重搜 |
| 精准度 | ≥0.70 | 引用跑题 → 换检索词 |
| 权威性 | ≥0.70 | GitHub引用过多/缺顶刊 → 换同行评审文献 |

### PIMA 实战结果

| 维度 | 首评 | 补救后 | 补救动作 |
|:-----|:----:|:------:|:---------|
| 覆盖度 | 0.80 | 0.95 | 补MIMIC-IV/联邦学习文献 |
| 权威性 | 0.80 | 1.00 | 补TRIPOD+AI/PROBAST+AI (BMJ) |

---

## 门2: 研究空白质量 (Q2)

### 提问模板

```
请按CARS模型评估论文的研究空白(Gap)质量(门2)：

1. 真实性(0-1): 这个Gap是真实存在的，还是人为制造的？至少有几个独立来源交叉确认？
2. 非平凡性(0-1): '没人做过'和'有理由必须做'之间的差距有多大？
3. 可填补性(0-1): 如果填补这个Gap，能解决什么具体问题？带来什么能力？
4. 连续性(0-1): Gap是否从文献综述(Related Work)自然过渡而来？有无断裂？

请评估当前Gap陈述的质量，提供改进建议。

**【必答】如果任何维度评分<0.8，请给出具体的补救方案：**
- Gap真实性不足：需要哪些额外的交叉来源来验证Gap？
- 非平凡性不足：如何重新定位Gap，使其从'没人做过'升级为'有理由必须做'？
- 连续性断裂：应该在Related Work的哪一段补充什么过渡句？请给出具体LaTeX代码
```

### 典型补救：过渡段 LaTeX 代码

当连续性不足时，在 Introduction 的 Related Work 末尾插入：

```latex
\subsection{The Disconnect Between Governance and Execution}

Recent initiatives by the medical informatics community have sought to curb this
reproducibility crisis through rigorous reporting and appraisal guidelines, most
notably TRIPOD+AI~\cite{collins2024tripod} and PROBAST+AI~\cite{wolff2025probast}.
While these frameworks provide indispensable \textit{post-hoc} evaluation checklists
for identifying risk of bias, they fundamentally operate at the macroscopic
governance level. They instruct clinicians and reviewers on \textit{what}
vulnerabilities to audit, but offer no computational protocols for data scientists
on \textit{how} to inherently prevent these biases during the coding and pipeline
formulation phases.

This creates a critical methodological vacuum: the disconnect between high-level
clinical governance and low-level engineering execution---a ``Governance-Execution
Gap.'' Without an executable, \textit{a priori} framework that forces strict
code-level compliance with these guidelines, predictive models will continue to
inadvertently leak data and fail retrospective PROBAST+AI audits.
```

---

## 门3: 科学假设质量 (Q3)

### 提问模板

```
请按图尔敏模型评估论文的科学假设质量(门3)：

1. 可证伪性(0-1): 核心假设有明确的淘汰标准吗？Λ≤0是否已作为数学不等式写入？
2. 具体性(0-1): 是否符合'If X then Y'形式？X和Y可测量吗？
3. 唯一性(0-1): 是否明确列出了业界默认的错误常识作为H₂替代假设？
4. 与Gap的对齐(0-1): 假设是否直接响应Gap？

给出每维评分(0-1)。

**【必答】如果任何维度评分<0.8，请给出具体的补救方案：**
- 可证伪性不足：淘汰标准应如何用Λ≤0的数学不等式形式化？请给出LaTeX代码
- 具体性不足：H₁和H₂应该如何改写为更精确的'If X then Y'形式？
- 无替代假设：H₂(Naive Oversampling Assumption)应该怎么写？
```

### 典型补救：假设段 LaTeX 代码

```latex
\subsubsection{Scientific Hypotheses and Falsification Criteria}

\textbf{Primary Hypothesis ($H_1$): The Recall Paradox \& Helix Efficacy.}
We hypothesize that the absence of hard-coded execution constraints (e.g.,
applying global SMOTE prior to cross-validation) generates a ``Recall Paradox,''
where aggregate metrics inflate while clinical sensitivity degrades.

\textbf{Alternative Hypothesis ($H_2$): The Naive Oversampling Assumption.}
Conventional wisdom operates under $H_2$: the assumption that global synthetic
oversampling uniformly benefits minority class detection.

\textbf{Formal Falsification Criteria.}
$H_1$ will be rejected if either:
\begin{equation}
    \Lambda \le 0
\end{equation}
\begin{equation}
    \text{Recall}_{\text{global}} \ge \text{Recall}_{\text{isolated}} + \delta
\end{equation}
where $\delta > 0$ is a clinically meaningful margin.
```

---

## 门4: 技术方案质量 (Q4)

### 提问模板

```
请评估论文的技术方案质量(门4)：

1. 可行性(0-1): 方案是否可在现有资源条件下实现？
2. 对齐度(0-1): 方案是否直接响应H₁/H₂假设？
3. 完整性(0-1): 数据→预处理→模型→评估→部署是否完整？
4. 可复现性(0-1): 各步骤是否详细到可复现？Algorithm有Nested CV吗？

给出每维评分(0-1)。

**【必答】如果任何维度评分<0.8，请给出具体的补救方案：**
- 可复现性不足：Algorithm 1应如何补充Nested CV？给出完整替换LaTeX代码
- 完整性缺失：缺什么环节？给出补充的LaTeX代码
```

---

## 门5: 论文质量 (Q5)

### 提问模板 — 标准7维评审

```
请对论文进行全面7维SCI质量评审：

1. 科学贡献(Scientific Contribution)
2. 方法学严谨性(Methodological Rigor)
3. 结果可信度(Results Credibility)
4. 完整性(Completeness) — IMRaD、表格、图表、合规声明
5. 清晰性(Clarity) — CARS Introduction、图尔敏Discussion
6. 新颖性(Novelty)
7. 引用质量(Citation Quality)

每维评分(0-1)和具体的改进建议。

**【必答】如果任何维度评分<0.90，请给出具体的补救方案和LaTeX代码**
```

### 典型补救：TRIPOD+AI合规声明

```latex
\subsection{Reporting Guidelines and Reproducibility}
The conduct and reporting of this study strictly adhere to the TRIPOD+AI
statement~\cite{collins2024tripod}. All predictive workflows---including the
execution of Algorithm~\ref{alg:isolation} with Nested CV---were documented to
align with the PROBAST+AI~\cite{wolff2025probast} mandates for mitigating
analysis domain bias. The complete Python codebase is accessible at
\url{https://www.kaggle.com/code/yakeworld126/crisp-dm-pima}.
```

---

## 全流程批量提问（回顾一次性评估）

当需要快速回顾时，单次提问覆盖全部5门：

```
请对这篇论文进行全流程质量评估，涵盖5个门：

门1: 文献检索质量 — 覆盖度、时效性、精准度、权威性
门2: 研究空白质量 — 真实性、非平凡性、可填补性、连续性(CARS)
门3: 科学假设质量 — 可证伪性、具体性、唯一性、与Gap对齐(图尔敏)
门4: 技术方案质量 — 可行性、对齐度、完整性、可复现性
门5: 论文质量 — 标准的7维SCI评审

每个门给出评分(0-1)和补救方案。
**【必答】对评分<0.85的维度给出具体补救方案和LaTeX代码**
```
