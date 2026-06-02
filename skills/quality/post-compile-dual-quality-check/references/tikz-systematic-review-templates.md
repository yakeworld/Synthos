# TikZ 系统综述论文图模板

> 2026-05-25 实战验证：rvo-ai-screening 论文(v1→v2 avg 0.814→0.834)
> 编译环境: pdflatex + elsarticle + MikTeX
> 所有模板均已在该论文中通过 `pdflatex -interaction=nonstopmode -halt-on-error` 编译验证

## 导言区依赖

```latex
\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows, positioning, calc, fit, backgrounds, patterns}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
```

## 1. PRISMA 2020 流程图

用于系统综述的"系统筛选与纳入"可视化。替换文本描述的"PRISMA flow diagram is shown in Figure X"。

```latex
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[node distance=3mm and 5mm, box/.style={rectangle, draw, rounded corners=2mm, align=center, minimum width=6cm, minimum height=0.8cm, font=\small}, arrow/.style={-stealth, thick}]
% Level 1: records identified
\node[box, fill=blue!8] (ident) {Records identified through database search\\\small(n = 1,784)};
\node[box, right=of ident, fill=blue!8, minimum width=4.5cm] (pub) {PubMed: 412\\Embase: 387\\WoS: 403\\Scopus: 354\\IEEE: 228};

% Level 2: after duplicates
\node[box, below=1.2cm of ident, fill=orange!8] (dedup) {Records after duplicates removed\\\small(n = 1,408)};
\draw[arrow] (ident.south) -- (dedup.north);
\node[box, right=of dedup, fill=red!8, minimum width=3.5cm] (dups) {Duplicates removed\\\small(n = 376)};
\draw[arrow, dashed] (ident.east) -- (dups.west);

% Level 3: screening
\node[box, below=1.2cm of dedup, fill=yellow!8] (screen) {Records screened\\\small(n = 1,408)};
\draw[arrow] (dedup.south) -- (screen.north);
\node[box, right=of screen, fill=red!8, minimum width=3.5cm] (excl1) {Excluded at title/abstract\\\small(n = 1,102)};
\draw[arrow, dashed] (screen.east) -- (excl1.west);

% Level 4: full text
\node[box, below=1.2cm of screen, fill=yellow!8] (full) {Full-text articles assessed\\\small(n = 306)};
\draw[arrow] (screen.south) -- (full.north);
\node[box, right=of full, fill=red!8, minimum width=4.5cm] (excl2) {Excluded (n = 232)\\no control group: 68\\sample size <50: 52\\non-discriminative: 47\\not RVO-related: 39\\no full text: 26};
\draw[arrow, dashed] (full.east) -- (excl2.west);

% Level 5: included
\node[box, below=1.2cm of full, fill=green!12] (incl) {Studies included in systematic review\\\small(n = 74)};
\draw[arrow] (full.south) -- (incl.north);

\node[box, below=1.2cm of incl, fill=green!16] (meta) {Studies included in meta-analysis\\\small(n = 42)};
\draw[arrow] (incl.south) -- (meta.north);
\end{tikzpicture}
\caption{PRISMA 2020 flow diagram of study selection.}
\label{fig:prisma}
\end{figure}
```

**要点**:
- 用 `fill=blue!8/orange!8/yellow!8/red!8/green!12` 渐变颜色区分阶段
- 用 `\small` 在节点内缩小字体容纳排除数
- `\draw[arrow, dashed] (ident.east) -- (dups.west)` 用虚线指向排除框
- 排除框在右侧，筛选链在中轴

## 2. HSROC SROC 曲线（pgfplots）

用于系统综述荟萃分析的汇总ROC曲线可视化。替代文本声明的"HSROC model yielded pooled AUC"。

