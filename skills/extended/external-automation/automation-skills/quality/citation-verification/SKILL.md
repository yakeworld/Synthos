---
name: citation-verification
description: "引用三验 — 参考文献是否存在(L1) + 引用是否得当(L2) + 引用是否全面(L3)。三位一体验证管线，从DOI验真到语义审查到遗漏检测。"
version: 2.4.0
author: Synthos
license: MIT
metadata:
  synthos:
    priority: P0
    atom_type: quality
    description: "参考文献三位一体验证。Phase 1: 是否存在（DOI验证、假DOI修复、PDF分诊）→ Phase 2: 是否得当（读PDF全文、对比引用语境、语义比对）→ Phase 3: 是否全面（独立检索、遗漏检测、补充建议）"
    signature: "paper_dir: str -> citation_report: dict (phase1, phase2, phase3, overall)"
    related_skills: [paper-references-scanning, bib-integrity-audit, pdf-download-racing, quality-gate, paper-quality-deep-review]
---

# Citation Verification — 参考文献三验

## 原理层 · 文言

| 概念 | 文言 | 义 |
|:-----|:---|:---|
| 引必可验 | **引必可验，无源即删** | 每条引用必须可验证，无真实来源则删除 |
| 道有归处 | **道有归处，方为真引** | 正式论文应有DOI，必须三方验证 |
| 引之所在 | **引之所在，文献确然** | 每篇文献必须确为论文所指论断提供支撑 |
| 不读全文 | **不读全文，不验引用** | 引用检查必须读PDF全文，非标题/摘要即可 |
| 篇篇过堂 | **篇篇过堂，无一遗漏** | 全部引用逐篇审查，非抽样 |
| 引必完备 | **当引则引，不当引者弃** | 检查遗漏的重要文献，不引冗余 |
| 质量闭环 | **引之验之，验之修之** | 验证后必须更新bib/tex，不修不闭 |

## IO_CONTRACT

- **input**: `paper_dir: str` — 论文管线目录（含01-manuscript、06-references）
- **output**: `citation_report: dict` — 三位验证报告
  ```json
  {
    "phase1_existence": {"doi_coverage", "verified", "failed", "fixed", "replaced"},
    "phase2_appropriateness": {"per_citation": [...], "errors", "pdf_fixes"},
    "phase3_completeness": {"score", "missing_papers": [...], "suggestions"},
    "overall": {"pass", "recommendation", "critical_issues"}
  }
  ```
- **side_effects**: 更新bib文件，修复DOI，替换虚假文献，生成验证报告

## 管线流程

```
输入: paper_dir
  ↓
Phase 1: 是否存在（原reference-verification）
  ├── 三方验DOI（SS + Crossref + PubMed）
  ├── 假DOI检测（doi.org 404 + "Resource not found" + SS无匹配 = 大概率伪造）
  ├── 真实DOI修复（SS搜索标题 → 纠正年份/页码/期刊）
  ├── 作者名校验（SS第一作者 ≠ bib作者 → 标记不删除）
  ├── 假DOI替代（论文不存在 → 找等效替代文献）
  └── PDF Triage分诊（经典/核心→下载，可替换→替换）
  ↓
Phase 2: 是否得当（原citation-appropriateness-verification）
  ├── 提取引用语境（tex中\cite前后句子）
  ├── 逐篇读PDF全文
  ├── 语义比对：标题/作者/年份/内容/方法一致性
  ├── PDF内容错误检测（strings/pdinfo验证）
  ├── 修复错误PDF
  └── 逐篇生成报告（恰当/不恰当/有问题）
  ↓
Phase 3: 是否全面（从paper-quality-deep-review Step 6合并）
  ├── 提取论文主题关键词
  ├── 独立检索同领域高引/经典/最新文献
  ├── 对比论文引用列表
  ├── 发现遗漏的重要文献
  └── 建议补充
  ↓
输出: 三位验证报告 + 修复后的bib
```

## Phase 1: 是否存在

### ⚡ 启动检查：SS API密钥

**每次Phase 1开始前必须检查SS API key是否可用。** 不带key的SS搜索会静默返回空（429被catch为空列表），导致假阴性——论文真实存在但被标记为"找不到"。

