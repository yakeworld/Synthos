# GOLDEN_SET.md — hypothesis-generation

> 对应原则：P1（认知原子语义可复现：同一输入 + 同一模型版本 → 等价结论通过金标准测试）
> golden_set_origin: self_defined

## 设计依据

本原子的金标准为自设（`self_defined`），因为研究假设生成目前没有公开的标准测试集。金标准的设计目标是验证：**给定相同的关联分析和研究空白，原子能否一致地生成合理、可检验的假设，并正确评分新颖性和可行性**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 生成策略 | 3/3 种 | 第一性原理、类比推理、贝叶斯思维 |
| 空白类型 | 4/4 种 | knowledge_gap、method_gap、population_gap、contradiction_gap |
| 关联类型 | 3/5 种 | contradiction、corroboration、methodological_contrast |
| 语言 | 英文 | 中文金标准为 v0.2 目标 |
| 边缘案例 | 2 种 | 空输入、单来源输入 |

## 测试用例 (cases/)

### case_001: 标准矛盾驱动假设
- **输入**: 2篇论文相互矛盾 + 1个研究空白（矛盾空白）
- **期望**: ≥1 hypothesis, novelty_score ≥ 0.5, testability ∈ {testable, partially_testable}

### case_002: 单来源方法论空白
- **输入**: 1个方法空白（缺少特定方法的验证），无关联
- **期望**: 至少1个方法类假设，novelty_score ≤ 0.6（单来源限制），rationale 包含方法论推理

### case_003: 跨领域类比假设
- **输入**: 多个跨领域关联 + 知识空白
- **期望**: 至少1个假设使用了类比推理（rationale 中包含跨领域参照），novelty_score ≥ 0.6

### case_004: 边缘案例 — 空输入
- **输入**: `associations: []`, `research_gaps: []`
- **期望**: 原子应返回错误 `_err("Missing associations and research_gaps")`，不应崩溃

### case_005: 多来源高新颖性
- **输入**: 3个关联 + 2个研究空白（知识空白 + 人群空白）
- **期望**: ≥2 hypotheses，按 novelty_score 降序排列，最高 novelty_score ≥ 0.5

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含完整的 Hypothesis 数组结构。

期望输出（v0.1.0）采用**语义等价判定**：
- `id` 格式必须匹配 `hyp_NNN`
- `source` 必须引用正确的上游 ID
- `novelty_score` 和 `feasibility_score` 在期望值的 ±0.15 范围内
- `testability` 必须精确匹配
- `text` 和 `rationale` 通过 LLM-as-judge 语义等价判定（Jaccard ≥ 0.3）

## pass_threshold: 0.70

含义：5 个测试用例中，至少 4 个通过（80%），但允许 1 个因评分偏差而失败。

### 阈值理由
- **不设 1.0**：假设生成存在固有创造性，同一空白可产生不同但同样合理的假设
- **不设 < 0.7**：核心评分维度（novelty_score、testability）是下游论证的基础，错误会传播
- **v0.1 暂时容忍**: 自设金标准仍在迭代，0.70 为初始阈值，随金标准成熟可上调至 0.80

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-05-10 | 初始自设金标准，5 个 case | Synthos Agent |
