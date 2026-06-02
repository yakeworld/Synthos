# 单周期 v1 论文创建模式

> 在无低分论文可修复且发现新空白时，单 cron 周期内从空白到编译论文的完整路径。

## 前置条件

- [ ] NotebookLM 可用（`notebooklm list` 返回结果）
- [ ] 有核心方向内的空白（新主题或交集空白）
- [ ] 目标为系统综述（无需实验代码）

## 步骤

### Step A: NotebookLM 逐问法（~60s）

```bash
# 检查是否有相关 NotebookLM 项目
notebooklm list | grep -i "<关键词>"

# 使用匹配的项目
notebooklm clear && notebooklm use <project_id>

# Q1 — 领域地图（短问题，< 200 tokens）
notebooklm ask "What are the main method categories for <topic>? List methods and their limitations briefly."

# Q2 — 共同盲区
notebooklm clear && notebooklm use <project_id> && \
notebooklm ask "What are the common blind spots across these methods?"

# Q3 — 形式化Gap
notebooklm clear && notebooklm use <project_id> && \
notebooklm ask "Formally articulate the gap: (1) Known consensus (2) Unknown blind spots (3) Why filling it matters."
```

**超时处理**：单次 ask ≥ 200 tokens 可能超时(120s)。拆成更短的问题重试。连续超时2次则跳过Q&A，直接用 project summary 和 source list 写论文。

### Step B: 写 paper.tex（~60s）

标准模板：
```latex
\documentclass[review]{elsarticle}
\usepackage{amsmath,amssymb,graphicx,hyperref,booktabs,multirow}
\usepackage[margin=2.5cm]{geometry}
\usepackage{algorithm,algpseudocode}
```

- thebibliography 模式：直接内联 bibitem
- 30-40 条引用覆盖核心领域（分群：经典奠基+近3年突破+综述）
- 结构：Introduction(RW+Gap+贡献) → Methods(PRISMA) → Results(分类层) → Discussion(缺口+框架) → Conclusion
- 数据类型标注：综述论文的数值声明标注引用来源

### Step C: 编译（~30s）

```bash
cd <paper-dir>
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
grep '^!' paper.log        # 应 = 0
grep -c 'undefined' paper.log  # 应 = 0 或仅 LaTeX Warning
```

常见编译错误：
- `natbib` option clash：elsarticle 内建 natbib，移除 `\usepackage{natbib}`
- `\\` 双反斜杠：patch 工具可能在 LaTeX 命令前多加一层反斜杠
- cite 未定义：pdflatex 两遍或注意 thebibliography 模式不支持 bibtex

### Step D: quality-report.md（~30s）

```markdown
## L0.5 数据诚实门 ✅
综述论文，所有声明基于引用，无原始实验数据声明。

## Layer A 7维评分
| D1 科学贡献 | 0.XX | 四层分类+缺口识别+收敛框架 |
| D2 方法学严谨性 | 0.XX | PRISMA搜索+QUADAS-2 |
| D3 结果可信度 | 0.XX | 引用准确，无原始数据 |
| D4 完整性 | 0.XX | 缺图缺表 |
| D5 清晰性 | 0.XX | CARS结构完整 |
| D6 新颖性 | 0.XX | 首次连接四层+五缺口 |
| D7 引用质量 | 0.XX | 引用数不足40 |
| **平均** | **0.XX** | |
```

v1 预期 avg 0.70-0.78。D7(0.65-0.70)、D4(0.65-0.70) 是主要拖累维度，下周期可快速修复。

**笔记本来源对 v1 质量的影响**：同一 NotebookLM 项目被复用于不同交集论文时，v1 avg 倾向于低端（0.70-0.74），因为 source 覆盖广而不深。有专用笔记本的交集论文倾向于高端（0.75-0.78）。这差别是正常的——下周期的 D7+D4 修复即可拉平。

### Step E: 更新 tracker

```json
{
  "phase": "working",
  "current_paper": "<paper-name>",
  "current_task": "v1 creation complete, avg=0.XX. Next: D7 citation expansion + D4 TikZ PRISMA + summary table",
  "next_action": "Round 1: D7(引)→D4(图表)→D2(形式化), 目标 0.XX→0.XX"
}
```

## v1 不可接受的情况

