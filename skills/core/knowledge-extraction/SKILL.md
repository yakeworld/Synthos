---


name: knowledge-extraction
description: "Directory index for knowledge-extraction: knowledge-extraction"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "paper_content: str, schema: dict -> structured_knowledge: dict (entities, relations, claims, evidence)"
    atom_type: skill
    priority: P1
    related_skills: [knowledge-acquisition, paper-knowledge-extraction]
---





# Knowledge Extraction

详细内容请加载此skill后按需执行。核心流程和命令已提炼如下：

## 快速参考

详细文档和完整命令列表已被移至 `references/` 目录以保持简洁。
This skill has been compressed. Full content is available in references/.

## IO_CONTRACT

- **input**: `paper_text: str, query_focus: str`
- **output**: `extracted: list[KnowledgeExtract]` — 包含 topic, method, dataset, metric, result, confidence, source, quote

> 对应原则：P2（机械原子暴露输入输出规范）

---

## Knowledge Entry Generation Mode

This skill also governs the **knowledge_entry** step of the research pipeline (step 4/4: literature_scan → gap_analysis → hypothesis_generation → **knowledge_entry**). When loaded for knowledge_entry generation, produce a synthesis document that integrates the outputs of all prior steps.

### IO_CONTRACT (knowledge_entry mode)

- **input**: `candidate_id: str, hypothesis_generation_output: dict, gap_analysis_output: dict, literature_scan_output: dict` — outputs from all 3 prior pipeline steps
- **output**: `knowledge_entry: dict` — markdown file with 9 required sections, 6-dimension quality score

### Required Sections

A knowledge_entry markdown file MUST contain the following sections in order:

| # | Section | Content | Source |
|:-:|:--------|:--------|:-------|
| 1 | **Pipeline Completion Summary** | Table with step scores (literature_scan, gap_analysis, hypothesis_generation, knowledge_entry) + score evolution (HG→KE delta + rationale) | All prior steps |
| 2 | **6-Dimension Quality Scoring** | Weighted scoring table with 6 dimensions (see reference `knowledge-entry-rubric.md`). Each dimension needs score + rationale paragraph. Show weighted total calculation. | Novel synthesis |
| 3 | **Domain Overview** | Natural history of the physiological system (3-5 paragraphs), clinical problem table (condition, prevalence, existing metric, gap), white space statement, "why now" justification | literature_scan + gap_analysis |
| 4 | **Model Architecture** | 2-ODE+PINN description: ODE-1 and ODE-2 dynamics (state vars, parameters, key behavior). ASCII diagram or equation blocks. Multi-scale temporal assessment table. Cross-ODE identifiability confound analysis (detection→assessment→mitigation→residual). | gap_analysis |
| 5 | **Entity Extraction** | Two tables: (a) Entities — name, type, description for all physiological systems, diseases, parameters, devices, kernels; (b) Relations — source, relation, target for structural_analog/neighbor, clinical_biomarker, integrates, etc. | All prior steps |
| 6 | **Hypothesis Portfolio** | Ranked table (rank, ID, title, composite, recommendation) + detailed description of primary hypothesis (statement, population, measurement, endpoint, rejection criteria, rationale) + discriminative experiment design (Pattern #5 phase table) | hypothesis_generation |
| 7 | **Kernel Registration** | Structured table: kernel ID, name, type, domain, state/parameters, dynamics, clinical inputs, connected kernels, unique contribution, clinical conditions | Novel synthesis |
| 8 | **Clinical Translation & Market** | Phase 1-4 pathway table (timeline, activity, success criterion). Addressable populations table (population, size, current test, PINN advantage). Zero-equipment justification. | gap_analysis + hypothesis_generation |
| 9 | **Critical Assessment & Limitations** | Star-rating table (novelty, data feasibility, clinical impact, model complexity, parameter identifiability, reproducibility) + key risks (3-5 items, each with mitigation). Pipeline completion summary (domain expansion trajectory, next actions). | All prior steps |

### Score Evolution Pattern

The knowledge_entry's 6-dimension weighted score is systematically 1-4% below the hypothesis_generation step score. This is EXPECTED and normal — the 6D rubric weights conservative dimensions (Methodological Soundness 0.20, Reproducibility 0.10) that don't appear in the 5-dimension hypothesis scoring rubric.

| State of gap_analysis | Typical Δ (HG → KE) | Notes |
|:---------------------|:-------------------:|:------|
| PASS (≥0.85) | −1 to −3 points | 6D rubric restores conservative judgment |
| CONDITIONAL (0.65-0.78) | −2 to −4 points | Larger delta because methodological concerns get more weight in 6D |

### 6-Dimension Quality Scoring Rubric

See `references/knowledge-entry-rubric.md` for the full rubric with detailed scoring criteria per dimension per score band.

### Examples

Existing knowledge_entry files follow this exact format. Reference examples:
- `outputs/papers/_knowledge_only/cochlear-mechanics-PINN/knowledge_entry_cochlear-mechanics-PINN.md` (auditory, K-013)
- `outputs/papers/_knowledge_only/baroreflex-regulation-PINN/knowledge_entry_baroreflex-regulation-PINN.md` (cardiovascular, K-010)
- `outputs/papers/_knowledge_only/respiratory-sinus-arrhythmia-PINN/knowledge_entry_respiratory-sinus-arrhythmia-PINN.md` (cardiopulmonary, K-011)
- `outputs/papers/_knowledge_only/vocal-fold-phonation-PINN/knowledge_entry_vocal-fold-phonation-PINN.md` (laryngeal, K-014 — most recent example)

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
