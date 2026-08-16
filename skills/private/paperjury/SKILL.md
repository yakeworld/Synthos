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

- [ ] 实验数值 claim 已回查 `03-code/`：无代码→FABRICATED、有代码数值不匹配→MISMATCH、独立复现→CLOSE，未凭 `paper.tex`/`state.json`/notebook 直接引用
- [ ] 数值审计输出 JSON+CSV 归档到 references/，claimed vs actual 逐条标注 CLOSE/MISMATCH/FABRICATED
- [ ] 每个 reviewer 独立阅读原文，未跨轮次共享笔记/结论（防泄漏污染评分）
- [ ] 需新实验才能验证的问题标记 OPEN 移交作者，未自行补数据或声称已验证
- [ ] 单轮 ≤10k tokens、多轮累计 ≤50k，超限自动终止并输出未决问题清单
- [ ] 流程按 L1-L2 结构 → 语义审查 → 修复 → L3-L4 → auto loop 深度庭审 → L5-L7 合规顺序执行
- [ ] 明确"不替代 peer review、仅为投稿前自查"，未编造实验

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Paperjury---
## 约束规则 · RULES
1. **数值不信任文档**：论文数值 claim 只信任独立运行代码的输出；`paper.tex`、`state.json`、notebook cell output 中的数字一律视为待验证，不直接引用。
2. **无代码即 FABRICATED**：指标无对应 `03-code/` 下脚本与输出 → 标记 FABRICATED，禁止标注 CLOSE 或放行。
3. **reviewer 独立**：每个 reviewer 必须独立阅读原文，禁止跨轮次共享笔记/结论，防泄漏污染评分。
4. **不编造实验**：遇到需新实验才能验证的问题，标记 OPEN 交给作者，禁止 paperjury 自行补数据或声称已验证。
5. **token 预算**：完整庭审单轮 ≤10k tokens，多轮 auto 累计 ≤50k tokens；超限自动终止并输出未决问题清单。
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[PAPE-001]** 论文包含实验指标 → 必须运行独立代码复现并归档 JSON/CSV，仅信任独立运行输出而非文档数值
- **[PAPE-002]** 指标无对应代码脚本或输出 → 直接标记为 FABRICATED，禁止标注 CLOSE 或放行
- **[PAPE-003]** 执行多轮审查时 → 每个 reviewer 必须独立阅读原文，严禁跨轮次共享笔记或结论以防评分污染
- **[PAPE-004]** 遇到需新实验才能验证的问题 → 标记为 OPEN 并移交作者，禁止自行补数据或声称已验证
- **[PAPE-005]** 审查流程启动时 → 遵循“结构检查(L1-L2) → 语义审查 → 修复 → 深度庭审(auto loop) → 合规检查(L5-L7)”的典型流水线
- **[PAPE-006]** 单轮庭审或累计多轮审查 → 严格控制在 10k/50k tokens 预算内，超限自动终止并输出未决问题清单