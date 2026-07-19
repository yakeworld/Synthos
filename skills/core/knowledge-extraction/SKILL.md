---
name: knowledge-extraction
category: core
signature: "knowledge-extraction -> core: 从单篇论文中提取结构化知识（实体、关系、主张、证据），输出 KnowledgeItem JSON。可选 pwbench 逆向工程模式。"
description: "从单篇论文中提取结构化知识（实体、关系、主张、证据），输出 KnowledgeItem JSON。可选 pwbench 逆向工程模式。"
author: Synthos
license: MIT
version: 2.2.0
entrypoint_type: cognitive
entrypoint_cmd: "从论文输入中提取实体、关系、主张、证据四域"
entrypoint_desc: "知识提取。输入: papers(list), 输出: knowledge_items(list)"
priority: P1
atom_type: cognitive-atom
allowed-tools: [terminal, read_file, write_file, web_extract, vision_analyze]
metadata:
  synthos:
    priority: P1
    atom_type: cognitive-atom
    description: "Single-paper structured knowledge extraction — entities, relations, claims, evidence"
    signature: "paper_content: str, schema: dict -> structured_knowledge: dict (entities, relations, claims, evidence)"
    related_skills: ['knowledge-acquisition', 'association-discovery', 'hypothesis-generation', 'pdf-to-markdown']
---

# Knowledge Extraction — 知识提取

> 从单篇论文中提取结构化知识。不做跨论文比较、不做假设生成、不做论证表达。
> 单篇为基，结构为纲。凡文必拆为实体、关系、主张、证据四域。无源不录，无据不传。

## 原理层·文言

> **格物致知。** 物格而后知至。单篇为基，结构为纲，四域为目。
>
> **凡文必拆：** 实体（谁/什么）、关系（如何关联）、主张（说了什么）、证据（凭什么说）。
> **无源不录：** 每项知识必须有明确的论文来源和位置标注。
> **无据不传：** 主观表述与客观事实必须分离，数值声明必须可追溯。
>
> **两模式：** 标准提取（知识消费）与逆向工程（知识再生产），各有所用，不可混淆。

## 方法层·白话

知识提取是认知管道第 2 步（ACQ → **EXT** → ASC → HYP → ARG → VER）。输入单篇论文全文/摘要，输出结构化 KnowledgeItem JSON。

### 两模式

| 模式 | 输入 | 输出 | 用途 |
|------|------|------|------|
| **standard** | 论文全文或摘要 | KnowledgeItem (4域) | 构建知识库，供 ASC/HYP 使用 |
| **pwbench** | 论文全文（去实验部分） | Idea (sparse/dense) + Experimental Log | 逆向工程 benchmark 用例 |

---

## 触发条件

- 上游 `knowledge-acquisition`（现指向 `literature`）产出论文，需要结构化
- 用户要求"提取/分析/总结这篇论文"
- 需要为 `association-discovery` 准备结构化输入
- 需要为论文写作提取文献证据

---

## 标准提取模式（standard）

### Step 1: 加载论文内容

优先 Markdown（markitdown），回退 raw text（pdftotext）。

```bash
# 方式A（首选）: markitdown 转换 → Markdown
# 保留表格结构、标题层级，provenance 标注更准
markitdown paper.pdf > /tmp/paper_content.md

# 方式B（回退）: pdftotext → raw text
# 当 markitdown 失败（扫描PDF/超大/加密）时使用
pdftotext -layout paper.pdf /tmp/paper_content.txt

# 方式C: 从已下载的 Markdown 文件直接读
cat /path/to/paper.md

# 方式D: 从摘要/网页
web_extract(url)  # 或直接粘贴摘要
```

**级联规则**：
1. 先跑 `markitdown paper.pdf > /tmp/try.md`
2. 检查输出：`wc -c /tmp/try.md` ≥ 200 且含文本 → ✅ 用 Markdown（设 `meta.source = "markdown_extracted"`）
3. 失败（空/超时）→ 回退 pdftotext（设 `meta.source = "pdf_text"`）

> **为什么优先 Markdown**：表格结构保留 → 证据提取更准（数值不乱）；标题层级保留 → section 标注从"猜"变"定"。

### Step 2: 四域结构化提取

按以下四域提取，每个域有统一格式：

#### 实体（Entities）

