# GOLDEN_SET.md — argument-expression

> 对应原则：P1（认知原子语义可复现：同一输入 + 同一模型版本 → 等价结论通过金标准测试）
> golden_set_origin: self_defined

## 设计依据

本原子的金标准为自设（`self_defined`），因为学术文本生成目前没有公开的标准测试集。金标准的设计目标是验证：**给定相同的假设和参考文献，原子能否生成符合 IMRaD 结构、逻辑连贯、引用正确的学术文本**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| IMRaD 结构 | 4/5 种 | introduction、methods、discussion、full_paper |
| 引用格式 | APA 7th | 内文引用 + 参考文献列表 |
| 语言 | 英文 | 中文金标准为 v0.2 目标 |
| 边缘案例 | 2 种 | 无 raw_papers（无引用）、空假设列表 |

## 测试用例 (cases/)

### case_001: 标准 Introduction 生成
- **输入**: 2个假设 + 1篇论文 + structure="introduction"
- **期望**: 输出含 introduction section，段落 ≥3，至少1个内文引用，至少1个 argument

### case_002: Methods 生成（推测性）
- **输入**: 1个假设（testable, feasibility=0.65）+ structure="methods"
- **期望**: 输出包含 proposed methods，methodology 描述清晰，标注为 proposed

### case_003: Full Paper 生成
- **输入**: 2个假设 + 3篇论文 + structure="full_paper"
- **期望**: 输出含 introduction/methods/results/discussion/references，arguments ≥4，references ≥3

### case_004: 边缘案例 — 空假设
- **输入**: `hypotheses: []` + structure="introduction"
- **期望**: 原子应返回 `_err("Missing hypotheses")`，不应崩溃

### case_005: 边缘案例 — 无 raw_papers
- **输入**: 2个假设 + structure="introduction" + 无 raw_papers
- **期望**: 正常生成文本，但内文引用使用 Hypothesis.id 标记（如 `[hyp_001]`），不编造引用

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含完整的 sections/arguments/references 结构。

期望输出（v0.1.0）采用**语义等价判定**：
- `section_type` 必须精确匹配
- `heading` 在允许的变体范围内匹配（如 "Introduction" vs "1. Introduction"）
- 每个 section 至少包含 1 个 paragraph
- 引用的 `evidence` 必须引用正确的上游 ID 或 DOI
- 参考文献格式通过格式检查器验证（APA 7th 基本规则）

## pass_threshold: 0.80

含义：5 个测试用例中，至少 4 个通过（80%）。

### 阈值理由
- **不设 1.0**：学术文本生成存在风格变体，同一假设可用不同措辞表达
- **不设 < 0.8**：结构完整性（IMRaD）和引用正确性是学术写作的基本要求，错误严重影响可用性
- **v0.1 暂时容忍**: 自设金标准仍在迭代，0.80 为初始阈值

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-05-10 | 初始自设金标准，5 个 case | Synthos Agent |
