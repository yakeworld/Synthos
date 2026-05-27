---
name: viewpoint-verification
description: "Multi-angle verification of hypotheses and arguments: counterarguments, falsification tests, robustness checks, and weakness identification. Calculates Bayesian-inspired confidence scores and returns structured verdicts. Use when the user asks to validate a hypothesis, find counterarguments, test a claim, check for bias, evaluate argument strength, or perform a literature-based sanity check on a research idea."
version: 1.3.0
author: Synthos Agent
license: MIT
allowed-tools: Read Write
signature: "hypothesis: Hypothesis, argument: Argument -> verdict: str, confidence_score: float, counterarguments: list[Counterargument]"
metadata:
  synthos_atom_type: "cognitive"
  synthos_version: "1.1.0"
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
  synthos_depends_on: "hypothesis-generation,argument-expression"
  synthos_author: "Synthos Agent"
  synthos_data_access_level: "verified_only"
---

# 观点验证 (Viewpoint Verification) - 认知原子 #6

## 原理层·文言

### 证伪之法

> 凡立论必可驳，凡假设必可证伪。不信则立，不驳则废。
> 证之以多方，验之于反例。六类反方，四维证伪。
> 置信者，证据之影也。无证则信低，有驳则疑增。
> 不专求证实，更孜孜于反证。此乃科学精神，亦认识论之基。
> 自知其不知，方为真知。

**核心理念**：观点验证是认知链的第六步，也是最终质量闸门。对假设和论证进行多角度批判性验证：寻找反方观点、设定证伪条件、评估鲁棒性、识别内部弱点。不专求证实，更孜孜于反证。

### 验证六要义

| 要义 | 文言释 | 含义 |
|:-----|:-------|:-----|
| 求反 | 求驳也 | 主动寻找反方观点而非确认 |
| 证伪 | 可破也 | 设定具体可操作的证伪条件 |
| 鲁棒 | 不迁也 | 检验假设在不同条件下的稳定性 |
| 寻弱 | 察漏也 | 识别逻辑矛盾和内部缺陷 |
| 评分 | 可信也 | 贝叶斯启发式置信度评分 |
| 反谄 | 不阿也 | 用户反驳时按协议让步，不盲目坚持 |

## 方法层·白话

### 触发条件

在以下情况加载本技能：

- 上游 argument-expression 已产出论点，需要验证其可靠性
- 用户要求"验证假设/找反证/检测偏差/评估论证强度"
- 需要对已生成的假设进行证伪检验
- 需要计算贝叶斯置信度分数

### 验证清单

- [ ] 已生成至少1个反方论点或反证条件
- [ ] 置信度评分基于证据强度计算（非主观判断）
- [ ] 弱点/局限性已明确标注
- [ ] 已应用反谄媚协议（Concession Threshold Protocol）
- [ ] 输出包含可操作的改进建议
- [ ] 无确认偏误（主动寻找了反证而非仅确认）
- [ ] **[熵减律]** 已记录 uncertainty_reduction 并写入 aggregate_confidence.verification_entropy_reduction
- [ ] **[日损]** 已执行简约性审计，标记了可选验证维度
- [ ] **[格物通理]** 每个 verification_result 包含 reasoning_path 推演路径
- [ ] **[天人合一]** 验证输出元数据中包含 observer_standpoint 声明

### 1. 职责（Scope）

对上游 `hypothesis-generation` 产出的 `hypotheses` 和 `argument-expression` 产出的 `arguments` 进行多角度批判性验证：寻找反方观点（counterarguments）、设定证伪条件（falsification conditions）、评估鲁棒性（robustness concerns）、识别内部弱点（weaknesses）。计算贝叶斯启发式置信度评分，并给出结构化裁决（verdict）。

本原子**不做**假设生成（那是 `hypothesis-generation` 的职责），**不做**论证撰写（那是 `argument-expression` 的职责），**不做**跨论文关联发现（那是 `association-discovery` 的职责）。它只回答一个问题：**"这个主张有多可靠？什么条件下它会失败？"**

### 2. 输入输出（Contract Summary）

详见 `references/IO_CONTRACT.md`。

