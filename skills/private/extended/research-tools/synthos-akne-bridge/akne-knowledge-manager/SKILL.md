---
name: akne-knowledge-manager
description: '**边界**：技能功能边界。'
signature: 'akne-knowledge-manager -> synthos-akne-bridge: synthetic skill for akne knowledge manager'
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
    signature: 'akne-knowledge-manager -> synthos-akne-bridge: synthetic skill for akne knowledge manager'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---

|
| 2026-06-27 | 2.0.0 | 重构：提炼思想/原理/IO Contract/流程/方法/规则。具体命令、案例移至 references/ |
| 2026-06-13 | 1.0.0 | 初始版本：内容级审计（矛盾、版本簇、研究空白、假设） |

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] 输出中的事实性陈述已逐条核查，无编造数据（准确为先）
- [ ] 每个结论可追溯到具体证据或数据源（证据驱动），无孤证断言
- [ ] 操作步骤可重复执行且结果可验证（可复现性）
- [ ] 多重原则冲突时按"准确 > 证据 > 可复现"优先级裁决，裁决过程留有记录
- [ ] 改进/变更已通过 Golden 集合（Input/Output/Error）测试验证
- [ ] 每项验证可执行、可记录、可复现，验证失败时已记录原因及修复方案
- [ ] 边界情况（空输入/极大值/异常）有明确错误信息和恢复指引

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Akne Knowledge Manager---

## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[AKNE-001]** 输出包含事实性陈述 → 必须经过事实核查，严禁编造数据
- **[AKNE-002]** 得出任何结论 → 必须确保其可追溯到具体的证据或数据源
- **[AKNE-003]** 执行操作步骤 → 必须保证过程可重复且结果可验证
- **[AKNE-004]** 面对多重原则冲突 → 严格遵循“准确 > 证据 > 可复现”的优先级顺序
- **[AKNE-005]** 进行系统改进或变更 → 必须通过 Golden 集合（输入/输出/错误）的测试验证
- **[AKNE-006]** 执行验证流程 → 确保每项验证可执行、可记录、可复现，失败时记录原因及修复方案
- **[AKNE-007]** 处理边界情况（空输入/极大值/异常） → 必须包含明确的错误信息和恢复指引

## 示例 · EXAMPLES

1. 内容级审计：发现单位矛盾（证据驱动，AKNE-002；方法见 references/content-audit-aug2026.md）→ 输入 BPPV 知识库源文件；提取各文件物理参数声明并交叉比对，发现 `BPPV拟真参数设置.md` 声明"耳石半径 0.5~15nm 平均7.5nm"，与碳酸钙晶体实际直径 5-30 μm 相差 1000 倍（致命级矛盾）→ 验证：每条矛盾标注文件路径 + 声明原文 + 正确值来源（准确为先，AKNE-001），审计结论可复算、可复现（AKNE-003）。
2. 改进走 Golden 验证（AKNE-005）→ 输入对 KnowledgeGraph 查询逻辑的修改；按 Golden 集合依次回放 Golden Input（正常路径）/Golden Output（格式校验）/Golden Error（失败路径）→ 验证：全部 Golden 测试通过；若冲突按"准确 > 证据 > 可复现"优先级裁决（AKNE-004）并留存裁决记录。
3. 边界情况处理（AKNE-007）→ 输入空实体名或未知实体的 QueryEngine 查询（路径/导入模式见 references/api-reference.md，如 `qe.resolve_entity()`）→ 操作/输出：返回明确错误信息与恢复指引（建议的查询入口或参数修正），而非静默空结果 → 验证：错误信息含上下文与恢复指引，步骤可重复执行且结果一致（可复现性），无孤证断言。