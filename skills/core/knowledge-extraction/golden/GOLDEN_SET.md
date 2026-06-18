# GOLDEN_SET.md — knowledge-extraction

> 对应原则：P1（认知原子语义可复现：同一输入 + 同一模型版本 → 等价结论通过金标准测试）
> golden_set_origin: self_defined

## 设计依据

本原子的金标准为自设（`self_defined`），因为学术论文知识提取目前没有公开的标准测试集。金标准的设计目标是验证：**给定相同的论文摘要，原子能否一致地提取核心发现、正确分类方法论和研究领域、合理识别局限和主题**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 方法论多样性 | 5/18 种 | RCT、cohort、cross_sectional、systematic_review、machine_learning |
| 领域多样性 | 4/9 种 | psychiatry、neurology、pediatrics、computational |
| 语言 | 英文 | 中文金标准为 v0.2 目标 |
| 摘要长度 | 150-400 词 | 覆盖典型学术摘要长度 |
| 边缘案例 | 2 种 | 无 DOI 论文、仅有标题无摘要论文 |

## 测试用例 (cases/)

### case_001: 标准 RCT 论文
- **输入**: 典型 RCT 摘要（包含 objective/methods/results/conclusion 四段式）
- **期望**: methodology=`randomized_controlled_trial`, ≥2 key_findings, evidence_level=`rct`

### case_002: 系统综述/Meta分析
- **输入**: PRISMA 结构化系统综述摘要
- **期望**: methodology=`meta_analysis_or_systematic_review`, evidence_level=`meta_analysis`

### case_003: 观察性研究（横断面）
- **输入**: 横断面调查研究摘要（survey-based, n=X）
- **期望**: methodology=`cross_sectional_survey`, sample_size 被正确提取

### case_004: 机器学习方法论文
- **输入**: 提出新 ML 模型的论文摘要（CNN/transformer/etc）
- **期望**: methodology=`machine_learning`, domain 至少不为 `unspecified`

### case_005: 边缘案例 — 无摘要
- **输入**: 仅有标题和作者，`abstract: ""`
- **期望**: findings=["Abstract not available"], methodology=`unspecified`, 原子不应报错

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含完整的 KnowledgeItem 结构。

期望输出（v0.1.0）采用**语义等价判定**：
- `methodology` 和 `domain` 必须精确匹配期望值
- `key_findings` 至少 1 条与期望值语义等价（通过人工评审或 LLM-as-judge）
- `key_themes` Jaccard 相似度 ≥ 0.5

## pass_threshold: 0.80

含义：5 个测试用例中，至少 4 个通过（80%）。

### 阈值理由
- **不设 1.0**：认知原子的非确定性允许合理的语义变异（同一发现的不同措辞）
- **不设 < 0.8**：方法论和领域分类是下游关联发现的基础，错误会传播
- **v0.1 暂时容忍**: 自设金标准仍在迭代，0.80 为初始阈值，随金标准成熟可上调至 0.85

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-05-10 | 初始自设金标准，5 个 case | Synthos Agent |
