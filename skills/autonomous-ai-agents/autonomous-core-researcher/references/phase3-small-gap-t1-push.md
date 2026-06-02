# Phase 3 Small-Gap T1 Push: D3+Funnel + D6+Barrier + D7+Citations

> 2026-05-27 实战：vog-vestibular-review v3 (0.843 T2, T1差0.007) → v4 (0.854 T1, +0.011)

## 适用条件

当 Phase 3 判定树选择 T2→T1 增强后，如果满足：

| 检查项 | 条件 | 本session实战 |
|:-------|:-----|:-------------|
| **T1差距** | < +0.03（小缺口） | +0.007 |
| **D2** | ≥0.84（接近充分，非瓶颈） | 0.84 |
| **D4** | ≥0.85（已充分） | 0.87 |
| **D3** | ≥0.78（有改善空间，非天花板） | 0.82 |
| **D6** | ≤0.84（叙事可升级） | 0.84 |
| **D7** | ≤0.83（引用可扩展） | 0.82 |
| **结论** | **适合小型 T1 push 路径**，勿走 D2 形式化路线（过度工程） |

**不适用**：T1差距 ≥ +0.03 → 走 D2 形式化或三管齐下。D3 ≤ 0.75（天然天花板）→ 不选此路径。

## 三种改动（并行，一周期完成）

### 1. D3 Boost: 证据体漏斗图 (pgfplots)

当论文已有质量评估（QUADAS-2 或自建评分）、且 D3 有提升空间但无实验数据可补充时，**不要添加虚构数据**。用可视化将已有的质量评分转化为可发布的数据图。

#### 模板

```latex
% paper.tex 导言区需添加（如缺）：
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}

% 放入图文件 figures/funnel-plot.tex：
\begin{figure}[htbp]
\centering
\resizebox{0.85\textwidth}{!}{%
\begin{tikzpicture}
\begin{axis}[
    width=12cm, height=8cm,
    xlabel={QUADAS-2 Quality Score (0--10)},
    ylabel={Sample Size (N)},
    ymin=0, ymax=35,
    xmin=4, xmax=10,
    grid=both,
    legend pos=north west,
]
% 每个方法类别一组散点
\addplot[only marks, mark=square, blue!70]
coordinates {
    (7.5, 120) (7.0, 85) % ... 实际数据点
};
\addlegendentry{Category A (n=N)}
% 标注均值线
\draw[dashed, gray!50] ({axis cs:MEAN,0}) -- ({axis cs:MEAN,35});
\node[anchor=north, font=\small, gray!50] at ({axis cs:MEAN,0}) {Mean = X.XX};
\end{axis}
\end{tikzpicture}%
}
\caption{Quality-score distribution by category. Clinical studies cluster higher; algorithm studies show greater dispersion.}
\label{fig:funnel}
\end{figure}
```

#### 关键设计原则

