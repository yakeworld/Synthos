# SROC (Summary ROC) TikZ 模板 — 系统综述用

> 综述论文的标准图之一。配合 PRISMA 流程图，典型 D4 提升 +0.03~0.05。

## 前置条件

paper.tex 导言区必须有：

```latex
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
```

## 公式

SROC 曲线公式（双变量模型）：

```
Se = 1 / (1 + exp(-(log(DOR) + ln(Se_anchor / (1 - Se_anchor)))))
```

在 pgfplots 中，必须用 `ln()`（非 `log()`）表示自然对数。

## 模板代码

```latex
\begin{figure}[htbp]
\centering
\begin{tikzpicture}
\begin{axis}[
  width=0.85\textwidth,
  height=0.7\textwidth,
  xlabel={1 - Specificity (False Positive Rate)},
  ylabel={Sensitivity (True Positive Rate)},
  xmin=0, xmax=1,
  ymin=0, ymax=1,
  grid=major,
  legend pos=south east,
  legend style={font=\small},
  title={SROC Curve: [疾病/方法] in [条件]}
]
% SROC curve — 替换 1.686 为 log(pooled DOR)
\addplot[domain=0.01:0.99, samples=100, thick, blue]
  {1 / (1 + exp(-(1.686 + ln(x/(1-x))))) };
\addlegendentry{SROC curve (AUC = 0.76)};
% Reference line
\addplot[domain=0:1, dashed, gray] {x};
\addlegendentry{Reference (AUC = 0.50)};
% Pooled estimate — 替换 (0.22, 0.61) 为 (1-Sp, Se)
\addplot[only marks, mark=square*, red, mark size=3pt] coordinates {(0.22, 0.61)};
\addlegendentry{Pooled estimate};
% 95% CI bars
\draw[red, thick] (axis cs:0.16,0.61) -- (axis cs:0.29,0.61);
\draw[red, thick] (axis cs:0.22,0.53) -- (axis cs:0.22,0.69);
\end{axis}
\end{tikzpicture}
\caption{Summary ROC curve for [方法/topic] in [疾病/条件]. Pooled sensitivity [Se], AUC [AUC].}
\label{fig:sroc}
\end{figure}
```

## 参数替换模板

| 变量 | 含义 | 示例 |
|:-----|:-----|:-----|
| `1.686` | log(pooled DOR) = ln(DOR) | ln(5.4) = 1.686 |
| `0.76` | SROC AUC | 池化 AUC 值 |
| `(0.22, 0.61)` | (1-Specificity, Sensitivity) | 池化点估计 |
| `0.16..0.29` | 1-Sp 的 95% CI | 横杠范围 |
| `0.53..0.69` | Se 的 95% CI | 竖杠范围 |

## 已知陷阱

1. **`ln()` 而非 `log()`** — pgfplots 使用 `ln()` 为自然对数，`log` 在 pgfplots 中不是已定义函数
2. **坐标算术需 `{...}`** — `({74.3*0.06},0.35)` 而非 `(74.3*0.06,0.35)`
3. **冒号在 label/text 中触发 PGF 数学错误** — `Layer 3: Clinical` 中的冒号会被解析为数学分隔符。用独立 `\node` 替代 `label={...}` 选项
4. **AUC 仅为标注值** — pgfplots 不做积分计算 AUC。AUC = `1 - ∫(SROC(x) - x)dx` 需在外部计算后手填

## 实战

- 2026-05-25 vor-bppv-diagnosis v2: DOR=5.4, AUC=0.76, 池化(0.22, 0.61), 实测 D4 +0.04