```latex
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[scale=0.85]
\begin{axis}[
    width=12cm, height=10cm,
    xlabel={1 $-$ Specificity (False Positive Rate)},
    ylabel={Sensitivity (True Positive Rate)},
    xmin=0, xmax=1,
    ymin=0, ymax=1,
    xtick={0,0.2,0.4,0.6,0.8,1},
    ytick={0,0.2,0.4,0.6,0.8,1},
    grid=both,
    grid style={gray!20},
    legend style={at={(0.03,0.03)},anchor=south west,font=\small},
    tick label style={font=\footnotesize},
    label style={font=\small},
]
% Diagonal reference line
\addplot[domain=0:1, dashed, gray!50, thick] {x};
\addlegendentry{No discrimination}

% HSROC curve — NOTE: use ln() NOT log() for natural log
\addplot[domain=0.01:0.99, smooth, thick, blue, samples=200] 
    {1 / (1 + exp(-(-ln(x/(1-x)) * 0.789 + 2.616)))};
\addlegendentry{HSROC curve}

% Pooled estimate
\addplot+[only marks, mark=square*, mark size=3pt, red] coordinates {(0.062,0.904)};
\addlegendentry{Pooled estimate}

% 95% confidence region (ellipse)
\draw[red, thick, dashed] (0.062,0.904) ellipse (0.028 and 0.027);

% Individual study points
\addplot+[only marks, mark=o, mark size=1.5pt, black!40] coordinates {
    (0.028,0.942) (0.034,0.958) (0.045,0.927) (0.018,0.963)
    (0.052,0.914) (0.071,0.896) (0.038,0.935) (0.089,0.881)
    (0.015,0.972) (0.042,0.928) (0.056,0.909) (0.092,0.874)
};
\addlegendentry{Individual studies}
\end{axis}
\end{tikzpicture}
\caption{Summary ROC curve with HSROC model fit. Blue: fitted curve. Red square: pooled estimate. Dashed ellipse: 95\% confidence region.}
\label{fig:sroc}
\end{figure}
```

**要点**:
- `ln(x/(1-x))` 用 `ln` 而非 `log`（pgfplots的`log`未定义）
- HSROC参数θ和Λ需要从数据中估计；示例中θ=2.616, Λ=0.789
- `(0.062,0.904)`是汇总敏感度+1-特异度坐标
- 置信椭圆用 `\draw[red, thick, dashed] (center x, center y) ellipse (semi_x, semi_y);`
- 散点数据点数量=纳入的研究/队列数，用从数据中提取的真实坐标

## 3. Deeks 漏斗图（pgfplots）

用于发表偏倚评估可视化。

```latex
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[scale=0.85]
\begin{axis}[
    width=12cm, height=9cm,
    xlabel={1/SE (Precision)},
    ylabel={Diagnostic Odds Ratio (ln scale)},
    xmin=0, xmax=35,
    ymin=1, ymax=8,
    ytick={1,2,3,4,5,6,7,8},
    yticklabels={2.72,7.39,20.09,54.60,148.41,403.43,1096.63,2980.96},
    grid=both,
    grid style={gray!20},
    legend style={at={(0.03,0.97)},anchor=north west,font=\small},
]
% Regression line
\addplot[domain=0:35, dashed, red, thick] {4.665 + 0.008*x};
\addlegendentry{Regression line (p=0.134)}

% Reference line at pooled DOR
\addplot[domain=0:35, dotted, gray, thick] {4.667};

% Individual study DOR vs precision
\addplot+[only marks, mark=o, mark size=2pt, blue] coordinates {
    (12.4,6.1) (8.7,5.8) (15.2,5.2) (6.3,4.9) (18.6,4.7)
    (10.1,5.5) (22.4,4.3) (4.8,5.9) (14.1,4.8) (9.3,5.1)
};
\addlegendentry{Individual studies}
\end{axis}
\end{tikzpicture}
\caption{Deeks' funnel plot asymmetry test. Each point: individual study.}
\label{fig:funnel}
\end{figure}
```

**要点**:
- 回归线斜率=0 → 无显著不对称
- y轴用ln DOR，刻度标签用指数形式显示原始值
- `\addplot[domain=0:35, dotted, gray, thick] {4.667};` 显示汇总ln DOR参考线

## 4. QUADAS-2 堆积柱状图（TikZ原生）

用于质量评估偏倚风险分布可视化。**注意坐标算术必须用`{...}`包裹**。

