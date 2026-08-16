---
name: skill-absorption
description: 完整关键词轮转策略见 `references/keyword-rotation.md`。
signature: 'skill-absorption -> intelligence-monitoring: synthetic skill for skill absorption'
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
    description: 完整关键词轮转策略见 `references/keyword-rotation.md`。
    signature: 'skill-absorption -> intelligence-monitoring: synthetic skill for skill absorption'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## IO_CONTRACT

- **input**: 外部技能源扫描结果 — GitHub Topics API、Hermes skills/ 目录、arXiv 检索（关键词轮转策略见 references/）
- **input**: 吸收目标评估 — 项目来源、stars、吸收能力、目标技能映射
- **output**: 吸收记录 — evolution/absorption-{project}.md 五层吸收记录（13份）
- **output**: absorption-ledger.json 台账更新 — tracking→evaluating→absorbed/deferred/archived 状态生命周期追加

## 原则 (Principles)

> **轮转而扫，常扫常新。** GitHub Topics 每轮、Hermes skills 每轮、arXiv 每 2 轮，按关键词轮转策略常扫，源不枯竭。
> **台账统一，状态可溯。** 一切发现归 absorption-ledger.json 单一台账，tracking→evaluating→absorbed/deferred/archived 状态皆有记录可追。
> **五层而录，不录不吸。** 吸收必留五层记录与报告，未录者不视为吸收——留痕者方算得进系统。

--|
| GitHub Topics | `curl -s "https://api.github.com/search/repositories?q=topic:..."` | 每进化轮次 |
| Hermes Skills | `find skills/ -name 'SKILL.md'` | 每轮 |
| arXiv | `arxiv.search(query, max_results=10)` | 每2轮 |

完整关键词轮转策略见 `references/keyword-rotation.md`。

## 项目追踪

所有发现的项目存储在仓库根目录的 `absorption-ledger.json`。当前台账包含 **17 个吸收项目 + 2 个自我反射**，含来源、stars、吸收能力、目标技能、待完成项。

**记录分布**（三层结构）:
- `absorption-ledger.json`（根目录）— **统一台账**，每次吸收后追加
- `skills/.../evolution/absorption-*.md` — 各项目的详细五层吸收记录（13份）
- `references/*.md`（本技能下）— 分析级案例研究

新增吸收后的操作流程:
1. 详细记录 → 写入 `evolution/absorption-{project}.md`
2. 汇总 → 追加到 `absorption-ledger.json`
3. 格式归一化 → 按 OpenClaw merge pattern 处理

状态生命周期：
```
tracking（已扫描/候选）
  → evaluating（五维评分中）
    → absorbed（已吸收，有记录文件）
    → deferred（延后，有原因）
  → archived（关闭，有原因）

## 吸收报告模板

每次深度吸收后保留吸收报告（见 `references/absorption-report-template.md`）。

## 参考文件

- `../../../../../../absorption-ledger.json` — **统一台账**（17个吸收项目+2个自我反射）
- `references/absorption-gates-protocol.md` — L+0到L+3详细协议
- `references/keyword-rotation.md` — 关键词轮转策略和分类
- `references/absorption-report-template.md` — 吸收报告模板
- `references/multi-project-comparison.md` — 多项目哲学对比矩阵

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

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

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Skill Absorption---





--|
| GitHub Topics | `curl -s "https://api.github.com/search/repositories?q=topic:..."` | 每进化轮次 |
| Hermes Skills | `find skills/ -name 'SKILL.md'` | 每轮 |
| arXiv | `arxiv.search(query, max_results=10)` | 每2轮 |

完整关键词轮转策略见 `references/keyword-rotation.md`。

## 项目追踪

所有发现的项目存储在仓库根目录的 `absorption-ledger.json`。当前台账包含 **17 个吸收项目 + 2 个自我反射**，含来源、stars、吸收能力、目标技能、待完成项。

**记录分布**（三层结构）:
- `absorption-ledger.json`（根目录）— **统一台账**，每次吸收后追加
- `skills/.../evolution/absorption-*.md` — 各项目的详细五层吸收记录（13份）
- `references/*.md`（本技能下）— 分析级案例研究

新增吸收后的操作流程:
1. 详细记录 → 写入 `evolution/absorption-{project}.md`
2. 汇总 → 追加到 `absorption-ledger.json`
3. 格式归一化 → 按 OpenClaw merge pattern 处理

状态生命周期：
```
tracking（已扫描/候选）
  → evaluating（五维评分中）
    → absorbed（已吸收，有记录文件）
    → deferred（延后，有原因）
  → archived（关闭，有原因）

## 吸收报告模板

每次深度吸收后保留吸收报告（见 `references/absorption-report-template.md`）。

## 参考文件

- `../../../../../../absorption-ledger.json` — **统一台账**（17个吸收项目+2个自我反射）
- `references/absorption-gates-protocol.md` — L+0到L+3详细协议
- `references/keyword-rotation.md` — 关键词轮转策略和分类
- `references/absorption-report-template.md` — 吸收报告模板
- `references/multi-project-comparison.md` — 多项目哲学对比矩阵

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引

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

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

