---
name: notebooklm-writing-workflow
description: "以NotebookLM Gemini为写作核心引擎的完整论文写作流程。覆盖P2阶段：Introduction/Methods/Results/Discussion/Abstract各节的NotebookLM Q&A生成模板、LaTeX提取与编译、引用交叉验证、版本管理。与paper-pipeline的P2阶段配合使用。吸收自paper-pipeline v3.6.0 + sci-paper-quality-review v1.7.0的实测经验（PD Torsion Review + VOR-Kappa角双论文实战）。"
version: 1.0.0
author: Synthos
license: MIT
allowed-tools: terminal read_file write_file patch cronjob
related_skills: [paper-pipeline, notebooklm-cli, sci-paper-quality-review, quality-gate]
execution_rule: "P2写作阶段强制以NotebookLM为引擎。不得跳过NotebookLM直接写论文节。每节必须走 ask→extract→compile→verify 四步。每2-3节后clear重建对话防超时。"
metadata:
  synthos_priority: P1
  tags: [writing, notebooklm, paper, p2, workflow]
  synthos_absorbed_from: "paper-pipeline v3.6.0 + sci-paper-quality-review v1.7.0实战经验"
---

# NotebookLM 论文写作工作流

> 引擎为核，不省不绕。一问一收，逐节成文。

---

## 原理层 · 文言

| 白话 | 文言 | 义 |
|:-----|:-----|:----|
| NotebookLM是写作核心引擎 | **引擎为核，不省不绕** | 所有写作必须通过NotebookLM Gemini Q&A生成，不可绕过直接写 |
| 每节单独提问，不一次全抛 | **一问一收，逐节成文** | 每节一个聚焦提问，答案决定下节方向 |
| Gemini能交叉验证引用真伪 | **互源互证，以文校文** | Gemini对比笔记本source与论文引用，发现孤证 |
| 每2-3节重建对话防超时 | **清则重建，断而不乱** | clear→use→ask三步重建对话，带浓缩摘要 |
| 引用验证优先于文采润色 | **引不证，文不饰** | 先核每个引用能否在source中找到，再优化表达 |
| 上传前删旧版，不堆积 | **新必废旧，无积无乱** | 每次上传新版本前删除旧版source |

---

## 方法层 · 白话

### 前置准备

#### 1. 检查并设置 Synthos 人格提示词（强制步骤）

**每次使用论文Notebook前，先检查是否已设Synthos人格。** 人格使Gemini在每次Q&A时遵循Synthos的7+1框架、7维评审标准和数据诚实原则。如果笔记本已有但未设过人格，必须补设。

**检查方法**（两步确认）：

```bash
# 方式一：查看当前配置（最快）
notebooklm configure --notebook <project_id>
# 返回 "Chat configured (no changes)" → 已有配置（不需要补设）
# 返回空或无输出 → 从未设过人格（需要补设！）

# 方式二：向Gemini提问验证（最可靠）
notebooklm use <project_id>
notebooklm ask "请先声明你的观察者位置，然后用1句话总结核心概念，再用7维标准评估。"
# 如果回答包含"观察者位置声明"、"7维评分"等格式 → ✅ 人格已生效
# 如果回答是通用风格、无框架标识 → ❌ 人格未设或丢失
```

**补设步骤**（仅在检查发现缺失时执行）：

```bash
# 1. 查看已有提示词文件
cat references/synthos-persona-prompt.md

# 2. 设置人格
notebooklm use <project_id>
notebooklm configure --persona "你是一位AI增强型临床科研战略顾问，拥有以下严格的方法论框架：..." --mode detailed

# 3. 验证
notebooklm ask "请先声明观察者位置，用1句话总结核心概念，再用7维标准评估。"
```

#### 2. 确定目标Notebook和认证状态

