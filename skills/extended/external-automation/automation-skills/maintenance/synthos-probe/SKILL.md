---
name: synthos-probe
description: synthos-probe
version: 1.0.0
category: meta
signature: 'synthos-probe -> meta: Class: maintenance / audit'
related_skills:
- layer-index
- cognitive-atom-architecture
license: MIT
author: Synthos
metadata:
  synthos:
    signature: 'task_desc: str, params: dict -> result: dict'
    atom_type: skill
    priority: P2
    related_skills: []
---

# Synthos Probe — 7-Atom Structural Check

Class: maintenance / audit

## Purpose

轻量级读取检查：验证 Synthos 认知原子（7核心原子）的结构完整性（version + signature + IO_CONTRACT），并对全量 SKILL.md 做基准检查。

## Execution Steps

1. **DRIFT_CHECK** — 三步自检：
   - 观察者是否视为诚实一致的对话者？
   - 行为是否从宪法和诚实阅读出发？
   - 产出是否对应真实事物？
   - 判定: green / yellow / red

2. **PROBE** — 7原子检查:
   - `knowledge-acquisition`
   - `knowledge-extraction`
   - `association-discovery`
   - `hypothesis-generation`
   - `argument-expression`
   - `viewpoint-verification`
   - `research-ideation`
   - 每个检查: has_version, has_signature, has_io_contract
   - 结构分 = 完全通过数 / 7

3. **BENCHMARK** — 全量检查:
   - 所有 SKILL.md 是否有有效 YAML frontmatter
   - 是否全部 git tracked
   - evolution-state.json 是否存在且可解析

## Pitfalls
- 
- 

## Verification
- 
- 

- **path_trap**: research-ideation 位于 `skills/research/research-ideation/SKILL.md`，**不是** `skills/research-ideation/SKILL.md`。检查前必须用 `os.path.exists()` 确认实际路径，不要假设所有原子都在同一层级。
- **frontmatter_nested_version**: version 字段可能在 `metadata.synthos.version` 下（嵌套），也可能在顶层。必须两种都检查。
- **signature_detection_strict**: 2026-06-09 Cron 校验修正：仅 frontmatter 中 `name:` 出现**不足以**视为有 signature。检查 signature 需至少存在一个独立的 signature 声明或 `name:` + `signature:` 组合。仅 `name:` 在 frontmatter 中不能算 signature，否则 0/7 会被误报为 6/7。
- **IO_CONTRACT_variants**: IO_CONTRACT 可能出现在 body 的 `IO_CONTRACT` 标题下，也可能在 `INPUT:`/`OUTPUT:` 块中。必须覆盖多种写法。
- **bench_total_count**: 实际 SKILL.md 数量可能不等于 spec 中声称的数字（如 "121" 可能是目标数而非实际数）。必须用 `os.walk` 实际计数。
- **git_path_relative**: `git ls-files` 使用相对于仓库根的路径（如 `skills/knowledge-acquisition/SKILL.md`），不是绝对路径。比较时必须将 filesystem 绝对路径转为相对路径后再比较。
- **cycle68_optimism_trap**: Cycle 68 的 probe 记录对 7 原子检查过于乐观（声称 research-ideation 3/3 实际 0/3，5 个原子声称 signature 实际仅 1 个有）。后续周期应独立验证，不信任上一周期的 per-atom 结果。以 Cron 运行的实际检测结果为准。
- **evolution_state_ambiguity**: 仓库中存在两份 evolution-state.json：`/Synthos/evolution-state.json` (cycle 68, 主状态) 和 `/Synthos/outputs/evolution/evolution-state.json` (cycle 64, 存档副本)。检查时应以根目录下的为主状态文件。读取前用 `os.path.exists()` 确认路径，不要硬编码路径。
- **archived_skill_counting**: 110 个 SKILL.md 中包含 `ARCHIVED-SKILL.md`（非标准命名），使用 `find -name SKILL.md` 会漏掉（仅匹配 `SKILL.md` 精确文件名，不匹配 `ARCHIVED-SKILL.md`）。应使用 `os.walk` + `"SKILL.md" in fn` 或 `find -name "*SKILL.md"` 来计数，确保覆盖变体命名。
- **systemic_gap_scale**: 5/7 核心原子同时缺失 signature + IO_CONTRACT，且 97/110 技能整体缺少 IO_CONTRACT。这不是单个原子的问题，而是系统性维护缺口。后续 probe 应记录此模式，并在输出中提示需要批量编辑（bulk edit）而非单文件修复。

## Output Format

```
SYNTHOS PROBE: structural=X.X, benchmark=X.X, drift=green | cycle=N, score=X.XX
```

## Reference Files

