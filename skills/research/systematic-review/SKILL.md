---
name: systematic-review
description: 系统综述与Meta分析工作流助手 — PRISMA流程、搜索策略设计、研究选择、质量评估、数据提取和综合支持。
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
    signature: 'topic: str -> review_plan: dict'
---

# Systematic Review Workflow

## 核心流程

```
1. 研究问题 формулировка (PICO/COARSE框架)
  ↓
2. 搜索策略 (PubMed/Scopus/Web of Science)
  ↓
3. 文献筛选 (标题→摘要→全文, PRISMA)
  ↓
4. 质量评估 (QUADAS-2 / ROBIS / Cochrane)
  ↓
5. 数据提取 (结构化表格)
  ↓
6. 综合分析 (Meta分析/叙述性综合)
  ↓
7. 报告 (PRISMA 2020 Checklist)
```

## PICO框架

| 要素 | 说明 | 示例 |
|:-----|:-----|:------|
| P (Population) | 目标人群 | PD患者 |
| I (Intervention) | 诊断/干预 | 3D眼动追踪 |
| C (Comparison) | 对照 | 传统量表 |
| O (Outcome) | 结局指标 | 诊断准确性 |

## PRISMA流程图 (TikZ)

```latex
\begin{figure}[htbp]
\centering
\resizebox{\textwidth}{!}{%
\begin{tikzpicture}[box/.style={rectangle, draw, rounded corners, minimum width=4cm, minimum height=0.8cm, font=\small, align=center}]
% Level 1: Identification
\node[box] (id) at (0,0) {Records identified\\through database searching};
\node[box, right=of id] (other) {Additional records\\from other sources};
% Level 2-4 similar structure
\end{tikzpicture}}
\caption{PRISMA 2020 flow diagram}
\end{figure}
```

详见 `references/prisma-template.tex`。

## 质量评估工具

| 研究类型 | 推荐工具 |
|:---------|:---------|
| 诊断准确性 | QUADAS-2 |
| RCT | Cochrane RoB 2 |
| 观察性研究 | ROBINS-I |
| 系统综述 | AMSTAR 2 |

## 参考文件

- `references/prisma-template.tex` — PRISMA流程图TikZ模板
- `references/search-strategy-template.md` — 搜索策略模板
- `references/data-extraction-form.md` — 数据提取表
- `references/meta-analysis-guide.md` — Meta分析指南
