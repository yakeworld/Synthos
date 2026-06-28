---
name: pima-audit
description: PIMA 方法论审计 — 完整的 32 模型 sklearn 基线扫描、数据泄露检测、正确方法论验证。覆盖从数据清洗到最终排名的全流程审计。
version: 2.0.0
author: Synthos
priority: P1
signature: "pima-audit -> processed_result"
---

# PIMA 方法论审计

## 原理层

> 方法论正确性 > 单一最优模型。跑 32 个模型不是为了选出最好的，而是为了证明方法论本身决定了上限。最优的模型会被后续方案纳为己用。

## 适用场景

- 需要系统性审计 ML 论文的方法论正确性（PIMA 模式）
- 需要跑 scikit-learn 全量基线对比
- 需要检测数据泄露模式
- 需要验证论文中声称的实验是否真实可复现

## 核心步骤

### 1. 论文声明提取

从论文 .md/.tex 中提取：
- 声称的模型数量（grep 数字+model/baseline/classifier）
- 数据集信息（来源、大小、特征数）
- 表格中的模型排名
- 方法论声明（是否提及零替换、pipeline 隔离等）

### 2. 代码结构扫描

```
paper_dir/
├── 01-manuscript/     # 论文稿
├── 03-code/
│   ├── *.py           # 实验脚本
│   └── *.ipynb        # notebook
├── 04-data/           # 原始数据
├── 07-quality/        # 质量检查报告
└── state.json         # 论文状态
```

关键文件：
- `comprehensive_pima_experiment.py` — 完整实验流程
- `run_helix_benchmark.py` — 27 模型基线（较精简）
- `crisp-dm-pima.ipynb` — 原始 notebook（需验证）

### 3. 模型数量审计（调用 model-count-audit）

- helix_benchmark: 27 个模型（显式定义）
- comprehensive_pima: 37 个（sklearn all_estimators 自动发现 + 3 外部）
- Table 2 声称: 32 个模型
- 差异原因：FixedThresholdClassifier、TunedThresholdClassifierCV 等 wrapper 不独立训练

### 4. 数据泄露检测

**正确流程：**

```python
# ZeroReplacer -> Imputer -> Scaler -> SMOTE -> 模型（都在 Pipeline 内）
pipeline = Pipeline([
    ('zero_replacer', ZeroReplacer(cols)),  # 只在 train 上 fit
    ('imputer', SimpleImputer()),
    ('scaler', StandardScaler()),
    ('smote', SMOTE()),
    ('clf', model)
])
```

**错误流程（数据泄露）：**

```python
X_scaled = StandardScaler().fit_transform(X)  # 数据泄露
```

**常见泄露模式：**
1. 全量标准化 — `StandardScaler().fit_transform(X)` 在 train_test_split 之前
2. 特征选择泄露 — SelectKBest/RFECV 在全量数据上 fit
3. 数据增强泄露 — SMOTE/BorderlineSMOTE 在全量数据上运行
4. 特征工程泄露 — 基于全量数据的统计构建特征

### 5. 实验可复现性验证

```
1. 用相同数据跑相同代码 -> 检查输出一致性
2. 检查 random_state 是否固定
3. 检查 cross_validate 是否 stratified
4. 检查 SMOTE 是否在 pipeline 内部（不在外部）
5. 检查每个模型独立的 pipeline（无共享 state）
```

### 6. 方法论正确性报告

生成报告包含：
- ✅ 数据清洗流程
- ✅ 交叉验证隔离
- ✅ SMOTE 位置
- ✅ 特征工程隔离
- ❌ 泄露检测

## 文献审计 Table 1 生成（v3.1 新增）

> 审计完实验代码后，必须也审计被引文献——论文声称对比的文献中有多少实际存在数据泄露？

### 触发条件

- 论文包含文献对比表（Table 1 为文献分析）
- 论文试图证明现有文献存在方法学缺陷
- 需要为论文 Introduction/Discussion 提供量化证据

### 工作流

#### Step 0: 数据源确认