| 方向 | 字段 | 来源 |
|------|------|------|
| 输入 | `hypotheses` (list[Hypothesis]) | 上游 `hypothesis-generation` |
| 输入 | `arguments` (list[Argument]) | 上游 `argument-expression` |
| 输入 | `evidence` (list[EvidenceNode]) | 上游证据链（可选） |
| 输出 | `verification_results` (list[Verification] + uncertainty_reduction + reasoning_path + minimal_verification + optional_dimensions) | 本原子生成 |
| 输出 | `aggregate_confidence` (AggregateConfidence + verification_entropy_reduction) | 本原子生成 |
| 输出 | `verdict` (string) | 本原子生成 |
| 输出 | `observer_standpoint` (dict) | 本原子生成（Step 0） |

### 3. 推理流程（Procedure）

**Step 0: 观察者位置声明** — 原子启动时记录认知链定位：

```yaml
observer_standpoint:
  cognitive_chain_position: 6 (ACQ→EXT→ASC→HYP→ARG→VER)
  upstream_atoms: [hypothesis-generation, argument-expression]
  downstream_atoms: [用户/paper-pipeline]
  validation_lens: "默认：批判性检验——寻找假设最脆弱的地方；可选：同行评审模拟——评估论文可发表性"
```

此声明嵌入每个验证流程的输出元数据中，确保观察者位置透明、可追溯。**不做**立场中性化承诺（那是伪客观），而是明确标注"谁在什么位置以什么透镜观察"。

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
      - **输出不确定性降低量**：`uncertainty_reduction = initial_confidence - final_confidence`
        - 记录验证前后置信度的差值，作为熵减信号
        - `uncertainty_reduction` 写入每个 `verification_result`
        - `aggregate_confidence` 增加 `verification_entropy_reduction` 字段（各假设均值）

   e.5 **[PW-Bench吸收] 引用质量修正 — Citation F1 门控**：
      - 提取当前假设/论点引用的所有参考文献
      - 使用 Python 或 LLM 对引用列表执行 P0/P1 分类（见 `references/citation-f1-methodology.md`）
      - 计算引用质量得分 = (P0数 + 0.5×P1数) / (P0数 + P1数)，空列表=0.0
      - 应用置信度修正：`confidence = confidence × min(1.0, citation_quality + 0.3)`
      - 在 verification_results.citation_quality 中记录引用质量得分
      - **注意**: 此修正仅作为弱信号，不单独触发 verdict 变化

   e.6 **[ARA吸收] 6维认识论评分校准 — Epistemic Scoring**：
      - 对当前假设/论点执行6维认识论评分（吸收自 Orchestra-Research/AI-research-SKILLs ARA Rigor Reviewer v3.0，8,492⭐）
      - 每个维度独立评分 1-5，并记录 strength/weakness/suggestion：

      | 维度 | 评估内容 | 评分标准 |
      |:-----|:---------|:---------|
      | **D1. 证据相关性** | 引用的证据是否实质支持每个主张？不仅是引用存在，而是内容对得上 | 1=无关/5=精确匹配 |
      | **D2. 可证伪性质量** | 证伪条件是否有意义、可操作、范围适当？ | 1=模糊/5=精确可测 |
      | **D3. 范围校准** | 主张是否精确匹配证据支持的边界，不多不少？ | 1=过度泛化/5=精确校准 |
      | **D4. 论证连贯性** | 叙事是否从问题→方案→证据形成逻辑脉络？ | 1=跳跃/5=严密链条 |
      | **D5. 探索完整性** | 是否诚实地记录了研究过程，包括失败？ | 1=隐瞒失败/5=完整记录 |
      | **D6. 方法严谨性** | 实验设计是否充分（基线、消融、复现报告）？ | 1=草率/5=完备 |

      - 计算6维平均分：`epistemic_score = (D1+D2+D3+D4+D5+D6) / 6`（范围 1.0-5.0）
      - 映射为置信度校准因子：`epistemic_factor = min(1.0, epistemic_score / 4.0)`（4.0≈"good"基准线）
      - 应用最终校准：`confidence = confidence × epistemic_factor`
      - 在 verification_results.epistemic_scoring 中记录各维度分数和校准因子
      - **注意**：此校准在所有其他修正（反方观点/弱点/鲁棒性/引用质量）之后执行，作为最终校准层

   e.7 **[哲学吸收] 多人格辩论校准 — Persona Debate**：
      - 当同一数据/论点存在多种解释路径时（如眼动数据同时支持神经生物学模型和生物力学模型），自动创建多视阈辩论：
      
      | Persona | 理论透镜 | 评估视角 |
      |:--------|:---------|:---------|
      | **Persona A** | 神经生物学模型 | 关注突触可塑性、神经递质通路、脑区激活模式 |
      | **Persona B** | 生物力学模型 | 关注惯性/力矩、组织力学特性、运动控制 |
      | **Persona C** | 进化心理学模型 | 关注适应价值、环境选择压力、跨物种比较 |
      
      - 辩论协议：
        ├── **Step 1**: 每个Persona独立解释数据 → 生成结构化论证（含预测+覆盖范围）
        ├── **Step 2**: 交叉驳斥 — A反驳B的解释，B反驳C，C反驳A
        ├── **Step 3**: 记录无法解释的残余数据 — 所有Persona都无法覆盖的观察
        └── **Step 4**: 输出综合评分 — `debate_verdict: {persona_A_conf, persona_B_conf, persona_C_conf, residual_data, recommended_lens}`

      - **触发条件**：仅当存在 ≥2 条不同解释路径时执行（非每次运行）
      - 校准因子：`debate_factor = max(persona_confs) / (max(persona_confs) + residual_ratio)` 越多残余数据越低置信
      - 最终置信度 = confidence × debate_factor

   f. **裁决（Verdict）**：
      - `supported`：confidence ≥ 0.80，无强反方观点
      - `partially_supported`：0.50 ≤ confidence < 0.80
      - `insufficient_evidence`：confidence < 0.50 且主要原因是证据不足
      - `likely_false`：confidence < 0.30 且有强反方观点
      - `requires_revision`：confidence < 0.40 且主要原因是内部逻辑矛盾

      每个 verification_result 的裁决必须包含 `reasoning_path: string` — **从先验到最终置信度的推演路径**：
      ```
      先验=0.7 → 反方观点-0.10(替代解释,strength=0.7) → 弱点-0.08(概念混淆) → 引用质量×0.92 → 认识论校准×0.88 → debate_factor×0.95 → 最终=0.45
      ```
      推理路径以单行字符串形式嵌入每个 `verification_result.reasoning_path`，列出每一步更新的原因。不可省略，不可简化为"综合评估"。

   **Step 2.7: 日损检查点** — 裁决完成后执行简约性审计：
      - 问："当前使用的验证维度是否都是必要的？"
      - 问："如果去掉一个验证维度（如不检查鲁棒性），裁决会变吗？"
      - 如果某维度不影响裁决 → 标记为 `optional: true`
      - 如果去掉后裁决不变 → 该假设的验证可简化为更少维度
      - 输出：在 verification_result 中增加 `minimal_verification: [使用的维度列表]` 和 `optional_dimensions: [可省略的维度]`