论文中出现的核心实体：
| 子类 | 说明 | 示例 |
|------|------|------|
| `method` | 方法/算法/模型 | PINN, ODE, CNN, transformer |
| `phenomenon` | 研究对象/现象 | 眼震, BPPV, 瞳孔对光反射 |
| `technology` | 技术/设备 | 眼动仪, VNG, vHIT |
| `concept` | 概念/理论 | 熵减, VOR适应, 感觉冲突 |
| `person` | 作者/研究者 | 仅限于论文明确引用的人物 |
| `institution` | 机构/团队 | 仅限于论文明确提及的机构 |

输出格式：
```json
{
  "name": "...",
  "type": "method|phenomenon|technology|concept|person|institution",
  "aliases": ["同义词/缩写"],
  "provenance": {"section": "Introduction", "sentence": "..."}
}
```

#### 关系（Relations）

实体间的显式关系：
```json
{
  "source": "实体A",
  "target": "实体B",
  "relation": "causes|correlates_with|predicts|contradicts|extends|depends_on",
  "direction": "unidirectional|bidirectional|undirected",
  "provenance": {"section": "...", "sentence": "..."}
}
```

#### 主张（Claims）

论文的核心主张/发现：
```json
{
  "claim": "具体陈述（可验证的命题）",
  "type": "finding|hypothesis|conclusion|limitation",
  "confidence": "stated|suggested|speculated",
  "evidence_refs": ["evidence条目索引"],
  "provenance": {"section": "...", "sentence": "..."}
}
```

区分三类置信度：
- `stated` — 论文明确断言（"Our results show that X..."）
- `suggested` — 论文暗示（"These findings suggest that X may..."）
- `speculated` — 论文推测（"X might be explained by Y..."）

#### 证据（Evidence）

支持主张的具体证据（数值、引用、数据）：
```json
{
  "evidence": "具体证据内容",
  "type": "numeric|l iterature_reference|experimental_result|clinical_observation",
  "value": 数值（如果是数值型）,
  "unit": "单位（如果是数值型）",
  "statistical_sig": "p<0.05"或null,
  "provenance": {"section": "...", "figure": "...", "table": "..."}
}
```

**数值声明必须标注位置**（section/figure/table/line number），不可只写"文中提到"。

### Step 3: 六维质量评分

对每个 KnowledgeItem 按 `references/knowledge-entry-rubric.md` 六维评分：

| 维度 | 权重 | 说明 |
|:----:|:----:|:-----|
| Gap Significance | 0.25 | 研究空白的重要性 |
| Methodological Soundness | 0.20 | 方法学合理性 |
| Result Completeness | 0.20 | 结果完整性 |
| Clinical Translation | 0.15 | 临床转化潜力 |
| Reproducibility | 0.10 | 可复现性 |
| Narrative Quality | 0.10 | 叙事质量 |

**通过阈值**: composite ≥ 0.70

### Step 4: 保存

```bash
# 保存结构化知识
mkdir -p outputs/{paper_dir}/07-quality/
python3 -c "import json; json.dump(knowledge_item, open('outputs/{paper_dir}/07-quality/knowledge.json','w'), indent=2, ensure_ascii=False)"
```

路径规范：`outputs/{paper_slug}/07-quality/knowledge.json`

---

## PW-Bench 逆向工程模式（pwbench）

> 适用场景：从已发表论文重建研究设计，用于评估管线对模糊输入的响应能力。

### 模式1: Sparse Idea

从论文提取高层概念（不含实验细节）。
- 用第一人称将来时："我们将探索..."
- 禁止引用、URL、作者名
- 不允许包含实验结果
- 避免 LaTeX 数学，用语言描述功能

输出 `idea_sparse.md`，四部分：
1. **Problem Statement** — 问题陈述
2. **Core Hypothesis** — 核心假设
3. **Proposed Methodology (high-level)** — 方法概述
4. **Expected Contribution** — 预期贡献

### 模式2: Dense Idea

从论文提取详细技术方案。
- 用第一人称将来时，保留数学公式
- 定义所有使用的变量
- 包含具体的架构选择和维度
- 不允许实验结果

输出 `idea_dense.md`，四部分（同上，但更详细）。

### 模式3: Full Reconstruction

从论文完整重建 Idea + Experimental Log。
- 提取完整研究设计
- 重建实验设置（参数、数据集、评估指标）
- 不包含真实实验结果（留给模型运行产生）

完整方法论见 `references/pwbench-reverse-engineer.md`。

---

## 输入契约

| 字段 | 类型 | 必需 | 默认 | 说明 |
|------|------|:----:|------|------|
| `paper_content` | string | ✅ | — | 论文全文或摘要 |
| `schema` | dict | ❌ | 4域默认 | 自定义提取schema |
| `mode` | string | ❌ | `standard` | `standard` 或 `pwbench` |
| `output_path` | string | ❌ | `outputs/{slug}/07-quality/knowledge.json` | 保存路径 |

