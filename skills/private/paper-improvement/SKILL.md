---
name: paper-improvement
description: "论文质量改进方法论 — 数值伪造修复、前沿文献补充、消融实验、统计显著性、声明添加的完整改进路径。"
version: 1.2.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: [paper-pipeline, sci-paper-quality-review, writing, reproducibility-audit, paper-improvement-patterns, openml-benchmark]

---

## IO_CONTRACT

- **input**: `paper_path: str, improvement_type: str, context: dict` — 论文路径、改进类型、上下文
- **output**: `result: dict` — 改进结果、编译状态

> 对应原则：P2（机械原子暴露输入输出规范）

## CHANGE_LOG

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-06-27 | 1.2.0 | 重构：提取思想/原则/方法/规则结构，具体代码与案例移至 references/ |
| 2026-06-30 | 1.3.0 | 新增方法12：四份标准审计报告生成（报告模板+判定规则+state.json更新规范） |

---

# Paper-Improvement: 论文质量改进方法论

## 一、思想

> 文以验法，改进即证。

论文的改进不是"修补错误"，而是**通过系统性验证增强论文的可信度**。每一处改进都应让审稿人更难质疑。

**核心洞察**：论文的弱点不在"写得不好"，而在"无法被验证"。数值无代码支撑、引用无法查证、组件贡献不明、统计无检验——这些才是致命伤。改进的本质是**建立可验证性链条**。

## 二、原则

### P1. 可验证性原则

每一项声称都应有对应证据链：数值→代码→输出文件。仅写声明不写代码=数据伪造。

### P2. 叙事一致性原则

不能只替换数字，必须重构叙事。数字变化时，故事也要变化。"metric inflation" → "metric collapse"。

### P3. 编译即验证原则

每次改进后必须编译通过。编译不通过 = 改进未生效。

### P4. 渐进验证原则

从最高优先级（数据伪造、作者署名）到最低优先级（图注、脚注）。先修硬伤，再修软伤。

## 三、方法

### 方法 1：数值伪造修复

**流程**：
1. 生成伪造检测对比报告
2. 读取 paper.tex，定位所有伪造/不一致数值
3. 选择修复策略（见下方模式选择）
4. 同步更新叙事逻辑（替换数字同时更新故事）
5. 清理伪造引用条目（.bib文件中不完整条目）
6. 更新 state.json 并重新编译验证

**修复模式选择规则**：
- **PATCH 模式**：少数数值变更（≤5 处，如仅 Table 中某几个值）。使用 `patch()` 逐处替换，保证 diff 可控。
- **重写模式**：大量数值变更（>10 处，如 Abstract + Table1 + Table2 + Table3 + Discussion + Conclusion 全部需要改）。直接 `write_file` 重写整个文件，避免 `patch` 累积错误和反斜杠污染。
- **判断标准**：数值变更跨越 ≥3 个 section → 重写；全在同一 section 内 → patch。

**关键规则**：
- 修正数值必须来自实际实验输出（ablation_v3.json等）
- 多实验JSON混淆陷阱：每个JSON有不同数值集，区分 `paper_claims`（旧错误值）、`actual_values`（修正值）、`levels`（原始输出）
- 以 `levels` 或 `actual_values` 为准，**不参考 `paper_claims`**
- **质量检查是起点，不是终点**：发现问题必须触发修复流程。质量检查 → 定位问题 → 选择修复模式 → 执行修复 → 编译验证 → 更新 state.json。不能只输出报告不执行修复。

### 方法 2：实验模型清单一致性校验

**流程**：
1. 提取 notebook 模型清单 — sklearn all_estimators + 手动过滤
2. 提取 helix_benchmark.py 模型清单 — 读取 CLASSIFIERS 列表
3. 对比差异 — 常见缺口：DummyClassifier、GaussianProcessClassifier；多余：LightGBM（若notebook未运行）
4. 修改 helix_benchmark.py — 添加缺失、删除多余、替换不一致
5. 重新运行，验证模型数量与 notebook 一致

**原则**：helix_benchmark.py 必须与 Jupyter notebook 的 `all_estimators()` 输出完全一致。

### 方法 3：虚假引用替换

**诊断三步**：
1. DOI批量验证 — `curl -sI "https://doi.org/<DOI>"` 检查返回码（302/200=✅, 404=🚨）
2. Crossref/SS搜索 — 用论文标题搜索真实DOI
3. 替代文献匹配 — 找语义等价的真实文献，优先OA

**替换六步**：
```
更新bib条目 → 更新正文引用键（sed） → 清理辅助文件 → 重编译 → 更新state.json → 更新综合质量报告
```

**注意**：用 sed 而非 patch 替换引用键（patch可能产生反斜杠污染）。

### 方法 4：声称性数值验证

**铁律**：任何声称"已验证"的数值必须有对应的可执行代码+输出文件。

**验证四步**：
1. 定位声明的数值集（在 paper.tex 中找到目标数值）
2. 搜索对应代码（在 03-code/ 中搜索脚本）
3. 运行或重写（若无对应脚本，写新脚本：`run_<model>_<cv_scheme>.py`）
4. 对比并更新（实际输出值若与声明不符，用实际值替换）

