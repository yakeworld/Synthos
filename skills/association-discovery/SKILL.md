---
name: association-discovery
description: "Identify relationships between knowledge items: contradictions, supplements, evolutions, supports, extends, uses, similar-to, and research gaps (P0-P3 rated). Builds knowledge graph. 7 typed edges from claude-paperloom absorption. Gap taxonomy from GAP absorption."
version: 1.3.0
author: Synthos Agent
license: MIT
allowed-tools: Read Write
signature: "knowledge_items: list[KnowledgeItem] -> associations: list[Association], research_gaps: list[Gap]"
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "1.3.0"
  synthos_skill_md_hash: "14e47ba9d49730ba31dd30c2686814b2fe4de0955e408f0f4abe5c86a4c0fa95"
  synthos_model_version_pin: "deepseek/deepseek-v4-pro@2026-05-10"
  synthos_model_tested_on: "2026-05-10T00:00:00Z"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_evidence_schema_ref: "references/EVIDENCE_SCHEMA.md"
  synthos_golden_set_ref: "golden/GOLDEN_SET.md"
  synthos_golden_set_origin: "self_defined"
  synthos_pass_threshold: "0.80"
  synthos_boundary_proof_ref: "references/BOUNDARY.md"
  synthos_change_log_ref: "references/CHANGE_LOG.md"
  synthos_asserted_compliance: "P0,P1,P2"
  synthos_depends_on: "knowledge-extraction"
  synthos_author: "Synthos Agent"
  synthos_data_access_level: "redacted"
---

# 关联发现 (Association Discovery) - 认知原子 #3

## 原理层·文言

> 「方以类聚，物以群分。」又「在天成象，在地成形，变化见矣。」
> 万物有象，象中有道。同中见异，异中求同。矛盾即机，空白即路。
> 取象通变，以观其会通。

### 联属之道

> 物以类聚，事以群分。孤立之知，不如关联之智。
> 两两相较，七型可辨：矛盾、补充、演进、支持、扩展、使用、相似。
> 聚则为图，散则为点。有联则有知，有图则有见。
> 见矛盾而知所争，见空白而知所缺。
> 联属既成，假设可生矣。

**核心理念**：关联发现是认知链的第三步。将孤立知识项两两比较，识别7种关联类型，构建知识图谱，检测研究空白。空白是假设生成的土壤——没有空白，就没有科学进步。

### 七型关联释义

| 关联类型 | 文言释名 | 含义 |
|:---------|:---------|:-----|
| contradiction | 相悖 | 结论冲突或方向相反 |
| supplement | 互补 | 同一问题的不同方面 |
| evolution | 演进 | 时序+方法论升级 |
| supports | 佐证 | 一篇为另一篇提供直接证据 |
| extends | 拓展 | 在另一篇基础上扩展范畴 |
| uses | 借用 | 直接使用另一篇的方法/数据 |
| similar-to | 相近 | 主题方法相似但独立完成 |

## 方法层·白话

### 触发条件

在以下情况加载本技能：

- 上游 knowledge-extraction 已产出 extracted_knowledge，需要发现论文间关联
- 需要构建知识图谱或检测研究空白
- 用户要求"找出这些文献之间的关系/矛盾/空白"
- 下游 hypothesis-generation 需要关联分析作为输入

### 1. 职责（Scope）

从上游 `knowledge-extraction` 产出的 `extracted_knowledge`（结构化知识项列表）中，系统性发现知识项之间的关联关系。核心任务：

- **两两比较知识项**，识别7种关联类型：矛盾（contradiction）、补充（supplement）、演进（evolution）、支持（supports）、扩展（extends）、使用（uses）、相似（similar-to）
- **构建知识图谱**：以知识项为节点、以关联为边，输出图的节点、边和统计信息
- **检测研究空白**：识别现有知识覆盖中的缺口，按优先级分类（critical / high / medium）

本原子**不做**单论文信息提取（那是 `knowledge-extraction` 的职责），**不做**假设生成（那是 `hypothesis-generation` 的职责）。它只回答一个问题：**"这些知识之间有什么关系？"**