```python
import os
assert os.environ.get("SEMANTIC_SCHOLAR_API_KEY", ""), (
    "SEMANTIC_SCHOLAR_API_KEY not set — SS search will silently fail"
)
```

❌ 不带key的SS搜索会静默返回空（429被catch为空列表）
✅ 带key后1000 req/min正常响应

### ⚡ 数据集引用替换（Phase 0.5 — 先于DOI验证）

**原则**: 数据集条目（`@misc`）应替换为引入/描述该数据集的论文（`@article`/`@inproceedings`）。

**原因**:
- 论文引用比原始数据集元数据更规范、更可检索
- 有DOI/PMID的可验证性，有引用次数反映权威性
- 审稿人更认可"参考原始论文"而非"参考UCI链接"

**流程**:

```python
# 1. 检测bib中的 @misc 数据集条目
# 2. 对每个数据集：
#    a. 查UCI/OpenML页面 → introPaperID（是否有官方intro paper）
#    b. 搜索SS "dataset name" → 找第一篇引入该数据集的论文
#    c. 找同主题高引OA论文作为替代（如intro paper无PDF）
# 3. 替换：@misc → @article/@inproceedings，更新bib key
# 4. 更新tex中所有旧key引用
# 5. 检查D10a回归（同上Phase 1.5）
```

**实战案例（2026-06-23 PIMA bib）**:

| 原条目 | 替换后 | 理由 |
|:-------|:-------|:------|
| `UCIEarlyDiabetes2020` (@misc) | `Islam2019EarlyDiabetes` (@inproceedings) | UCI dataset 529官方intro paper |
| `CDCBRFSS2015` (@misc) | `Pierannunzi2013BRFSS` (@article, 545 cit, OA) | BRFSS方法论综述，比原始数据更权威 |
| `Smith1988` (已为@article) | 保持 | PIDD原始论文 |

**铁律**: 替换后论文无PDF不构成回退理由——论文引用本身正确比PDF存在更重要。intro paper无PDF是出版商的限制，不在你控制范围内。

### 假DOI检测模式

| 信号 | 含义 | 行动 |
|:-----|:-----|:-----|
| `doi.org` 返回 HTTP 404 | DOI不存在 | ⚡ 标记怀疑，进入语义搜索纠正 |
| Crossref API 返回 "Resource not found" | DOI未被Crossref索引 | 同上 |
| SS API 搜不到该标题/作者 | 可能论文根本不存在 | 找替代文献 |
| **三者同时成立** | **几乎确定是LLM编造的假DOI** | 标记为FABRICATED，找替代 |
| **doi.org 404 + Crossref 404 + SS搜标题发现论文但DOI不同** | DOI被篡改，论文真实存在 | 用SS返回的真实DOI替换bib元数据 |

**关键区分**: "DOI 404 + SS搜不到"=完全虚构（6/10案例）；"DOI 404 + SS搜到不同DOI"=DOI篡改（3/10案例）。前者需要找替代文献，后者只需修复DOI+元数据。

### 无PDF触发假DOI怀疑流程

**经验规律（2026-06-23 PIMA bib实证）**: 下载失败 + DOI 404 → 先验为假DOI，非网络/出版商问题。在该批41篇中，15篇下载失败→10篇DOI假或错（67%概率），仅5篇是真实的网络/付费墙问题。

**用户提问"没有全文的论文有没有可能是虚假论文"的正确答案是"是的，~2/3概率"**。

**流程**:
```
引用无PDF
  ↓
查询doi.org + Crossref + SS
  ├→ 三方全404 → 完全虚构，找替代
  ├→ DOI 404但SS标题搜索找到论文 → DOI篡改，修复
  └→ DOI真实 → 网络/付费墙问题，PDF Triage分诊
```

**铁律**: 不要假设"无PDF是因为付费墙"。先验假DOI，再考虑付费墙。

### 大规模验证的模式规律（2026-06-23 从41篇PIMA bib实证）

```
批量验证中的"下载失败"有 ~67% 概率是DOI本身假，非网络/工具问题。

41篇DOI → 15篇下载失败 → 10篇DOI假或错（67%）
  ├→ 3篇真实论文但DOI被篡改（年份/期刊/文献类型全错）
  ├→ 1篇DOI真实但作者名编造
  └→ 6篇完全虚构（论文在学术数据库中不存在）
```