3. **聚合**：汇总所有 Verification，计算 `aggregate_confidence`（均值、最小值、分布），给出整体 `verdict`。

4. **[泛化] 反谄媚门控 — Concession Threshold Protocol**

   应用标准的 [反谄媚阈值协议](/media/yakeworld/sda2/Synthos/docs/shared/CONCESSION_THRESHOLD_PROTOCOL.md)（从 viewpoint-verification 提取并泛化到所有技能）。

   当用户反驳验证结论时，执行三步协议：

   **Step 1: 对反驳打分 1-5**（评分标准见共享协议文档）
   **Step 2: 记录每次决策** — `[DA-DECISION: Score X/5 | ACTION: ...]`
   **Step 3: 强制规则** — 不因坚持让步、不准连续让步、让步率监控

5. **[伦理扩展层] 伦理影响评估 — Ethics Screening**

   **触发条件**：当验证对象涉及医学/脑机接口/人类受试者/基因编辑/神经增强等领域时，执行此可选检查：

   ```yaml
   ethics_screening:
     domain: "医学"  # 触发领域
     risk_level: enum[low, medium, high, critical]
     
     check_1: "双刃剑评估 — 该技术是否存在潜在滥用方向？"
       - 正面应用: "..."
       - 潜在风险: "..."
       - 风险等级: medium
     
     check_2: "受试者保护 — 研究方案是否涉及人类受试者？"
       - 涉及人群: "ADHD患儿"
       - 伦理审查需求: "需要IRB批准"
       - 知情同意: "需监护人签署"
     
     check_3: "社会影响 — 研究成果是否可能被误用？"
       - 误用场景: "..."
       - 影响范围: "..."
     
     recommendation: "建议：在发表前增加伦理声明段落，明确研究边界和限制条件。"
   ```

   **位置**：此检查为扩展层，不改变VER核心流程。当领域匹配时自动附加到验证结果中。
   详见 `references/ETHICS_SCREENING.md`。