### 2. 输入输出（Contract Summary）

详见 `references/IO_CONTRACT.md`。

| 方向 | 字段 | 来源 |
|------|------|------|
| 输入 | `extracted_knowledge` (list[KnowledgeItem]) | 上游 `knowledge-extraction` |
| 输入 | `field_summary` (FieldSummary) | 上游 `knowledge-extraction`（可选） |
| 输出 | `associations` (list[Association]) | 本原子生成 |
| 输出 | `knowledge_graph` (KnowledgeGraph) | 本原子生成 |
| 输出 | `research_gaps` (list[ResearchGap]) | 本原子生成 |

### 3. 推理流程（Procedure）

1. **读取输入**：检查 `input_dict` 中是否存在 `extracted_knowledge`。若为空或不存在，返回 `_err("Missing extracted_knowledge")`。若知识项数量 < 2，返回 `_err("Need at least 2 knowledge items")`。

2. **两两比较**：对所有知识项 pair (i, j) 执行以下子步骤：
   a. **主题重叠检测**：计算 `key_themes` 的 Jaccard 相似度，筛选有潜在关联的对（阈值 ≥ 0.1）。
   b. **关联分类**（吸收自 claude-paperloom 的7类型图谱）：对通过筛选的对，分析其关系类型：
      - **矛盾 (contradiction)**：两篇论文的核心发现相互冲突或结论方向相反（如 Paper A 报告正效应，Paper B 报告无效或负效应）
      - **补充 (supplement)**：两篇论文研究同一问题的不同方面，结果互相补充但不冲突（如 A 研究诊断，B 研究治疗）
      - **演进 (evolution)**：一篇论文在时间或方法上构成另一篇的后续发展（year 差异 + 方法论升级，如 cross_sectional → RCT）
      - **支持 (supports)**：一篇论文的发现或方法为另一篇提供直接证据支持
      - **扩展 (extends)**：一篇论文在另一篇的基础上扩展了范畴（如人群扩展、条件泛化）
      - **使用 (uses)**：一篇论文直接使用另一篇的方法、数据或框架
      - **相似 (similar-to)**：两篇论文主题/方法高度相似但独立完成（无明确引用关系）
   c. **置信度评估**：为每个关联估算 confidence（0.0–1.0），考虑因素：主题重叠度、方法论可比性、证据等级一致性、时序关系。
   d. **显著性描述**：为 `significance` 字段撰写该关联为什么重要的简短说明。

3. **构建知识图谱**：
   a. 为每个 KnowledgeItem 创建 GraphNode（`type: "paper"`）。
   b. 为每个 Association 创建 GraphEdge（`source → target`，带 type 和 confidence）。
   c. 计算 GraphStats：total_nodes, total_edges, contradictions, supplements, evolutions, supports, extends, uses, similar_to, gaps。
   
   > **常量成本链接**（吸收自 claude-paperloom）：当知识项 > 30 时，用 Jaccard 预筛选+<30候选项限制，确保第100篇论文的关联成本与第10篇相同。

