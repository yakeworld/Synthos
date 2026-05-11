# Synthos 原子 I/O Schema 全集 v1.0

> 地位：**原子层契约**。6个认知原子 + 1个路由器的 input_schema / output_schema 整体敲定。
> 所有原子 SKILL.md 必须以此文件为 I/O 规范的唯一权威来源。
> 
> 设计原则：原子之间通过 schema 解耦——上游只承诺输出 shape，下游只依赖输入 shape。

---

## 0. 路由器（Task Router）

**类型**: COGNITIVE  
**职责**: 解析用户 query → 判定复杂度 → 输出最短原子链。  
**P0要求**: output 包含 routing_rationale（路径选择理由）。

### input_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `query` | string | ● | 用户自然语言请求 |

### output_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `task_type` | string (enum) | ● | `"literature_search"` \| `"research_analysis"` \| `"academic_writing"` \| `"full_verification"` \| `"general_research"` |
| `complexity` | string (enum) | ● | `"simple"` \| `"medium"` \| `"complex"` \| `"full"` |
| `atom_chain` | list[string] | ● | 有序原子名列表，如 `["knowledge-acquisition", "knowledge-extraction", "association-discovery"]` |
| `skip_reasons` | list[string] | ● | 每个被跳过原子的跳过理由 |

> **注**: `routing_rationale` 不在路由器 output 中。路径选择理由由组合层 Pipeline 在记录 CallGraph 时生成（`ctx.record_routing(rationale=...)`），不属原子职责。路由器只负责"判定走哪条链"，不负责"解释为什么走这条链"——解释是组合层的 P0 责任。

### 非重叠性证明

路由器的唯一职责是"决定走哪条链"。它不产生研究数据（不进入 evidence_chain 数据流），不执行认知操作。与其他6个认知原子的关系是**调用者-被调用者**，不存在功能重叠。

---

## 1. 知识获取（Knowledge Acquisition）

**类型**: MECHANICAL  
**职责**: 多源学术搜索 → 返回论文元数据和摘要。  
**P0要求**: 每个数据源产生 evidence_chain 节点（API URL + fetch_time）。

### input_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `query` | string | ● | 搜索查询字符串（来自路由器或用户） |
| `search_query` | string | | `query` 的别名，向后兼容 |
| `sources` | list[string] | | 数据源优先级列表，默认 `["semantic_scholar", "pubmed", "crossref", "arxiv"]` |
| `max_results` | integer | | 最大返回论文数，默认 10 |
| `domain` | string | | 研究领域过滤（可选） |

### output_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `raw_papers` | list[Paper] | ● | 论文列表 |
| `metadata` | Metadata | ● | 检索元数据 |

**Paper 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `title` | string | ● | 论文标题 |
| `doi` | string | | DOI（去重主键） |
| `abstract` | string | | 摘要文本（可能为空，如PubMed不返回摘要） |
| `year` | integer | | 发表年份 |
| `authors` | list[string] | ● | 作者姓名列表 |
| `source` | string | ● | 数据来源：`"semantic_scholar"` \| `"pubmed"` \| `"crossref"` \| `"arxiv"` |

**Metadata 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `total_found` | integer | ● | 去重后的实际论文数 |
| `sources_used` | list[string] | ● | 成功返回结果的数据源列表 |
| `search_query` | string | ● | 实际执行的查询字符串 |
| `max_results_requested` | integer | ● | 请求的最大结果数 |
| `timestamp` | string | ● | ISO时间戳 |

### evidence_chain 要求

- 每个成功返回的 `sources_used` 产生一个 evidence 节点：`{source_type: "url", source_ref: "<API endpoint>?query=...", fetch_time: "..."}`
- 如果 `total_found == 0`：额外产生 `{source_type: "empty_result"}` 节点，指向 `empty_result_evidence.json`

---

## 2. 知识提取（Knowledge Extraction）

**类型**: COGNITIVE  
**职责**: 论文元数据 → 结构化知识项。  
**上游**: 原子1（知识获取）  
**P0要求**: 每个 extracted_knowledge 项的 findings 须引用来源论文的 DOI。

### input_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `raw_papers` | list[Paper] | ● | 来自原子1的 output |
| `extract_fields` | list[string] | | 需提取的字段，默认 `["methodology", "findings", "limitations", "key_themes"]` |

### output_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `extracted_knowledge` | list[KnowledgeItem] | ● | 每个论文的结构化提取结果 |
| `field_summary` | FieldSummary | ● | 跨论文的领域级摘要 |

