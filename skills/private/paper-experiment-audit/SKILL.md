---
name: paper-experiment-audit
description: '**边界**：技能功能边界。'
signature: 'paper-experiment-audit -> private: synthetic skill for paper experiment audit'
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
    description: '**边界**：技能功能边界。'
    signature: 'paper-experiment-audit -> private: synthetic skill for paper experiment audit'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

|
| 2026-06-29 | 2.1.0 | 新增：数据集版本陷阱（WDBC 699 vs 569）、消融实验可复现性检查、thebibliography与bib同步检查、fig6重复引用检测 |
| 2026-06-24 | 1.4.0 | 新增 OpenML 外部数据库实验真实性验证、多 JSON 源 Ensemble 交叉验证 |
| 2026-06-23 | 1.3.0 | 新增多脚本-多输出交叉验证 |
| 2026-06-21 | 1.2.0 | 新增 SHAP 模型源验证、声称-实验交叉验证、后台自动执行模式 |

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] 数据集版本已固定：审计前已记录并锁定数据集版本（如 WDBC 699 vs 569 样本数差异），未跨版本对比指标
- [ ] 消融实验可复现：每个消融配置有独立运行脚本 + 输出 JSON/CSV，复现结果与声称差值 ≤0.5% 视为一致
- [ ] 引用同步无 MISMATCH：thebibliography 内条目与 references.bib 一一对应，缺项/余项均已标记并修复
- [ ] 图表引用无冗余：同一 fig（如 fig6）正文重复引用超过 2 次已标记冗余并合并为单次引用
- [ ] 指标多源交叉验证：同一指标有 ≥2 个独立脚本生成的 JSON/CSV 输出交叉核对，单一来源已标记 UNVERIFIED
- [ ] 结论可追溯：每个审计结论可追溯到具体证据或数据源，遵循"准确 > 证据 > 可复现"优先级

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

## Golden 集合 · GOLDEN SET

- **Golden Input**: 一篇含 WDBC 实验的 LaTeX 论文目录——`thebibliography` 与 `references.bib` 并存、含消融实验独立运行脚本 + 输出 JSON、正文 fig6 重复引用 3 次（覆盖正常审计路径）
- **Golden Output**: 六条 VERIFICATION 全部打勾的审计日志——数据集版本锁定（699/569 分别记录）、消融复现差值 ≤0.5% 判"一致"、thebibliography↔bib 无 MISMATCH、fig6 冗余引用合并为单次、同一指标 ≥2 独立源交叉核对、每条结论可溯源（精确匹配审计日志模板）
- **Golden Error**: 跨版本对比（699 vs 569）或消融复现差值 >0.5% 时，输出 MISMATCH 标记并列出差值来源与版本号，阻断后续结论（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Paper Experiment Audit---

## 约束规则 · RULES
1. **数据集版本固定**：审计实验前必须记录数据集版本（如 WDBC 699 vs 569 样本数差异），禁止跨版本对比指标。
2. **消融实验可复现**：每个消融配置须有独立运行脚本 + 输出 JSON/CSV，复现结果与声称差值 ≤0.5% 视为一致。
3. **引用同步**：`thebibliography` 内条目与 `references.bib` 必须一一对应，缺项/余项均标记 MISMATCH 并修复。
4. **图表唯一引用**：同一 fig（如 fig6）在正文中被重复引用超过 2 次 → 标记冗余，合并为单次引用。
5. **多源交叉验证**：同一指标须有 ≥2 个独立 JSON/CSV 输出（不同脚本）交叉核对，单一来源视为 UNVERIFIED。
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[PAPE-001]** 审计实验前 → 必须记录并固定数据集版本（如 WDBC 样本数差异），禁止跨版本对比指标
- **[PAPE-002]** 验证消融实验可复现性 → 每个配置须有独立脚本及输出文件，复现结果与声称差值 ≤0.5% 方视为一致
- **[PAPE-003]** 检查参考文献一致性 → `thebibliography` 与 `references.bib` 须一一对应，缺项或余项均标记 MISMATCH 并修复
- **[PAPE-004]** 检测图表引用冗余 → 同一 fig 在正文中被重复引用超过 2 次时，标记冗余并合并为单次引用
- **[PAPE-005]** 验证指标数据真实性 → 同一指标须有 ≥2 个独立脚本生成的 JSON/CSV 输出交叉核对，单一来源视为 UNVERIFIED
- **[PAPE-006]** 形成审计结论 → 必须遵循“准确 > 证据 > 可复现”优先级，确保每个结论可追溯到具体证据或数据源

## 示例 · EXAMPLES

1. **输入**: 一篇论文用 WDBC 数据集对比两个模型 F1。**操作**: 按规则 1（PAPE-001）审计前先记录锁定数据集版本，发现基线用 699 样本、新方法用 569 样本 → 判定跨版本对比，标记无效。**验证**: VERIFICATION 第一条（数据集版本固定）通过，审计结论引用版本号而非仅指标数字（PAPE-006）。
2. **输入**: 论文声称去掉模块 A 后精度掉 2.1%。**操作**: 按规则 2（PAPE-002）用该消融配置的独立运行脚本复现，读输出 JSON 与声称值比对。**验证**: 复现差值 ≤0.5% → 判"一致"；若 >0.5% 记 MISMATCH 并列出差值来源（证据驱动，结论可溯源）。
3. **输入**: 检查某指标只有单一 `metrics.json` 来源，且 fig6 在正文出现 4 次。**操作**: 按规则 5（PAPE-005）将该指标标 UNVERIFIED 并补第二个独立脚本输出交叉核对；按规则 4（PAPE-004）将 fig6 重复引用合并为单次。**验证**: VERIFICATION 中"指标多源交叉验证"与"图表引用无冗余"两条均打勾，修复处写入审计日志。