4. **识别研究空白**（吸收自 GAP 结构化分类法 v0.1.0 —— GAP 原子已合并入本原子）：
   
   4.1 **矛盾检测**：对每个聚类内部和跨聚类检测4类矛盾：
   | 矛盾类型 | 检测条件 | 示例 |
   |:---------|:---------|:-----|
   | **结论矛盾** | A报告正向结果，B报告负向结果 | 药物A有效 vs 无效 |
   | **方法矛盾** | 相似方法得出不同结论 | 样本量/人群差异 |
   | **假设矛盾** | 不同的底层假设导致冲突 | 机制解释不同 |
   | **时间矛盾** | 早期结论被后期证据推翻 | 2020 vs 2025结论 |
   
   4.2 **方法论缺口检测**：检测5类系统性缺口：
   - **样本缺口（sample_gap）**：所有研究集中在特定人群，缺少其他人群
   - **技术缺口（tech_gap）**：现有方法无法测量关键变量
   - **纵向缺口（longitudinal_gap）**：只有横断面研究，缺少纵向追踪
   - **机制缺口（mechanism_gap）**：观察到现象但机制不明
   - **验证缺口（validation_gap）**：模型/算法未在独立数据集验证
   
   4.3 **未答问题提取**：从文献的"未来工作"、"局限性"部分提取显式和隐式问题：
   - **显式**：作者明确说"需要进一步研究..."
   - **隐式**：从局限性推断出的延伸问题
   
   4.4 **全局空白检测**：
   a. 检测未配对的知识项（与其他项主题相似度均 < 0.1 的孤立节点）→ 标记为潜在空白。
   b. 检测主题内部的结构性缺失（如某个 `domain` 只有 observational studies，缺乏 RCT 证据）。
   c. 检测 `field_summary.identified_contradictions` 和 `knowledge_gaps` 中未解决的矛盾或空白 → 提升优先级。
   d. 检测文献中作者声明的"未来工作"方向。

   4.5 **空白评级**（P0-P3 四维评级，吸收自 GAP 原子）：
   | 维度 | P0 | P1 | P2 | P3 |
   |:-----|:---|:---|:---|:---|
   | 重要性 | 影响领域核心范式 | 影响重要子领域 | 有价值但非核心 | 边缘增量 |
   | 时效性 | 亟需解决 | 1-2年内 | 2-5年 | 长期 |
   | 可行性 | 现有技术可解 | 需适度努力 | 需重大突破 | 理论尚不成熟 |
   | 证据基础 | ≥5篇矛盾文献 | 3-4篇 | 1-2篇 | 单篇或推测 |
   最终优先级 = max(重要性, 时效性) + feasibility modifier。

5. **构建证据链**：每个 Association 和 ResearchGap 的证据节点引用其来源 KnowledgeItem 的 id。详见 `references/EVIDENCE_SCHEMA.md`。

6. **输出**：返回 `_ok({"associations": [...], "knowledge_graph": {...}, "research_gaps": [...]})` 信封。

### 4. 边界判断（When NOT to use this atom）

详见 `references/BOUNDARY.md`。典型排除场景：

- 如果只有单篇论文，无需关联发现 → 不需要本原子，`knowledge-extraction` 的输出即可。
- 如果需要从论文中提取结构化信息 → 这是 `knowledge-extraction` 的职责，本原子只处理已结构化的知识项。
- 如果需要基于空白和关联生成可检验的假设 → 这是 `hypothesis-generation` 的职责，本原子只报告空白，不生成假设。
- 如果输入是 PDF 或原始论文元数据 → 先经过 `knowledge-acquisition` → `knowledge-extraction` 管道。
- **PW-Bench 逆向工程**（从论文重构 Idea + Experimental Log）→ `knowledge-extraction` 的**可选增强模式**，不在本原子范围内。

### 5. 证据链输出要求（Evidence Summary）

详见 `references/EVIDENCE_SCHEMA.md`。每个 `Association` 必须携带：
- `source_type: "atom_output"`, `source_ref: "extracted_knowledge"`, `note: "引用 KnowledgeItem.id=<item1_id>, <item2_id>"`

每个 `ResearchGap` 必须携带：
- `evidence` 字段引用具体论文的 KnowledgeItem.id 或统计信息，说明为什么判定为空白。

### 6. 示例（Minimal Example）

**输入**：
```json
{
  "extracted_knowledge": [
    {
      "id": "10.3389/fpsyt.2023.1260031",
      "title": "AI-based eye tracking for ADHD screening",
      "key_findings": ["CNN model reliably discriminated ADHD (n=112) from TD (n=325)"],
      "methodology": "cross_sectional_comparative",
      "domain": "pediatric_psychiatry",
      "key_themes": ["ai_screening", "child_adhd"],
      "evidence_level": "cross_sectional",
      "year": 2023
    },
    {
      "id": "10.1000/j.adhd.2024.001",
      "title": "RCT of eye-tracking-based ADHD diagnosis in adults",
      "key_findings": ["Eye-tracking biomarkers showed 89% sensitivity in RCT (n=450)"],
      "methodology": "randomized_controlled_trial",
      "domain": "psychiatry",
      "key_themes": ["eye_tracking", "adult_adhd"],
      "evidence_level": "rct",
      "year": 2024
    }
  ]
}
```