6. **构建证据链**：每个 counterargument、falsification_condition、robustness_concern 的证据节点见 `references/EVIDENCE_SCHEMA.md`。

7. **输出**：返回 `_ok({"verification_results": [...], "aggregate_confidence": {...}, "verdict": "..."})` 信封。

### 4. 边界判断（When NOT to use this atom）

详见 `references/BOUNDARY.md`。典型排除场景：
- 如果用户想要生成新假设 → 这是 `hypothesis-generation` 的职责
- 如果用户想要撰写论证文本 → 这是 `argument-expression` 的职责
- 如果用户想要发现跨论文关联 → 这是 `association-discovery` 的职责
- 如果用户只想要论文信息而不评估主张 → 直接用 `knowledge-extraction` 输出即可

### 5. 证据链输出要求（Evidence Summary）

详见 `references/EVIDENCE_SCHEMA.md`。每个 `Verification` 必须携带：
- `CounterArgument` → `source_type: "doi"` | `"atom_output"` | `"reasoning"`
- `falsification_condition` → `source_type: "falsification_test"`
- `robustness_concern` → `source_type: "robustness_check"`
- 逻辑推理型反方观点必须在 `note` 中标注 `[INFERRED]`
- 如果无法找到外部反方证据，置信度上限 ≤ 0.6

### 6. 示例（Minimal Example）

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
      "uncertainty_reduction": 0.25,
      "reasoning_path": "先验=0.7 → 反方观点-0.10(替代解释,strength=0.7) → 反方观点-0.12(普适性挑战,strength=0.8) → 弱点-0.08(概念混淆) → 鲁棒性-0.05(样本不均衡) → 最终=0.45",
      "verdict": "insufficient_evidence"
    }
  ],
  "aggregate_confidence": {
    "mean_confidence": 0.45,
    "min_confidence": 0.45,
    "confidence_distribution": "uniform",
    "verification_entropy_reduction": 0.25,
    "overall_verdict": "insufficient_evidence"
  },
  "verdict": "insufficient_evidence"
}
```

### 7. 参考文件索引（References）

- IO 契约：`references/IO_CONTRACT.md`
- 证据链 schema：`references/EVIDENCE_SCHEMA.md`
- 边界证明：`references/BOUNDARY.md`
- 金标准：`golden/GOLDEN_SET.md`
- 变更日志：`references/CHANGE_LOG.md`
- **[PW-Bench吸收] 引用质量评价方法论**：`references/citation-f1-methodology.md`

## 命令层·English

- **Signature**: `hypothesis: Hypothesis, argument: Argument -> verdict: str, confidence_score: float, counterarguments: list[Counterargument]`
- **Allowed tools**: `Read`, `Write`
- **Input**: `hypotheses` (list[Hypothesis]) from upstream `hypothesis-generation`, `arguments` (list[Argument]) from upstream `argument-expression`
- **Output**: `verification_results` (list[Verification] with counterarguments/falsification/robustness/weaknesses/confidence/uncertainty_reduction/reasoning_path), `aggregate_confidence` (AggregateConfidence with verification_entropy_reduction), `verdict` (string)
- **Observer standpoint** (Step 0): declares cognitive chain position (6), upstream/downstream atoms, validation lens before processing
- **Prior confidence**: 0.7 (neutral); deductions from counterarguments, weaknesses, robustness concerns
- **Uncertainty reduction** (Step 2e): `uncertainty_reduction = initial_confidence - final_confidence`, recorded per result + aggregated as `verification_entropy_reduction`
- **Reasoning path** (Step 2f): string tracing each step from prior to final confidence (e.g. "prior=0.7 → counterargument-0.10 → weakness-0.08 → final=0.52")
- **Minimal verification** (Step 2.7): post-verdict simplicity audit — optional dimensions flagged, minimal_verification list output
- **Verdict thresholds**: supported (≥0.80), partially_supported (0.50-0.79), insufficient_evidence (<0.50), likely_false (<0.30 + strong counterarguments), requires_revision (<0.40 + logical flaws)
- **Citation quality correction**: `confidence × min(1.0, citation_quality + 0.3)`
- **Epistemic scoring**: 6-dimensions (D1-D6), average 1-5, factor = min(1.0, score/4.0)
- **Persona debate**: optional, triggered for ≥2 competing explanations
- **Concession Threshold Protocol**: required when user challenges verdict
- **Ethics screening**: auto-triggered for medical/BCI/human-subject domains
- **Do NOT**: generate hypotheses, write arguments, discover associations