| 类型 | 比例 | 特征 | 处理 |
|:-----|:-----|:------|:-----|
| **完全虚构** | 60% | 三方查询全无，论文不存在 | 删除，找替代 |
| **DOI篡改** | 30% | 论文真实存在但DOI/年份/期刊全错 | 修复DOI+元数据 |
| **作者编造** | 10% | DOI真实但bib作者信息错 | 保留条目（作者不影响引用） |

### 替代文献决策树

```
假DOI → 论文不存在
  ├→ 论文主题是否被其他已有文献覆盖？
  │   ├→ 是 → 已有条目可直接引用，删除本条
  │   └→ 否 → 需要找替代
  │       ├→ 搜索同主题高引论文（SS/Google Scholar）
  │       ├→ 选标准：同论点支持 + 更高或同等权威 + 有公开PDF
  │       └→ 新增条目到bib
  └→ 论文是否为核心/被审计论文？
      ├→ 核心 → 替代必须严谨，可能需要多篇
      └→ 非核心 → 可删除不影响论证
```

### PDF Triage 分诊决策表

| PDF状态 | 引用重要性 | 行动 |
|:--------|:----------|:-----|
| ✅ 有PDF | 任何 | 进入Phase 2 |
| ❌ 无PDF | **经典/核心**（方法论奠基、领域标杆、核心论证依赖） | 多级下载（Tor+Sci-Hub → OA直连 → PMC），3源失败则标注"PDF暂缺" |
若同一论文在正文中被多次引用其方法（如SHAP），建议核实真实作者名。

### ⚡ 铁律：重要性由Agent判断，不问用户

Phase 1发现假DOI后，Agent必须自行判断哪些论文重要、哪些可弃。判断依据：①与论文核心论题的关系；②领域地位（经典/高引 vs 低影响力）；③替代成本。判定后直接执行，在报告中附推理链。不写分类脚本，不给用户选项，不问"这个要不要"。

### ⚡ D10a回归检查（Phase 1→Phase 1.5）

Phase 1修改bib后必须交叉验证tex引用与bib键的一致性。用`comm -23`检查tex引用但bib不存在的键。2026-06-23 PIMA实战：bib删除6篇假 → tex仍引用4篇失效键 → 修复后D10a恢复100%。

### 真实案例簇（2026-06-23 PIMA bib）

| Bib Key | 假信号 | 根因 | 行动 |
|:--------|:-------|:-----|:-----|
| Kapoor2023Leakage | DOI 404 + SS找到但年份不同 | 年份篡改 | 修复DOI+year+vol |
| Norgeot2020MI-CLAIM | DOI 404 + SS找到不同DOI | 期刊替换 | 修复DOI+journal+vol+pages |
| Haixiang2017Imbalanced | DOI 404 + SS找到不同DOI | 类型替换 | @inproceedings→@article，换DOI |
| Stiglic2012Missing | 三方全无 | 完全虚构 | 删除，Garcia-Laencina2010替代 |
| Mehta2024 | 三方全无 | 完全虚构 | 删除，由Kapoor覆盖 |
| Wen2024Leakage | 三方全无 | 完全虚构 | 删除，由Kapoor+McDermott覆盖 |
| Fernandez2018Imbalanced | 三方全无 | 完全虚构 | 删除，He2009Imbalanced替代 |
| Grunspun2019Quality | 三方全无 | 完全虚构 | 删除，已有TRIPOD+PROBAST覆盖 |
| Wu2024BRFSS | DOI真实但作者错 | 作者编造 | 保留条目 |
| Char2018Clinical | DOI 404 + Crossref 404 + SS标题搜索找到不同DOI | metadata全对但DOI不存在 | 修复DOI (10.1056/NEJMp1703288→10.1056/NEJMp1714229) |
| Saeedi2019 | PDF存在且DOI真实，但全文以WITHDRAWN开头 | 已撤回论文 | 整条删除，IDF2021覆盖 |
| Varoquaux2018CV | PDF存在，arXiv ID真实，但内容是天体物理论文 | arXiv ID被替换为同ID不同论文 | 重定向到真实DOI: NeuroImage 2017 |
| Varoquaux2018Overoptimism | 同上——arXiv ID指向神经科学论文 | 完全虚构 | 删除（CV论文已覆盖相同论点） |
| Balloccu2020SMOTE | DOI指向金融论文(Hedging Crash Risk) | DOI完全错误，引用虚构 | 删除（已有Chawla+Blagus+Batista覆盖） |
| Amri2025 | DOI指向海洋光学论文 | DOI完全错误，引用虚构 | 删除（Toleva+Ansari已覆盖） |
| Sali2025→Toleva2025 | 作者名编造(Sali→Toleva)，期刊名错 | 作者编造 | 修复作者+期刊+key名 |
| Tonin2025→Ansari2025ML | 作者名编造(Tonin→Ansari)，期刊名错 | 作者编造 | 修复作者+期刊+key名 |

