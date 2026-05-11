---
name: hypothesis-generation
description: Generate testable research hypotheses based on literature analysis. Evaluates novelty, reasonableness, and testability of each hypothesis. Returns structured hypotheses with reasoning chains. Use when the user asks to propose research ideas, generate hypotheses, brainstorm research directions, or identify novel approaches in a specific field.
license: MIT
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "1.1.0"
  synthos_skill_md_hash: "pending"
  synthos_model_version_pin: "deepseek/deepseek-v4-pro@2026-05-11"
  synthos_model_tested_on: "2026-05-10T00:00:00Z"
  synthos_io_contract_ref: "references/IO_CONTRACT.md"
  synthos_evidence_schema_ref: "references/EVIDENCE_SCHEMA.md"
  synthos_golden_set_ref: "golden/GOLDEN_SET.md"
  synthos_golden_set_origin: "self_defined"
  synthos_pass_threshold: "0.70"
  synthos_boundary_proof_ref: "references/BOUNDARY.md"
  synthos_change_log_ref: "references/CHANGE_LOG.md"
  synthos_asserted_compliance: "P0,P1,P2"
  synthos_mechanical_atoms: ""
  synthos_depends_on: "association-discovery"
  synthos_author: "Synthos Agent"
allowed-tools: delegate_task Read Write Execute
---

# 假设生成 (Hypothesis Generation)

## 1. 职责（Scope）

基于上游 `association-discovery` 产出的 `associations`（跨论文关联分析结果）和识别的 `research_gaps`（研究空白），生成可检验的研究假设。每个假设附带：唯一 ID、假设文本、推理依据、来源追溯、新颖性评分、可行性评分、可检验性评估。

本原子**不做**关联发现（那是 `association-discovery` 的职责），**不做**论证表达（那是 `argument-expression` 的职责）。它只回答一个问题：**"基于已知的关联和空白，可以提出什么新假设？"**

## 2. 输入输出（Contract Summary）

详见 `references/IO_CONTRACT.md`。

| 方向 | 字段 | 来源 |
|------|------|------|
| 输入 | `associations` (list[Association]) | 上游 `association-discovery` |
| 输入 | `research_gaps` (list[ResearchGap]) | 上游 `association-discovery` |
| 输出 | `hypotheses` (list[Hypothesis]) | 本原子生成 |

## 3. 推理流程（Procedure）

1. **读取输入**：检查 `input_dict` 中是否存在 `associations` 和 `research_gaps`。若两者均为空或不存在，返回 `_err("Missing associations and research_gaps")`。
2. **分析空白与关联模式**：对每个 `research_gap`，检查其关联的 `associations` 条目。识别空白类型（知识空白、方法空白、人群空白、矛盾空白）。
3. **生成候选假设**：对每个空白生成 1-3 个候选假设。使用以下生成策略：
   a. **第一性原理**：从基本事实和原理推导可能的解释。
   b. **类比推理**：跨领域类比启发新方向。
   c. **贝叶斯思维**：基于先验概率（已有文献支持度）更新假设可能性。
4. **CRISP-DM 组成模板**（v1.1 新增——吸收自 KILO-KIT CBU 模式）：对每个高分假设（novelty ≥ 0.6），生成一个 CRISP-DM 实验设计方案作为 `crispdm_plan` 字段：
   a. **业务理解（Business Understanding）**：假设的科研背景和预期价值
   b. **数据理解（Data Understanding）**：需要收集什么数据，现有数据是否足够
   c. **数据准备（Data Preparation）**：数据清洗、特征工程方案
   d. **建模（Modeling）**：选择什么方法/模型验证假设
   e. **评估（Evaluation）**：用什么指标衡量假设是否成立
   f. **部署（Deployment）**：如果验证成功，如何转化临床应用或进一步研究
5. **评分与排序**：对每个假设进行三维评分：
   a. **新颖性评分** (0-1)：与现有文献对比的原创程度。≥0.6 认为有新颖性。
   b. **可行性评分** (0-1)：研究实施的现实可行性。≥0.5 认为可行。
   c. **可检验性** (testable/partially_testable/not_testable)：是否可通过实验或观察验证。
6. **构建证据链**：每个 Hypothesis 的 `source` 字段引用其依据的 association ID 或 research_gap ID。详见 `references/EVIDENCE_SCHEMA.md`。
7. **输出**：返回 `_ok({"hypotheses": [...]})` 信封，按 `novelty_score * feasibility_score` 降序排列。