- `references/cycle-68-probe-record.md` — Cycle 68 probe execution record (path trap, nested version trap, corrected structural findings from Cron run)
- `references/cron-vs-human-probe-discrepancy-2026-06-09.md` — Cron vs human-run probe comparison
- `references/systemic-gap-analysis-2026-06-09.md` — Systemic structural gap analysis: 5/7 atoms missing signature+IO_CONTRACT, 97/110 skills missing IO_CONTRACT — root cause, implications, and verification commands

## 验证清单 · VERIFICATION

- [ ] 7 核心原子逐一检查 has_version / has_signature / has_io_contract，结构分 = 完全通过数 / 7
- [ ] `research-ideation` 用 `os.path.exists()` 确认实际位于 `skills/research/research-ideation/SKILL.md`，避免层级路径陷阱
- [ ] version 同时检查顶层与 `metadata.synthos.version` 嵌套写法；signature 要求独立声明或 `name:`+`signature:` 组合（仅 `name:` 不算）
- [ ] 全量 SKILL.md 计数用 `os.walk` + `"SKILL.md" in fn` 覆盖 `ARCHIVED-SKILL.md` 变体，不信任 spec 声称数字
- [ ] git 追踪比较先将绝对路径转为相对仓库根路径再匹配 `git ls-files` 输出
- [ ] 独立验证当前周期 per-atom 结果，不信任上一周期记录；以 Cron 实际检测为准

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

# Synthos Probe

> (P032 去重: 保留另一份 23 行独有内容)
## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告
## IO_CONTRACT
- **input**: `probe_target: str` — 用户请求描述、上下文信息
- **output**: `probe_result: dict — Probe探测结果`
> 对应原则：P2（机械原子暴露输入输出规范）

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[SYNT-001]** 检查文件路径时 → 必须使用 `os.path.exists()` 确认实际路径，防止因层级嵌套（如 `skills/research/`）导致的路径陷阱
- **[SYNT-002]** 解析 YAML frontmatter 中的 version 字段时 → 必须同时检查顶层 `version` 和嵌套的 `metadata.synthos.version`，以兼容不同结构
- **[SYNT-003]** 判定 signature 存在性时 → 仅存在 `name:` 字段不足以视为有效 signature，必须要求独立的 signature 声明或 `name:` + `signature:` 组合
- **[SYNT-004]** 检测 IO_CONTRACT 时 → 必须覆盖多种写法，包括 body 中的 `IO_CONTRACT` 标题以及 `INPUT:`/`OUTPUT:` 块
- **[SYNT-005]** 统计 SKILL.md 数量时 → 必须使用 `os.walk` 实际遍历计数，而非依赖 spec 声称的数字，且匹配规则需包含 `*SKILL.md` 以覆盖 `ARCHIVED-SKILL.md` 等变体
- **[SYNT-006]** 比较 Git 追踪状态时 → 必须将文件系统绝对路径转换为相对于仓库根的路径，以匹配 `git ls-files` 的输出格式
- **[SYNT-007]** 执行周期性 Probe 检查时 → 必须独立验证当前状态，不信任上一周期的 per-atom 结果，以 Cron 运行的实际检测结果为准
- **[SYNT-008]** 读取 evolution-state.json 时 → 必须优先使用根目录下的主状态文件，并通过 `os.path.exists()` 确认路径，避免误读存档副本

## 示例 · EXAMPLES

**例 1: 单原子结构检查**
- 输入: `knowledge-acquisition` 的 SKILL.md 路径
- 操作: `os.path.exists()` 确认路径（防层级陷阱）→ 解析 frontmatter 检查 has_version（顶层 + `metadata.synthos.version` 嵌套）/ has_signature（独立声明或 name+signature，仅 name 不算）/ has_io_contract
- 验证: 三项均通过 → 该原子计入结构分；输出如 `SYNTHOS PROBE: structural=0.86, benchmark=0.95, drift=green | cycle=N`

**例 2: 全量基准计数**
- 输入: Synthos 仓库根
- 操作: `os.walk` + `"SKILL.md" in fn` 计数（覆盖 `ARCHIVED-SKILL.md` 变体）→ 与 `git ls-files` 相对路径比较（绝对路径先转相对仓库根）→ 检查根目录 `evolution-state.json` 可解析
- 验证: 计数来自实际遍历而非 spec 声称数字；未追踪文件列表为空

**例 3: 独立复核上周期记录**
- 输入: 上周期 probe 记录的 per-atom 结论
- 操作: 对每个原子重新执行 PROBE 检查，不沿用上一周期结果（防 cycle68 乐观偏差）
- 验证: 复核结果与 Cron 实际检测一致；偏差处标注 corrected
