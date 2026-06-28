---
name: mlops-—-机器学习运维
version: 1.0.0
priority: P2
signature: "mlops -> processed_result"
---

# mlops — 机器学习运维

> 子技能目录，提供 mlops 工具链的桥接和辅助能力。

## 子技能

| 技能 | 描述 | 调用类别 |
|------|------|----------|
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

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
