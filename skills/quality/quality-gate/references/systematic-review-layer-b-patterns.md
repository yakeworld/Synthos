# Systematic Review: Layer B (Gemini) 常见弱项模式

> 从 vor-bppv-diagnosis(0.85 T1), kappa-vor-calibration(0.77→0.84 T2), kappa-bppv-nystagmus(0.83 T2) 三次 Layer B 评审归纳。

## 核心发现

Gemini Layer B 对系统综述的 **D4(完整性)** 和 **D7(引用质量)** 评审比 Layer A 更严格。这是跨论文一致的模式。

## D4 完整性：标准低于 0.80 时

| 现象 | 初审分 | 修复 | 预期提升 |
|:-----|:-----:|:------|:--------:|
| 无 PRISMA 2020 引用 | 0.75 | 在 Methods 中加 `\cite{page2021prisma}` | +0.05 |
| 缺 Study Selection 流程图(PRISMA Flow) | 0.75 | 加 TikZ PRISMA 2020 四阶段流程图 | +0.03 |
| 无 Supplementary Summary Table | 0.75 | 加核心纳入研究特征表 | +0.03 |
| 系统综述方法未标注 PRISMA 标准 | 0.75 | 在 Search Strategy 段明确 "遵循 PRISMA 2020" | +0.02 |

**Bibitem 模板**:
```
\bibitem{page2021prisma} M.J. Page, J.E. McKenzie, P.M. Bossuyt, et al.,
The PRISMA 2020 statement: an updated guideline for reporting systematic reviews,
\textit{BMJ} 372 (2021) n71.
```

## D7 引用质量：标准低于 0.80 时

| 现象 | 初审分 | 修复 | 预期提升 |
|:-----|:-----:|:------|:--------:|
| 部分 bibitem 未在正文引用 | 0.75 | 逐篇检查，适当位置插入 `\cite{}` | +0.05-0.10 |
| 未区分核心/非核心研究 | 0.75 | 文中首引时加 `*` 标记核心纳入研究 | +0.03 |
| 引用格式不一致 | 0.80 | 统一 bibitem 的 journal/volume/pages | +0.02 |
| 缺关键方法论文献(GUM/Moher等) | 0.80 | 补 PRISMA 声明、GUM 不确定度指南 | +0.03 |

## 快速修复流程

```bash
# 1. 查未引用 bibitems
grep -oP 'bibitem\{[^}]+\}' paper.tex | sed 's/bibitem{//;s/}//' | sort > /tmp/bibitems.txt
grep -oP 'cite\{[^}]+\}' paper.tex | grep -oP '\{[^}]+\}' | tr ',' '\n' | sed 's/{//;s/}//' | sort -u > /tmp/cited.txt
comm -23 /tmp/bibitems.txt /tmp/cited.txt  # 未引用的

# 2. 查 PRISMA 引用
grep -i 'prisma\|page2021' paper.tex

# 3. PRISMA 流程图 TikZ 模板
# 见 quality-gate/templates/tikz-prisma-flow.tex
```