**不要从 BBL 或网络 API 重新验证**——Synthos 论文的参考文献已经过质量检查，直接使用本地 PDF：

```
Synthos/outputs/papers/<paper-name>/06-references/
├── *.pdf                 ← 已验证全文
├── pdfs/                 ← 95+ 篇按DOI命名的PDF
└── pdfs_md/              ← 40+ 篇Markdown摘要
```

**使用前先确认**：新论文的文献是否已归入此目录。若未归入，先运行 `paper-pipeline` 下载验证。

#### Step 1: 批量文本提取

所有 PIMA/糖尿病相关论文集中在 `pdfs/` 目录，用 `pdftotext` 批量转换：

```bash
for pdf in pdfs/*.pdf; do
    pdftotext "$pdf" "/tmp/$(basename "$pdf" .pdf).txt" 2>/dev/null || true
done
```

#### Step 2: 指标提取（用 Codex tmux 会话）

使用 `codex-tmux-control` skill 在后台 Codex 会话中执行提取，**不要用 delegate_task**。

**发送指令格式**：
1. 将完整任务写入文件（`/tmp/codex_task.md`）
2. 发 `send-keys '请读取 /tmp/codex_task.md 并执行'` 加 Enter
3. 20-30s 后 `capture-pane` 检查进度

**每篇论文提取项：**
- Dataset（PIDD/BRFSS/其他）
- Accuracy（精确值）
- F1-Score（精确值，未报告填 "NR"）
- Sensitivity / Specificity / AUC（如有）
- **零值处理**——胰岛素/血压/皮肤厚度=0 是否被识别为医学缺失值？
- **SMOTE 位置**——Global（在拆分前）/ Within-fold（正确）/ No
- **CV 方法**——k-fold / train-test split / 无
- **泄露路径**——一句话描述预处理在全数据集上执行的链条

#### Step 3: 泄露严重度分类

| 严重度 | 条件 | 标记 |
|:-------|:-----|:----|
| **CRITICAL** | SMOTE/聚类/特征选择 在 CV 之前全局应用 | 🔴 |
| **MODERATE** | 零值替换/缩放/上采样 在 split 之前全局应用 | 🟡 |
| **MILD** | 归一化层记忆训练集统计量，或预处理顺序略模糊 | 🟢 |
| **NONE** | 独立的 train/test 集，或方法论文献 | ✅ |

#### Step 4: 零值处理检测（PIMA 特有）

医学上不可能为零的特征（PIDD 特有的）：
- `Insulin` — 48.7% 的值为 0（临床不可能）
- `SkinThickness` — 29.6% 的值为 0
- `BloodPressure` — 0 代表未测量
- `BMI`, `Glucose` — 0 代表缺失

**检查方法**：在论文 PDF 中搜索 `zero`, `missing`, `impute`, `replace`, `insulin`, `bp`, `skin`

**已知结果**（2026-06-24 实证）：
- 仅 ~13% 的 PIMA 论文（2/15）正确识别这些零值为医学缺失
- Ali2025 (Sci. Rep.) ✅ 明确标注：`"Zero values in pregnancy, BP, skin, insulin, BMI are not biologically conceivable"`
- Hossain2025 ✅ 检查零值并替换为均值
- 多数论文：完全忽略此问题

#### Step 5: 生成 Table 1（LaTeX）

使用 `longtable` + `booktabs` 生成论文级表格，13 列：

```latex
\begin{longtable}{p{2.2cm} p{2.5cm} p{1.3cm} c c c c c c c p{2.5cm} p{2.8cm} c}
\caption{Literature comparison — data leakage analysis.}
\label{tab:literature_audit} \\
\toprule
\textbf{Reference} & \textbf{Journal} & \textbf{Dataset} &
\textbf{Acc (\%)} & \textbf{F1} & \textbf{Sens. (\%)} &
\textbf{Spec. (\%)} & \textbf{AUC} & \textbf{Zero Handling} &
\textbf{SMOTE} & \textbf{CV Method} & \textbf{Leakage Path} &
\textbf{Severity} \\
```

