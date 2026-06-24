# 文献对比表（Table 1）构建工作流

> 用于方法论审计/系统性综述类论文的 Table 1（文献对比表）。覆盖从原始PDF阅读到结构化表格产出的完整流程。

## 触发条件

- 论文需要"文献对比表"（Table 1：比较已有研究的性能指标与方法学质量）
- 用户要求"提取所有统计数值"、"分析数据处理环节"
- 审稿人要求补充与其他研究的对比
- 用户说"table f1缺失，请仔细阅读文献原文"

## 核心原则

**读原文，不引二手**：每个数据点必须来自原始文献的 PDF 全文，不从摘要或二次引用中提取。

| ❌ 错误做法 | ✅ 正确做法 |
|:-----------|:-----------|
| 从 Semantic Scholar 摘要复制指标 | `pdftotext paper.pdf -` 读取全文找结果章节 |
| 从其他论文的文献回顾表抄数据 | 逐篇提取数字并标注具体页码 |
| 依赖 LLM 记忆中的论文数据 | 调用 Codex tmux 或 delegate_task 逐篇读取 |

## 工作流

### Step 1: 确定入组文献清单

筛选标准：
- 使用了同一数据集（如 PIDD、BRFSS、130-US Hospitals）
- 有明确报告的分类性能指标（Accuracy、F1、Sensitivity 等）
- 能够获取或已有 PDF 全文

**不要入组**：
- 仅报告相关性或回归分析的论文
- 不涉及监督分类的方法论文
- 未经验证的 LLM 编造引用（检查 DOI/Crossref/Semantic Scholar）
- 纯综述论文（无实验数据）

### Step 2: 逐篇读取 PDF，提取数据

使用 `pdftotext` 提取全文，搜索以下关键词：

```bash
pdftotext "paper.pdf" - | grep -i -A3 -B2 "accuracy\\|f1\\|f-score\\|f_measure\\|sensitivity\\|specificity\\|recall\\|precision\\|roc\\|auc\\|result\\|table"
```

**必须提取的字段**：
1. **论文标识**：标题、作者（第一作者+年份）、期刊名、DOI
2. **数据集**：使用的数据集名称、样本量、特征数
3. **报告指标**：Accuracy（数值+单位）、F1-Score / F-measure（数值）、Sensitivity/Recall、Specificity、AUC（如有）
4. **数据预处理**：缺失值处理方法（删除/均值/中位数/0填充）、SMOTE（是否使用、是否全数据集）、特征缩放（StandardScaler 等）、特征选择方法
5. **验证方法**：是否使用 CV？k-fold？stratified？train/test split 比例？
6. **其他**：过采样/欠采样方法、异常值处理、类别权重

### Step 3: 分析数据泄露（核心步骤）

对每篇论文逐环节检查：

| 检查环节 | 判定标准 | 泄露严重程度 |
|:---------|:---------|:------------|
| **Global SMOTE** | SMOTE 在 train/test split 之前运行 | 🔴 CRITICAL — 合成样本含测试集信息 |
| **Global scaling** | StandardScaler 参数在全数据集上计算 | 🔴 CRITICAL |
| **Global imputation** | 中位数/均值在全数据集计算而非 fold 内 | 🟡 MODERATE |
| **Global feature selection** | 信息增益/相关系数在全数据集上计算 | 🔴 CRITICAL |
| **No CV** | 只用单次 train/test split | 🟡 MODERATE |
| **Unclear split** | 没有明确说明 split 方法或比例 | 🟡 MODERATE |
| **Outlier removal global** | 异常值剔除在全数据集上进行 | 🟡 MODERATE |
| **No stratification** | k-fold 无分层抽样 | 🟢 LOW |

**泄露链分析格式**（输出到表格的 Leakage Path 列）：
```
SMOTE→FeatureSel→CV  # 按执行顺序列出
Up-sample→Split       # 上采样后分训练测试
```

### Step 4: 构建数据泄露因果链

对每个泄露论文，写出具体的数据流（如 Codex 输出的格式）：

```
原始 PIDD: 500 neg / 268 pos (768 total)
→ SMOTE 在全数据集上 → 268→536 pos (1036 total)
→ K-means 聚类在全 SMOTE'd 数据集上
→ 异常值剔除 → 651 instances
→ 10-fold CV（但数据已污染）
→ 报告 99.6% 准确率
```

用于表格的详细脚注或附注。

### Step 5: 确定表格形式

#### PIDD 方法论审计表 — 已验证可编译的 LaTeX 模板

用于 `elsarticle` (3p 双栏) 期刊，11 列详细版：