## 4. 边界判断（When NOT to use this atom）

详见 `references/BOUNDARY.md`。典型排除场景：
- 如果用户只需要跨论文比较或关联分析 → 这是 `association-discovery` 的职责，不需要本原子。
- 如果用户只需要将已有假设写成论文段落 → 这是 `argument-expression` 的职责，不需要本原子。
- 如果输入中没有任何研究空白（全部已知）→ 本原子产出可能为空或仅包含低新颖性假设。
- 如果任务是验证已有假设 → 应使用 `viewpoint-verification`，而非本原子。

## 5. 证据链输出要求（Evidence Summary）

详见 `references/EVIDENCE_SCHEMA.md`。每个 `Hypothesis` 必须携带：
- `source`: 引用上游 `Association.id` 或 `ResearchGap.id`
- `rationale`: 推理过程文本，说明假设如何从关联/空白推导而来
- 证据链节点类型：`atom_output`（引用上游原子输出）

## 6. 示例（Minimal Example）

**输入**：
```json
{
  "associations": [
    {
      "id": "assoc_001",
      "type": "contradiction",
      "paper_a": "10.3389/fpsyt.2023.1260031",
      "paper_b": "10.1002/pcn5.70095",
      "description": "Paper A finds eye tracking effective for ADHD screening; Paper B finds no significant difference vs. clinical interview",
      "strength": 0.65
    }
  ],
  "research_gaps": [
    {
      "id": "gap_001",
      "description": "No study compares eye tracking metrics across ADHD subtypes (inattentive vs. hyperactive-impulsive vs. combined)",
      "type": "knowledge_gap",
      "related_associations": ["assoc_001"]
    }
  ]
}
```

**输出**（简化）：
```json
{
  "hypotheses": [
    {
      "id": "hyp_001",
      "text": "Eye tracking saccade metrics differ significantly across ADHD subtypes, with hyperactive-impulsive subtype showing greater saccade variability than inattentive subtype",
      "rationale": "The contradiction between Paper A and B may be explained by unaccounted subtype heterogeneity. If eye tracking effectiveness varies by subtype, this would explain inconsistent results.",
      "source": "gap_001",
      "novelty_score": 0.72,
      "feasibility_score": 0.65,
      "testability": "testable"
    },
    {
      "id": "hyp_002",
      "text": "Combining eye tracking metrics with continuous performance test scores improves ADHD screening accuracy beyond either method alone",
      "rationale": "Association assoc_001 shows inconsistent unimodal results. Multi-modal approaches often outperform single modalities in clinical screening.",
      "source": "assoc_001",
      "novelty_score": 0.55,
      "feasibility_score": 0.80,
      "testability": "testable"
    }
  ]
}
```

## 7. 质量要求

- **新颖性**：假设的原创程度（与现有文献对比）
- **合理性**：与现有知识的逻辑一致性
- **可检验性**：假设是否可以通过实验/观察验证
- **明确性**：假设表述是否清晰具体，包含可操作变量

## 8. 约束

- 必须基于已有关联和空白，不得凭空捏造
- 必须说明推理过程（rationale 字段）
- 必须评估新颖性和可行性（评分 0-1）
- 每个假设必须有唯一 ID

## 9. 失败模式

- **无新颖假设** → 扩大关联分析范围或引入跨领域知识
- **假设不可检验** → 重新表述为可操作假设，降低抽象层级
- **评分虚高** → 交叉验证评分，提供评分依据

## 10. 依赖

- 上游：`association-discovery`
- 下游：`argument-expression`、`viewpoint-verification`

## 11. Synthos 维度

- **第一性原理**：从基本事实和原理推导
- **类比**：跨领域类比启发
- **贝叶斯思维**：基于先验概率更新

## 12. 注意事项

从关联到假设的飞跃——这是核心创新环节，需要最大的人类监督。假设质量直接决定下游产出的学术价值。

## 13. 参考文件索引（References）

- IO 契约：`references/IO_CONTRACT.md`
- 证据链 schema：`references/EVIDENCE_SCHEMA.md`
- 边界证明：`references/BOUNDARY.md`
- 金标准：`golden/GOLDEN_SET.md`
- 变更日志：`references/CHANGE_LOG.md`