## Phase 2: 是否得当

### 核心理念

**API仅验证"文献存在且标题匹配"，无法验证"文献是否支持论文论断"。"引用是否得当"是质的要求，必须全文阅读PDF。**

### Step 1: 提取引用语境

```bash
grep -n -B2 -A2 '\\cite' <paper>.tex > cite_contexts.txt
```

**注意**: 引用语境是语义审查的核心——必须知道论文在引用时"说了什么"，才能判断文献是否支持。

### Step 2: 逐篇阅读PDF全文

对每篇参考文献PDF：
1. 使用 `pymupdf` (fitz) 或 `pdfplumber` 提取全文文本
2. 记录：标题、作者、年份、摘要、关键段落
3. 对于图片/图表较多的PDF，记录主要方法的文字描述

### Step 3: 语义比对

| 比对维度 | 检查内容 | 判断标准 |
|----------|----------|----------|
| **标题匹配** | PDF标题是否与bib中的title一致 | ✅ 一致为恰当 |
| **作者匹配** | PDF作者是否与bib中的author一致 | ✅ 一致为恰当 |
| **年份匹配** | PDF年份是否与bib中的year一致 | ✅ 一致为恰当 |
| **内容验证** | PDF核心内容是否支撑论文的论断 | ✅ 支撑为恰当 |
| **主题一致性** | PDF主题是否与引用语境一致 | ✅ 一致为恰当 |
| **方法一致性** | PDF描述的方法是否与论文引用的方法一致 | ✅ 一致为恰当 |

**判断级别**:
- ✅ **完全恰当**: 所有维度一致，PDF内容确实支撑论断
- ⚠️ **恰当但有技术问题**: 引用本身正确但PDF内容有问题
- ❌ **不恰当**: 标题/作者/年份/内容不匹配，或PDF内容不支持论断

### 错误分类

| 错误类型 | 严重程度 | 处理方式 |
|----------|----------|----------|
| PDF内容完全错误 | 🔴 严重 | 重新下载，修复后重新审查 |
| PDF内容部分不匹配 | 🟡 中等 | 标注并在报告中说明 |
| 引用语境与文献内容不一致 | 🔴 严重 | 修正引用语境或替换文献 |
| 缺失PDF全文 | 🟡 中等 | 经PDF Triage分诊后处理 |
| DOI错误导致内容错误 | 🔴 严重 | 修正DOI，重新下载 |
| 作者/年份错误 | 🟡 中等 | 修正Bib条目 |

### PDF内容错误检测

```bash
# 方法1: strings搜索论文主题关键词
strings ref.pdf | grep -i "论文关键词1|论文关键词2|论文关键词3"

# 方法2: pdfinfo检查页数和标题
pdfinfo ref.pdf | grep "Title:"

# 方法3: 检查PDF前1000字符的语义
head -c 1000 ref.pdf | strings

# 方法4: ⚡ WITHDRAWN论文检测 — 2026-06-23发现Saeedi2019已被撤回
head -c 500 ref.pdf | strings | grep -i "withdrawn\|retracted\|removed\|this article has been"
```

### ⚡ WITHDRAWN论文检测（Phase 2新增）

**2026-06-23 PIMA实战发现**: Saeedi2019的PDF存在且DOI真实，但全文以"WITHDRAWN: This article has been withdrawn at the request of the author(s) and/or editor."开头。

**流程**:
```bash
# 对每篇通过DOI验证进入Phase 2的PDF，先跑withdrawn检测
for pdf in *.pdf; do
    if strings "$pdf" | head -100 | grep -qi "withdrawn\|retracted\|this article has been withdrawn"; then
        echo "❌ WITHDRAWN: $pdf"
    fi
done
```

