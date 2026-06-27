---
name: citation-verification
description: "引用三验 — 参考文献是否存在(L1) + 引用是否得当(L2) + 引用是否全面(L3)。三位一体验证管线。"
version: 3.0.0
author: Synthos
license: MIT
metadata:
  synthos:
    priority: P0
    atom_type: quality
    signature: "paper_dir: str -> citation_report: dict (phase1, phase2, phase3, overall)"
    related_skills: [paper-citation-health, paper-pipeline, quality-gate]
---

# 引用三验 — 参考文献验证

## 原理

> 引必可验，无源即删。道有归处，方为真引。
> 引之所在，文献确然。不读全文，不验引用。
> 篇篇过堂，无一遗漏。当引则引，不当引者弃。

每条引用必须可验证。验证分三层：
1. **Phase 1 — 是否存在**：DOI验真、假DOI检测、替代文献、PDF分诊
2. **Phase 2 — 是否得当**：读PDF全文、语义比对、错误检测
3. **Phase 3 — 是否全面**：独立检索、遗漏检测、补充建议

## IO Contract

- **input**: `paper_dir: str` — 论文管线目录（含01-manuscript、06-references）
- **output**: 三位验证报告 + 修复后的bib
- **side_effects**: 更新bib、修复DOI、替换虚假文献、生成验证报告

## 管线流程

```
输入: paper_dir
  ↓
Phase 1: 是否存在（DOI验真 → 假DOI检测 → 替代 → PDF Triage）
  ↓
Phase 2: 是否得当（提取语境 → 读PDF → 语义比对 → 错误检测）
  ↓
Phase 3: 是否全面（提取主题 → 独立检索 → 对比 → 遗漏检测）
  ↓
输出: 三位验证报告 + 修复后的bib
```

## Phase 1: 是否存在

### 启动检查

每次Phase 1开始前必须检查SS API密钥。不带key的SS搜索会静默返回空（429被catch为空列表）。

```python
import os
assert os.environ.get("SEMANTIC_SCHOLAR_API_KEY", ""), (
    "SEMANTIC_SCHOLAR_API_KEY not set — SS search will silently fail"
)
```

### 数据集引用替换（Phase 0.5）

**原则**：`@misc`数据集条目应替换为引入/描述该数据集的论文（`@article`/`@inproceedings`）。

原因：论文引用比原始数据集元数据更规范、更可检索、有DOI/PMID可验证、审稿人更认可。

流程：检测`@misc` → 查UCI/OpenML页→找官方intro paper或SS首引 → 替换为`@article` → 更新tex引用 → D10a回归检查。

### 假DOI检测

| 信号 | 含义 | 行动 |
|:-----|:-----|:-----|
| doi.org 404 + Crossref 404 + SS无匹配 | 几乎确定伪造 | 标记FABRICATED，找替代 |
| doi.org 404 + SS找到不同DOI | DOI篡改，论文真实 | 修复DOI+元数据 |
| 无PDF + DOI 404 | 先验假DOI（67%概率） | 不解释为付费墙，验证 |

**三验铁律**：DOI 404 + Crossref 404 + SS搜不到 = 完全虚构；DOI 404 + SS搜到不同DOI = 篡改。前者需找替代，后者修复。

### 替代文献决策树

```
假DOI → 论文不存在
  ├→ 论文主题是否被其他已有文献覆盖？
  │   ├→ 是 → 已有条目可直接引用，删除本条
  │   └→ 否 → 需要找替代（同主题高引 + 有公开PDF）
  └→ 是否为核心/被审计论文？
      ├→ 核心 → 替代必须严谨，可能需要多篇
      └→ 非核心 → 可删除不影响论证
```

### PDF Triage 分诊

| PDF状态 | 引用重要性 | 行动 |
|:--------|:----------|:-----|
| ✅ 有PDF | 任何 | 进入Phase 2 |
| ❌ 无PDF | 经典/核心 | 多级下载（Tor+Sci-Hub→OA直连→PMC） |

**铁律**：Agent自行判断重要性，不问用户。依据：①与核心论题的关系；②领域地位；③替代成本。

### D10a回归检查

Phase 1修改bib后必须交叉验证tex引用与bib键的一致性。`comm -23`检查tex引用但bib不存在的键。删除假DOI后，tex中`\\cite{deleted_key}`变成孤儿引用，D10a骤降。

## Phase 2: 是否得当

### 核心理念

API仅验证"文献存在且标题匹配"，无法验证"文献是否支持论文论断"。必须全文阅读PDF。

### Step 1: 提取引用语境

```bash
grep -n -B2 -A2 '\\\\cite' <paper>.tex > cite_contexts.txt
```

引用语境是语义审查的核心——必须知道论文"说了什么"，才能判断文献是否支持。

### Step 2: 逐篇阅读PDF

对每篇参考文献PDF：
1. 使用 `pymupdf` (fitz) 或 `pdfplumber` 提取全文
2. 记录：标题、作者、年份、摘要、关键段落
3. 图片/图表较多的PDF，记录主要方法的文字描述