```bash
# 验证NotebookLM可用性
notebooklm list | grep -i <project_keyword>
notebooklm use <partial_id>
notebooklm status

# 确认source底座充足
notebooklm source list | wc -l        # 目标≥30个source
notebooklm source clean --dry-run     # 清理重复/错误source
```

#### 2. 确认paper目录结构

```
outputs/papers/<paper-name>/
├── paper.tex           # 主文件（含\documentclass + \begin{document} + references + \end{document}）
├── sections/           # 各节独立文件（可选）
├── references.bib      # BibTeX引用
├── figures/            # 图文件
├── pdfs/               # 引用PDF
├── CHANGELOG.md        # 版本变更
└── QUALITY.md          # 质量状态跟踪
```

#### 3. 本地资产审计

在启动NotebookLM写作前，先确认本地已有资产（避免Gemini生成的引用完全无法在本地验证）：

```bash
# 文献资产
ls pdfs/*.pdf 2>/dev/null | wc -l
grep -c '\\bibitem' paper.tex

# 数据资产（如有实验数据）
ls simulation_results.json 2>/dev/null
```

---

### 逐节写作流程

写作顺序：**Results → Methods → Discussion → Introduction → Abstract**

每节的通用四步流程：

```
Step 1: notebooklm ask → Gemini生成该节内容（含source引用[N]）
Step 2: 提取LaTeX文本 → 嵌入paper.tex
Step 3: 编译验证 → 修复LaTeX错误
Step 4: 引用交叉验证 → 确认每个引用在NotebookLM source中可追溯
```

#### Step 1 — NotebookLM Q&A 模板

每节提问前先建立新对话（避免上下文堆积）：

```bash
notebooklm use <project_id>    # 切换Notebook（自动开始新对话，不需clear）
```

##### P2.1 Introduction 模板

```
请基于项目所有源文件，用SCI标准IMRaD格式写出完整的Introduction部分。

要求：
1) Background段落：[主题]的全球/临床背景
2) Related Work按主题分组：现有[类1]方法、[类2]方法的成就与局限
3) Gap段落：指出具体空白及[具体原因数]个根本原因
4) Contribution列表：编号列出本文的3-5个贡献
5) 对比表：表格对比ours与代表系统在[维度1]/[维度2]/[维度3]等维度

格式要求：
- 全部用LaTeX格式输出
- 每个论点必须引用笔记本source中的论文（标注[N]编号）
- 贡献声明中用\citep{}格式
- 对比表用\begin{tabular}格式
```

##### P2.2 Methods 模板

```
请用LaTeX格式写出论文Methods部分。

要求：
1) 系统/架构描述（如有）：核心原理、组件、流程图描述
2) 数据来源/仿真设置：来源、样本量、参数
3) 核心算法协议：参数设置、步骤
4) 验证设计：交叉验证/仿真设计/统计分析

格式要求：
- 全部用LaTeX输出
- 每个方法步骤必须说明为什么这样设计
- 关键公式用\begin{equation}格式
- 标明哪个步骤与现有参考文献中的方法不同（创新点）
```

##### P2.3 Results 模板

```
请用LaTeX格式写出论文Results部分。

铁律：只呈现数据，不解释（解释归Discussion）。

要求：
1) 实验/仿真设置简述
2) 主要结果表（\begin{tabular}格式，含具体数值）：[指标1]/[指标2]/[指标3]
3) 辅助结果表（如消融实验/参数敏感性）
4) 结果图描述（不包含实际图文件，只写caption和引用）

数据来源：
- 所有数值必须来自项目实际运行的输出文件
- 如果数值来自仿真代码运行结果，标注"simulated"
- 如果数值尚未获得（临床数据pending），标注"[To be completed with clinical data]"
- 不得编造或估算任何数值
```

##### P2.4 Discussion 模板

