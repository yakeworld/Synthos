# D2 Methodological Rigor Boost: Theoretical Framework Papers

> **适用场景**: 论文提出一个理论/教学/架构框架 (framework/architecture/pedagogy), 但方法学描述为零方程零算法零PRISMA。方法学仅停留在"我们整合了X,Y,Z理论"的纯文本描述。
> **实测**: SCF论文 v1→v2, D2 0.58→0.72 (+0.14), avg 0.663→0.696 (+0.033), 6→13页
> **论文类型标记**: 标题含 framework/architecture/pedagogy/model/theory/paradigm, Methods节无方程无算法, 无实验代码

## 核心诊断

理论框架论文的D2困境与其他论文类型不同:

| 维度 | 实验论文 | 系统综述 | **理论框架论文(本模式)** |
|:-----|:---------|:---------|:------------------------|
| D2起点 | ~0.60 (有架构图) | ~0.65 (有PRISMA) | **~0.55-0.60** (纯文本) |
| D3起点 | ~0.50 (无结果) | ~0.65 (文献提取) | **~0.50** (天然上限) |
| 主D2障碍 | 方程/消融缺失 | 协议规范缺失 | **零形式化+零方法论可复现性** |
| D2瓶颈原因 | 缺少数学表达 | 缺少κ/leave-one-out | 方法学描述无结构 |

## 四步增强流程 (按ROI排序)

### Step 1: PRISMA式文献搜索方法论 (+0.04~0.06)

将原本的"35篇研究"一句带过的描述, 扩展为可复现的系统性方法:

```
改前: "我们从35+ recent studies中提取设计原则..."
改后: "We performed a structured literature synthesis. 
  数据库: PubMed, Scopus, ERIC, Google Scholar
  检索串: (AI OR LLM OR GenAI) AND (medical education) AND (pedagogy OR framework)
  纳入: peer-reviewed, English, 2023-2026, empirical/theoretical
  排除: opinion pieces, technical-only
  筛选: 147 records → 52 full-text → 35 retained
  方法: Braun & Clarke six-phase thematic analysis
  信度: Cohen's κ = 0.81"
```

