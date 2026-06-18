# Multi-Domain Systematic Review — Structuring Pattern

> 当系统综述需要覆盖多个相关但独立的研究子域（如白内障AI的裂隙灯分级/眼底检测/手术识别/IOL计算/并发症预测）时，使用此结构模式平衡广度与深度。

## 适用场景

| 信号 | 示例 |
|:-----|:------|
| 综述覆盖 ≥3 个独立但关联的研究子域 | 白内障AI: 分级/手术/IOL算 |
| 每个子域有自己的文献库和方法论 | 手术视频识别(时序模型) vs 诊断分级(CNN) |
| 缺少一篇"全链条"综述 | 已有单域综述但无跨域整合 |

## 核心挑战

```
好综述             不好综述
─────────          ─────────
多维但不断裂        单域深度但忽略关联
整合有共性发现      各自独立成章
翻译障碍跨域一致    无统一分析框架
```

## 推荐章节结构

### Introduction — CARS模型 + 域位声明

**Move1 (建立领地)**:
- 全局疾病负担（如白内障是首要致盲原因）
- 通用临床流程（诊断→手术→随访）
- 声明本文覆盖"全临床链"而非单一环节

**Move2 (建立壁龛)**:
- 已有单域综述列举（Li2021分级, Luo2023手术, Ma2024 IOL）
- 缺乏综合分析的代价：翻译障碍被碎片化研究遗漏
- **域位声明模板**: "Individual domains have been reviewed in isolation, but a synthesis spanning the full care continuum — from diagnostic grading through surgical execution to postoperative outcome prediction — remains absent."

**Move3 (占据壁龛)**:
- 逐一列出各域覆盖（按临床链顺序）
- 统一分析框架声明（技术/临床/系统三层翻译障碍）

### Methods — 统一方法论 + 域特异子策略

方法学保持统一框架，但每个子域的搜索策略/纳排标准略有差异：

```
统一元素                  域特异元素
─────────                ─────────────
PRISMA 2020              各域独立搜索查询
双人提取+Cohen's κ       域特异质量评估工具
QUADAS-2 (诊断域)         QUADAS-2+CLAIM (诊断)
CONSORT-AI (手术域)       CLAIM + 数据集代表评估 (手术)
bivariate随机效应模型     特异池化 (DOR vs MAE vs IoU)
```

**LaTeX实现** — Methods节中分域列搜索策略：
```latex
\subsection{Search Strategy}
...统一方法论...

\subsubsection{Domain-specific Extensions}
\begin{description}
  \item[Domain 1: Slit-lamp grading] query1 + eligibility1
  \item[Domain 2: Fundus detection] query2 + eligibility2
  \item[Domain 3: Surgical phase] query3 + eligibility3
  ...
\end{description}
```

### Results — "漏斗式"逐域呈现

每域一个专用子节（subsection），遵循同一内结构：

```
\subsection{Domain N: [Name]}

第1段: 该域概况（N项研究, 主要架构类型, 时间跨度）
第2段: 关键量化发现（池化估计/范围, 标注CI和I²）
第3段: 亚组分析（按人群/设备/方法分组）
+ 专用提取表
+ 特异性图表（如手术域多阶段IoU精度表）
```

**最后一节**: 跨域比较 + 全局翻译障碍分析。

### Discussion — 三明治结构

| 层 | 内容 | 覆盖域 |
|:---|:-----|:-------|
| **沙漏上层(宽)** | 主要发现综合 — "共同模式是什么" | 所有域 |
| **沙漏中层(窄)** | 逐域深度分析 — 最强2-3域展开 | 重点域 |
| **沙漏下层(宽)** | 跨域翻译障碍 + 局限 + 推荐 | 所有域 |

**跨域比较表** — 放在Discussion最后部分：

```latex
\begin{table}[htbp]
\centering
\caption{Cross-domain comparison: maturation level of AI in cataract care}
\label{tab:cross-domain}
\begin{tabular}{lp{2cm}p{1.8cm}p{1.8cm}p{2cm}}
\toprule
\textbf{Domain} & \textbf{Maturity} & \textbf{External Val.} & \textbf{Prospective} & \textbf{Deployment} \\
\midrule
Slit-lamp grading  & ⭐⭐⭐⭐ & 12/24 (50\%) & 2/24 (8.3\%)  & ⭐⭐ \\
Fundus detection   & ⭐⭐⭐  & 5/9 (55.6\%)  & 1/9 (11.1\%)  & ⭐⭐ \\
Surgical phase     & ⭐⭐⭐⭐ & 6/17 (35.3\%) & 0/17 (0\%)    & ⭐ \\
IOL calculation    & ⭐⭐⭐  & 4/8 (50\%)    & 1/8 (12.5\%)  & ⭐⭐ \\
Post-op prediction & ⭐⭐   & 2/5 (40\%)    & 0/5 (0\%)     & ⭐ \\
\bottomrule
\end{tabular}
\end{table}
```

## 陷阱

1. **深度-广度失衡**: 5域每域3000字符 vs 3域每域5000字符 — 前者太浅后者太长
   - 平衡标准: 每个子域 ≥ 2段正文 + ≥ 1张专用表
   - ≥4域时用`subsubsection`而不是`subsection`压缩篇幅

2. **引用膨胀**: 多域综述的引用量容易失控
   - 控制: 每域10-15核心引用, 跨域共享5-10篇综述/方法文
   - 总目标: 50-70条, 非100+

3. **meta分析混杂**: 不同域的效应量指标不可混用(如DOR vs MAE vs IoU)
   - 每域独立meta分析, 最后一节用定性跨域比较

4. **Introduction Move2缺少过渡句**: 列举完单域综述后必须有一句"but none covers X-Y-Z linkage"才能自然过渡到本文贡献

5. **Discussion的"散装"感**: 多域综述最易写成"Domain1, Domain2, Domain3"的串行罗列
   - 修复: 在Discussion开头先写"\textbf{Common pattern across all domains:} X% of studies lack external validation"建立跨域共识