**后续**: WITHDRAWN论文有四种处理方式：
1. 如果已有更新版本（如IDF2021覆盖Saeedi2019）→ 删除，用新版替代
2. 如果无直接替代 → 标记为"已撤回，需找替代"
3. 如果论点已被其他引用覆盖 → 直接删除
4. ⚡ 不保留WITHDRAWN论文作为引用

### ⚡ arXiv ID验证陷阱（Phase 2新增）

**2026-06-23 PIMA实战发现**: Varoquaux2018CV的arXiv ID `1804.06880` 和 Varoquaux2018Overoptimism的 `1810.08651` 都是真实的arXiv ID，但指向不同论文（分别为白矮星天文学和神经科学）。

**arXiv验证协议**:
```python
# 对每个arXiv DOI，检查标题是否匹配
# 核心：arXiv ID 存在 ≠ arXiv论文正确
arxiv_id = extract_arxiv_id(doi)  # e.g. "1804.06880"
r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}")
title_from_ss = r.json().get("title", "")
assert title_matches_bib(title_from_ss), (
    f"arXiv:{arxiv_id} 指向论文 '{title_from_ss}', 非bib中的预期标题"
)
```

**arXiv验证规律**:
- DOI形如 `10.48550/arXiv.XXXX.XXXXX` → 必须验证arXiv论文的标题/作者
- arXiv ID是申请时的序列号，论文提交后内容可变
- LLM可能编造arXiv ID或使用真实的arXiv ID但错误关联

### ⚡ 作者名编造模式（Phase 2新增）

**2026-06-23 PIMA实战发现**: Sali2025→实际作者是Toleva(2025, Bioengineering)；Tonin2025→实际作者是Ansari(2025, Frontiers in Medicine)。bib中作者名被完全替换。

**检测方法**:
```python
# Phase 1只验证DOI存在性+标题匹配
# Phase 2必须验证PDF第一作者是否匹配bib中的第一作者
pdf_first_author = extract_first_author_from_pdf(pdf_path)
bib_first_author = bib_author_field.split(" and ")[0].split(",")[0].strip()
if pdf_first_author.lower() != bib_first_author.lower():
    # ⚡ 标记为作者编造
    mark_as("AUTHOR_FABRICATED")
    # 不需要删除条目——论文真实存在，metadata标题/年份正确
    # 只需修复bib中的author字段+journal字段
```

**处理**: 作者编造不需要删除条目——论文本身真实存在。只需修复bib中的author字段（从PDF提取真实作者名）。期刊名/卷号可能也错，一并修复。

### ⚡ DOI存在但内容错误的模式（Phase 2新增）

**2026-06-23 PIMA实战发现两种新假DOI模式**:

| 模式 | 案例 | 特征 |
|:-----|:-----|:------|
| **跨域替换** | Balloccu2020SMOTE (DOI→金融论文), Amri2025 (DOI→海洋光学) | DOI真实存在、通过SS/Crossref验证、标题完全无关。**完全虚构的引用伪装在真实DOI背后** |
| **WITHDRAWN沿用** | Saeedi2019 | DOI真实、可下载，但论文已撤回 |

**检测流程**:
```
Phase 1通过（DOI存在）→ Phase 2读PDF
  ├→ 标题匹配？ → ✅ 正常进入语义比对
  ├→ 标题不匹配？ → ❌ 跨域替换，删除引用，找替代
  └→ WITHDRAWN？ → ❌ 已撤回，同上处理
```

**铁律**: DOI验证通过不等于引用正确。Phase 2的PDF标题/作者验证是发现跨域替换的唯一手段。

### ⚡ Phase 2并行化策略（推荐用法）

**大论文（30+引用）的Phase 2验证推荐用并行子智能体**:

```python
# 将引用分为3-4批，每批约8-10篇
batches = [
    Batch_A: 方法论/框架类（Kapoor, Varoquaux, Collins, TRIPOD...）
    Batch_B: 方法细节类（SMOTE/插补/统计类）
    Batch_C: 背景/临床/数据集类（流行病学/伦理/MIMIC...）
]

# 每批作为一个delegate_task，包含：
# - 引用语境（tex中cite上下文）
# - 预期（bib中的title/author/year）
# - 验证方法（pdftotext提取→标题/作者/内容比对）
results = await parallel_run(batches)  # 3路并行
```

