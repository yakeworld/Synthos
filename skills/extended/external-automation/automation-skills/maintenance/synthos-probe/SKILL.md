---
name: synthos-probe
description: "Class: maintenance / audit"
version: 1.0.0
license: MIT
author: Synthos
metadata:
  synthos:
    signature: "task_desc: str, params: dict -> result: dict"
    atom_type: skill
    priority: P2
    related_skills: []

---





## IO_CONTRACT

- **input**: `probe_target: str` — 用户请求描述、上下文信息
- **output**: `probe_result: dict — Probe探测结果`

> 对应原则：P2（机械原子暴露输入输出规范）

# Synthos Probe — 7-Atom Structural Check
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

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