```
请用LaTeX格式写出论文Discussion部分。使用图尔敏论证模型。

要求：
1) 3-4个核心论点，每个包含：
   - Claim(主张)：本研究结论
   - Grounds(根据)：引用Results中的具体数据
   - Warrant(保证)：为什么数据能支撑结论
   - Rebuttal(反驳)：可能的反对意见
2) Limitations子节：编号列出≥3条局限性
   - 每条必须诚实且对应实际限制
   - 不是"未来工作"，是真正的局限
3) 与已有工作的对比：本方法的优劣势定位

格式要求：
- 每个Limitation前标注编号：\item \textbf{[名称]}：[内容]
- Discussion中每个\citep{}必须确实在Results中被讨论过
```

##### P2.5 Abstract + Title 模板

```
请根据已经写好的Introduction/Methods/Results/Discussion，写出论文的Title和Abstract。

要求：
1) Title：10-20词，含核心技术关键词
2) Abstract（LaTeX格式）：
   - Background（1-2句）：领域背景和问题
   - Methods（2-3句）：核心方法和关键参数
   - Results（2-3句）：主要发现和量化结果（具体数值）
   - Conclusion（1-2句）：关键结论和意义
3) Keywords：6-8个关键词，用\sep分隔
```

---

#### Step 2 — LaTeX提取与嵌入

Gemini输出的LaTeX文本需要后处理：

```bash
# 1. 保存Gemini输出到节文件
# （手动从terminal输出复制到对应section文件）

# 2. 验证格式完整性
grep -c '\\begin{' sections/intro.tex        # 应≥3个环境
grep -c '\\citep{' sections/intro.tex        # 引用数合理

# 3. 嵌入主文件
# 在paper.tex的对应位置添加：
% >> section: intro
\input{sections/intro.tex}
% << section: intro
```

**注意**：Gemini输出的LaTeX可能有格式问题：
- 可能缺少`\begin{document}`框架（只含章节内容）
- `\citep`格式可能不一致（有时用`\cite`）
- 表格可能缺少列数声明
- 公式的`$`可能不对称

修复原则：每嵌入一节约编译一次，不积压多节同时修。

---

#### Step 3 — 编译验证

每写完2-3节后编译验证：

```bash
cd outputs/papers/<paper-name>
xelatex -interaction=nonstopmode paper.tex 2>&1 | grep "^!"
# 如果零错误，跑BibTeX第二次编译
bibtex paper 2>&1 | tail -3
xelatex -interaction=nonstopmode paper.tex 2>&1 | tail -3
xelatex -interaction=nonstopmode paper.tex 2>&1 | grep "Output"
```

**编译错误排查优先级**：
1. 表格列数不匹配（最常出）
2. `\citep`格式错误
3. 公式`$`不对称
4. 下划线未转义

不要用`patch`工具修复LaTeX（双转义反斜杠问题）。用`sed`或Python脚本字符级替换。

---

#### Step 4 — 引用交叉验证

这是NotebookLM写作的独特价值——让Gemini验证引用是否真实：

```bash
notebooklm ask "请将我写的论文中每个\citep{}引用的文献与笔记本中的source进行交叉对比。
对每个引用，报告：
✅ 可在source中找到直接支撑
⚠️ 有间接相关但不完全匹配
❌ 无法在source中找到任何确证（标记为'孤证'）"
```

**处理孤证**：
- ❌ 孤证 → 从论文中删除该引用，替换为可确证的文献
- ⚠️ 间接相关 → 在引用前加"see also"或改用更精确的引用
- ✅ 确证 → 保持

---

### 版本管理与上传

#### 上传新版到NotebookLM

```bash
# 1. 查现有source
notebooklm source list | grep "paper.pdf"

# 2. 删旧版
echo "y" | notebooklm source delete <old_source_id>

# 3. 上传新版
notebooklm source add paper.pdf

# 4. 验证新source ID
notebooklm source list | grep "paper.pdf"
```

#### 每次更新后自动触发双质量检查

P2写作完成后（整篇论文所有节写完），**不等用户问，自动执行**：

