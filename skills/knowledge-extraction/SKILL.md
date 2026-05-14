---
name: knowledge-extraction
description: Extract structured knowledge from academic paper metadata and abstracts. Returns structured JSON with per-paper findings, methodology classification, domain tags, limitations, and field-level summary. Use when upstream knowledge-acquisition has returned raw_papers and structured extraction is needed before association discovery.
license: MIT
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "0.1.0"
  synthos_skill_md_hash: "51b3b4ade3128abd12b46e05e197ad7308b52259d3e313e3a01051d3a69157ed"
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
  synthos_mechanical_atoms: ""
  synthos_depends_on: "knowledge-acquisition"
  synthos_author: "Synthos Agent"
allowed-tools: Read Write
metadata:
  synthos_data_access_level: "redacted"

# 知识提取 (Knowledge Extraction)

## 1. 职责（Scope）

从上游 `knowledge-acquisition` 产出的 `raw_papers` 中，逐论文提取结构化知识：核心发现、研究方法分类、领域标签、研究局限、主题关键词。输出 `extracted_knowledge`（单论文粒度）和 `field_summary`（跨论文领域摘要）。

本原子**不做**跨论文比较（那是 `association-discovery` 的职责），**不做**假设生成（那是 `hypothesis-generation` 的职责）。它只回答一个问题：**"这篇论文说了什么？"**

## 2. 输入输出（Contract Summary）

详见 `references/IO_CONTRACT.md`。

| 方向 | 字段 | 来源 |
|------|------|------|
| 输入 | `raw_papers` (list[Paper]) | 上游 `knowledge-acquisition` |
| 输出 | `extracted_knowledge` (list[KnowledgeItem]) | 本原子生成 |
| 输出 | `field_summary` (FieldSummary) | 本原子生成 |

## 3. 推理流程（Procedure）

1. **读取输入**：检查 `input_dict` 中是否存在 `raw_papers`。若为空或不存在，返回 `_err("Missing raw_papers")`。
2. **逐论文提取**：对每篇论文执行以下子步骤：
   a. 从 `title` + `abstract` 中识别**核心发现**（寻找结果性陈述：found/show/demonstrate/reveal/indicate + 具体效应）。
   b. 分类**研究方法**：匹配13种方法论模式（RCT、cohort、cross-sectional、machine_learning、eye_tracking 等），见 `references/IO_CONTRACT.md` 的枚举。
   c. 判定**研究领域**：从关键词和摘要上下文映射到9个领域之一（neurology、psychiatry、pediatrics 等）。
   d. 提取**研究局限**：作者声明或可推断的局限性。
   e. 标注**主题标签**：诊断、治疗、机制、风险评估、评估工具等。
   f. 估算**证据等级**：meta_analysis > rct > cohort > cross_sectional > case_series > expert_opinion。
3. **跨论文摘要**：汇总所有逐论文提取结果，产出 `field_summary`：
   - 主要方法论分布
   - 聚合主题（注明频次）
   - 初步矛盾点
   - 初步知识空白
4. **构建证据链**：每个 KnowledgeItem 的证据节点引用其来源论文的 DOI。详见 `references/EVIDENCE_SCHEMA.md`。
5. **输出**：返回 `_ok({"extracted_knowledge": [...], "field_summary": {...}})` 信封。

## 4. 边界判断（When NOT to use this atom）

详见 `references/BOUNDARY.md`。典型排除场景：
- 如果只需要论文的标题/DOI，不需要结构化提取 → 直接用 `raw_papers`，不调用本原子。
- 如果需要跨论文比较或关联分析 → 这是 `association-discovery` 的职责，本原子只提供结构化输入。
- 如果输入是 PDF 文件路径（而非已解析的元数据） → 需要机械原子 `pdf_parser`，不在本原子范围内。
- **如需从论文逆向工程重构研究设计**（PW-Bench 的 Sparse Idea / Dense Idea / Experimental Log）→ 本原子的**可选增强模式**，见 `references/pwbench-reverse-engineer.md`。

## 5. 证据链输出要求（Evidence Summary）

详见 `references/EVIDENCE_SCHEMA.md`。每个 `KnowledgeItem` 必须携带：
- `source_type: "doi"`, `source_ref: "<DOI>"`, `note: "Extracted from abstract"`
- 如果论文无 DOI，使用 `source_type: "atom_output"`, `source_ref: "raw_papers[index]"`

## 6. 示例（Minimal Example）

**输入**：
```json
{
  "raw_papers": [
    {
      "title": "AI-based eye tracking for ADHD screening",
      "doi": "10.3389/fpsyt.2023.1260031",
      "abstract": "OBJECTIVE: To explore AI-based eye tracking for ADHD screening... RESULTS: CNN model reliably discriminated ADHD (n=112) from TD (n=325)...",
      "year": 2023,
      "authors": ["Chen X", "Wang S"],
      "source": "pubmed"
    }
  ]
}
```

**输出**（简化）：
```json
{
  "extracted_knowledge": [{
    "id": "10.3389/fpsyt.2023.1260031",
    "title": "AI-based eye tracking for ADHD screening",
    "key_findings": ["CNN model reliably discriminated ADHD (n=112) from TD (n=325)"],
    "methodology": "cross_sectional_comparative",
    "domain": "pediatric_psychiatry",
    "limitations": ["Binary classification only", "No external validation"],
    "key_themes": ["ai_screening", "child_adhd"],
    "evidence_level": "cross_sectional"
  }],
  "field_summary": {
    "total_papers_processed": 1,
    "dominant_methodologies": ["cross_sectional_comparative"],
    "key_themes_aggregated": ["ai_screening (1)"],
    "knowledge_gaps": ["No subtype classification"]
  }
}
```

## 7. 参考文件索引（References）

- IO 契约：`references/IO_CONTRACT.md`
- 证据链 schema：`references/EVIDENCE_SCHEMA.md`
- 边界证明：`references/BOUNDARY.md`
- 金标准：`golden/GOLDEN_SET.md`
- 变更日志：`references/CHANGE_LOG.md`
- **[PW-Bench吸收] 逆向工程方法论**：`references/pwbench-reverse-engineer.md`