⚠️ 子智能体可能误报（如检测脚本bug）。建议对子智能体的关键发现做抽样人工复核。

## Phase 3: 是否全面

### 核心理念

论文的引用不仅要"存在"和"得当"，还要**完整**——该领域高引/经典/最新文献是否都被覆盖？是否有重要文献被遗漏？

### 引用质量五维评分

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| 权威性 | 30% | 期刊影响因子、被引次数、作者声誉 |
| 相关性 | 25% | 与论题的直接关联度 |
| 时效性 | 20% | 是否包含最近3年的文献 |
| 多样性 | 15% | 是否涵盖多个学派/方法/观点 |
| **完整性** | **10%** | **是否有重要文献未引用 ← 本阶段核心** |

### 完整性检测流程

1. **提取论文主题**: 从摘要、引言、关键词中提取主题词
2. **独立检索**: 用SS/PubMed检索同主题高引文献（按citationCount排序）
3. **对比引用列表**: 将Top N高引文献与论文引用列表对比
4. **遗漏分类**:
   - 🔴 **关键遗漏**: 该领域奠基性/里程碑论文，引文超1000，不引会被审稿人质疑
   - 🟡 **建议补充**: 近3年高引新作，引文超100，补充可加强论证
   - 🔵 **可选项**: 相关但不必须
5. **生成补充建议**

```python
def detect_missing_papers(paper_keywords, current_refs, top_n=20):
    """
    检测遗漏的重要文献
    - paper_keywords: 论文主题关键词列表
    - current_refs: 论文当前引用列表（DOI集合）
    - top_n: 检索top N高引文献
    """
    # 1. SS搜索高引文献
    results = ss_search(" ".join(paper_keywords), limit=top_n)
    
    # 2. 过滤已引用的
    missing = []
    for paper in results:
        doi = paper.get("externalIds", {}).get("DOI", "")
        if doi and doi not in current_refs:
            missing.append({
                "doi": doi,
                "title": paper.get("title", ""),
                "citations": paper.get("citationCount", 0),
                "year": paper.get("year", 0),
                "reason": classify_missing(paper, paper_keywords)
            })
    
    # 3. 按重要性排序
    missing.sort(key=lambda x: -x["citations"])
    return missing
```

### ⚡ Phase 3 CRISP-DM系列论文遗漏检测

**常见遗漏模式**: CRISP-DM方法论论文的引用往往只含原始文献（Shearer 2000, Wirth 2000），忽略20年后的综述和系统评价。

**2026-06-23 PIMA实战发现**:
- **Martinez-Plumed et al. 2021** — "CRISP-DM Twenty Years Later" (IEEE TKDE, 332 cit, doi:10.1109/TKDE.2019.2962680) — CRISP-DM从数据挖掘到数据科学的演变
- **Schroer et al. 2021** — "A Systematic Literature Review on Applying CRISP-DM" (Procedia CS, 555 cit, doi:10.1016/j.procs.2021.01.199) — CRISP-DM应用系统综述

**流程**:
```python
if paper_cites_crispdm:
    check_missing = [
        "Martinez-Plumed 2021 CRISP-DM Twenty Years Later",
        "Schroer 2021 SLR on CRISP-DM"
    ]
    for missing in check_missing:
        if missing not in current_refs:
            flag_as("CRISP-DM review missing")
```

### 遗漏判定标准

| 类别 | 条件 | 处理 |
|:-----|:-----|:-----|
| 🔴 关键遗漏 | 被引>1000 + 主题>80%匹配 + 发表>3年 | 必须补充 |
| 🟡 建议补充 | 被引>100 + 主题>60%匹配 | 推荐补充 |
| 🔵 可选项 | 其他 | 视情况 |

## 输出格式