**KnowledgeItem 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `id` | string | ● | 唯一标识（优先用DOI，否则 `item_N`） |
| `title` | string | ● | 论文标题（来自 raw_papers） |
| `abstract` | string | | 摘要（截断至500字符） |
| `key_findings` | list[string] | ● | 从摘要中提取的核心发现（每条 ≤200字符） |
| `methodology` | string | ● | 研究方法分类（如 `"cross_sectional_comparative"`） |
| `methods_detail` | string | | 研究方法的具体描述 |
| `domain` | string | ● | 研究领域分类（如 `"pediatric_psychiatry"`） |
| `limitations` | list[string] | | 论文自身声明或可推断的局限 |
| `key_themes` | list[string] | ● | 主题标签（用于后续关联发现） |
| `sample_size` | integer | | 样本量（如可获取） |
| `year` | integer | | 发表年份 |
| `evidence_level` | string | | 证据等级：`"meta_analysis"` \| `"rct"` \| `"cohort"` \| `"cross_sectional"` \| `"case_series"` \| `"expert_opinion"` \| `"dataset"` \| `"methodology"` |

**FieldSummary 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `total_papers_processed` | integer | ● | 处理的论文总数 |
| `year_range` | string | | 年份范围，如 `"2023-2026"` |
| `dominant_methodologies` | list[string] | | 按频次排序的方法列表 |
| `key_themes_aggregated` | list[string] | | 跨论文聚合的主题（注明出现频次） |
| `identified_contradictions` | list[string] | | 初步识别的矛盾点 |
| `knowledge_gaps` | list[string] | | 初步识别的研究空白 |

### 非重叠性证明 vs 原子3

原子2产出的是**单论文粒度的结构化描述**（"这篇论文说了什么"）。  
原子3产出的是**跨论文粒度的关系**（"这两篇论文之间是什么关系"）。  
边界：原子2不做跨论文比较；原子3不做单论文提取。

### evidence_chain 要求

- 每个 KnowledgeItem 的 evidence 节点：`{source_type: "doi", source_ref: "<DOI>", note: "Extracted from abstract"}`

---

## 3. 关联发现（Association Discovery）

**类型**: COGNITIVE  
**职责**: 结构化知识项 → 关联类型 + 知识图谱 + 研究空白。  
**上游**: 原子2（知识提取）

### input_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `extracted_knowledge` | list[KnowledgeItem] | ● | 来自原子2的 output |
| `field_summary` | FieldSummary | | 来自原子2的领域摘要（可选，用于加速） |

### output_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `associations` | list[Association] | ● | 知识项间的关联列表 |
| `knowledge_graph` | KnowledgeGraph | ● | 节点-边图结构 |
| `research_gaps` | list[ResearchGap] | ● | 系统识别的研究空白 |

**Association 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `type` | string (enum) | ● | `"contradiction"` \| `"supplement"` \| `"evolution"` |
| `item1` | string | ● | 关联方1的 id（引用 KnowledgeItem.id） |
| `item2` | string | ● | 关联方2的 id |
| `item1_title` | string | ● | 人类可读的引用（截断80字符） |
| `item2_title` | string | ● | 同上 |
| `description` | string | ● | 关联的自然语言描述 |
| `confidence` | float | ● | 0.0–1.0，关联的置信度 |
| `significance` | string | | 为什么这个关联重要 |

**KnowledgeGraph 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `nodes` | list[GraphNode] | ● | 节点（KnowledgeItem + 研究空白） |
| `edges` | list[GraphEdge] | ● | 边（关联） |
| `statistics` | GraphStats | ● | 图统计 |

- **GraphNode**: `{id, label, year, type: "paper"|"gap", domain}`
- **GraphEdge**: `{source, target, type, confidence}`
- **GraphStats**: `{total_nodes, total_edges, contradictions, supplements, evolutions, gaps}`

**ResearchGap 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `type` | string | ● | 空白类型标签 |
| `description` | string | ● | 人类可读的空白描述 |
| `confidence` | float | ● | 这个空白确实存在的置信度 |
| `evidence` | string | ● | 为什么判定为空白（引用具体论文或统计） |
| `priority` | string (enum) | ● | `"critical"` \| `"high"` \| `"medium"` |

### 非重叠性证明 vs 原子2/4

原子2：单论文粒度提取（不做比较）。  
原子3：跨论文粒度关联（不做提取、不做假设）。  
原子4：基于关联和空白**生成假设**（原子3不生成假设，只报告空白）。

### evidence_chain 要求

- 每个 Association 的 evidence 节点：`{source_type: "atom_output", source_ref: "extracted_knowledge", note: "引用 KnowledgeItem.id=<item1>, <item2>"}`

---

## 4. 观点生成（Hypothesis Generation）