```latex
% Preamble 需要的包 (确保已导入):
% \usepackage{booktabs}
% \usepackage{array}

% 表格代码
{\small
\setlength{\tabcolsep}{3pt}
\begin{table*}[t]
\centering
\caption{Systematic literature audit of PIDD ML studies: reported performance and data leakage analysis.}
\label{tab:comparison}
\resizebox{\textwidth}{!}{%
\begin{tabular}{@{}llccccclp{3.2cm}c@{}}
\toprule
\textbf{Ref.} & \textbf{Journal} & \textbf{Acc} & \textbf{F1} & \textbf{Sen} & \textbf{Spe} & \textbf{AUC} & \textbf{Zero} & \textbf{Preproc} & \textbf{Leakage Path} & \textbf{Sev.}\\
\midrule
Paper A (Year) & Journal & 99.60 & NR & NR & NR & NR & X & SM:G FS:G & SMOTE→K-Means→Outlier→CV & CRI\\
Paper B (Year) & Journal & 77.10 & 0.77 & 97 & 94 & NR & O & Im:G & Zero-impute(full)→5fCV & MOD\\
\textbf{Ours} & \textbf{---} & \textbf{77.20} & \textbf{0.697} & \textbf{---} & \textbf{---} & \textbf{---} & \textbf{O} & \textbf{All W} & \textbf{All preproc in 10fCV} & \textbf{NON}\\
\bottomrule
\end{tabular}%
}
\vspace{4pt}
{\raggedright\scriptsize 
Acc=Accuracy; F1=F1-score; Sen=Sensitivity; Spe=Specificity; AUC=Area Under Curve;
Zero=Zero-value handling (O=correct, X=incorrect/missing, --=N/A);
Preproc: G=Global, W=Within-fold; SM=SMOTE; FS=Feat.sel.; Sc=Scaling; Im=Imput.;
Sev.: CRI=global preproc before CV; MOD=partial before split; MIL=minor; NON=none.
NR=Not Reported.\par}
\end{table*}
}
```

列说明：
- **Ref.** — 作者（年份），如 "Akbar (2023)"
- **Journal** — 期刊名缩写
- **Acc / F1 / Sen / Spe / AUC** — 报告指标，NR = Not Reported
- **Zero** — 零值处理正确性（O=正确识别胰岛素=0等为缺失值；X=未处理；--=不适用）
- **Preproc** — 预处理方法（G=Global全局；W=Within-fold fold内；SM=SMOTE；FS=特征选择；Sc=缩放；Im=插补）
- **Leakage Path** — 泄露链（→ 表示执行顺序，CV 加粗表示最后才做 CV）
- **Sev.** — 严重度（CRI/MOD/MIL/NON）

#### 格式 A：精简版（4-5 行，适合正文）

| Reference | Journal | Acc | F1 | Leakage? | Leakage Path |
|:---------|:-------|:--:|:--:|:--------:|:------------|
| Author et al. (Year) | Journal Name | 99.6% | 0.996 | ✅ CRITICAL | SMOTE→FeatSel→CV |
| This study | — | 78.2% | 0.594 | ❌ no | Within-fold CV |

#### 格式 B：详细版（含列）

| Reference | Year | Journal | Dataset | Reported Acc | Reported F1 | Data Leakage? | Leakage Type | Preprocessing Method | CV Method |
|:---------|:----:|:-------|:-------|:-----------:|:----------:|:------------:|:------------|:--------------------|:----------|

**注意**：如果目标论文只报 accuracy 不报 F1，在 F1 列填"NR"（Not Reported），并在分析中注明"不报 F1 本身就是方法学缺陷"。

### Step 6: 输出

产出两个文件：
1. **CSV**：`/tmp/{paper}-literature-analysis.csv`
2. **Markdown**：`/tmp/{paper}-literature-analysis.md` — 含泄露链详细分析的报告

## 工具链选择

### 方式 A：tmux Codex（推荐，已验证有效）

适合 10+ 篇论文的批量分析。file injection 模式：

```bash
# 1. 将完整任务写为文件
vim /tmp/codex_paper_analysis_task.md

# 2. tmux 中发送简短指令
tmux send-keys -t codex-xxx '请读取 /tmp/codex_paper_analysis_task.md 并执行'
# 3. 第二次调用单独发送 Enter
tmux send-keys -t codex-xxx Enter
```

**铁律**：
- `send-keys` 的指令和 Enter 必须是两条独立 Hermes terminal() 调用
- 长指令（>200 字符）使用文件注入法
- 如果发送了不完整的指令，用 `tmux send-keys -t codex-xxx Escape` 取消

#### 已验证的 PDF 分析指令（2026-06-24 成功执行）