- LLM虚构定量数值（必须标记为 TBD/estimated）
- 编译失败
- cite↔bibitem 不匹配
- 不在核心方向范围内（scope guard 拦截）
- quality-report.md 未生成

## ⚠️ 空白分析论文变体（当 NotebookLM + OpenAlex 均无直接文献时）

对于某些临床交叉主题（如 BPPV×PD、Kappa角×BPPV），NotebookLM 项目可能包含两边的独立文献但**不含交叉文献**，OpenAlex 搜索可能返回 500 错误或噪声结果。此时标准 v1 模式不适用——改做**空白分析论文（Gap Analysis Paper）**：

### 判断条件

- NotebookLM Q1 测试显示笔记本含 A 方和 B 方的文献，但**无双边交叉内容**
- OpenAlex 搜索 BPPV+PD 等组合关键词返回噪声结果（PPPD、智能手机应用、骨导声音等无关论文）
- Semantic Scholar 触发 429 限速
- **核心结论**: 该交叉领域确实无人系统研究过

### 论文结构变体

标准 IMRaD 结构保持不变，但内容侧重不同：

| 节 | 标准模式 | 空白分析模式变体 |
|:---|:---------|:-----------------|
| **Methods** | PRISMA 搜索流程 | 详细记录**搜索过程透明化**：数据库、检索词、返回0结果的事实。验证搜索策略的完整性 |
| **Results** | 提取文献数据 | **间接证据合成**：分别提取 A 方(老年BPPV)和 B 方(PD前庭功能)的独立发现，推测交集情况 |
| **Discussion** | 对比/解释 | **搜索失败作为核心发现**：'The true prevalence of BPPV in PD populations remains unknown' |
| **Limitations** | 方法局限性 | 缺少直接文献本身就是主要局限+也是**核心贡献** |
| **Recommendations** | 可选 | **强制**：基于间接证据的5-6条可执行筛选/治疗/研究建议 |

### v1 质量预期（更低）

| 维度 | 标准 v1 | 空白分析 v1 | 原因 |
|:-----|:-------:|:-----------:|:-----|
| D1 贡献 | 0.70-0.75 | 0.70-0.73 | 缺口+框架仍有效 |
| D2 方法 | 0.70-0.75 | **0.65-0.70** | 无文献可提取 → 搜索方法论显弱 |
| D3 可信 | 0.65-0.70 | **0.60-0.65** | 无直接数据源 |
| D4 完整 | 0.65-0.70 | 0.70-0.75 | 框架/建议/空白表可补偿 |
| D5 清晰 | 0.70-0.75 | 0.70-0.75 | CARS 结构不变 |
| D6 新颖 | 0.70-0.78 | **0.75-0.80** | 真空白 → 新颖性更高 |
| D7 引用 | 0.65-0.70 | 0.70-0.75 | 可引用两边的核心文献 |
| **平均** | **0.70-0.78** | **0.70-0.74** | 低端正常，下周期可提至T3 |

D6 可能略高（真空白 > 常规综述）但 D2/D3 拉低平均。这是正常的——下周期 D4 加图+D2 PRISMA方法论+ D7 补引可提至 T3。

### 实战

2026-05-26: bppv-pd-clinical-review v1 (Core4∩Core5, avg=0.723 T4)
- NotebookLM 4a0f1345 Q1: BPPV文献存在但仅为VOR探针，无双边临床交叉
- OpenAlex: BPPV+PD搜索返回噪声(BPPV in elderly, 但非PD特定)
- 论文结构: 间接证据(老年BPPV+PD前庭+跌倒风险) → 4条PD predispos因素 → 1张PD-CRM表 → 5条建议 → 6个空白
- next_action: D7补引(39→50+) + D4 PRISMA流程图 + 研究特征表

使用 elsarticle + thebibliography 模式时，引用命令为 `\citep{}` 和 `\citet{}`（elsarticle 原生命令），而非标准 `\cite{}`。所有引用验证脚本必须同时处理三种格式。标准验证：
```bash
# 同时捕捉 \cite{...}, \citep{...}, \citet{...}
grep -oP '\\\\[ct]ite[tp]?\\{[^}]+\\}' paper.tex | sed 's/\\\\[ct]ite[tp]?{//;s/}//' | tr ',' '\n' | sed 's/^ *//;s/ *$//' | sort -u
```