**类型**: COGNITIVE  
**职责**: 关联 + 空白 → 可检验的研究假设。  
**上游**: 原子3（关联发现）

### input_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `associations` | list[Association] | ● | 来自原子3 |
| `research_gaps` | list[ResearchGap] | ● | 来自原子3 |
| `domain_knowledge` | string | | 用户提供的额外领域知识（可选） |

### output_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `hypotheses` | list[Hypothesis] | ● | 3–5个可检验的研究假设 |
| `metadata` | HypothesisMeta | ● | 假设集元数据 |

**Hypothesis 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `id` | string | ● | 唯一标识，如 `"H1_3d_subtype"` |
| `text` | string | ● | 假设的完整文本表述（≤500字符） |
| `rationale` | string | ● | 推理过程：基于哪个空白/关联 |
| `source` | string (enum) | ● | `"research_gap"` \| `"contradiction"` \| `"supplement"` \| `"evolution"` \| `"cross_domain_analogy"` |
| `source_ref` | string | | 引用的空白/关联的 id |
| `novelty_score` | float | ● | 0.0–1.0，假设的新颖程度 |
| `feasibility_score` | float | ● | 0.0–1.0，检验该假设的可行性 |
| `testability` | string (enum) | ● | `"highly_testable"` \| `"testable"` \| `"moderately_testable"` \| `"requires_operationalization"` |
| `required_n` | string | | 检验所需的估计样本量 |
| `crispdm_plan` | dict | | CRISP-DM实验设计方案：含business_understanding/data_understanding/data_preparation/modeling/evaluation/deployment 子字段（v1.1新增） |

**HypothesisMeta 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `total_hypotheses` | integer | ● | 生成的假设数 |
| `mean_novelty` | float | | 平均新颖性 |
| `mean_feasibility` | float | | 平均可行性 |
| `from_gaps` | integer | | 源自空白的假设数 |
| `from_contradictions` | integer | | 源自矛盾的假设数 |
| `from_other` | integer | | 源自其他来源的假设数 |

### 非重叠性证明 vs 原子3/5

原子3：报告"这里有个空白"（描述性）。  
原子4：基于空白提出"这个空白可以用这个假设来填补"（生成性）。  
原子5：将假设转化为论证文本（表达性）——原子4不写论文段落。

### evidence_chain 要求

- 每个 Hypothesis 的 evidence 节点：`{source_type: "atom_output", source_ref: "research_gaps" (或 "associations"), note: "gap_id=<id>"}`

---

## 5. 论证表达（Argument Expression）

**类型**: COGNITIVE  
**职责**: 假设 + 证据 → 结构化论文章节 + 论据链。  
**上游**: 原子4（观点生成）+ 原子1（知识获取——引用原文支持）

### input_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `hypotheses` | list[Hypothesis] | ● | 来自原子4 |
| `structure` | string (enum) | ● | `"introduction"` \| `"methods"` \| `"results"` \| `"discussion"` \| `"full_paper"` |
| `raw_papers` | list[Paper] | | 来自原子1，用于参考文献和证据引用 |
| `extracted_knowledge` | list[KnowledgeItem] | | 来自原子2，用于引用具体发现 |

### output_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `sections` | list[Section] | ● | 论文章节列表 |
| `arguments` | list[Argument] | ● | 论证链 |
| `references` | list[Reference] | | 参考文献列表 |

**Section 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `title` | string | ● | 章节标题（如 `"Introduction"`） |
| `content` | string | ● | 学术写作文本 |
| `key_claims` | list[string] | ● | 该章节的核心主张列表 |
| `word_count` | integer | | 词数估计 |

**Argument 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `claim` | string | ● | 论证主张 |
| `evidence` | list[string] | ● | 支持证据（引用具体论文或KnowledgeItem） |
| `reasoning` | string | ● | 从证据到主张的推理链 |
| `hypothesis_id` | string | | 关联的 Hypothesis.id |
| `counterargument_addressed` | string | | 主动回应的反方观点（如有） |

**Reference 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `title` | string | ● | 论文标题 |
| `doi` | string | | DOI |
| `year` | string | | 发表年份 |
| `authors` | string | | 作者列表（截断至3人+et al.） |
| `citation_key` | string | | 文内引用键（如 `Chen2023`） |

### 非重叠性证明 vs 原子4/6

原子4：生成假设（"应该研究什么"）。  
原子5：将假设表达为学术论证（"如何写成论文"）。  
原子6：验证假设和论证（"这个论证有什么漏洞"）——原子5不主动证伪自己。

### evidence_chain 要求

- 每个 Argument 的 evidence 节点：`{source_type: "atom_output", source_ref: "extracted_knowledge" (或 "raw_papers"), note: "ref=<KnowledgeItem.id>"}`