**输出**（简化）：
```json
{
  "associations": [
    {
      "type": "evolution",
      "item1": "10.3389/fpsyt.2023.1260031",
      "item2": "10.1000/j.adhd.2024.001",
      "item1_title": "AI-based eye tracking for ADHD screening",
      "item2_title": "RCT of eye-tracking-based ADHD diagnosis in adults",
      "description": "Paper 2 upgrades Paper 1's cross-sectional design to RCT, expands from child to adult population",
      "confidence": 0.85,
      "significance": "Evidence level upgrade from cross-sectional to RCT strengthens causal inference for eye-tracking biomarkers"
    }
  ],
  "knowledge_graph": {
    "nodes": [
      {"id": "10.3389/fpsyt.2023.1260031", "label": "AI-based eye tracking...", "year": 2023, "type": "paper", "domain": "pediatric_psychiatry"},
      {"id": "10.1000/j.adhd.2024.001", "label": "RCT of eye-tracking-based...", "year": 2024, "type": "paper", "domain": "psychiatry"}
    ],
    "edges": [
      {"source": "10.3389/fpsyt.2023.1260031", "target": "10.1000/j.adhd.2024.001", "type": "evolution", "confidence": 0.85}
    ],
    "statistics": {
      "total_nodes": 2,
      "total_edges": 1,
      "contradictions": 0,
      "supplements": 0,
      "evolutions": 1,
      "gaps": 0
    }
  },
  "research_gaps": [
    {
      "type": "population_gap",
      "description": "No studies on adolescent ADHD (age 13-17) for eye-tracking diagnosis",
      "confidence": 0.75,
      "evidence": "Paper 1 covers children (n=112), Paper 2 covers adults (n=450); adolescent cohort missing",
      "priority": "P1",
      "falsification_condition": "If a study covers age 13-17 ADHD-ET, this gap is closed"
    }
  ]
}
```

### 7. 参考文件索引（References）

- IO 契约：`references/IO_CONTRACT.md`
- 证据链 schema：`references/EVIDENCE_SCHEMA.md`
- 边界证明：`references/BOUNDARY.md`
- 金标准：`golden/GOLDEN_SET.md`
- 变更日志：`references/CHANGE_LOG.md`

### 验证清单

运行本技能后，确认以下检查项：

- [ ] 至少2个知识项完成了两两比较
- [ ] 识别出的关联类型在7种枚举范围内（contradiction/supplement/evolution/supports/extends/uses/similar-to）
- [ ] 每个关联有置信度评分（0.0-1.0）
- [ ] 知识图谱节点和边的结构完整
- [ ] 研究空白按P0-P3评级且附带 falsification_condition
- [ ] 常量成本链接已启用（知识项>30时使用Jaccard预筛选）

## 命令层·English

- **Signature**: `knowledge_items: list[KnowledgeItem] -> associations: list[Association], research_gaps: list[Gap]`
- **Allowed tools**: `Read`, `Write`
- **Input**: `extracted_knowledge` (list[KnowledgeItem]) from upstream `knowledge-extraction`
- **Output**: `associations` (list[Association]), `knowledge_graph` (KnowledgeGraph), `research_gaps` (list[ResearchGap])
- **Edge types**: `contradiction`, `supplement`, `evolution`, `supports`, `extends`, `uses`, `similar-to`
- **Gap priority**: P0 (paradigm-shifting) > P1 (important) > P2 (valuable) > P3 (incremental)
- **Scalability**: Jaccard pre-filter for >30 items to maintain O(n) cost
- **Do NOT**: extract single-paper info, generate hypotheses, parse PDFs