### Step 3: 语义比对

| 维度 | 检查内容 | 标准 |
|------|----------|------|
| 标题匹配 | PDF标题 vs bib title | ✅ 一致 |
| 作者匹配 | PDF第一作者 vs bib author | ✅ 一致 |
| 年份匹配 | PDF年份 vs bib year | ✅ 一致 |
| 内容验证 | PDF核心内容支撑论文论断？ | ✅ 支撑 |
| 主题一致性 | PDF主题 vs 引用语境 | ✅ 一致 |
| 方法一致性 | PDF方法 vs 引用方法 | ✅ 一致 |

**判断级别**：
- ✅ 完全恰当：所有维度一致
- ⚠️ 恰当但有技术问题
- ❌ 不恰当：标题/作者/年份/内容不匹配

### 错误检测

```bash
# WITHDRAWN检测
strings ref.pdf | head -100 | grep -qi "withdrawn\|retracted\|this article has been withdrawn"

# PDF标题验证（防Nature/Springer串流）
pdfinfo ref.pdf | grep "Title:"
```

### ⚡ 必须验证的陷阱

1. **WITHDRAWN论文** — PDF存在且DOI真实，但全文以WITHDRAWN开头。有PDF≠该被引用。对每篇PDF做withdrawn检测。
2. **arXiv ID不防伪** — 真实arXiv ID可能指向不同论文。必须验证arXiv论文的标题/作者是否匹配预期。
3. **作者名编造** — DOI真实、标题/年份正确，但作者名被LLM编造。Phase 1"DOI存在"验证通过，Phase 2的PDF第一作者比对才能发现。
4. **DOI存在但内容无关** — 跨领域DOI。Balloccu2020SMOTE的DOI指向金融论文。Phase 1通过但Phase 2读PDF发现标题无关。
5. **Nature/Springer串流** — 相邻文章容易串流。SS OA链接和MedData下载均可能串流。**必须用pdfinfo验证PDF标题匹配bib标题**。
6. **SS API不带key静默失败** — 必须设置环境变量。
7. **速率限制** — Crossref和SS有速率限制，加 `time.sleep()`。

## Phase 3: 是否全面

### 核心

引用不仅要"存在"和"得当"，还要**完整**——该领域高引/经典/最新文献是否都被覆盖？

### 引用质量五维评分

| 维度 | 权重 | 标准 |
|------|------|------|
| 权威性 | 30% | 影响因子、被引次数、作者声誉 |
| 相关性 | 25% | 与论题的直接关联度 |
| 时效性 | 20% | 最近3年文献 |
| 多样性 | 15% | 多个学派/方法/观点 |
| **完整性** | **10%** | **重要文献未引用 ← 核心** |

### 完整性检测流程

1. 从摘要/引言/关键词提取主题词
2. 用SS/PubMed检索同主题高引文献（按citationCount排序）
3. 对比论文引用列表
4. 遗漏分类：
   - 🔴 关键：被引>1000 + 主题>80%匹配 + 发表>3年 → 必须补充
   - 🟡 建议：被引>100 + 主题>60%匹配 → 推荐补充
   - 🔵 可选项：其他
5. 生成补充建议

### CRISP-DM系列论文遗漏检测

CRISP-DM方法论论文常只引用原始文献(Shearer 2000, Wirth 2000)，忽略20年后的综述。必须检查：
- Martinez-Plumed 2021 "CRISP-DM Twenty Years Later" (IEEE TKDE, 332 cit)
- Schroer 2021 "A Systematic Literature Review on Applying CRISP-DM" (Procedia CS, 555 cit)

## 与quality-gate的关系

本技能对应 **quality-gate G5 的三层检查**：
- G5形式检查（D10a、DOI、孤儿、僵尸）→ Phase 1输出
- G5实质检查（引用是否得当）→ Phase 2输出
- G5完整性检查（是否遗漏）→ Phase 3输出
- G5最终判定 → 本技能整体输出

## 使用场景

- 论文投稿前引用质量终审
- 论文修改后的引用重新验证
- 批量引用检查
- 引用质量年度/季度审计

## 参考文件

- `references/pima-crispdm-phase2-review-2026-06-23.md` — Phase 2完整审计实例（PIMA bib实战）
- `references/pima-bib-fabrication-analysis.md` — 假DOI模式统计与检测规则

## 版本历史

| 版本 | 日期 | 变更 |
|:-----|:-----|:-----|
| 3.0.0 | 2026-06-27 | 重构为"原理-流程-三阶段"结构，从29KB压缩至~15KB。真实案例和详细陷阱移至references/目录。 |
| 2.4.0 | 2026-06-23 | 新增Phase 2完整审计参考文件 |
| 2.2.0 | 2026-06-23 | 新增WITHDRAWN检测/arXiv不防伪/DOI跨域/作者编造 |
| 2.0.0 | 2026-06-23 | 合并三技能：reference-verification + citation-appropriateness + 全面性评估 |