---

## 6. 观点验证（Viewpoint Verification）

**类型**: COGNITIVE  
**职责**: 假设 + 论证 → 多角度验证（反方、证伪、鲁棒性）。  
**上游**: 原子4（观点生成）+ 原子5（论证表达）

### input_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `hypotheses` | list[Hypothesis] | ● | 来自原子4 |
| `arguments` | list[Argument] | | 来自原子5（可选——可以单独验证假设） |
| `extracted_knowledge` | list[KnowledgeItem] | | 来自原子2，用于检索对立证据 |

### output_schema

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `verification_results` | list[Verification] | ● | 每个假设的验证结果 |
| `aggregate_confidence` | float | ● | 整体置信度（所有假设的平均） |
| `verdict` | string (enum) | ● | `"strongly_supported"` \| `"moderately_supported"` \| `"weakly_supported"` \| `"insufficient_evidence"` |

**Verification 子结构**：

| 字段 | 类型 | 必需 | 描述 |
|------|------|:--:|------|
| `hypothesis_id` | string | ● | 引用 Hypothesis.id |
| `hypothesis_text` | string | ● | 假设文本（截断150字符便于阅读） |
| `counterarguments` | list[string] | ● | 反方观点（至少1条） |
| `falsification_conditions` | list[string] | ● | 什么情况下这个假设被证伪（至少1条） |
| `robustness_concerns` | list[string] | ● | 跨条件/跨人群的稳定性担忧 |
| `weaknesses` | list[string] | | 假设或论证的内在弱点 |
| `confidence_score` | float | ● | 0.0–1.0，综合置信度 |
| `verdict` | string (enum) | ● | 单假设判定：`"strongly_supported"` \| `"plausible"` \| `"questionable"` |

### 非重叠性证明 vs 原子3/4/5

原子3：发现关联（"A和B有矛盾"）——不做价值判断。  
原子6：评估假设（"这个假设的反方证据充分，置信度低"）——做价值判断。  
原子4/5：正向构建；原子6：反向证伪。这是认知闭环的对称性设计。

### evidence_chain 要求

- 每个 Verification 的 evidence 节点：`{source_type: "atom_output", source_ref: "extracted_knowledge" (用于反方证据), note: "counterargument sourced from KnowledgeItem.id=<id>"}`

---

## 附录 A · 全链路数据流图

```
用户 query
  │
  ▼
[Router] ──→ CallGraph (routing_rationale)
  │
  ▼ atom_chain
[1.知识获取]  raw_papers ─────────────────────────────┐
  │                                                     │
  ▼                                                     │
[2.知识提取]  extracted_knowledge + field_summary       │
  │                                                     │
  ▼                                                     │
[3.关联发现]  associations + knowledge_graph + gaps     │
  │                                                     │
  ▼                                                     │
[4.观点生成]  hypotheses                                │
  │                                                     │
  ├──────────────────────────────────────────────────┐  │
  ▼                                                  ▼  ▼
[5.论证表达]  sections + arguments + references   (raw_papers 回引)
  │
  ▼
[6.观点验证]  verification_results + aggregate_confidence
```

## 附录 B · 非重叠性矩阵

|  | 提取 (2) | 关联 (3) | 假设 (4) | 论证 (5) | 验证 (6) |
|--|:--:|:--:|:--:|:--:|:--:|
| **提取 (2)** | — | 粒度不同 | 粒度不同 | 职责不同 | 职责不同 |
| **关联 (3)** | 粒度不同 | — | 描述 vs 生成 | 结构 vs 文本 | 发现 vs 评估 |
| **假设 (4)** | 粒度不同 | 描述 vs 生成 | — | 生成 vs 表达 | 正向 vs 反向 |
| **论证 (5)** | 职责不同 | 结构 vs 文本 | 生成 vs 表达 | — | 构建 vs 拆解 |
| **验证 (6)** | 职责不同 | 发现 vs 评估 | 正向 vs 反向 | 构建 vs 拆解 | — |

矩阵对称。所有原子对之间都有可清晰陈述的边界。

## 附录 C · Schema 版本策略

- 本文档版本号 `v1.0`。修改 schema 属于**细则演化**（见宪法第五部分第3条），走受控变更流程。
- Schema 字段的**新增**（不删除、不改变已有字段语义）→ minor 版本升级 → 下游兼容。
- Schema 字段的**删除或语义改变**→ major 版本升级 → 可能破坏下游。
- 原子自身的 `version` 字段与 schema 版本解耦——schema 版本变化的传播由 pipeline 的 Context 处理。