**列说明**：

| 列 | 内容 | 取值 |
|:---|:-----|:-----|
| Reference | 作者 (年份) | e.g. "Akbar (2023)" |
| Journal | 期刊缩写 | e.g. "Telematika" |
| Dataset | 使用数据集 | PIDD / BRFSS / 其他 |
| Acc (%) | 报告准确率 | 数值或 NR |
| F1 | 报告 F1 | 数值或 NR |
| Sens. (%) | 敏感性 | 数值或 NR |
| Spec. (%) | 特异性 | 数值或 NR |
| AUC | AUC | 数值或 NR |
| Zero Handling | 零值处理正确? | ✅ / ❌ / NR |
| SMOTE | SMOTE 位置 | Global / Within-fold / No |
| CV Method | 验证方法 | e.g. "10-fold CV" |
| Leakage Path | 泄露链条 | 箭头 $\to$ 串联 |
| Severity | 严重度 | CRITICAL / MODERATE / MILD / NONE |

**行排序**：按严重度（CRITICAL→NONE），同级按年份降序。严重度之间用 `\midrule` 分隔。

**底部加一行**：`\textbf{This study}` 作为正确方法对比基线。

**脚注**（在 `\endlastfoot` 前）：
```latex
\multicolumn{13}{l}{\footnotesize{NR = Not Reported; Zero Handling: $\checkmark$Correct / $\times$Incorrect / NR; SMOTE: Global/Within-fold/No.}}
```

#### Step 6: 将 Table 1 嵌入论文

生成的 `.tex` 文件直接放入 `01-manuscript/` 目录，在主 `.tex` 文件中用 `\input{table1_literature_audit.tex}` 引用。

### 已知结果（2026-06-24 实证）

**分析论文数**：23 篇（15 PIMA 经验 + 8 方法论）

**泄露严重度分布**：
| 严重度 | 数量 | 代表论文 |
|:-------|:----:|:---------|
| CRITICAL | 2 | Akbar (99.6%), Talari (99.14%) |
| MODERATE | 6 | Kalagotla (78.2%), Hossain (94.17%), Ali (77.1%), Perdana (77.86%), Shams (89%), Naz (98.07%) |
| MILD | 1 | Chinnababu (83.11%) |
| NONE | 3 | Smith, Pranto (review), Kurniawan (非PIDD) |

**零值处理**：仅 2/15 篇（13%）正确识别了胰岛素/血压/皮肤厚度中的零值为医学缺失。

### 参考文件

- `references/pima-literature-audit-2026-06-24.md` — 完整文献审计数据（23 篇论文的逐篇分析、泄露链、输出文件路径）
- `references/table1-latex-template.md` — Table 1 LaTeX 模板和生成指南

## 跨数据集方法论一致性验证（v3.0 新增）

> 参考：`references/cross-dataset-audit-2026-06-21.md` — 包含具体数值、数据集详情和输出文件路径。

### 核心发现

数据泄露不是 PIDD 特有的现象，而是在所有糖尿病数据集中**系统性存在**。

| 数据集 | 样本量 | 正确方法 F1 | 泄漏方法 F1 | 膨胀幅度 |
|:-------|:-------|:-----------|:-----------|:---------|
| PIDD (n=768) | 768 | 0.6604 | 0.7083 | **+7.3%** |
| Australian (n=768) | 768 | 0.4845 | 0.7034 | **+45.2%** |
| Diabetes 130-US (n=8,200) | 8,200 | 0.2141 | 0.7026 | **+228%** |

### 泄漏的缩放律（Scaling Law of Leakage）

> **数据集规模越大，数据泄露导致的结果膨胀越严重。**
> 泄漏后的 F1 趋近于 ~0.70，不受原始数据集正确方法 F1 的影响。

解释：大样本数据集有更多"犯错的自由度"——全局 SMOTE 可以从更多负样本中生成合成正样本，从而掩盖更大的模型缺陷。

### 文献审计（Literature Audit via Semantic Scholar）

