---
name: viewpoint-verification
description: "Multi-angle verification of hypotheses and arguments: counterarguments, falsification tests, robustness checks, and weakness identification. Calculates Bayesian-inspired confidence scores and returns structured verdicts. Use when the user asks to validate a hypothesis, find counterarguments, test a claim, check for bias, evaluate argument strength, or perform a literature-based sanity check on a research idea."
license: MIT
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "0.1.0"
  synthos_skill_md_hash: "9224c10a88b51ce0bda48e8ecebd687027ead6cf02ab2f75eaa338c88d6439ac"
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
  synthos_depends_on: "hypothesis-generation,argument-expression"
  synthos_author: "Synthos Agent"
allowed-tools: Read Write
---

# 观点验证 (Viewpoint Verification) — 认知原子 #6

## 1. 职责（Scope）

对上游 `hypothesis-generation` 产出的 `hypotheses` 和 `argument-expression` 产出的 `arguments` 进行多角度批判性验证：寻找反方观点（counterarguments）、设定证伪条件（falsification conditions）、评估鲁棒性（robustness concerns）、识别内部弱点（weaknesses）。计算贝叶斯启发式置信度评分，并给出结构化裁决（verdict）。

本原子**不做**假设生成（那是 `hypothesis-generation` 的职责），**不做**论证撰写（那是 `argument-expression` 的职责），**不做**跨论文关联发现（那是 `association-discovery` 的职责）。它只回答一个问题：**"这个主张有多可靠？什么条件下它会失败？"**

## 2. 输入输出（Contract Summary）

详见 `references/IO_CONTRACT.md`。

| 方向 | 字段 | 来源 |
|------|------|------|
| 输入 | `hypotheses` (list[Hypothesis]) | 上游 `hypothesis-generation` |
| 输入 | `arguments` (list[Argument]) | 上游 `argument-expression` |
| 输入 | `evidence` (list[EvidenceNode]) | 上游证据链（可选） |
| 输出 | `verification_results` (list[Verification]) | 本原子生成 |
| 输出 | `aggregate_confidence` (AggregateConfidence) | 本原子生成 |
| 输出 | `verdict` (string) | 本原子生成 |

## 3. 推理流程（Procedure）

1. **读取输入**：检查 `input_dict` 中是否存在 `hypotheses`。若为空或不存在，返回 `_err("Missing hypotheses")`。`arguments` 和 `evidence` 为可选增强输入。

2. **逐假设验证**：对每个 hypothesis 执行以下子步骤：

   a. **寻找反方观点（Counterarguments）**：
      - 检查上游 `evidence` / `extracted_knowledge` 中是否存在矛盾发现
      - 匹配6类反方观点模式：直接矛盾、替代解释、方法论批判、证据空白、普适性挑战、选择偏差
      - 评估每个反方观点的力度（strength: 0.0–1.0）
      - 如果无外部证据，生成逻辑推理型反方观点（标记 `[INFERRED]`）

   b. **设定证伪条件（Falsification Conditions）**：
      - 为每个假设定义可操作的证伪条件（具体的测量指标 + 阈值）
      - 遵循 Popper 精神：什么观测结果会证明假设为假？
      - 每个证伪条件必须可操作（可被实验检验）

   c. **鲁棒性评估（Robustness Concerns）**：
      - 检查假设在不同条件下的稳定性（样本、方法、人群、时间）
      - 识别假设依赖的隐含前提（如正态性假设、线性假设）
      - 标注条件变化时假设可能失效的场景

   d. **弱点识别（Weaknesses）**：
      - 检查假设自身的逻辑一致性
      - 识别循环推理、概念混淆、因果方向不明等内部缺陷
      - 检查证据支持的充分性和质量

   e. **置信度计算（Confidence Score）**：
      - 先验置信度 = 0.7（中性先验，可被证据调整）
      - 每个有效反方观点（strength ≥ 0.3）扣 0.05–0.15（根据 strength 线性映射）
      - 每个内部弱点扣 0.08
      - 每个未解决的鲁棒性关切扣 0.05
      - 证据质量评分作为置信度上限
      - 最终置信度裁剪至 [0.0, 1.0]

   f. **裁决（Verdict）**：
      - `supported`：confidence ≥ 0.80，无强反方观点
      - `partially_supported`：0.50 ≤ confidence < 0.80
      - `insufficient_evidence`：confidence < 0.50 且主要原因是证据不足
      - `likely_false`：confidence < 0.30 且有强反方观点
      - `requires_revision`：confidence < 0.40 且主要原因是内部逻辑矛盾

