---
name: quality-gate
description: ⚡ P0 闸门技能。四层质量架构：L0.5数据诚实门 + L1-L4交付闸门 + G1-G7论文闸门 + SCI 7维评审。通用铁律：任务完成→质量评估→不达标→循环执行。
license: MIT
allowed-tools:
- terminal
- read_file
- write_file
- search_files
metadata:
  synthos:
    version: 2.10.0
    priority: P0
    atom_type: meta-quality
    author: Synthos
    signature: 'deliverable: str -> gate_result: dict'
    related_skills:
    - project-experience-distillation
    - evolution
    - sci-paper-quality-review
    - paper-pipeline
    absorbed_skills:
    - post-compile-dual-quality-check
    - dual-quality-check-v2
    - bib-integrity-audit
    - reference-quality-triage
    - academic-thesis-review
    execution_note: 吸收内容见 references/*-absorbed.md
---

# Quality Gate — 质量闸门

## IO_CONTRACT

- **input**: `deliverable: str` — 待评估交付物标识（论文/技能/代码/文档）
- **input**: `quality_requirements: dict` — 质量要求（G1-G7 阈值、SCI 维度、领域特定标准）
- **input**: `context: dict` — 项目上下文（来源、目标、约束）
- **output**: `gate_result: dict` — 闸门结果（pass/fail + 详细评分 + 问题列表）
- **output**: `dimension_scores: dict` — 各维度评分（科学贡献/方法学/结果/完整性/清晰性/新颖性/引用）
- **output**: `action_items: list[dict]` — 待修复项清单（含优先级和修复建议）

## 核心理念（文言）

| 白话 | 文言 | 义 |
|:-----|:-----|:----|
| 无记录=门不通过 | **无录不过** | 无skill_view记录视为未执行 |
| G5引用质量最关键 | **引质为要，G5最重** | 论文质量上限=引用质量 |
| 凡数必源，不源不取 | **无源不取** | 无实验记录的数据声明=编造 |
| 一次一个维度 | **一维一渡** | 每次只聚焦一个等级，不跳步 |

## 四层架构

| 层 | 范围 | 触发 |
|:---|:-----|:------|
| L0 动灵层 | 交付物方向与系统生长路径一致性 | 每次评估前 |
| L0.5 数据诚实门 | 每个可验证数据声明是否有源文件支撑 | 每次论文评审前 |
| L1 响应级 | 当前会话输出质量 | PreResponse Hook |
| L2 项目级 | 交付物D1-D6 | 项目阶段完成 |
| L3 管线级 | 论文G1-G7原子闸门 | 写作管线每阶段切换 |
| L4 内容级 | SCI 7维评审 | G7通过后自动 |

## L0.5 数据诚实门

提取论文中所有数值声明→逐条追溯源文件：

| 声明类型 | 源文件验证方法 |
|:---------|:--------------|
| 进化数据 | `evolution-state.json` → evolution_count / trust_score |
| 基准测试 | `BENCHMARKS.md` → golden test输出 |
| 实验结果 | 实验代码输出/JSON文件/日志 |
| 对比基线值 | 追溯原始论文PDF确认具体数值 |

**通过条件**：全部数据声明有源✅或已标注estimated🟡。否则❌不通过。

## G1-G7 论文闸门

| 闸门 | 检查 | 通过条件 |
|:-----|:-----|:---------|
| G1 ACQ | 文献搜索 | ≥60候选, ≥30 PDF |
| G2 EXT | 知识提取 | 结构化提取 |
| G3 ASC | 关联空白发现 | 关联+空白矩阵 |
| G4 HYP | 假设生成 | 可证伪假设 |
| G5 ARG | 论文论证+引用全文验证 | 无虚构引用+无僵尸/孤儿 |
| G6 VER | 观点验证 | 验证通过 |
| G7 latex | 编译验证 | cite×bib×pdf三维匹配 |
| G7b DOI补全 | DOI 完整性 | ≥90%条目有DOI，缺失自动补全+Crossref验证 |

详细检查清单见 `references/writing-pipeline-checklist.md`。

## Layer B 评分阈值（NotebookLM 产出）

| 分数 | 判定 | 动作 |
|------|------|------|
| ≥0.85 | T1 通过 | 可直接进入校准分 G1-G7 计算 |
| 0.75-0.84 | T2 临界 | 需改进后复检 |
| <0.75 | 不通过 | 退回写作阶段 |

## 双质量评分

```
Layer A: 本地7维评审（基于实际读到的paper.tex）
Layer B: NotebookLM Gemini 7维评审
校准分 = min(Layer A, Layer B)

| 校准平均分 | 判定 |
|:----------:|:-----|
| ≥0.85 | T1 PASS |
| ≥0.80 | T2 PASS |
| ≥0.75 | T3 PASS |
| <0.75 | FAIL → 自动修订循环 |
```

修订循环：不达标→自动修订→重评。连续3轮无进展→降级目标期刊。

## 关键陷阱

- G5c门：Layer B执行前必须验证NotebookLM源数 ≥ D8×80%
- L0.5文献观察≠实验发现：措辞必须分级
- 实验数值必须有实验代码（不可编造）
- 消融表所有行必须来自同一模型管线
- 派生值同步检查：修改原始值后重算百分比/ratio
- **D7 < 0.80 或 DOI 覆盖率 < 90% → 必须自动补全，不跳过 G7b → 不进入 Layer B 重评**

## L0.5 数据诚信 — 反模式：伪UCI管线（2026-06-06 实战记录）

判定条件（全部命中即FAIL）：
1. 声称数据集特征（如"UCI Healthcare Dataset, 5179样本, 4.9%卒中率, 11% BMI缺失"）与实际数据核心统计量不一致
2. manuscript.tex中的实验结果数值与 model_results.csv / experiment JSON 完全不符
3. 合成数据冒充真实公开数据集（work_summary.md承认"Generated synthetic"但论文中冒充"UCI"）
4. 所有8个模型的 accuracy/AUC 在论文中被系统性夸大 >10pp

2026-06-06 失败记录 — stroke-prediction 管线：
- 声称 UCI Healthcare Dataset（卒中率4.9%, BMI 11%缺失, 年龄20-80）
- 实际数据：卒中率20.6%, BMI 0%缺失, 年龄0-90 → 合成数据冒充真实
- manuscript.tex 声称 GBM accuracy=97.15%, AUC=0.985
- model_results.csv 实际：GBM accuracy=79.25%, AUC=0.6402 → 所有8个模型系统性夸大13-23pp
- 结论：此管线完全未执行 G1-G7 任何阶段，无 state.json，无 step_*.md

修复建议：
1. 如果数据集为合成 → 论文中明确声明 synthetic dataset，不冒充公开数据集
2. manuscript.tex 数值必须与实验代码输出完全一致（逐行核对）
3. 管线必须执行 G1-G7，有 state.json + step_*.md + quality report

根因：非专业Agent执行管线时未加载 quality-gate SKILL.md，不知 L0.5 必要性。

## 方法论文选题质量前置审计（2026-06-06 实战记录）

判定"方法论文"方向价值的三个维度：
1. 是否从临床流程/真实问题出发 → 不是"跑8个ML模型比accuracy"
2. 是否有方法论创新架构 → 如 HCS-3WT 的三向决策（Clear Negative / Clear Positive / Gray Zone）
3. 是否可独立于特定数据集 → 方法论论文的价值在方法本身，不在数据集

失败模式（stroke prediction 原始方案）：
- 仅做"UCI Healthcare Dataset + 8 ML模型对比" → 教学项目，非科研论文
- 无方法论创新 → 无 gap，无假设，无临床价值
- 无法达到 T1 期刊标准（即使修正数值）

成功模式（HCS-3WT 乳腺癌论文）：
- 从临床诊断流程出发 → 发现"灰区"未处理的结构性缺陷
- 提出三向决策架构 → Clear Negative / Clear Positive / Gray Zone
- 用真实数据验证 → 10×5 CV, 79%自动化率, 99.35%自动化准确率
- 核心贡献是架构创新 → 不依赖特定数据集

管线决策规则：
- 选题被判定为"伪UCI管线"或"教学项目" → 降级为 Method Gate FAIL
- 用户要求执行此方向时 → 诚实记录局限性，严格按管线执行，压力测试双质量门
- 管线执行中发现选题价值有限 → 在 pre-audit 记录，但继续完整执行（验证方法论正确性）
- 管线完成后 → 建议将精力转向更有价值的方向（如 eye-tracking + stroke biomarker）

## Protocol/Design 论文质量门特例

协议论文（Protocol/Design Paper）的 D3（结果）维度天然受限——结果为理论设计值或仿真结果，非真实临床数据。评估时需区分：

| 论文类型 | D3 通过基线 | 原因 |
|----------|-------------|------|
| 实验论文（含真实数据） | ≥0.75 | 结果应有实测值、显著性检验 |
| Protocol/Design 论文 | ≥0.55 | 结果为理论设计值 + 仿真/Monte Carlo |
| Method 论文（算法创新） | ≥0.70 | 结果应有对比实验（即使仅仿真） |

**D3 增强路径（protocol → T1）**：
1. 补充仿真代码（不只是描述，要实际跑代码产生数值）→ D3 0.55 → 0.75
2. 与小样本真实数据（N≥50）做初步验证 → D3 0.75 → 0.85+
3. 补充 baseline 对比（standard LR, RF, XGBoost）→ D3 0.75 → 0.80+

**D3 降级场景**：
- 理论设计值无仿真支撑 → D3 < 0.50 → FAIL
- 仅有数值目标无实际运行 → D3 0.40-0.50 → T3 or FAIL

## D1 "First" 声称限定规则

连续使用 "first" 声称需满足：
1. **必须加限定词**：改为 "to our knowledge, the first..." 或 "the first X that Y"
2. **限定范围**：不泛化到整个领域，限定到具体场景（如 "for PD silent aspiration" 而非 "for all neurological disorders"）
3. **PROSPERO/ClinicalTrials.gov 搜索记录**是支撑 "first protocol" 声称的必要证据
4. 单篇论文 "first" 声称 ≤ 2 处，过多会触发审稿人质疑

## G7b DOI 自动补全协议（v2.10.0 新增）

**铁律**：D7 < 0.80 或 DOI 覆盖率 < 90% → 不跳过，必须自动补全，不进入 Layer B 重评。

**局限**：DOI 覆盖率受限于文献学事实。Pre-DOI era 论文、未接入 Crossref 的期刊/会议论文集、数据集论文可能无法补全 DOI。G7b 要求补全尝试但不强求 90% 当所有尝试均失败时，在 quality-report.md 中记录不可补原因。

执行顺序：
1. 统计覆盖率：`grep -c '^@' references.bib && grep -c 'doi\\s*=' references.bib`
2. 对缺失 DOI 条目：期刊论文 → Crossref 搜索补全；数据集 → 找原始论文 DOI（如 UCI dataset → Wolberg 1997 Cancer）；机构报告 → EU Publications Office
3. 对已有 DOI 条目：逐条 `curl "https://api.crossref.org/works/$doi"` → 检测假 DOI（status≠ok）
4. 重复 DOI → pdfinfo 确认 → 保留正确条目
5. 对无法补全的条目：通过 PubMed esummary（`elocationid` 为空）或 Crossref 404 确认无 DOI → 标记为合理例外
6. 更新 qc-d8-refs.md → 重编译 pdflatex × 2 → 重新触发 Layer B 评审

**不可补全情形（见 references/crossref-doi-lookup-edge-cases-2026-06-07.md）**：
- 1997 年前论文（DOI 系统建立前）
- PAKDD/NeurIPS 等未接入 Crossref 的会议论文集
- 1995 年前未接入 Crossref 的老期刊论文
- 数据集/仓库论文（DOI 存在但 Crossref 映射错误）

## 管线完整性审计 — 批量扫描与统一化协议 (2026-06-07 新增)

### 触发条件

当论文管线出现以下任一症状时，应执行完整审计：
- 论文目录数 ≥ 50 篇
- Layer B 质检覆盖率 < 50%
- 有 tex 无 bib > 50%
- 有 state.json 但无 quality report > 30%
- 双目录/无 symlink 或目录结构不统一

### 审计流程（四步）

**Step 1: 全面扫描**
- 遍历 `outputs/papers/` 下所有论文目录
- 对每篇记录：has_tex, has_bib, has_state.json, has_layer_b, has_quality_report, d8, d10a, score, score_label
- 分类：complete (tex+bib+state+quality) / pipeline (tex+bib无state) / partial (有state或step无完整) / empty (无任何痕迹)
- **PARTIAL 论文关键特征**: 实测 54/55 篇有.tex但完全缺失 references.bib。0.2% 极值是 dual-ellipse-fitting 有 tex+bib。.bib 缺失意味着无法计算 D8/D10a，需单独处理——不是清理而是从头生成 bib。四类论文策略不同：
  - COMPLETE → DOI 补全/引用微调
  - PIPELINE → 清理孤儿/僵尸，确保 D10a≥95%
  - PARTIAL → 需先生成 references.bib（无法直接 D8 扫描）
  - EMPTY → 完整管线重建

**Step 2: 问题识别**
- D8/D10a/DOI 检查：对每篇有 references.bib 的论文，逐篇统计引用匹配
- Layer B 缺口：标记所有 T1/T2 论文和完整管线论文中缺 Layer B 的
- 引用问题：孤儿（cited∉bib）、僵尸（bib∉cited）、DOI覆盖率

**Step 3: 任务编排**
- 生成 `paper-queue.json`，按优先级排序：
  - P1: 紧急修复（bib为空、孤儿+僵尸、T1缺Layer B）
  - P1: DOI 补全（覆盖率 <90%）
  - P2: 批量 D8/D10a 检查（按论文类型分组为 1-3 个 batch 任务）
- 批量任务格式：包含 `papers` 数组，处理时一次性处理所有论文

**Step 4: 统一化执行**
- 对每篇论文补充统一的目录结构：
  ```
  paper-name/
  ├── 01-manuscript/      # paper.tex, references.bib, step_*.md
  ├── 06-references/      # PDFs, references.bib
  ├── 07-quality/         # quality-report.md (或 qc-d8-refs.md)
  └── state.json          # 管线状态
  ```
- 每篇必须有的文件：paper.tex(≥5000字)、references.bib(≥30条)、quality-report.md、state.json

### 批量任务设计原则

- 84个单篇任务 → 合并为 11个任务（减少87%）
- repair/layer_b/doi_fix 保持单独（需具体处理）
- d8_d10a_doi 按论文管线类型批量合并（COMPLETE/PIPELINE/PARTIAL）
- cron 每 30 分钟执行一次，每次处理 1 个任务
- 批量任务（d8_d10a_batch）一次处理所有论文

### 审计结果模板

审计报告写入 `outputs/researchaudit/paper-status-audit-YYYY-MM-DD.md`，包含：
- 总体统计（总数/完整管线/部分管线/空白/Layer B覆盖率）
- T1 论文表（校准分/D8/D10a/DOI/Layer B/管线状态）
- 分类明细（complete/pipeline/partial/empty）
- D8/D10a/DOI 检查清单
- Layer B 质检缺口
- G1-G7 管线执行审计
- 统一规范建议

### 关键陷阱

- **Paper.tex 双位置**：根目录和 `01-manuscript/` 都可能存在，只统计根级别（`-maxdepth 2`）
- **Queue 格式**：`paper-queue.json` 使用 `"papers"` 数组用于批量任务（d8_d10a_batch），repair/layer_b/doi_fix 为单篇任务。批量任务需一次性处理所有论文，不可跳过。
- **引用孤儿不等于管线失败**：bib 为空可能是手动删除了文件，但 tex 中的引用仍存在。需区分"管线未执行"（无state无step）vs "管线执行了但引用丢失"（有state有step但bib空）
- **L0.5 伪UCI管线**：合成数据冒充真实数据集且 L0.5 全部命中 → 整个管线 FAIL，不可通过后续步骤
- **Paper.tex 双位置**：根目录和 `01-manuscript/` 都可能存在，只统计根级别（`-maxdepth 2`）
- **Queue 格式**：`paper-queue.json` 使用 `"papers"` 数组用于批量任务（d8_d10a_batch），repair/layer_b/doi_fix 为单篇任务。批量任务需一次性处理所有论文，不可跳过。
- **引用孤儿不等于管线失败**：bib 为空可能是手动删除了文件，但 tex 中的引用仍存在。需区分"管线未执行"（无state无step）vs "管线执行了但引用丢失"（有state有step但bib空）
- **多 bib 文件环境**：项目根目录和 01-manuscript/、06-references/ 可能各有 references.bib。执行 repair 任务时必须检查所有 bib 文件并同步更新；修复后验证所有副本一致。
- **审计报告可能过时**：paper-status-audit-*.md 是历史快照，不反映中间修复。执行 repair/repair 任务时应先独立运行 D8/D10a/DOI 扫描确认当前状态，而非直接依赖审计报告中的孤儿/僵尸数字。
- **多 tex 文件环境**：01-manuscript/ 和根目录可能各自有 .tex。修复引用时应以最新管线版本（通常有最多 cite 且 bib 条目完整的）为主；根目录旧版 tex 的 key mismatch（如 Wolberg1999Breast vs Wolberg1997Breast）应统一为正确键名。
- **BibTeX key 不一致**：同一文献可能在 tex 中使用不同 key（如 Wolberg1999Breast vs Wolberg1997Breast），需全文统一。修复时应以 bib 文件中的 key 为准。
- **DOI 解析≠文献匹配**：Crossref 解析的 DOI 可能指向正确格式但内容不匹配的文献（如 Arch Surg 的 DOI 不是 AQCH 论文）。添加 DOI 前必须精确验证标题、作者、期刊、年份四维匹配。见 `references/crossref-doi-lookup-edge-cases-2026-06-07.md`。
- **DOI 不可补全情形**：Pre-DOI era 论文（1997年前）、未接入 Crossref 的老期刊、部分会议论文集（PAKDD/NeurIPS）、数据集/仓库论文 — 这些不是工具问题而是文献学事实。G7b 协议允许合理例外，不应强制 90%。见 `references/crossref-doi-lookup-edge-cases-2026-06-07.md`。
- **PubMed 确认无 DOI**：PubMed esummary 的 `elocationid` 字段为空 = 该文献确实无 DOI（非工具问题）。
- **Crossref `filter` 参数陷阱**：在 `/works` 路由中，年份过滤必须使用 `filter=from-date=YYYY,to-date=YYYY`，**不能**使用 `from=YYYY&to=YYYY` 作为查询参数——后者返回 400 Bad Request。见 `references/crossref-doi-lookup-pattern.md`。
- **多源耗尽协议**：DOI 搜索必须依次尝试 Crossref → Semantic Scholar → PubMed → DOI resolver。任一来源成功即记录。全部失败且论文年代 < 2000 → 标记为合理例外。见 `references/membranous-scc-doi-fix-2026-06-07.md`。
- **DOI 搜索年份参数**：Semantic Scholar API 不支持年份过滤，Crossref API 的年份过滤必须用 `filter=` 参数。PubMed 使用 `[Date - Publication]` 字段标签。不同 API 的年份过滤机制不同，不可混用。
- **BibTeX DOI 字段检测**：使用 `re.search(r'\\bdoi\\s*=\\s*\\{', entry, re.IGNORECASE)` 而非 `'doi=' in entry`，因为空格和大小写可能不一致。见 `references/crossref-doi-lookup-pattern.md`。

## 补充说明：docx 引用格式提取（2026-06-07 新增）

当论文以 .docx 格式提供而非 .tex 时，引用格式可能是 `[N]`（如 `[1]`, `[5, 6]`, `[12, 13, 14]`）。使用 python-docx 提取段落文本后：

- 错误方法：`re.findall(r'\[(\d+)\]', text)` — 会漏掉 `[5, 6]` 中的 5 和 6（因为中间有逗号）
- 正确方法：`re.findall(r'\[([^\]]+)\]', text)` 然后对每个匹配用 `re.findall(r'\d+', match)` 提取所有数字

参见 `references/docx-citation-extraction-2026-06-07.md` 获取完整示例。

## 补充说明：系统综述 meta 分析论文评估模式（2026-06-07 新增）

系统综述/Meta 分析论文的质量评估有固定检查清单：

**方法学合规性（必查）**：
- PRISMA 2020 引用与流程图
- PROSPERO/ClinicalTrials.gov 注册编号
- QUADAS-2/QUAPAS 质量评估
- 统计方法：Bivariate 随机效应、HSROC、Deeks 漏斗图、Spearman 阈值效应、I² 异质性、Meta 回归

**引用质量**：D8≥30、D10a 孤儿=0/僵尸=0、DOI≥90%（或合理例外）

**结构**：IMRaD + Abstract + Limitations + 补充材料（Tables/Figures）

**典型 7 维评分范围**：
- D1 科学贡献：0.75-0.85（首次系统综述较高，有类似综述较低）
- D2 方法学：0.85-0.95（PRISMA+PROSPERO+QUAPAS 齐全可高）
- D3 结果可信度：0.65-0.80（DOR 低则偏低，样本量大则偏高）
- D4 完整性：0.80-0.90（IMRaD 完整 + 补充材料丰富）
- D5 清晰性：0.75-0.85
- D6 新颖性：0.65-0.80（首次综述较高）
- D7 引用质量：0.70-0.85（D8/D10a/DOI 达标则高）

**校准分通常落在 0.75-0.82 区间（T2 通过）**。通过 Layer B 可提升或下降 0.02-0.05。

## 参考文件

- `references/writing-pipeline-checklist.md` — G1-G7详细检查清单
- `references/bibitem-integrity-verification.md` — Bibitem完整性验证
- `references/systematic-review-layer-b-patterns.md` — Layer B(Gemini)系统综述D4/D7弱项修复模式
- `references/ref-citation-audit-protocol.md` — 引用审计协议
- `references/data-leakage-audit-protocol.md` — 数据泄露审计
- `references/full-claim-l05-verification-2026-06-01.md` — 全量声明L0.5验证
- `references/pre-commit-security-scan.md` — 提交前安全扫描
- `references/gap-hypothesis-congruence.md` — G5d空假一致性门
- `references/pipeline-completeness-audit-2026-06-08.md` — 2026-06-08 更新：107篇论文，Layer B 42%，T1 2篇，T2 8篇
- `references/pipeline-completeness-audit-2026-06-07.md` — 2026-06-07 首次全面审计
- `references/quality-report-location-discovery-2026-06-08.md` — 质量报告位置发现：4-5种文件名模式在不同目录下的扫描策略，2026-06-08实战记录
- `references/crossref-doi-lookup-pattern.md` — Crossref DOI 搜索模式与陷阱（分层搜索、400错误修复、thebibliography→BibTeX转换）
- `references/crossref-doi-lookup-edge-cases-2026-06-07.md` — DOI 不可补全场景（Pre-DOI、会议论文集、数据集论文、Crossref陷阱）
- `references/doi-fix-off-axis-iris-2026-06-07.md` — off-axis-iris DOI fix 实战记录
- `references/membranous-scc-doi-fix-2026-06-07.md` — membranous-scc-reconstruction 4篇pre-DOI era论文完整排查记录
- `references/d8-d10a-partial-paper-execution-2026-06-07.md` — PARTIAL 论文 D8/D10a 批量扫描执行记录：54/55 篇缺失 .bib，4 类管线策略差异
- `references/docx-citation-extraction-2026-06-07.md` — docx 格式论文的引用格式提取方法（[N] 和 [5, 6] 组合引用处理）