```json
{
  "paper": "pima-crispdm",
  "review_date": "2026-06-23",
  "phase1_existence": {
    "total_entries": 37,
    "verified_dois": 33,
    "fixed_dois": 3,
    "replaced_dois": 6,
    "fabricated_dois": 10,
    "pdf_coverage": "31/37"
  },
  "phase2_appropriateness": {
    "total_citations": 37,
    "fully_appropriate": 35,
    "issues_found": 2,
    "pdf_errors_fixed": 1
  },
  "phase3_completeness": {
    "authority_score": 8.5,
    "relevance_score": 9.0,
    "timeliness_score": 7.0,
    "diversity_score": 8.0,
    "completeness_score": 7.5,
    "missing_papers": [
      {"doi": "10.xxxx/xxxxx", "title": "...", "citations": 500, "priority": "🔴"}
    ],
    "suggestions": ["补充2025-2026年最新文献"]
  },
  "overall": {
    "pass": true,
    "recommendation": "ACCEPT with minor revisions",
    "critical_issues": []
  }
}
```

## 伦理声明模板

```markdown
## 伦理声明

**本审查遵循科研诚信铁律：**

1. **逐篇验证**: N篇参考文献全部经过逐篇验证，非抽样检查
2. **全文阅读**: N篇完整阅读PDF全文
3. **语境比对**: 每篇参考文献的引用语境与其实际内容逐一比对
4. **完整性评估**: 独立检索同主题文献，评估引用完整性
5. **无虚假引用**: 所有引用均为真实存在的文献
6. **无编造数据**: 未在任何参考文献中编造数据或结论
7. **透明度**: 本报告完整记录每篇文献的审查过程和结论
```

## 与quality-gate的关系

本技能对应 **quality-gate G5 的三层检查**：
- G5形式检查（D10a、DOI、孤儿、僵尸）→ Phase 1输出
- G5实质检查（引用是否得当）→ Phase 2输出
- G5完整性检查（是否遗漏重要文献）→ Phase 3输出
- G5最终判定 → 本技能整体输出

## 使用场景

- 论文投稿前引用质量终审
- 论文修改后的引用重新验证
- 批量引用检查（多篇论文）
- 引用质量审计（年度/季度）

## 自动化程度

| 步骤 | 自动化程度 | 说明 |
|------|-----------|------|
| Phase 1: DOI验真 | ✅ 高 | 脚本自动跑三方API |
| Phase 1: PDF Triage | ✅ 高 | 文件系统检查+规则判断 |
| Phase 2: 引用语境提取 | ✅ 高 | grep解析tex |
| Phase 2: PDF全文提取 | ✅ 高 | pymupdf/pdfplumber |
| Phase 2: 语义比对 | ⚠️ 中 | 需要大模型辅助判断 |
| Phase 3: 遗漏检测 | ✅ 高 | SS搜索+对比 |
| Phase 3: 遗漏分类 | ⚠️ 中 | 需要领域知识辅助 |
| 报告生成 | ✅ 高 | 模板填充 |

## 陷阱（合并自原两个技能）

1. **默认跳转到"下载缺失PDF"模式** — 必须先分诊再下载。2026-06-21实战：27/39 (69%)无PDF → 分诊后17篇可替换、10篇经典/核心。
2. **arXiv DOI不通过Crossref验证** — 正常现象，不标记失败
3. **数据集无DOI** — 保留条目，不强制要求DOI
4. **会议论文DOI可能缺失** — 优先SS搜索
5. **速率限制** — Crossref和SS都有速率限制，加`time.sleep()`
6. **PDF内容错误不会报错** — DOI下载成功不代表内容正确。实测3/7 (42.9%) PDF内容完全错误。
7. **引用语境可能被修改** — 论文修改后必须重新审查引用
8. **PDF文件名与Bib Key不映射** — 审查前必须建立映射表
9. **年份/页码篡改** — 假DOI常见模式。检测：DOI 404时SS搜标题，对比真实DOI的年份/卷号
10. **SS API不带key静默失败** — 必须读取环境变量 `SEMANTIC_SCHOLAR_API_KEY` 并传入header
11. **Nature/Springer DOI内容漂移** — 2026-06-23 PIMA实战：Norgeot MI-CLAIM论文 (DOI 10.1038/s41591-020-1041-y) 的SS OA链接下到的PDF是Topol评论而非原文。Nature系列DOI的相邻文章容易串流。**必须用pdfinfo验证PDF标题是否匹配bib标题**。
12. **D10a回归（bib修后tex断链）** — Phase 1删除假DOI后，tex中`\cite{deleted_key}`变成孤儿引用，D10a骤降。必须在Phase 1末尾重新核查D10a并修复所有tex失效引用。
13. **"无PDF"不是付费墙问题，是假DOI警报** — 2026-06-23 PIMA实战：Char2018Clinical无PDF，DOI 404，然而metadata看似完全合理（标题/作者/期刊/年份全对）。用户提出"没有全文的论文有没有可能是虚假论文"→验证发现DOI完全虚构。铁律：下载失败+DOI 404 = 先验假DOI，然后按流程处理（见假DOI检测模式）。不要解释为"付费墙/网络问题"——67%概率是假。
14. **LibGen可下载书籍章节（book chapter）** — 书章（如Springer Advances in Intelligent Systems and Computing系列）不在PubMed索引，无PMID，MedData走不通。优先走LibGen（via Tor），DOI搜索失败时尝试ISBN搜索。

