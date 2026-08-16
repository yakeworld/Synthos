---
name: mlops
description: Skill file
signature: 'mlops -> private: synthetic skill for mlops'
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
    description: Skill file
    signature: 'mlops -> private: synthetic skill for mlops'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

|
| codex-llm-routing | Route OpenAI Codex CLI (v0.139+) to local/third-party LLMs via Responses API proxy | quick |
| ellipse-3d-anatomy-constrained | 用户特异性推导：椭圆→3D圆通过解剖约束（R=2r, d=√3r）消除方位角模糊 | ultrabrain |
| evaluation/ | mlops/evaluation — 模型评估与实验追踪（含 lm-evaluation-harness, weights-and-biases） | quick |
| inference/ | mlops/inference — 模型推理服务与优化（含 llama-cpp, obliteratus, outlines, vllm） | quick |
| models/ | mlops/models — 模型架构（含 audiocraft, segment-anything-model） | quick |
| research/ | mlops/research — ML 研究框架（含 dspy） | ultrabrain |
| training/ | mlops/training — 模型训练与微调（含 axolotl, fine-tuning-with-trl, unsloth） | quick |

## 使用场景

- Codex CLI 本地模型路由
- 眼动追踪 3D 椭圆还原
- 完整的 mlops 工具链（评估、推理、训练、模型）

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

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

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Mlops — 机器学习运维---

## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[MLOP-001]** 输出涉及数据或结论时 → 必须经过事实核查且可追溯到具体证据源，严禁编造
- **[MLOP-002]** 执行任何操作步骤时 → 必须确保过程可重复且结果可验证，以保障可复现性
- **[MLOP-003]** 接收输入参数时 → 必须严格校验类型、范围及格式，拒绝无效输入
- **[MLOP-004]** 生成返回值时 → 必须保持结构、编码及命名的一致性
- **[MLOP-005]** 发生异常或错误时 → 错误信息必须包含上下文背景及明确的恢复建议
- **[MLOP-006]** 处理代码执行请求时 → 禁止执行未验证的任意代码且不暴露内部状态
- **[MLOP-007]** 进行功能改进或测试时 → 必须以 Golden 集合（输入/输出/错误）为单一真理来源进行验证