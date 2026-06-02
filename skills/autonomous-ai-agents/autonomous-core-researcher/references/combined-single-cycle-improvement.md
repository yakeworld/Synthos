# 三管齐下单周期提升模式（Combined Single-Cycle Improvement）

> 2026-05-25 实战：vor-3d-eye-tracking v1 (avg 0.76 T3) → v2 (avg 0.836 T2) 单周期+0.076

## 触发条件

同时满足以下三条时，不要逐轮修复，在一个周期内全部完成：

| 维度 | 条件 | 检查方法 |
|:-----|:-----|:---------|
| D7 | ≥15个未引用bibitem | `grep -oP '\\\\bibitem\{[^}]+\}'` vs `grep -oP '\\\\(?:cite\|citep\|citet)\{[^}]+\}'` Python交叉验证 |
| D4 | 缺PRISMA流程图或架构图 | `grep -c '\\\\begin{figure}' paper.tex` → 系统综述应有≥1 Fig |
| D2 | 缺形式化方程或数学定义 | `grep -c '\\\\begin{equation}' paper.tex` → 应有≥1 Eq |

## 执行顺序：D7 → D4 → D2

### Step 1: D7 Strategy A — 整合未引用bibitem

**分析**: 用Python找出所有未引用bibitem，按主题分组（BPPV/vHIT/PD/可穿戴/方法学等）

**8个标准插入位置**（系统综述）：
1. `Methods/Quality` — vHIT规范数据引用
2. `Results/Gap 1` — 算法比较方法
3. `Results/Gap 2` — 特征跟踪替代方法
4. `Results/Gap 3` — VOR数学建模
5. `Discussion/BPPV` — 临床指南+ML+分类学
6. `Discussion/PD` — 生物标志物+vHIT诊断+前庭认知
7. `Discussion/Future` — 可穿戴+DL+临床应用
8. `Discussion/Introduction` — 临床综述+康复

**插入技巧**：每个位置插入2-4个相关bibitem的`\cite{key1, key2, key3}`，附简短句子说明。

**验证**:
```python
import re
with open('paper.tex') as f:
    content = f.read()
bibitem_keys = re.findall(r'\\bibitem\{([^}]+)\}', content)
cite_pattern = r'\\(?:cite|citep|citet)\{([^}]+)\}'
cited_keys = set()
for item in re.findall(cite_pattern, content):
    for key in item.split(','):
        cited_keys.add(key.strip())
uncited = [k for k in bibitem_keys if k not in cited_keys]
print(f"Uncited: {len(uncited)}/{len(bibitem_keys)} = {len(bibitem_keys)-len(uncited)}/{len(bibitem_keys)} ({100*len(cited_keys & set(bibitem_keys))/len(bibitem_keys):.0f}%)")
```

### Step 2: D4 TikZ PRISMA流程图

使用 `autonomous-core-researcher` skill 的 `references/tikz-systematic-review-templates.md` 中的模板。

**vor-3d-eye-tracking PRISMA 模板**（紧凑型，8节点）:
```latex
\begin{figure}[htbp]
\centering
\resizebox{\textwidth}{!}{%
\begin{tikzpicture}[
  box/.style={rectangle, draw, rounded corners=2mm, minimum width=3.5cm, minimum height=0.8cm, align=center, font=\small},
  arrow/.style={->, >=stealth, thick},
  node distance=1.2cm
]
\node[box, fill=blue!10] (ident) {Records identified\\XX total};
\node[box, fill=red!10, below=of ident] (dedup) {Duplicates removed\\XX};
\node[box, fill=blue!10, below=of dedup] (screen) {Title/abstract screened\\XX};
\node[box, fill=red!10, left=of screen] (excl1) {Excluded\\XX};
\node[box, fill=blue!10, below=of screen] (full) {Full-text reviewed\\XX};
\node[box, fill=red!10, left=of full] (excl2) {Excluded\\XX};
\node[box, fill=green!10, below=of full] (incl) {Included\\XX studies};
\node[box, fill=green!10, right=of incl, xshift=1cm] (details) {Modal1: XX\\Modal2: XX\\...};
\draw[arrow] (ident) -- (dedup);
\draw[arrow] (dedup) -- (screen);
\draw[arrow] (screen) -- (excl1);
\draw[arrow] (screen) -- (full);
\draw[arrow] (full) -- (excl2);
\draw[arrow] (full) -- (incl);
\draw[arrow] (incl) -- (details);
\end{tikzpicture}}
\caption{PRISMA 2020 flowchart.}
\label{fig:prisma}
\end{figure}
```

### Step 3: D2 形式化方程

**标准系统综述误差传播方程**（直接修改数值即可复用）:

```latex
\begin{equation}
\sigma_{G_{\text{VOR}}}^2 = \left(\frac{\partial G}{\partial \theta_{\text{opt}}}\right)^2 \sigma_{\theta_{\text{opt}}}^2 
+ \left(\frac{\partial G}{\partial \phi_{\text{tor}}}\right)^2 \sigma_{\phi_{\text{tor}}}^2 
+ \left(\frac{\partial G}{\partial \psi_{\text{LP}}}\right)^2 \sigma_{\psi_{\text{LP}}}^2 
+ \left(\frac{\partial G}{\partial \alpha_{\text{canal}}}\right)^2 \sigma_{\alpha_{\text{canal}}}^2
\label{eq:error_propagation}
\end{equation}
```

**VOR增益光学不确定性方程**:
```latex
\begin{equation}
\Delta G_{\text{opt}} = G_{\text{VOR}} \cdot \frac{\sin(\theta + \Delta\theta_{\text{opt}}) - \sin\theta}{\sin\theta}
\approx G_{\text{VOR}} \cdot \Delta\theta_{\text{opt}} \cdot \cot\theta
\label{eq:gain_uncertainty_optical}
\end{equation}
```

### 验证流程

```bash
# 1. 编译
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex

# 2. 检查错误
grep '^!' paper.log              # 应为0
grep 'undefined' paper.log       # 应为0

# 3. 检查输出
grep 'Output written on' paper.log

# 4. 检查PDF大小
ls -la paper.pdf
```