1. L0.5数据诚实门（凡数必源）
2. Layer A 本地7维评审（sci-paper-quality-review）
3. Layer B NotebookLM Gemini 7维评审（含引用交叉验证）
4. 校准分 = 两方最低分
5. 校准分 < 阈值 → 自动进入修订循环（不提问）

---

### 论文类型适配

| 论文类型 | 写作顺序 | 特殊注意事项 |
|:---------|:---------|:-------------|
| **综述/方法论论文**（如PD Torsion Review） | Framework→Evidence→Discussion→Intro→Abstract | 用四叉戟假设模板(H₁/H₁.₅/H₂/H₃)；Data Honesty Statement必须标注哪些数值是理论推算 |
| **技术/工程论文**（如VOR-Kappa角） | Results→Methods→Discussion→Intro→Abstract | 仿真数据用"simulated"标注；临床数据用"[To be completed]"标记 |
| **系统描述论文**（如Synthos） | Methods(Architecture+Evolution)→Results→Discussion→Intro→Abstract | 架构图强制TikZ输出；Limitations需先修后论 |

---

## 命令层 · English

### Quick Reference

```bash
# === P2 Cycle: per-section ===
notebooklm use <project_id>
notebooklm ask "<section_prompt_template>"
# → extract LaTeX → embed → compile → verify

# === Compile ===
cd outputs/papers/<name>/
xelatex paper.tex && bibtex paper && xelatex paper.tex && xelatex paper.tex

# === Upload ===
notebooklm source list | grep paper.pdf      # find old
echo "y" | notebooklm source delete <id>     # delete old
notebooklm source add paper.pdf              # upload new

# === Citation verification ===
notebooklm ask "Verify each citation in my paper against notebook sources. Tag each: ✅found ⚠️partial ❌not found"

# === Trigger dual quality check ===
# Load sci-paper-quality-review skill
skill_view("sci-paper-quality-review")
# Run L0.5 → Layer A → Layer B → calibrate → cycle
```

### Trigger Conditions

Use this skill when:

1. **P2写作开始** — 准备从头写一篇论文。先加载此skill获取各节模板
2. **P2写作中** — 写完一节后准备写下一节。load本skill获取当前节的模板
3. **引用验证** — 论文写完需要验证引用是否真实。走Step 4
4. **版本上传** — 论文更新后需要上传新版到NotebookLM。走版本管理节
5. **P2完成** — 所有节写完，自动触发双质量检查

### Pitfalls

| # | 陷阱 | 正确做法 |
|:-:|:-----|:---------|
| 1 | **跳过NotebookLM直接写论文节** | 每节必须经过 `notebooklm ask` 生成或验证 |
| 2 | **长对话超时** | 每2-3节后重建对话：`use && ask`（不需要clear） |
| 3 | **上传新版未删旧版** | 先 `source list | grep paper.pdf` 找到旧版再上传 |
| 4 | **patch修复LaTeX导致双转义** | 用 `sed` 或Python脚本替代 `patch` |
| 5 | **引用未交叉验证** | 每轮更新后必须跑一次引用验证ask |
| 6 | **D3被编造的外部对比表误导** | 先过L0.5数据诚实门再进入7维评审 |
| 7 | **Gemini生成的表格列数不匹配** | 编译前检查`\begin{tabular}{...}`的列数声明 |
| 8 | **质量评审后未修复即上传新版** | 评审发现问题→修复→再上传→再评审，循环到达标 |
| 9 | **忘记更新knowledge-graph节点** | P5发布后更新 `knowledge-graph/nodes/<paper>.md` 的(S,D,R)状态 |

### References

本技能是与以下技能配合使用的操作层：
- `paper-pipeline` — 总的管线编排器（P1-P5流程定义）
- `notebooklm-cli` — NotebookLM CLI命令参考
- `sci-paper-quality-review` — 7维SCI评审+双质量检查
- `quality-gate` — 过程闸门（G1-G7+L0.5）