任务模板（写入 `/tmp/codex_paper_analysis_v2.md`）：
```
# 任务：论文文献数据提取与信息泄露分析
工作目录: 06-references/ 或 pdfs/

### 需要阅读的论文
在 pdfs/ 目录下逐篇读取（先用 pdftotext 转文本）：

1. Akbar2023.pdf
2. Talari2024.pdf
...

### 每篇论文需要提取的信息
1. 论文标题、作者、年份、期刊
2. 使用的数据集（PIDD/BRFSS/其他）
3. 报告的性能指标（精确数值）
4. 数据处理方法
5. 验证方法

### 信息泄露分析
检查以下6种泄露模式：
1. Global SMOTE
2. Global scaling
3. Global imputation
4. Global feature selection
5. CV implementation (fold内/外?)
6. Zero-value handling

### 输出
CSV: /tmp/{paper}-literature-analysis_v2.csv
Markdown: /tmp/{paper}-literature-analysis_v2.md
```

Codex 处理 23 篇论文耗时约 **2 分 12 秒**（vLLM qwen3.6-35b）。

### 方式 B：delegate_task（不推荐）
子代理无 memory、无技能上下文，600s 超时限制。仅适合 3-5 篇论文。

### 方式 C：手动 Hermes 分步执行
适合 1-3 篇论文。

## 验证步骤：检测 LLM 编造引用

在数据提取前，必须先验证论文是否存在：

```bash
# 无 PDF 的引用项高度可疑
ls pdfs/ | grep -i "AuthorName"
# 或用 SS API
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=AuthorName+year+title" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('data',[])), 'results')"
```

**经验法则** (PIDD 论文，2026-06-24 验证)：
- 有 PDF 的论文 → 几乎都是真实的（4/4 验证通过）
- 无 PDF 的论文 → 极可能是 LLM 编造（5/6 完全没有记录，1/6 作者名对但论文不同）
- 报告 Acc > 99% 且无 PDF → 100% 编造（Kurniawan 100%, Deepalakshmi 97.27% 等）

## 表格插入流程（论文版本管理）

⚠️ **常见错误：插入到错误的 paper.tex 版本**

Synthos 管线中一个论文可能有多个副本：
| 位置 | 用途 | 
|:-----|:-----|
| `outputs/papers/{paper_id}/01-manuscript/paper.tex` | ✅ **正确的管线主版本** |
| `academic_writer/{paper_id}/` | ❌ 开发中版本，可能已过时 |
| `投稿文件汇总/{paper_id}/` | ❌ 投稿历史版本 |

**规则**：始终编辑 `outputs/papers/{paper_id}/01-manuscript/paper.tex`。如果表格需要 `longtable` 但目标期刊使用双栏格式，用 `table*` + `\resizebox{\textwidth}{!}` 替代。

## 陷阱与注意事项

### 1. PDF 损坏
```bash
pdftotext paper.pdf - 2>&1 | head -1
# "Couldn't find trailer dictionary" → 文件损坏，重新下载
```

### 2. 论文实际值 ≠ 论文声称值
以正文结果表格中的值为准，不是摘要。有时论文声称的数值在正文表格中都不存在（如 Chinnababu 声称 99.81% PIDD 准确率，但正文只报告了 83.11%）。

### 3. LLM 编造引用
无 PDF 的引用项高度可疑。验证：Semantic Scholar API / Crossref API。无 PDF 且无法验证的引用禁止入表。

### 4. EOC 论文的处理
已被期刊发出 Expression of Concern 的论文（如 Talari2024 PLOS ONE）——建议删去或加脚注，避免审稿人质疑。

### 5. 跨年份同一方法
同一作者的系列论文使用完全相同的方法和数据——合并或标注 "identical methodology"。

### 6. 多个 paper.tex 副本
编辑前确认工作在 `outputs/papers/{paper_id}/01-manuscript/paper.tex`，不是开发目录中的其它版本。

### 7. LaTeX Unicode 符号问题
表格中的 ✅ (U+2705) 和 ✗ (U+2717) 导致 LaTeX 编译错误。替换为 `\textsf{O}` 和 `\textsf{X}` 或简单使用 O/X 缩写。

### 8. longtable 在 table* 中不可用
双栏期刊使用 `table*` 环境（跨栏），`longtable` 不能放在 `table*` 内。解决办法：
- 使用 `\resizebox{\textwidth}{!}{\begin{tabular}...\end{tabular}}` 
- 脚注放在 `\end{tabular}` 后的 `\vspace{4pt}{\raggedright\scriptsize ... \par}`

## 参考
- `paper-pipeline` — 完整论文管线
- `codex-tmux-control` — Codex tmux 会话控制
- `paper-improvement` — 论文改进（含数值修复）
- `reproducibility-audit` — 可复现性审计（含数据泄露分析方法论）