```latex
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[scale=0.85]
% Risk of Bias title
\node[anchor=west, font=\bfseries] at (0,3.2) {Risk of Bias};

% Data: each domain has Low/High/Unclear percentages (scale: 1% = 0.04cm)
% Patient Selection: Low=74.3%, High=16.2%, Unclear=9.5%
\fill[green!60!black!20] (0,2.8) rectangle ({74.3*0.04},2.2);
\fill[red!60!black!20] ({74.3*0.04},2.8) rectangle ({(74.3+16.2)*0.04},2.2);
\fill[yellow!60!black!20] ({(74.3+16.2)*0.04},2.8) rectangle (4.0,2.2);

% Index Test: Low=81.1%, High=9.5%, Unclear=9.4%
\fill[green!60!black!20] (0,2.0) rectangle ({81.1*0.04},1.4);
\fill[red!60!black!20] ({81.1*0.04},2.0) rectangle ({(81.1+9.5)*0.04},1.4);
\fill[yellow!60!black!20] ({(81.1+9.5)*0.04},2.0) rectangle (4.0,1.4);

% Labels
\node[anchor=east, font=\small] at (-0.2,2.5) {Patient Selection};
\node[anchor=east, font=\small] at (-0.2,1.7) {Index Test};

% Percentage labels — NOTE: avoid % in node content
\node[font=\tiny, right] at ({74.3*0.04+0.02},2.5) {74.3 percent};
\node[font=\tiny, right] at ({81.1*0.04+0.02},1.7) {81.1 percent};

% Legend
\node[rectangle, fill=green!60!black!20, minimum width=0.4cm, minimum height=0.4cm] at (1.2,-4.5) {};
\node[right, font=\small] at (1.7,-4.5) {Low Risk};
\node[rectangle, fill=yellow!60!black!20, minimum width=0.4cm, minimum height=0.4cm] at (4.0,-4.5) {};
\node[right, font=\small] at (4.5,-4.5) {Unclear};
\node[rectangle, fill=red!60!black!20, minimum width=0.4cm, minimum height=0.4cm] at (7.0,-4.5) {};
\node[right, font=\small] at (7.5,-4.5) {High Risk};
\end{tikzpicture}
\caption{QUADAS-2 quality assessment summary. Stacked bars showing proportions of low, unclear, and high risk of bias.}
\label{fig:quadas}
\end{figure}
```

**要点**:
- 坐标算术必须用 `{...}` 包裹：`({74.3*0.04}, y)` ✅ 而非 `(74.3*0.04, y)` ❌
- 多重运算用嵌套括号：`({(74.3+16.2)*0.04}, y)`
- 避免在节点文本中使用 `%` 符号；用"percent"替代
- 颜色命名用 `green!60!black!20` 而非 `green!60` 以保持视觉一致性
- y轴间距0.8cm，每个条高度0.6cm（留0.2cm间隙）

## 5. 三层架构框架图

用于理论框架/系统架构的可视化。

```latex
\begin{figure}[htbp]
\centering
\resizebox{\textwidth}{!}{%
\begin{tikzpicture}[
    node distance=0.8cm and 0.6cm,
    atom/.style={rectangle, draw, fill=blue!10, rounded corners=2mm, minimum width=1.8cm, minimum height=0.6cm, font=\small},
    layer/.style={rectangle, draw, fill=gray!5, dashed, rounded corners=3mm, inner sep=4mm},
]
% Layer 3 (top)
\node[layer, label={[above,font=\bfseries]Layer 3: Meta-Rules}] (L3) at (0,4.5) {};
\node[atom] (C1) at (-3.2,4.5) {Component A};
\node[atom] (C2) at (0,4.5) {Component B};
\node[atom] (C3) at (3.2,4.5) {Component C};

% Layer 2 (middle)
\node[layer, label={[above,font=\bfseries]Layer 2: Process}] (L2) at (0,2.5) {};
\node[atom] at (-2.0,2.5) {Step 1};
\node[atom] at (2.0,2.5) {Step 2};

% Layer 1 (bottom)
\node[layer, label={[above,font=\bfseries]Layer 1: Atoms}] (L1) at (0,0.5) {};
\node[atom] at (-2.5,0.5) {Atom A};
\node[atom] at (0,0.5) {Atom B};
\node[atom] at (2.5,0.5) {Atom C};

% Vertical arrows
\draw[<->, >=stealth, dashed, red!50] (L3.south) -- (L2.north);
\draw[<->, >=stealth, dashed, red!50] (L2.south) -- (L1.north);
\end{tikzpicture}}
\caption{Three-layer architecture.}
\label{fig:architecture}
\end{figure}
```

**要点**: 用 `\resizebox{\textwidth}{!}{% ... %}` 包裹；层间用dashed+red!50双向箭头。

## 验证流程

每次插入TikZ图后执行：

```bash
# 1. 验证反斜杠未被patch双转义
sed -n 'LINE_NUM p' paper.tex | od -c | head -1
# 应显示: \   b   e   g   i   n   {   f   i   g   u   r   e
# 非:     \   \   b   e   g   i   n   {

# 2. 单次编译
pdflatex -interaction=nonstopmode -halt-on-error paper.tex 2>&1 | tail -10

# 3. 第二次编译（跨引用）
pdflatex -interaction=nonstopmode -halt-on-error paper.tex 2>&1 | tail -5

# 4. 检查页数变化
grep 'Output written on paper.pdf' paper.log
```
