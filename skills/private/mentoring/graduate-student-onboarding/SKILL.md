---
name: graduate-student-onboarding
description: 'Scope tiers:'
signature: 'graduate-student-onboarding -> mentoring: synthetic skill for graduate student onboarding'
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
    description: 'Scope tiers:'
    signature: 'graduate-student-onboarding -> mentoring: synthetic skill for graduate student onboarding'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

|
| **Memory** | Write the convergence decision as a durable fact |
| **Cron: autonomous-core-researcher** | Update prompt: list allowed + prohibited directions explicitly |
| **Cron: paper-repair** | Add scope constraint — only repair in-scope papers |
| **Cron: paper-quality-review** | Skip out-of-scope papers |
| **Cron: paper-layer-b-review** | Skip out-of-scope papers |
| **Cron: literature-monitor** | Core directions → full report; peripheral → appendix only |

Scope tiers:
- **Core** (全流程): 5 pillars + Synthos + teaching + algorithm components + public dataset analysis
- **Peripheral** (仅空白+假设): cornea/lens/vitreous/tear film/tinnitus/concussion biomechanics

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] 研究方向已按 Scope tiers 分为 Core（全流程：5 pillars + Synthos + 教学 + 算法组件 + 公开数据集）与 Peripheral（仅空白+假设：角膜/晶状体/玻璃体/泪膜/耳鸣/脑震荡生物力学）
- [ ] 每个 Cron 任务（autonomous-core-researcher / paper-repair / paper-quality-review / paper-layer-b-review / literature-monitor）prompt 中显式列出允许与禁止的方向
- [ ] paper-repair 仅修复范围内（in-scope）论文；paper-quality-review 与 paper-layer-b-review 对范围外论文执行跳过
- [ ] literature-monitor 输出分级：核心方向生成完整报告，外围方向仅作附录
- [ ] 收敛决策（convergence decision）已作为持久化事实写入 Memory，后续 cron 与手动操作基于同一状态
- [ ] 所有输出通过准确性核查（无编造数据），结论可追溯到具体证据/数据源，操作步骤可重复验证

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

# Graduate Student Onboarding---

## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[GRAD-001]** 研究范围界定 → 将方向划分为核心（全流程）与外围（仅空白+假设）层级，并据此分配不同的处理深度
- **[GRAD-002]** 自动化任务配置 → 在 Cron 任务中显式列出允许与禁止的方向，确保执行边界清晰
- **[GRAD-003]** 论文处理流程 → 对范围外的论文执行跳过或仅修复范围内内容的约束，避免资源浪费
- **[GRAD-004]** 文献监控输出 → 核心方向生成完整报告，外围方向仅作为附录处理，以区分信息优先级
- **[GRAD-005]** 关键决策记录 → 将收敛决策作为持久化事实写入记忆，确保后续操作基于一致的状态
- **[GRAD-006]** 输出质量保障 → 遵循准确 > 证据 > 可复现的优先级，确保所有结论可追溯且操作可重复