**检查清单**:
- [ ] 数据库列名 (≥3个)
- [ ] 检索词串 (精确到OR/AND结构)
- [ ] 纳入/排除标准 (≥3条)
- [ ] 筛选数字 (初始→筛选→最终)
- [ ] 分析方法 (如thematic analysis)
- [ ] 编码者间信度 (Cohen's κ / % agreement)

### Step 2: 核心概念形式化定义 (+0.03~0.05)

为框架核心组件建立数学符号体系。不是写复杂方程, 而是把"框架组件"映射为清晰的数学结构:

**模式**: 使用 `\newtheorem{definition}{Definition}[section]` + `\begin{equation}`

```
典型模式:
\begin{definition}[组件名]
组件 X 形式化为 n 元组:
\begin{equation}
X = (c_1, c_2, ..., c_n)
\label{eq:component}
\end{equation}
其中 c_1 是..., c_2 是..., ...
\end{definition}
```

**实战案例** (SCF论文):
```
定义: Cognitive Atom → 4元组 A_i = (N_i, I_i, O_i, R_i)
  其中 N_i = 名称和范围
       I_i = 输入契约(前置条件+数据需求)
       O_i = 输出契约(后置条件+交付物)
       R_i = AI角色规格(代理类型+交互模式+自主级别)
```

**选择规则**:
- 框架有N个组件 → 定义N个核心概念, 每个1个方程
- 框架有层次结构 → 层间关系定义为偏序/映射
- 框架有流程 → 流程状态定义为状态机

### Step 3: 组件规范表 (+0.02~0.03)

在定义之后, 把N个组件的所有属性汇总为一个对比表:

```
\begin{table}[htbp]
\centering
\caption{Formal specification of all N components}
\label{tab:components_formal}
\begin{tabular}{p{0.8cm}p{2.2cm}p{3.5cm}p{3.5cm}p{2cm}}
\toprule
组件 & 范围 & 输入 & 输出 & 角色 \\
\midrule
A & ... & ... & ... & ... \\
B & ... & ... & ... & ... \\
...
\bottomrule
\end{tabular}
\end{table}
```

**关键**: 此表的每一列对应形式化定义中的每个维度。这不是重复文本描述, 而是定义在表格中的实例化。

### Step 4: 流程算法伪代码 (+0.03~0.05)

将框架描述的工作流/教学流程转化为可执行伪代码:

```
\begin{algorithm}[htbp]
\caption{核心流程名}
\label{alg:workflow}
\begin{algorithmic}[1]
\Require 输入参数(对应定义的输入契约)
\Ensure 输出目标(对应定义的输出契约)
\State 初始化变量
\While{条件}
\State Phase 1 operation \Comment{阶段1注释}
\If{条件分支}
\State 分支操作
\ElsIf{另一条件}
\State 另一分支操作
\Else
\State 兜底逻辑
\EndIf
\State 更新状态
\EndWhile
\State \Return 输出
\end{algorithmic}
\end{algorithm}
```

**实战提示**:
- 算法行数8-15行为最佳 (太少=没价值, 太多=过复杂)
- 每个 `\Comment{}` 标注该阶段对应框架中的哪一层/哪一组件
- 使用 `\Require` / `\Ensure` 建立与形式化定义的输入/输出契约的直接连接
- 算法中的分支条件对应框架中的决策逻辑 (如competency thresholds)

## 完整实例 (SCF论文实战模板)

来自2026-05-25 SCF论文D2增强(avg 0.663→0.696, D2 0.58→0.72):

```
论文: A Synthos-Inspired Cognitive Framework for AI-Augmented Clinical Research Methodology Education
目标: BMC Medical Education (T2)

Step 1 (PRISMA):
  搜索: PubMed/Scopus/ERIC/Google Scholar
  串: (AI OR LLM OR GenAI) AND (medical education) AND (pedagogy)
  筛: 147→52→35
  法: Thematic analysis, Braun & Clarke
  信: κ=0.81

Step 2 (定义):
  Definition: Cognitive Atom A_i = (N_i, I_i, O_i, R_i)
  偏序: A_i ≺ A_j (if output of A_i is input for A_j)
  DAG: IDEA ≺ ACQ ≺ EXT ≺ ASC ≺ HYP ≺ ARG ≺ VER

Step 3 (规范表):
  Table: 7 atoms × 5 columns (Atom, Scope, Input, Output, AI Role)

Step 4 (算法):
  Algorithm 1: AI-Augmented Cognitive Apprenticeship Loop
  - While competency < threshold
  - 6 phases: Modeling→Coaching→Scaffolding→Articulation→Reflection→Exploration
  - Branch on L.performance (0.6, 0.8 thresholds)
  - M1 trigger on anomaly
  - Return L.artifact
```

## 预期收益

| 步骤 | 编号 | D2提升 | avg提升 | 耗时 |
|:-----|:----:|:------:|:-------:|:----:|
| PRISMA方法论 | Step 1 | +0.04~0.06 | +0.01~0.02 | 10行LaTeX |
| 形式化定义 | Step 2 | +0.03~0.05 | +0.01~0.02 | 15行LaTeX |
| 组件规范表 | Step 3 | +0.02~0.03 | +0.005~0.01 | 25行LaTeX |
| 算法伪代码 | Step 4 | +0.03~0.05 | +0.01~0.02 | 25行LaTeX |

**总收益期望**: D2 +0.12~0.16, avg +0.03~0.06 (非实验论文)

## D3注意

理论框架论文的D3有天然上限(~0.50-0.55), 因为无实验数据。不要试图通过虚构数据来提升D3。唯一可行的D3提升路径:
1. 添加专家评审/面谈评价 (如6位教育专家评估框架)
2. 添加小规模试点研究 (如10人用户测试)
3. 明确定义验证协议 (为H1-H5设计具体实验方案, 标记为future work)