## 输出契约

```json
{
  "meta": {
    "title": "论文标题",
    "authors": ["作者列表"],
    "doi": "10.xxxx",
    "extraction_mode": "standard|pwbench",
    "extracted_at": "ISO时间戳",
    "source": "markdown_extracted|pdf_text|abstract"
  },
  "entities": [
    {"name": "...", "type": "...", "aliases": [...], "provenance": {...}}
  ],
  "relations": [
    {"source": "...", "target": "...", "relation": "...", "provenance": {...}}
  ],
  "claims": [
    {"claim": "...", "type": "...", "confidence": "...", "evidence_refs": [...], "provenance": {...}}
  ],
  "evidence": [
    {"evidence": "...", "type": "...", "value": null, "unit": null, "provenance": {...}}
  ],
  "summary": "结构化摘要（200字内）",
  "quality_score": {
    "dimensions": {"gap_significance": 0.0, ...},
    "composite": 0.0,
    "pass": true|false
  },
  "evidence_chain": [
    {"source_type": "doi", "source_ref": "<DOI>", "fetch_time": "<ISO>"}
  ]
}
```

---

## 陷阱（Pitfalls）

| # | 陷阱 | 正确做法 |
|:-:|:-----|:---------|
| 1 | **跳过局限性提取** — 只提取正面发现，忽略论文的 Limitations 部分 | 局限性是下游 HYP 发现研究空白的关键输入，必须提取 |
| 2 | **数值声明无位置标注** — 只写"文中提到准确率95%"但不标来源位置 | 数值声明必须标注 section/figure/table，不可模糊 |
| 3 | **混淆主观与客观** — 将作者推测（"X may be due to Y"）当作事实断言 | 必须标注置信度（stated/suggested/speculated） |
| 4 | **跨论文污染** — 一次提取多篇论文 | 本原子只做单篇提取。多篇比较是 ASC 的职责 |
| 5 | **生成式幻觉** — 在提取中添加原文没有的内容 | 所有输出必须可追溯到原文具体句子，用 provenance 锁定 |
| 6 | **pwbench 模式混入实验结果** — 逆向工程时错误包含了实验数据 | Sparse/Dense Idea 不允许包含实验结果——这是留给模型自行运行验证的 |
| 7 | **忘记保存 JSON** — 提取后只在对话中输出，未持久化 | 必须保存到 `outputs/{paper_dir}/07-quality/knowledge.json` |
|| 8 | **摘要不够用** — 只读了摘要就提取，错失全文细节 | 优先读全文 PDF，用 markitdown 转 Markdown。摘要只能用于快速筛选 |
|| 9 | **只用了 pdftotext 丢失表格和结构** — 表格列被打散，数值证据不准；标题层级模糊，section 标注靠猜 | 优先用 `markitdown`（保留 Markdown 结构），失败才回退 `pdftotext -layout` |

---

## 验证清单

- [ ] 输入已验证：paper_content 非空，有来源标记
- [ ] 加载方式已尝试 markitdown → 失败才回退 pdftotext
- [ ] meta.source 正确标记（markdown_extracted / pdf_text / abstract）
- [ ] 四域完整：entities, relations, claims, evidence 均有数据
- [ ] 置信度区分：所有 claim 标注了 stated/suggested/speculated
- [ ] 数值有位置：所有数值声明标注了 section/figure/table
- [ ] 可追溯：每条 claim 有 provenance（原文句子引用）
- [ ] 无跨论文：未在一份输出中包含多篇论文
- [ ] 质量评分：composite ≥ 0.70 则标记为 PASS
- [ ] 已保存：JSON 写入 07-quality/knowledge.json
- [ ] pwbench 模式：Idea 不含任何实验数据

## 边界声明

- 本原子只做**单篇论文**结构化提取，不做跨论文比较
- 不生成假设（那是 HYP 的职责）
- 不构建论证（那是 ARG 的职责）
- 不验证观点正误（那是 VER 的职责）
- PW-Bench 逆向工程不改变"单论文结构化提取"的核心定位

## 相关文件

- `references/IO_CONTRACT.md` — 输入输出契约细节
- `references/EVIDENCE_SCHEMA.md` — 证据链节点结构
- `references/BOUNDARY.md` — 边界声明的正式版本
- `references/knowledge-entry-rubric.md` — 六维质量评分标准
- `references/pwbench-reverse-engineer.md` — PW-Bench 逆向工程完整方法论
- `references/CHANGE_LOG.md` — 变更记录
