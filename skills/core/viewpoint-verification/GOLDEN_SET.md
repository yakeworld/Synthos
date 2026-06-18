# GOLDEN_SET.md — viewpoint-verification

> 对应原则：P1（认知原子语义可复现：同一输入 + 同一模型版本 → 等价结论通过金标准测试）
> golden_set_origin: self_defined

## 设计依据

本原子的金标准为自设（`self_defined`），因为假设验证的评估目前没有公开的标准测试集。金标准的设计目标是验证：**给定假设和论证，原子能否一致地识别反方观点、合理设定证伪条件、发现鲁棒性关切、识别内部弱点，并计算出合理的置信度评分**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 验证场景 | 4/5 种 | 有明确反方、充分支持、证据不足、需修订（缺 `likely_false`） |
| 反方观点类型 | 3/8 种 | direct_contradiction、alternative_explanation、generalizability_challenge |
| 假设领域 | 3 种 | 医学、心理学、计算方法 |
| 假设复杂度 | 3 级 | 简单（单机制）、中等（多因素）、复杂（含交互） |
| 边缘案例 | 1 种 | 假设陈述模糊、无可检验条件 |

## 测试用例 (cases/)

### case_001: 有明确反方观点的假设
- **输入**: 假设 "ADHD 的眼动追踪筛查可以替代临床访谈"，有已发表的相反证据
- **期望**: ≥1 counterargument（type=direct_contradiction），confidence_score ≤ 0.5，verdict ∈ {partially_supported, insufficient_evidence}

### case_002: 证据充分支持的假设
- **输入**: 假设 "认知行为疗法对轻中度抑郁症有效"，有大量 RCT 和 meta-analysis 支持
- **期望**: counterarguments 为 0 或为弱反方（strength ≤ 0.3），confidence_score ≥ 0.85，verdict = supported

### case_003: 证据不足的假设
- **输入**: 假设 "新型生物标志物 X 可早期预测阿尔茨海默病"，仅有 1 项小型横断面研究支持
- **期望**: ≥1 counterargument（type=evidence_gap 或 generalizability_challenge），confidence_score ≤ 0.4，verdict = insufficient_evidence

### case_004: 内部矛盾/需修订的假设
- **输入**: 假设 "社交媒体使用导致青少年焦虑"，但论证中包含 "相关性不代表因果性" 的自我矛盾
- **期望**: ≥1 weakness（内部逻辑矛盾），falsification_conditions 非空，verdict = requires_revision

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含完整的 Verification 结构。

期望输出（v0.1.0）采用**语义等价判定**：
- `verdict` 必须精确匹配期望值
- `counterarguments` 至少 1 条与期望值语义等价（类型匹配 + 方向一致）
- `falsification_conditions` 至少 1 条是可操作的（含有具体指标和阈值）
- `weaknesses` 如期望非空，至少 1 条匹配
- `confidence_score` 在期望值的 ±0.15 范围内

## pass_threshold: 0.80

含义：4 个测试用例中，至少 3 个通过（75% 向上取整 = 80%，即 3.2 → 4 个中 3 个通过）。

### 阈值理由
- **不设 1.0**：验证的严格程度可能有合理的风格差异（更保守 vs 更宽松的置信度校准）
- **不设 < 0.75**：verdict 和 counterargument 类型是下游决策的基础，错误会误导用户
- **v0.1 暂时容忍**: 自设金标准仍在迭代，0.80 为初始阈值，随金标准成熟可上调至 0.85

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-05-10 | 初始自设金标准，4 个 case | Synthos Agent |