15. **WITHDRAWN论文有PDF但不该被引用** — 2026-06-23发现Saeedi2019。PDF存在且DOI真实，但全文以WITHDRAWN开头。Phase 2必须对每篇PDF做withdrawn检测。

16. **arXiv ID不防伪** — 2026-06-23发现Varoquaux2018CV (arXiv:1804.06880)和Varoquaux2018Overoptimism (arXiv:1810.08651)都是真实arXiv ID但指向错误论文。arXiv的DOI形如10.48550/arXiv.XXXX.XXXXX，SS/Crossref都能验证通过。**必须验证arXiv论文的标题/作者是否匹配预期**。

17. **DOI存在但内容无关** — 2026-06-23发现Balloccu2020SMOTE (DOI→金融论文)和Amri2025 (DOI→海洋光学)。DOI真实存在、通过SS/Crossref验证、指向完全无关领域。这是比"DOI 404假DOI"更隐蔽的模式——LLM使用真实的跨领域DOI伪装引用。

18. **作者名编造而非整篇虚构** — 2026-06-23发现Sali2025→真实作者Toleva, Tonin2025→真实作者Ansari。论文真实存在，bib的标题/年份/DOI都对，但作者名被LLM编造。Phase 1的"DOI存在"验证通过了，但Phase 2的PDF第一作者比对才能发现。

19. **MedData重复Nature/Springer串流（已发现两次）** — Norgeot MI-CLAIM论文 (DOI 10.1038/s41591-020-1041-y) 在SS OA链接和MedData两次下载中均串流到Eric Topol的评论 (DOI 10.1038/s41591-020-1042-x)。Nature系列DOI相邻文章容易串流。**必须用pdfinfo验证PDF标题是否匹配bib标题，不信任任何OA/MedData输出**。

## 版本历史

- **v2.4.0 (2026-06-23)**: 新增Phase 2完整审计参考文件。新增陷阱19（MedData重复Nature串流）。新增Norgeot MI-CLAIM两次MedData串流记录。

- **v2.3.0 (2026-06-23)**: 新增Phase 3 CRISP-DM系列遗漏检测模式（Martinez-Plumed 2021 + Schroer 2020）。新增Phase 2完整审计参考文件(`references/pima-crispdm-phase2-review-2026-06-23.md`)。新增陷阱19（CRISP-DM遗漏模式）。
- **v2.2.0 (2026-06-23)**: 新增Phase 2三大发现——WITHDRAWN论文检测/arXiv ID不防伪/DOI存在但内容无关。新增作者名编造模式。新增并行化策略(parallel delegation for 30+ citations)。新增陷阱15-18。更新真实案例簇。
- **v2.1.0 (2026-06-23)**: 新增Char假DOI案例（metadata正确但DOI完全虚构）。新增"无PDF→假DOI怀疑"检测流程和铁律。新增SS搜标题发现不同DOI的第四种假DOI信号。新增LibGen书籍章节下载提示。强化SS API key位置为Phase 1顶部⚡检查。
- **v2.0.0 (2026-06-23)**: 合并 reference-verification (v1.2) + citation-appropriateness-verification (v1.0.1) + 引用全面性评估（从paper-quality-deep-review Step 6抽取）。三位一体管线。新增Phase 3完整性检测流程。
- **v1.2.0 (2026-06-21)**: 原reference-verification。新增PDF Triage分诊。
- **v1.0.1 (2026-06-18)**: 原citation-appropriateness-verification。新增PDF内容错误陷阱。
- **v1.0.0 (2026-06-18)**: 原skills初始版本。
