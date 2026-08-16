---
name: akne-knowledge-manager
description: '**边界**：技能功能边界。'
signature: 'akne-knowledge-manager -> synthos-akne-bridge: synthetic skill for akne
  knowledge manager'
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
    signature: 'akne-knowledge-manager -> synthos-akne-bridge: synthetic skill for
      akne knowledge manager'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
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

- **Golden Input**: BPPV 知识库源文件集（含 `BPPV拟真参数设置.md` 等），用于内容级审计——提取各文件物理参数声明并交叉比对（正常路径，AKNE-002）。
- **Golden Output**: 审计结论中每条矛盾标注 文件路径 + 声明原文 + 正确值来源（如"耳石半径 0.5~15nm"与碳酸钙晶体实际 5-30 μm 相差 1000 倍），可复算、可复现（准确为先，AKNE-001/003）。
- **Golden Error**: 对空实体名或未知实体执行 `qe.resolve_entity()` 查询 → 预期返回明确错误信息与恢复指引（建议的查询入口或参数修正），而非静默空结果（边界情况，AKNE-007）。

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Akne Knowledge Manager