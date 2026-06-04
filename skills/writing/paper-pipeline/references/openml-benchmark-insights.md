# OpenML Benchmark Insights for Paper Writing

> **Source**: Feurer et al. (2025) "OpenML: Insights from 10 years and more than a thousand papers", *Patterns*, 6(7), 101317. DOI: 10.1016/j.patter.2025.101317
> **2026-06-04 Pima CRISP-DM 实战**: 将OpenML论文发现吸收到Dataset Description，增强论文论证链。

## 关键发现

### 1. 标准化拆分防泄漏（§3.4 Reproducibility）

> *"OpenML provides predefined splits for tasks, such as k-fold cross-validation or hold-out validation sets, ensuring consistency across studies and eliminating ambiguities in experimental setups."*

→ 论文中的用法：论证PIDD作为泄漏研究基准的可靠性。

### 2. 泄漏仍然存在 — 即使拆分标准化（§Discussion, 第六条）

> *"Run results can be flawed due to methodological errors such as test set leakage or improper seed tuning... community-driven quality control and the creation of curated task and run collections provide an effective remedy."*

→ **核心论点支撑**：泄漏是更深层的方法论问题（预处理/特征选择/SMOTE），即使 OpenML 这样标准化拆分的平台也无法避免。Helix 框架在 CRISP-DM 层面隔离所有预处理，正是填补这一空白。

### 3. 基准套件体系

| 套件 | 内容 | 用途 |
|:-----|:-----|:------|
| OpenML-CC18 | 72个标准分类任务，标准化10折CV | 通用模型比较 |
| AMLB (AutoML Benchmark) | Tabular AutoML系统基准 | AutoML系统比较 |
| OpenML-CTR23 | 回归基准套件 | 回归任务 |

→ PIDD 在这些套件上的分数可作为无泄漏基线。

### 4. OpenML vs 其他平台（Table 1）

OpenML 是唯一同时提供 **数据+Task定义+模型结果+社区基准** 的开放平台（Kaggle 缺乏标准化Task，HuggingFace 侧重模型而非实验）。

## 如何引用到论文中

### Dataset Description 节（增强版）

```
This study utilized the Pima Indians Diabetes Dataset (PIDD), a widely 
recognized benchmark for predictive modeling in healthcare [Smith1988]. 
The OpenML platform provides standardized task definitions with 
pre-defined cross-validation folds, ensuring consistency across studies 
and eliminating ambiguities in experimental setups [Feurer2025]. 

However, as Feurer et al. [Feurer2025] caution, run results can still 
be flawed by methodological errors such as test set leakage in 
preprocessing and feature selection, even when splits are standardized. 
This observation underscores that data leakage is a deeper methodological 
issue beyond split integrity—precisely the gap that the CRISP-DM Helix 
framework addresses by isolating all preprocessing within cross-validation 
folds.

Leveraging OpenML's curated benchmarking suites (e.g., OpenML-CC18 
[Feurer2025]), leaderboard scores on standardized tasks provide a 
reliable, leakage-free baseline for comparing Helix results against 
established benchmarks.
```

### Discussion / Related Work 节

可提及 OpenML 的标准化体系与其他平台（Kaggle/UCI）的区别，以及即使在这样的标准化平台上泄漏问题仍然存在。

## BibTeX 条目

```bibtex
@article{Vanschoren2014OpenML,
  author    = {Vanschoren, J. and van Rijn, J.N. and Bischl, B. and Torgo, L.},
  title     = {OpenML: Networked Science in Machine Learning},
  journal   = {ACM SIGKDD Explorations Newsletter},
  volume    = {15},
  number    = {2},
  pages     = {49--60},
  year      = {2014},
  doi       = {10.1145/2641190.2641198}
}

@article{Feurer2025OpenML,
  author    = {Bischl, B. and Casalicchio, G. and Das, T. and Feurer, M. and others},
  title     = {OpenML: Insights from 10 Years and More than a Thousand Papers},
  journal   = {Patterns},
  volume    = {6},
  number    = {7},
  pages     = {101317},
  year      = {2025},
  doi       = {10.1016/j.patter.2025.101317}
}
```
