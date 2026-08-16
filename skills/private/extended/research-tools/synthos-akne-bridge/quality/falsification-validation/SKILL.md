---
name: falsification-validation
description: 'Every test must produce:'
signature: 'falsification-validation -> quality: synthetic skill for falsification
  validation'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: 'Every test must produce:'
    signature: 'falsification-validation -> quality: synthetic skill for falsification
      validation'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---


## IO_CONTRACT

- **input**: 待证伪的技能假设 — 声明、适用场景、可检验条件
- **input**: 真实任务输入（非 mock/synthetic）— 用于执行证伪测试
- **output**: 证伪测试结果 — 每个测试含真实输入、期望输出、实际输出、通过/反证判定
- **output**: 技能信任分级 — 0.9-1.0 继续使用 / 0.5-0.7 需重设计 / <0.5 替换技能

## 原则 (Principles)

- **以真为试**：证伪之试必用真实任务输入，mock 数据所成之验，不足以证其能。
- **留痕存证**：每试须存输入、过程日志、输出、度量于 `test-results/`，无迹之验不可复，不可复则不诚。
- **逆证为要**：但跑期望通过之试者，自欺也；反证之证与成功之证同须采集。
- **信由渐积**：信任分级依屡次证据而移，一单点之验不足以定高下，亦不足以成弃。

|
| 0.9-1.0 | High Trust | Continue using |
| 0.7-0.9 | Medium Trust | Increase monitoring |
| 0.5-0.7 | Low Trust | Redesign needed |
| < 0.5 | Unreliable | Replace skill |


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[FALS-001]** 执行证伪测试时 → 必须使用真实任务输入，严禁使用 mock 或合成数据
- **[FALS-002]** 设计测试用例时 → 必须包含期望失败的反证测试，避免仅运行预期通过的自欺式验证
- **[FALS-003]** 记录测试结果时 → 必须将输入、过程日志、输出及度量完整归档至 `test-results/` 以确保可复现性
- **[FALS-004]** 评估技能信任度时 → 必须基于屡次累积的证据动态调整分级，禁止依据单点数据定论
- **[FALS-005]** 判定测试有效性时 → 必须采用量化指标对比期望与实际输出，拒绝主观的“看起来不错”评估
- **[FALS-006]** 处理验证失败时 → 必须记录具体原因、上下文及修复建议，确保错误信息具备恢复指引

## Evidence Requirements

Every test must produce:

1. **Input Data**: Real task input (not mock/synthetic)
2. **Processing Log**: Intermediate results from skill execution
3. **Output Results**: Final output from the skill
4. **Comparison**: Analysis of how output matches expectations
5. **Metric Calculations**: Quantitative quality scores
6. **Evidence Storage**: All artifacts saved to `test-results/` directory

## Anti-Patterns to Avoid

- Testing with mock data instead of real data
- Subjective "looks good" assessments without metrics
- Only running tests that you expect to pass
- Updating trust based on single data points
- Ignoring failure evidence
- Using inconsistent metric thresholds across tests
- Not collecting evidence for tests that pass
- Assuming skill works because it "seems right"

## Related

- Bayesian probability theory
- Karl Popper's falsificationism
- Scientific method and hypothesis testing
- ML model evaluation and validation
- A/B testing and experimental design

## 验证清单 · VERIFICATION

- [ ] 每个证伪测试均使用真实任务输入，无 mock/synthetic 数据（FALS-001、以真为试）
- [ ] 测试用例集包含期望失败的反证测试，未只跑预期通过的自欺式验证（FALS-002、逆证为要）
- [ ] 每项测试归档完整证据链至 `test-results/`：真实输入、过程日志、输出、期望对比、量化度量（FALS-003、Evidence Requirements 1-6）
- [ ] 测试判定采用量化指标对比期望与实际输出，无"看起来不错"式主观评估（FALS-005）
- [ ] 技能信任分级（0.9-1.0 / 0.7-0.9 / 0.5-0.7 / <0.5）基于屡次累积证据动态更新，未依据单点数据定论（FALS-004、信由渐积）
- [ ] 失败测试已记录具体原因、上下文与修复建议；通过测试同样留痕存证（FALS-006、Anti-Patterns: 不忽略失败证据、不为通过测试收集证据）

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

## Golden 集合 · GOLDEN SET

- **Golden Input**: 待证伪技能声明 — 如 "citation-verification 技能在 pima-crispdm 数据集上可检出 ≥95% 虚构引用"，含适用场景与可检验条件。
- **Golden Output**: 每个测试产出完整证据链 — 真实输入（非 mock）、处理日志、最终输出、期望对比、量化指标，全部归档至 `test-results/`；技能信任分级更新（如 0.85 → High Trust，继续监控）。
- **Golden Error**: 仅用 mock 数据执行测试，3/3 通过即判 "技能可靠" → 诊断：违反"以真为试"原则，反证路径缺失；修复：改用真实任务输入重跑，并补充期望失败的反证测试用例，重新采集证据。
