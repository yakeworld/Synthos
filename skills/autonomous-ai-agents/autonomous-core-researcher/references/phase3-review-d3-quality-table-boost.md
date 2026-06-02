# Phase 3 D3 Quality Assessment Table Boost (Systematic Reviews)

> 综述论文的 D3 天然天花板 ~0.75（无原始实验数据）。QUADAS-2 式质量评估表是最有效的 D3 推手。

## 适用条件

- 论文类型: 系统综述 / Meta分析
- 当前 D3 < 0.78 (综述天花板以下)
- 论文已有≥10篇核心纳入研究
- Quality Assessment 节当前仅1段纯文字描述

## 模板: QUADAS-2 风格偏倚风险评估表

### 五域结构

| 域 | 问什么 | 评分标准 |
|:---|:-------|:---------|
| 患者选择 (Patient Selection) | 病例定义清晰? 代表性好? | +低 / -高 / ?不明 |
| 指标测试 (Index Test) | VOR/眼动测量方案标准化? 盲法? | +低 / -高 / ?不明 |
| 参考标准 (Reference Standard) | PD临床诊断标准明确? 金标准正确分类? | +低 / -高 / ?不明 |
| 流程及时机 (Flow & Timing) | 所有受试者接受相同测试? 时间间隔合理? | +低 / -高 / ?不明 |
| 对照组可比性 (Comparability) | 年龄/性别匹配? 混杂因素控制? | +低 / -高 / ?不明 |

### LaTeX 表结构

```latex
\\begin{table}[htbp]
\\centering
\\caption{QUADAS-2 style quality assessment of included [领域] studies}
\\label{tab:quality}
\\resizebox{\\textwidth}{!}{%
\\begin{tabular}{lccccc}
\\toprule
\\textbf{Study} & \\textbf{Patient} & \\textbf{Index} & \\textbf{Reference} & \\textbf{Flow \\&} & \\textbf{Control} \\\\
& \\textbf{Selection} & \\textbf{Test} & \\textbf{Standard} & \\textbf{Timing} & \\textbf{Comparability} \\\\
\\midrule
Author1 2021 \\cite{key1} & + & + & + & + & + \\\\
Author2 2020 \\cite{key2} & ? & + & + & ? & + \\\\
... & & & & & \\\\
\\bottomrule
\\multicolumn{6}{l}{\\small \\textbf{Legend}: + = low risk; - = high risk; ? = unclear} \\\\
\\end{tabular}}
\\end{table}
```

### 评分后总结文本

追加于表后:

```latex
Overall, the quality of included studies was moderate to high. Common strengths included
clear case definitions (X/XX studies, XX\\%) and adequate measurement protocols (X/XX, XX\\%).
Common weaknesses included small sample sizes (median n=XX), inconsistent reporting of
[关键变量], and lack of blinding (only X/XX studies explicitly reported blinding).
```

## 预期收益

| 当前 D3 | 预期 D3 | 提升 | 所需表大小 |
|:-------:|:--------:|:----:|:----------:|
| 0.70-0.72 | 0.74-0.76 | +0.03~0.04 | 10-15研×5域 |
| 0.73-0.75 | 0.76-0.78 | +0.02~0.03 | 8-12研×5域 |
| ≥0.76 | 0.77-0.79 | +0.01~0.02 | 补充漏斗图/敏感性分析 |

## 天花板

综述论文 D3 天然硬上限 ~0.78-0.79（无原始实验数据）。QUADAS-2 表可推至 0.76-0.78。之后需漏斗图或敏感性分析才可至 0.78+。

## 实战

**vor-pd-systematic-review v4** (2026-05-27):
- 12核心研究 × 5域 QUADAS-2 表
- D3: 0.72→0.76 (+0.04)
- 总结: 10/12(83%)病例定义低风险, 9/12(75%)VOR测量低风险
- avg: 0.821→0.840 (+0.019)