**关键陷阱**：
- "We verified"类声明最危险——容易在修改叙事时凭空写出
- LR 脚本不验证 CatBoost
- 主基准不验证跨数据集

### 方法 5：SHAP 模型身份验证

**验证三步**：
1. 查看 comprehensive_results.json 的 `shap_analysis.model` 字段 → 确认实际分析的模型
2. 对比 paper.tex 中的 SHAP 描述 → 若非同一模型则修正
3. 对比 SHAP 特征重要性数值 → 确认来自该次运行

### 方法 6：前沿文献补充

**流程**：
1. 搜索 2024-2026 年相关领域最新文献（arXiv, PubMed, OpenAlex）
2. 在 Discussion/Related Work 中整合 3-5 篇前沿文献
3. 确保文献与论文方法有逻辑关联
4. 在 references.bib 中添加 BibTeX 条目
5. 在正文中使用 `\citep{}` 或 `\citet{}` 引用（不用裸 `\cite{}`）

### 方法 7：消融实验

**流程**：
1. 识别方法的关键组件
2. 创建 4 个渐进变体（V1-V4），每步增加一个组件
3. 报告每个变体的指标
4. 分析每个组件的贡献度
5. 消融表放在 Appendix 中

### 方法 8：统计显著性分析

**流程**：
1. 对每个对比基线进行配对 t-test
2. 使用 Wilcoxon 符号秩检验作为非参数替代
3. 计算 95% 置信区间（Bootstrap 1000次）
4. 报告 p-value 和 Cohen's d 效应量
5. 表格呈现结果，放在 Appendix

### 方法 9：审稿意见处理

**优先级**：🔴P0硬伤 → 🔴P1方法论 → 🟡P1可解释性 → 🟢P2论证 → 🟢P2写作

**流程**：提取修复点标优先级 → 先修P0 → 逐点修 → 每修一点编译验证（4轮）→ 记录到 fix-log.md

**每次修改后必须验证**：
- 跨数据集CV方案是否与主基准一致
- SHAP分析的模型身份是否与实际代码执行一致
- 声称性数值是否有对应代码输出
- 作者署名在 submission 和 manuscript 两个版本中一致

### 方法 10：声明添加

必需声明：Data Availability Statement、Code Availability Statement、Ethical Statement、CRediT authorship contribution statement。

### 方法 11：参考文献PDF批量收集

**铁律**：永远优先调用 `Synthos/tools/paper-manager/download_one.py`。

**四层降级架构**：arXiv直连 → SS OA → EuropePMC → (SciHub → LibGen → EuropePMC → MedData)。

## 四、规则

### R1. 触发条件

当需要：
- G7 评审指出具体改进项
- 用户明确要求"改进论文"或"优化改进"
- G7 通过后仍需提升质量分至 0.85+
- 可复现性审计检测到论文声称值无代码支撑
- 用户要求"修复论文数据"或"替换伪造值"
- 凡引必查检测到DOI返回404

### R2. 编译验证（每次改进后必须执行）

```
1. 备份 paper.tex
2. 清理辅助文件：.aux, .bbl, .blg, .log, .out, .toc
3. 编译 5 轮：pdflatex → bibtex → pdflatex → pdflatex → pdflatex
4. 检查 paper.log 中是否有 Error（应为 0）
5. 检查未定义引用警告（应为 0）
6. 检查 \begin{...} 和 \end{...} 数量是否匹配
7. 确认 PDF 页数合理（通常 8-15 页）
```

### R3. LaTeX patch 陷阱防护

**反斜杠污染**：patch 可能将 `\cite` 变成 `\\cite`。修复：每次 patch 后立即运行字符串替换清理：
```python
content.replace('\\\\cite', '\\cite').replace('\\\\textbf', '\\textbf')
```

**铁律**：每次 patch 后必须检查 `\cite`、`\textbf`、`\section`、`\%` 是否被污染。

**D10a计算陷阱**：.bib 文件使用 `@type{key}` 格式，不是 LaTeX 的 `\bibitem` 格式。使用 `@(\w+)\{([^,\s]+)` 正则提取条目 key。

### R4. 防错清单

- [ ] 备份原始文件
- [ ] 清理辅助文件后重编译
- [ ] 编译无 Error（exit code 允许 1，因为有 warning）
- [ ] 无未定义引用
- [ ] BibTeX 条目数 ≥ 30
- [ ] 引用在正文中都被引用（D10a=80%+ 即可）
- [ ] `\begin{}` 和 `\end{}` 数量匹配
- [ ] 新增内容逻辑连贯，不重复

### R5. 编译失败诊断

| 症状 | 根因 | 修复 |
|------|------|------|
| Exit code 1, 但PDF生成成功 | 有警告（非错误） | 检查 .log 中 undefined citation |
| bibtex 报错 "No file name" | 上轮 pdflatex 未生成 .aux | 先跑一轮 pdflatex |
| 未定义引用逐轮增加 | bibtex 未运行或 .aux 过期 | 完整清理后重跑 5 轮 |
| 编译无限循环 Rerun | 引用/页码变化未收敛 | 5 轮后检查 |