**方法：**
1. 用 Semantic Scholar API 搜索特定数据集的论文
2. 对每篇论文检查：SMOTE 位置、CV 方法、train/test 隔离、数值合理性
3. 生成数据泄露风险评分

**已知结果：**
- PIDD 论文：70%+ 使用全局 SMOTE，平均报告 accuracy 94.4%（不可信）
- Australian 论文：极少（审计不足），泄漏后 F1 膨胀 +45.2%
- Diabetes 130-US 论文：几乎无学术论文专门审计
- Kaggle 论文：极高的过拟合风险

### 执行步骤

#### Step 1: 选择跨数据集

```python
# 优先选择：
# 1) 同领域但不同人群（种族泛化）：PhysioNet INSCAT (印度), Australian (澳洲)
# 2) 同领域但不同规模：Diabetes 130-US (8,200), PIDD (768)
# 3) 其他二分类临床问题：WDBC (乳腺癌), Heart Disease (心脏病)
```

#### Step 2: 在每个数据集上复现方法论审计

```python
# 通用审计脚本 audit_cross_dataset.py：
# 输入：任意 CSV 数据（特征+标签列）
# 输出：
#   - 32基线排名（correct pipeline）
#   - 方法论消融（7组：A0正确, A1-无元特征, A2-1:1权重, A3-无三重乘积, A4-1:10极端权重, Leak1-全局SMOTE, Leak2-全局预处理）
#   - 数据泄露检测
#   - 最优模型
```

核心同单数据集审计，但需要在**完全相同实验条件下**运行。

#### Step 3: 跨数据集对比表

生成跨数据集对比表：
```markdown
| 数据集 | 基线最优 | 漏泄后虚高 | 膨胀率 | 
|-------|---------|-----------|-------|
| A     | 0.66    | 0.71      | +7%   |
| B     | 0.48    | 0.70      | +45%  |
| C     | 0.21    | 0.70      | +228% |
```

#### Step 4: 文献验证

在目标数据集的学术论文中验证一致性：
1. 用 Semantic Scholar API 搜索 `dataset X` + `machine learning`
2. 过滤出 report accuracy > 90% 或 F1 > 0.70 的论文
3. 标注这些论文的数据泄露风险
4. 形成：「跨数据集方法论审计 vs 已有论文声明」的对比论证

### 论文升级建议

**原始论调：** "在 PIDD 上证明了方法论正确性的重要性"
**升级后：** "在 3 个数据集上发现**同样的数据泄露问题**——方法论审计的普适性"

推荐增加 2 个数据集：
1. PhysioNet INSCAT（种族泛化 - 印度人群）
2. Diabetes 130-US（规模+真实性 - 美国医院）

形成：PIDD (美国本土) + INSCAT (印度人群) + 130-US (美国大型)
论证链：方法论验证 → 种族泛化 → 规模验证

## Pitfall

1. **Notebook 不是可复现记录** — 如果 notebook 里所有单元格都没有输出（cell outputs），它只是一个设计草稿。实验代码必须是独立的 `.py` 脚本。
2. **helix_benchmark 不完整** — 27 个模型 vs 32 个声称。missing: DummyClassifier, GaussianProcessClassifier, StackingClassifier, TunedThresholdClassifierCV, FixedThresholdClassifier。
3. **Pima 论文 vs HCS-3WT 论文是不同范式** — Pima: 方法论审计（32 基线）；HCS-3WT: 新架构验证（7 模型）。不要混为一谈。
4. **跨数据集审计必须保证实验条件一致** — 同样的 ZeroReplacer、Pipeline 结构、CV 设置、评估指标。否则跨数据集对比无意义。
5. **泄漏后的 F1 趋同 ~0.70 是一个经验观察，不是理论保证** — 需要在更多数据集上验证。
6. **Semantic Scholar API 可能漏检** — 不返回所有论文。建议用 CrossRef 或 PubMed 补充。
7. **OpenML 公开实验可以作为第三方验证** — PIDD (ID:292) 有 200+ 公开实验，其中 accuracy > 90% 的很可能存在泄漏。

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
