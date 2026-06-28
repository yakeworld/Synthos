---
name: paper-experiment-audit
description: 论文实验审计 — 从代码+数据+文档提取研究空白+假设。方法论与规则，具体审计步骤见 references/。
version: 2.0.0
author: Synthos
license: MIT
metadata:
  synthos:
    priority: P1
    atom_type: pipeline
    description: "Paper experiment audit — extract research gaps and hypotheses from code+data+docs. Methodology and rules."
    signature: "paper_dir: str -> audit_report: dict"
    related_skills:
      - paper-quality-deep-review
      - paper-pipeline
      - reproducibility-audit
      - code-verification-workflow
---

# 论文实验审计

## 思想

> **论文声称跑了多少个模型？代码里实际跑了多少个？这是审计的第一问题。**
> 逆向追踪：论文声称 → 代码实现 → 数据加载 → 结果输出 → 验证完整性。

## 原理

1. **逆向审计**：不信任论文文本中的任何数值声明，从代码端提取"实际"作为基准，与论文"声称"交叉验证。
2. **代码即真**：代码目录中所有实验脚本的输出文件（JSON/CSV）是唯一的真理源。论文中的数值若无对应代码路径支撑，即为虚构。
3. **多源交叉**：多实验脚本 → 多输出文件 → 多 JSON 源 → 任一源不匹配即标记不一致。
4. **声称-路径映射**：每条论文数值声明必须能映射到至少一个代码路径（脚本+模型+CV方案）。

## IO Contract

- **Input**: paper_dir (str) — 论文目录路径
- **Output**: audit_report (dict) — 含模型对比、数据集验证、伪造标记、修复建议

## 核心流程

### 总览

```
方法论对齐 → 定位代码 → 提取模型 → 验证Notebook → 多源交叉验证 → 数据集验证 → 生成报告
```

### 阶段说明

| 阶段 | 方法 | 产出 |
|------|------|------|
| 方法论对齐 | 论文 Methods 节 vs 代码实现对比 | 对齐矩阵 |
| 定位代码 | 搜索标准化代码和原始开发代码目录 | 代码清单 |
| 提取模型 | 正则匹配 + all_estimators + JSON 结果提取 | 模型列表 |
| 验证 Notebook | 检查 cell 类型分布、outputs 完整性、HCS-3WT 实现 | 完整性报告 |
| 多源交叉 | 多脚本→多输出→实际值 vs 论文声称 | 不一致清单 |
| 数据集验证 | OpenML/sklearn/CSV 来源验证、可访问性检查 | 数据集清单 |

## 各阶段方法

### 阶段1：方法论对齐（Pre-Check）

在检查模型数量之前，必须先确认论文声称的实验设计与代码实现一致。

**数据集对齐**：论文 Methods 节中数据集名 vs 代码实际加载的文件。对比样本量、特征数、患病率。

**方法论对齐**：
- 论文声称的基线算法是否在代码中实际定义？
- 消融等级/方法论变体是否与代码匹配？
- 交叉验证策略（fold 数、分层）是否与代码一致？

**数据集命名检查**：LLM 撰写的论文文本可能引用审计论文中的数据集名，但代码加载的是不同的公开数据集。

### 阶段2：代码定位

论文实验代码出现在两个路径，必须同时检查：
- `Synthos/outputs/papers/<paper>/03-code/` — 标准化代码
- `academic_writer/article*/` — 原始开发代码

### 阶段3：模型提取

从代码中提取模型名称的三种方法：
1. 正则匹配：`(clf|model)\s*=\s*(\w+Classifier)`
2. sklearn all_estimators 自动发现
3. 从 JSON 结果提取

**统计口径**：scikit-learn 全部分类器 40 个 → 过滤后 34 个 → 加 XGBoost/LightGBM/CatBoost 37 个 → 去重后 ~32 个有效模型。

### 阶段4：多源交叉验证

**多脚本-多输出**：每个脚本产生不同的输出文件。追踪每个脚本的输出路径，列出所有 actual_values 与论文声称逐一对比。任一输出文件中都不存在 → 数据虚构。