### 方法 12：四份标准审计报告生成

**触发条件**：论文已通过所有 G1-G7 闸门（state.json gate_status=PASS, quality_score ≥ 85），但 07-quality/ 目录中缺少完整的 4 份标准审计报告（report-1 到 report-4）。常见于已走完管线但报告文件被删除或未生成的论文。

**核心流程**：

```
读取论文全文 → 分析 state.json + references.bib + 各 step_*.md → 生成 4 份标准报告 → 更新 state.json audit_status → 标记队列 VERIFIED
```

**步骤**：

1. **读取论文全文**：`01-manuscript/paper.tex` — 提取所有数值、方法、结论、引用
2. **读取 state.json**：提取 quality_score、gate_status、gates_result、reference_health、d8_d10a_scan
3. **读取 step_*.md**：从 07-quality/ 中提取已有质量检查信息
4. **读取 references.bib**：验证 D8/D10a
5. **生成 4 份报告**（见下方模板规范）

**报告模板规范**：

| 报告 | 文件名 | 核心内容 |
|:----:|:------|:--------|
| 报告一 | `report-1-universal-six-domains.md` | 通用六域评分（Q1假说→Q6价值），六域总分/60，问题清单（P0/P1/P2） |
| 报告二 | `report-2-*(specialty).md` | 方法论专项（ODE/PINN/Sklearn等），检查项逐项判定，消融实验验证，指标检查 |
| 报告三 | `report-3-references-audit.md` | 每个引用键的恰当性判定，D8/D10a审计，引文网络分析，缺失引用检测 |
| 报告四 | `report-4-inspector-report.md` | 凡数必源矩阵（所有数值→原文溯源），凡引必查清单，代码诚实验证，虚构检测扫描 |

**报告四·凡数必源矩阵规范**：
- 扫描 paper.tex 中所有数值声明（百分比、R²、MAPE、Accuracy、阈值、Sobol指数等）
- 每个数值必须标注源位置（论文段落/Table编号/行号）
- 检查跨位置一致性（Abstract vs Results vs Table vs Conclusion）
- 可追溯率 = 可溯源数值 / 总数值声明

**报告四·凡引必查清单规范**：
- 每个引用键检查：是否有PDF/DOI、体裁是否匹配、DOI是否有效
- 通过率 ≥ 90% 为 PASS

**判定规则**：
- 四份报告全部 [OK] PASS → gate_status 更新为 VERIFIED，audit_status = "VERIFIED"
- 任何报告有 P0 → 标记 BLOCKED，标注具体问题
- 报告有 P1/P2 但无 P0 → 仍可 VERIFIED，P1/P2 作为已知弱项记录

**更新 state.json**：
- 添加 `audit_status: "VERIFIED"` 或 `"BLOCKED"`
- 添加 `audit_date`
- 添加 `audit_reports` 文件列表
- 添加 `audit_summary`（关键指标汇总）
- 添加 `pipeline_trace` 条目记录审计步骤

**常见陷阱**：
- 论文类型决定报告二标题：ODE 用 `report-2-ode-pinn-specialty.md`，Sklearn 用 `report-2-sklearn-specialty.md` 等
- references.bib 可能格式损坏（如 113-nystagmus 的 author/title/year 字段混乱）→ D8/D10a 功能完整但格式需修复标记为 WARN
- 纯合成数据论文（如 113-nystagmus）无临床验证 → 已在 Limitations 中说明的可接受，标记为已知限制而非缺陷
- "Accuracy" 指标定义不清晰 → 在报告中要求澄清，但不阻断审计

## 四、参考

| 文件 | 内容 |
|------|------|
| `references/benchmark-alignment-checklist.md` | 实验模型清单一致性校验清单 |
| `references/hcs3wt-fake-doi-replacement-2026-06-25.md` | HCS-3WT实战：假DOI替换记录 |
| `references/hcs3wt-p0-remediation-full-cycle-2026-06-29.md` | HCS-3WT实战：质量检查→P0修复完整闭环（数值伪造修复模式选择、引用批量修复、数据集统一） |
| `references/pima-catboost-claim-verification-2026-06-25.md` | PIMA实战：CatBoost声称验证 |
| `references/latex-citation-replacement-fallback.md` | LaTeX引用替换回退方案（sed）|
| `references/latex-compilation-workflow.md` | LaTeX编译工作流详细说明 |
| `references/standard-audit-report-templates.md` | 四份标准审计报告模板和生成规范 |
| `BOUNDARY.md` | 技能边界声明 |
| `EVIDENCE_SCHEMA.md` | 技术证据架构 |
| `IO_CONTRACT.md` | 输入输出规范 |

## 六、版本历史

- **v1.0.0** (2026-03): 初始版本
- **v1.1.0** (2026-06): 新增虚假引用替换、SHAP验证、OpenML基准对比
- **v1.2.0** (2026-06): 重构为思想/原则/方法/规则结构

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。



# Paper Improvement

