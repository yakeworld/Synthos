---
name: paperjury
description: '**典型流程**: 论文完成 → quality-gate L1-L2 → paperjury review → 修复 → quality-gate L3-L4 → paperjury auto lo'
signature: 'paperjury -> private: synthetic skill for paperjury'
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
    description: '**典型流程**: 论文完成 → quality-gate L1-L2 → paperjury review → 修复 → quality-gate L3-L4 → paperjury auto lo'
    signature: 'paperjury -> private: synthetic skill for paperjury'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


|
| G1-G7 结构检查 | 语义审查（claim 是否站得住） |
| 编译检查 | 编辑安全 + 防漂移 |
| 批量 cron 扫描 | 单篇深度庭审 |
| 确定性指标 | 语义判断 + 确定性 guards |

**典型流程**: 论文完成 → quality-gate L1-L2 → paperjury review → 修复 → quality-gate L3-L4 → paperjury auto loop → quality-gate L5-L7 → 投稿。

## 使用示例

```
审稿，重点看实验和 claim 是否站得住。
把 introduction 这段改紧一些，但不要改变 claim。
跑一下 submission-readiness / 合规检查。
```

## 限制

1. 不替代 peer review，只是投稿前自查
2. 不编造实验，遇到需要新实验的问题交给作者
3. 完整庭审约 10k tokens/轮，多轮 auto 30-50k
4. 每个 reviewer 必须独立阅读，不能跨轮次泄漏

### 数值回查（实验数据审计）

当论文有实验指标时，**必须**先运行 `references/experimental-data-integrity-audit.md`：
1. 提取所有数值 claim（F1/AUC/Recall 等）
2. 检查 03-code/ 下是否有对应代码和输出
3. 无代码 → 标记 FABRICATED；有代码但数值不匹配 → MISMATCH
4. 运行独立复现，输出 JSON+CSV 归档
5. 对比 claimed vs actual，标注 CLOSE/MISMATCH/FABRICATED

**核心原则**：不信任 paper.tex、state.json、notebook cell output 中的数字。只信任独立运行的代码输出。

## 参考文件

- references/paperjury-analysis.md — 引擎原理 v3 消化吸收笔记
- references/doi-pdf-validation-lessons.md — DOI + PDF 验证经验教训
- ref/absorption-plan.md — Synthos 吸收方案（方法论转化指南）
- references/experimental-data-integrity-audit.md — 论文数值 claim 代码回查协议（pima-crispdm 实战提炼：逐条验证 F1/AUC/Recall 等指标是否有代码输出支撑）

## 相关技能

- **quality-gate**: 结构化质量门（G1-G7），L4 可调用 paperjury review
- **paper-cron-scan**: 白空间扫描，与 paperjury 互补
- **sci-paper-quality-review**: SCI 论文结构/格式检查，与 paperjury 互补
- **paper-pipeline**: 论文管线编排，paperjury 是其质量审查工具

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

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Paperjury---





|
| G1-G7 结构检查 | 语义审查（claim 是否站得住） |
| 编译检查 | 编辑安全 + 防漂移 |
| 批量 cron 扫描 | 单篇深度庭审 |
| 确定性指标 | 语义判断 + 确定性 guards |

**典型流程**: 论文完成 → quality-gate L1-L2 → paperjury review → 修复 → quality-gate L3-L4 → paperjury auto loop → quality-gate L5-L7 → 投稿。

## 使用示例

```
审稿，重点看实验和 claim 是否站得住。
把 introduction 这段改紧一些，但不要改变 claim。
跑一下 submission-readiness / 合规检查。
```

## 限制

1. 不替代 peer review，只是投稿前自查
2. 不编造实验，遇到需要新实验的问题交给作者
3. 完整庭审约 10k tokens/轮，多轮 auto 30-50k
4. 每个 reviewer 必须独立阅读，不能跨轮次泄漏

### 数值回查（实验数据审计）

当论文有实验指标时，**必须**先运行 `references/experimental-data-integrity-audit.md`：
1. 提取所有数值 claim（F1/AUC/Recall 等）
2. 检查 03-code/ 下是否有对应代码和输出
3. 无代码 → 标记 FABRICATED；有代码但数值不匹配 → MISMATCH
4. 运行独立复现，输出 JSON+CSV 归档
5. 对比 claimed vs actual，标注 CLOSE/MISMATCH/FABRICATED

**核心原则**：不信任 paper.tex、state.json、notebook cell output 中的数字。只信任独立运行的代码输出。

## 参考文件

- references/paperjury-analysis.md — 引擎原理 v3 消化吸收笔记
- references/doi-pdf-validation-lessons.md — DOI + PDF 验证经验教训
- ref/absorption-plan.md — Synthos 吸收方案（方法论转化指南）
- references/experimental-data-integrity-audit.md — 论文数值 claim 代码回查协议（pima-crispdm 实战提炼：逐条验证 F1/AUC/Recall 等指标是否有代码输出支撑）

## 相关技能

- **quality-gate**: 结构化质量门（G1-G7），L4 可调用 paperjury review
- **paper-cron-scan**: 白空间扫描，与 paperjury 互补
- **sci-paper-quality-review**: SCI 论文结构/格式检查，与 paperjury 互补
- **paper-pipeline**: 论文管线编排，paperjury 是其质量审查工具

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

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Paperjury
