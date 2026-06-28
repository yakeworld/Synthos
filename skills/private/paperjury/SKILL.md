---
name: paperjury
description: "投稿前 AI 陪审团审稿 — 审稿 → 裁定 → 修改 → 复查 闭环。把论文提交前自查做成一套闭环流程，确保 claim 够稳、实验支撑结论、格式不被 desk-reject。"
version: 1.0.0
category: writing
tags: [paper-review, quality, submission-readiness]
signature: "paperjury -> processed_result"
---

# PaperJury — 投稿前 AI 陪审团审稿（Synthos 吸收版）

> **核心哲学**: PaperJury 不是「让 AI 多写一点」，而是让 AI **先像 reviewer 一样认真挑错**，再让确定性脚本守住可验证边界。Synthos 吸收的是其方法论（庭审协议、编辑安全护栏），不是其 Node.js 实现。

## ⚠️ 吸收方法论铁律（2026-06-18 实战教训）

> **用户纠正**: "我们是消化和吸收，不是拷贝和抄袭技能，要按照synthos思想和规范，进行技能消化吸收。"
>
> 此教训已写入 `references/absorption-plan.md`。核心要点：
> - **不拷贝代码**：任何实现细节（Node.js scripts、文件结构）都不应复制到 Synthos
> - **提取方法论**：只提取跨平台可复用的设计原则和问题分类逻辑
> - **按 Synthos 规范重构**：所有吸收的内容必须通过 quality-gate L4 语义审查
> - **增强已有技能**：优先增强现有技能（如 quality-gate L4），而非创建独立技能

## 吸收原则（Synthos vs PaperJury 原始）

| PaperJury 原始 | Synthos 吸收 | 理由 |
|:---------------|:-------------|:-----|
| Node.js 确定性脚本 | Hermes terminal 命令 + Python 脚本 | 运行环境不同 |
| Claude Code CLI | Hermes skill_view + terminal | 交互协议不同 |
| LEDGER.json + passage_id | 等价概念保留，实现方式不同 | 方法论相同 |
| 不硬编码路径 | **保留六条硬规则** | 这是跨平台的通用原则 |
| 独立 skill 文件 | **融入 quality-gate L4** | Synthos 不创建独立技能，而是增强现有能力 |

## 核心方法论（Synthos 原生表达）

### 庭审协议（Trial Protocol）

```
分配评审者 → 通读全文 → 去重聚类 → 争议审议 → 批量快路径 → 召回审计 → 起草修改 → 编辑安全 → 收敛判定
```

1. **分配评审者**: N=3 领域专家，每人一个 subfield overlay
2. **通读全文**: 每位 reviewer 必须**引用原文**（quote-verify），引不出 = 没真读
3. **去重聚类**: 跨 reviewer 问题按 significance/kind/corroboration 聚类
4. **争议审议（trial）**: 对 substantive-major 问题开庭。5 人陪审团 → quorum ≥ 80% + 单侧 > 60% → 决策。无效 → invalid-drop；可修复 → valid-fixable + close_criterion；需作者判断 → author-required
5. **批量快路径（polish）**: mechanical 和 minor 问题批量处理
6. **召回审计**: 救回误丢问题 + 抽检强共识 major
7. **起草修改**: 每个 valid-fixable 起草最小改动 patch
8. **编辑安全**: anchor-diff + cross-ref → meaning-audit（frozen anchor）/ edit-audit（risky non-anchor）
9. **收敛判定**: 汇总本轮结果，判定是否收敛

### 六条硬规则

1. **未经作者显式确认，绝不改手稿。**
2. **评审者/陪审员相互隔离。**
3. **每条可修复问题有明确修复标准（close_criterion）。**
4. **不把内部记录写进被审文本。**
5. **分歧靠讨论解决，谈不拢再由人 override。**
6. **所有路径和文件配置在运行时解析，不硬编码。**

## 编辑工具箱（Writing Toolkit）

编辑层只处理单 passage、LaTeX-safe 的写作操作：

| 工具 | 用途 |
|:-----|:-----|
| translate-to-english | 中文 → 英文 LaTeX（最高价值） |
| polish-english | 句子级重写到 venue 标准 |
| de-ai | 去除 AI 痕迹（leverage, delve, utilize...） |
| compress | 语法压缩（5-15 词），不丢 claim |
| expand | 显式化隐含结论（5-15 词），不编造 |
| caption | 图表标题重写到 venue 标准 |
| experiment-analysis | 实验数据 → 结果段落，不数字转储 |
| logic-check | 编辑后自检：逻辑矛盾、术语切换、Chinglish |

## 与 quality-gate 的集成

| quality-gate | PaperJury |
|:-------------|:----------|
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
- references/absorption-plan.md — Synthos 吸收方案（方法论转化指南）
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

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