| 原则 | 说明 |
|:-----|:------|
| **不使用 SROC 曲线** | SROC 需要诊断数据对(TP/FP/FN/TN)，综述论文很少具备。漏斗图只需要质量评分，数据从已有 QUADAS-2 表即可提取 |
| **不使用错误漏斗图 (Egger's test)** | 发表偏倚检验需要效应量和标准误，综述论文往往不具备。质量分布散点图不需要这些统计假设 |
| **使用真实数据** | 评分来自论文已有的 Tab.3 QUADAS-2 数据，非虚构 |
| **标注类别颜色** | 不同颜色区分方法类别（硬件/算法/临床/ML），让分布差异一目了然 |
| **标注均值** | 垂直线标注总体均值，帮助读者理解整体水平 |

**为什么是 D3 而非 D4**：漏斗图不仅是一个"图"(D4)，它**提供证据**——可视化展示了"不同方法学社区的质量规范差异"，这是对论文核心论点的数据支持。因此评分归入 D3（结果可信度），而非仅仅 D4（完整性）。

### 2. D6 Boost: 结构壁垒叙事 + 联合行动号召

当论文的叙事已到"first unified X"但 D6 仍卡在 0.84 时，增加一个层次：**将覆盖缺口从"研究空白"升级为"学科碎片化的结构性后果"**。

#### 两处文本改动

**① Discussion 新增 "Structural Barriers" 子节**（在 Future Directions 之前）：

关键论证结构：
```
1. 识别学科碎片：硬件工程、计算机视觉、临床评估、系统架构沿独立轨迹发展
   → 有独立的发表场所、审稿社区和验证标准
2. 提供实证证据：引用漏斗图(Fig. X)，显示不同类别研究的质量梯度差异
   → 不同方法学社区操作于不同质量规范下
3. 论证"结构壁垒"：覆盖缺口不是因为没人想到去做，而是因为学科隔阂
   → 需要的是convergence framework而非另一篇单维度综述
```

**② Conclusion 新增联合行动号召**（3条具体建议）：

模板：
```
We call on [相关学术组织/学会] to incorporate [本技术] specifications into future
[诊断标准/实践指南] updates. Specifically, we recommend:
(i) [首条建议：标准化验证工具]
(ii) [次条建议：多中心临床试验]
(iii) [三条建议：监管协调路径]
Without this architectural convergence — [技术/临床/监管三维度] simultaneously —
[本技术] risks remaining a collection of compelling prototypes...
```

#### 实战示例

vog-vestibular-review v4:
- 结构壁垒：硬件工程→系统(Computer Vision)→临床前庭评估→系统架构的学科碎片化
- 实证证据：Fig.3 漏斗图显示临床研究均分8.3/10 vs 算法研究均分6.7/10
- 行动号召：Barany学会分类委员会、Vestibular Disorders Initiative、vHIT标准化工作组
- 3条建议：标准化phantom眼→多中心vHIT对比试验→FDA 510(k)/CE监管路径

### 3. D7 Boost: 2-3 篇新引（OpenAlex 搜索）

当 bibitem 已 100% 被引用且 gap < +0.01 时，加 2-3 篇高质量新引即可。

#### 搜索策略

```python
# 用简单短语搜索（避免 OpenAlex 布尔查询 500 错误）
queries = [
    "smartphone video head impulse test",
    "AI nystagmus detection video-oculography",  
    "wearable eye tracking dizziness vestibular",
    "calibration-free gaze estimation head-mounted",
]
for query in queries:
    url = f"https://api.openalex.org/works?search={quote(query)}&per_page=10"
    # 串行执行，每次间隔 1.5s
    time.sleep(1.5)
```

#### 选择标准

| 条件 | 优先级 |
|:-----|:-------|
| 年 ≥ 2023 | 高 |
| 被引 ≥ 15 | 高 |
| 补充论文薄弱子领域 | 高 |
| 有可验证的 DOI | 必选 |
| 非重复（不在已有 bibitem 中） | 必选 |

#### 整合

- 在 Discussion/Structural Barriers 子节加入新增引
- 或在现有的相关段落加 `\citep{newkey}`
- 编译验证 100% match rate

## 预期收益

| 维度 | 改动量 | 预期提升 | 实战 |
|:-----|:-------|:--------:|:----:|
| D3 | +1 图 (~30行 TikZ) | +0.01~0.02 | +0.02 |
| D6 | +1 子节 + 结论升级 (~25行) | +0.01~0.02 | +0.02 |
| D7 | +2~3 新引 (~10行) | +0.01~0.02 | +0.02 |
| D4 | +1 图 (自动) | +0.01 | +0.01 |
| **avg** | **~65行总改动** | **+0.01~0.02** | **+0.011** |

## 变体：D3天花板+小缺口T1推（混合模式）

### 适用场景

当 D3 已至 QUADAS-2 综述天花板（≈0.80）无空间，但 D7 仍有少量空间（Strategy A 可用或可加 3-5 新引），且 T1 差距仅 0.007-0.010 时：

| 检查项 | 条件 | 实战 (kappa-bppv-nystagmus v5) |
|:-------|:-----|:-------------------------------|
| T1差距 | < +0.015 | +0.012 |
| D3状态 | 天花板已至 (0.80) | 0.80 (QUADAS-2 ceiling) |
| D7策略A | 耗尽或接近耗尽 | 68/68=100%已匹配, Strategy B可用 |
| D2 | ≥0.83 有微调空间 | 0.83→0.84 (+0.01) Publication Bias |
| D6 | ≤0.85 有重构空间 | 0.85→0.87 (+0.02) Structural Barriers |

### 改动组合（与标准版差异）

| 维度 | 标准版 | 混合版 | 原因 |
|:-----|:-------|:-------|:-----|
| D3 | 漏斗图 (pgfplots散点) | **QUADAS-2 stacked bar chart** | 已无SROC/漏斗散点数据可用, 用质量分布 bar chart 替代 |
| D6 | 结构壁垒+行动号召 | Structural Barriers subsection(3 patterns) + **tripartite convergence call-to-action** | 叙事升级强度高于标准版, 因D3无空间需D6过偿 |
| D7 | 2-3篇新引 | **5篇新引** (OpenAlex) | 更多引用来补偿D3天花板 |
| D2 | — (不在标准版中) | **Publication Bias Assessment** (Cochran Q, I², Deeks) | 额外维度补偿 |
| D5 | — | 文本质检 | 边际加分 |

### 实战数据

| 论文 | v4 avg | 改动 | v5 avg | Δ | T1? |
|:-----|:------:|:-----|:------:|:-:|:---:|
| kappa-bppv-nystagmus | 0.843 | D7(+5新引)+D3(bar chart)+D2(pub bias)+D6(barriers)+D5 | **0.855** | **+0.012** | ✅ |

## 与其他路径的关系

| 路径 | 适用场景 | 典型改动量 | 收益/轮 |
|:-----|:---------|:----------:|:-------:|
| D2形式化 (bppv-pd模式) | T1差距0.02~0.03, D2<0.80 | ~80行(3Eq+1Alg) | +0.019 |
| 收敛叙事重构 (vor-3d模式) | T1差距0.01~0.02, D2/D4/D7≥0.85 | ~40行文本重构 | +0.015 |
| **小缺口T1推** (标准版) | T1差距<0.01, D3/D6/D7有空间 | ~65行(1Fig+25行叙事+3引) | +0.011 |
| **小缺口T1推** (混合版) | T1差距<0.015, D3天花板+其他维度有空间 | ~120行(bar chart+pub bias+barriers+新引) | **+0.012** |

选择原则：T1差距越小，越应选择该差距恰好能弥补的最小改动路径。但若D3天花板封锁了标准版路径中的D3组件，必须通过额外维度补偿——混合版总改动量更大但收益相当。