**多 JSON 源 Ensemble**：论文声称的 Ensemble 成员必须与至少一个 JSON 源完全匹配。不一致标记 `ENSEMBLE_MEMBER_MISMATCH`。

**SHAP 模型源验证**：论文声称 SHAP 分析的模型 vs 代码实际选择的 best model。不一致 → SHAP 数值来自错误模型。

**声称-实验交叉验证**：每条数值声明必须有对应的代码路径。`CLAIMED_BUT_NEVER_RUN` 标记论文声称的模型-CV 组合在代码中不存在。

### 阶段5：数据集验证

验证 OpenML 数据集名称格式、sklearn 内置数据集存在性、CSV 文件路径正确性。论文引用 OpenML 作为基线时，检查代码是否有 `fetch_openml` 调用。

## 规则

1. **先方法论对齐，后模型审计** — 不一致时停止后续审计
2. **两个代码路径都要检查** — 标准化目录可能只包含旧版 notebook
3. **多脚本追踪** — 每个脚本的输出文件可能覆盖同一 JSON，追踪最终写入路径
4. **Ensemble 一致性** — 论文声称的 Ensemble 成员必须与至少一个 JSON 源完全匹配
5. **SHAP 模型源** — 检查代码自动选择的 best model 是否与论文声称一致
6. **声称-路径映射** — 每条数值声明必须有至少一个代码路径支撑
7. **OpenML 引用验证** — 论文引用 OpenML 时代码必须有对应 fetch 操作
8. **后台执行长时任务** — >30 秒的实验脚本 delegate 给后台，不阻塞对话

## 数值一致性审计（Numerical Consistency Audit）— 铁律级检查

**触发条件**：任何论文有 experiment_results.json 输出 + .tex 正文时执行。这是所有审计步骤中最重要的前置检查。

**核心原则**：论文声称的数值必须在 experiment_results.json 中找到精确对应。任一 >5% 偏差 → P0 级别不一致。

**审计步骤**：

1. 提取论文所有数值声明（Table、Abstract、正文、Conclusion）
2. 从 experiment_results.json 独立计算所有数值
3. 逐一对比：单分类器 ACC/REC/PREC/F1/AUC → 误差>2% 为 P0；HCS-3WT 关键指标 → 误差>3% 为 P0
4. 检查参数一致性：k 值、CV 策略、数据集描述、预处理步骤
5. 更新论文以匹配 JSON（JSON 为真理源）
6. LaTeX 编译验证（检查 Table 最后一行是否缺 `\\`）
7. 更新 state.json（score 更新，last_modification 记录）

**关键检查点**：
- k=N 特征数：论文 k=6 vs 代码 k=15 → 精度差异 2-5% → 必须统一
- 样本量：论文 699 vs UCI WDBC 569 → 必须修正
- 所有关键数值在全文所有位置（Abstract/Intro/Table/Results/Discussion/Conclusion）必须一致
- 更新后必须 grep 全文检查旧数值残留

**参考**：`references/paper-json-numerical-consistency-check.md`

## 常见参数不一致陷阱

### k=N 特征数不匹配
**症状**：论文称 k=6，代码 k=15。不同 k 值导致精度差异 2-5%。
**检测**：grep 论文中所有 k= 出现位置，grep 代码中 SelectKBest 或 k= 参数。
**修复**：统一代码与论文的参数值。通常以论文声称为准（临床可解释性需要更少的特征），然后重新运行实验。

### 交叉验证策略不一致
**症状**：论文称 10×5 CV，代码用 5×2 CV 或 3×5 CV。
**检测**：对比论文 Methods 节与代码中的 n_splits、n_repeats 参数。
**修复**：统一后重新运行实验。

### 样本量/特征数不一致
**症状**：论文称 699 样本，UCI WDBC 实际 569。
**检测**：对比论文描述与 experiment_results.json 中 n_samples。
**修复**：以数据集实际为准，更新论文所有引用位置。