3. **聚合**：汇总所有 Verification，计算 `aggregate_confidence`（均值、最小值、分布），给出整体 `verdict`。

4. **构建证据链**：每个 counterargument、falsification_condition、robustness_concern 的证据节点见 `references/EVIDENCE_SCHEMA.md`。

5. **输出**：返回 `_ok({"verification_results": [...], "aggregate_confidence": {...}, "verdict": "..."})` 信封。

## 4. 边界判断（When NOT to use this atom）

详见 `references/BOUNDARY.md`。典型排除场景：
- 如果用户想要生成新假设 → 这是 `hypothesis-generation` 的职责
- 如果用户想要撰写论证文本 → 这是 `argument-expression` 的职责
- 如果用户想要发现跨论文关联 → 这是 `association-discovery` 的职责
- 如果用户只想要论文信息而不评估主张 → 直接用 `knowledge-extraction` 输出即可

## 5. 证据链输出要求（Evidence Summary）

详见 `references/EVIDENCE_SCHEMA.md`。每个 `Verification` 必须携带：
- `CounterArgument` → `source_type: "doi"` | `"atom_output"` | `"reasoning"`
- `falsification_condition` → `source_type: "falsification_test"`
- `robustness_concern` → `source_type: "robustness_check"`
- 逻辑推理型反方观点必须在 `note` 中标注 `[INFERRED]`
- 如果无法找到外部反方证据，置信度上限 ≤ 0.6

## 6. 示例（Minimal Example）

**输入**：
```json
{
  "hypotheses": [
    {
      "id": "H1",
      "statement": "AI-based eye tracking can replace clinical interviews for ADHD screening in children",
      "rationale": "CNN model achieved 0.89 AUC in discriminating ADHD (n=112) from TD (n=325)",
      "novelty_score": 0.7,
      "testability_score": 0.8,
      "source_gaps": ["No subtype classification", "No external validation"]
    }
  ],
  "arguments": [
    {
      "id": "A1",
      "claim": "Eye tracking is objective and scalable compared to subjective clinical interviews",
      "premises": ["Clinical interviews rely on subjective judgment", "Eye tracking provides quantitative metrics"],
      "evidence_chain": [],
      "section": "introduction"
    }
  ]
}
```

**输出**（简化）：
```json
{
  "verification_results": [
    {
      "hypothesis_id": "H1",
      "counterarguments": [
        {
          "statement": "Clinical interviews capture functional impairment context that eye tracking cannot measure",
          "type": "alternative_explanation",
          "strength": 0.7,
          "source": "reasoning"
        },
        {
          "statement": "AUC of 0.89 in small single-site sample (n=112) may not generalize; external validation needed",
          "type": "generalizability_challenge",
          "strength": 0.8,
          "source": "atom_output"
        }
      ],
      "falsification_conditions": [
        "H1 is falsified if external validation (n >= 500, multi-site) yields AUC < 0.75",
        "H1 is falsified if eye tracking fails to detect inattentive-subtype ADHD (sensitivity < 0.70)"
      ],
      "robustness_concerns": [
        "Model performance may degrade under different lighting conditions or eye tracker hardware",
        "CNN decision boundaries may not align with clinical diagnostic criteria",
        "Sample imbalance (112 ADHD vs 325 TD) may inflate AUC"
      ],
      "weaknesses": [
        "Confuses 'can discriminate' with 'can replace clinical interviews' — diagnostic triage is not replacement",
        "No comparison against existing screening tools provided"
      ],
      "confidence_score": 0.45,
      "verdict": "insufficient_evidence"
    }
  ],
  "aggregate_confidence": {
    "mean_confidence": 0.45,
    "min_confidence": 0.45,
    "confidence_distribution": "uniform",
    "overall_verdict": "insufficient_evidence"
  },
  "verdict": "insufficient_evidence"
}
```

## 7. 参考文件索引（References）

- IO 契约：`references/IO_CONTRACT.md`
- 证据链 schema：`references/EVIDENCE_SCHEMA.md`
- 边界证明：`references/BOUNDARY.md`
- 金标准：`golden/GOLDEN_SET.md`
- 变更日志：`references/CHANGE_LOG.md`
