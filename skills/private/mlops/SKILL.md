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

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
