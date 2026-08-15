---
name: cognitive-atom-architecture
description: All original reference files, templates, and scripts should be intact at `~/.hermes/skills/cognitive
signature: 'cognitive-atom-architecture -> meta: synthetic skill for cognitive atom architecture'
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
    description: All original reference files, templates, and scripts should be intact at `~/.hermes/skills/cognitive
    signature: 'cognitive-atom-architecture -> meta: synthetic skill for cognitive atom architecture'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


## Reference Files (intact — see linked_files)

All original reference files, templates, and scripts should be intact at `~/.hermes/skills/cognitive-atom-architecture/references/`. See `skill_view('cognitive-atom-architecture', file_path=...)` to access individual references.

## IO_CONTRACT

- **input**: `philosophical_framework: md` — 7+1 东西融合哲学框架（`references/philosophical-foundations.md` 及各维度定义）
- **input**: `target_skill: SKILL.md` — 待追溯工程约束的原子技能文件（`skills/` 下各原子）
- **output**: `engineering_constraints` — 按 5 步流程（extract→trace→classify→fix→verify）从哲学约束追溯到原子技能的可执行约束
- **output**: `references/` — 完整参考文件集（philosophical-foundations / synthos-dimension-guide / 验证与融合 pattern，v4.0.0 四件套）

## 示例 · EXAMPLES

1. **基本用法**: 标准输入 → 标准输出
2. **边界用例**: 空输入、特殊字符、异常路径
3. **错误场景**: 缺失依赖、权限不足、网络异常

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每个示例必须可独立运行、有明确输入输出、包含错误处理。

**Session additions (2026-05-23):**
- `east-west-syncretism-pattern.md` — Methodology for merging Eastern ontology with Western epistemology into a single 7+1 framework. 4-step synthesis, per-dimension mapping table, known pitfalls.
- `philosophy-engineering-verification-pattern.md` — Methodology for verifying that a philosophical framework produces actionable engineering constraints in atomic skills. 5-step flow: extract→trace→classify→fix→verify.

Key reference files added in v4.0.0:
- `references/philosophical-foundations.md` — full 7+1 Syncretic Framework with per-dimension definitions and engineering constraints
- `references/synthos-dimension-guide.md` — per-dimension evaluation methods and atomic mappings
- `references/philosophy-engineering-verification-pattern.md` — methodology for tracing philosophical constraints through atomic skills (2026-05-23)
- `references/east-west-syncretism-pattern.md` — pattern for merging Eastern and Western philosophical concepts into unified engineering constraints

# Cognitive Atom Architecture---





## Reference Files (intact — see linked_files)

All original reference files, templates, and scripts should be intact at `~/.hermes/skills/cognitive-atom-architecture/references/`. See `skill_view('cognitive-atom-architecture', file_path=...)` to access individual references.

## 示例 · EXAMPLES

1. **基本用法**: 标准输入 → 标准输出
2. **边界用例**: 空输入、特殊字符、异常路径
3. **错误场景**: 缺失依赖、权限不足、网络异常

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每个示例必须可独立运行、有明确输入输出、包含错误处理。

**Session additions (2026-05-23):**
- `east-west-syncretism-pattern.md` — Methodology for merging Eastern ontology with Western epistemology into a single 7+1 framework. 4-step synthesis, per-dimension mapping table, known pitfalls.
- `philosophy-engineering-verification-pattern.md` — Methodology for verifying that a philosophical framework produces actionable engineering constraints in atomic skills. 5-step flow: extract→trace→classify→fix→verify.

Key reference files added in v4.0.0:
- `references/philosophical-foundations.md` — full 7+1 Syncretic Framework with per-dimension definitions and engineering constraints
- `references/synthos-dimension-guide.md` — per-dimension evaluation methods and atomic mappings
- `references/philosophy-engineering-verification-pattern.md` — methodology for tracing philosophical constraints through atomic skills (2026-05-23)
- `references/east-west-syncretism-pattern.md` — pattern for merging Eastern and Western philosophical concepts into unified engineering constraints

# Cognitive Atom Architecture

## 验证清单 (Verification)

- [ ] `~/.hermes/skills/cognitive-atom-architecture/references/` 下原始参考文件、模板、脚本完整无损（v4.0.0 四件套齐全）
- [ ] 哲学框架按 5 步流程（extract→trace→classify→fix→verify）在原子技能中追溯出可执行的工程约束
- [ ] 每个示例可独立运行、输入输出明确、含错误处理（边界/错误场景各一）
- [ ] 违反约束规则的操作被拒绝或隔离，未暴露内部状态