### 特征工程步骤不一致
**症状**：论文称使用 Yeo-Johnson 变换+3个工程特征，代码实现不同。
**检测**：对比论文 Methods 节与代码预处理部分。
**修复**：统一后重新运行实验。

### 2026-06-29 实战：P0 数值修复完整流程（HCS-3WT）
**症状**：论文 Table 2 中5个单分类器精度与 JSON 偏差>2%；HCS-3WT 自动化率 79.07% vs JSON 70.93%；论文称 n=699 样本但 UCI WDBC 实际 569。
**根因**：代码用 k=15 特征但论文声称 k=6；代码用 k=15 精度降低，论文数值来自更早的 k=6 版本或不同预处理。
**修复流程**（7步铁律）：
1. 统一代码参数：`SelectKBest(k=15)` → `SelectKBest(k=6)`（以论文声称为准，临床可解释性需要更少特征）
2. 重新运行实验：`python3 run_hcs3wt.py`，输出更新 `experiment_results.json`
3. 更新论文 Table 2：所有单分类器 ACC/REC/PREC/FN/AUC 替换为 k=6 实验值
4. 更新论文 Table 3：HCS-3WT 自动化率、准确率、灰区大小等替换为 k=6 实验值
5. 更新所有正文引用：Abstract/Intro/Table/Results/Discussion/Conclusion 中所有旧数值（grep 全文检查）
6. 修复图脚本：fig3/fig4 从硬编码改为从 `experiment_results.json` 读取
7. 编译验证 + 更新 state.json：score 更新，last_modification 记录变更
**关键规则**：
- 每次 patch 后检查 Table 最后一行是否缺 `\\\\`（导致 `\\bottomrule` 错误）
- 更新后必须 `grep` 全文检查旧数值残留
- 数据集描述（样本量、特征数）也必须同步更新

### 2026-06-29 实战：论文图片完整性审计（HCS-3WT）
**症状**：`05-figures` 目录有 6 张图（fig1-fig6），但论文正文只引用了 1 张（fig1），5 张缺失。
**检测方法**：
1. 从 LaTeX 提取所有 `\\includegraphics{...}` 路径 → 得到论文引用的图
2. 从 `05-figures/` 目录获取所有 `.pdf` 文件列表
3. 对比两者：目录中存在但论文未引用的 = 缺失
**修复**：在 LaTeX 正文中为每张缺失图添加 `\begin{figure}...\includegraphics...\end{figure}` 块。
**关键规则**：
- 每次审计论文必须同时检查：数值一致性 + 图片完整性（论文引用 vs 目录存在）
- 图片缺失不仅是"少了张图"，更是"数据支持不够"——每张数据图都应有对应的生成脚本
- 检查 `03-code/experiments/` 目录中生成脚本数量是否 >= `05-figures/` 中 PDF 数量

## 参考文件

- `references/diabetes-datasets-reference.md` — 糖尿病相关公开数据集参考
- `references/multi-script-cross-verify.md` — 多实验脚本输出交叉验证方法
- `references/notebook-vs-script-pattern.md` — Notebook vs Python 脚本对应关系模式
- `references/paper-json-numerical-consistency-check.md` — 论文数值与experiment_results.json一致性审计方法
- `references/hcs3wt-p0-numerical-remediation-2026-06-29.md` — HCS-3WT实战：P0数值修复完整案例（k=6统一、数值替换、编译验证）
- `references/hcs3wt-figure-audit-2026-06-29.md` — HCS-3WT实战：论文图片完整性审计（fig2-fig6缺失检测与修复方法）

## 版本历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-06-27 | 2.0.0 | 重构：提炼思想/原理/IO Contract/流程/方法/规则。具体命令、案例移至 references/ |
| 2026-06-24 | 1.4.0 | 新增 OpenML 外部数据库实验真实性验证、多 JSON 源 Ensemble 交叉验证 |
| 2026-06-23 | 1.3.0 | 新增多脚本-多输出交叉验证 |
| 2026-06-21 | 1.2.0 | 新增 SHAP 模型源验证、声称-实验交叉验证、后台自动执行模式 |

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


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
