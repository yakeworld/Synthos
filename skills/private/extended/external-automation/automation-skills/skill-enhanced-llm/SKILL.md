---
name: skill-enhanced-llm
description: Skill Enhanced Llm
signature: 'skill-enhanced-llm -> automation-skills: synthetic skill for skill enhanced llm'
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
    description: Skill Enhanced Llm
    signature: 'skill-enhanced-llm -> automation-skills: synthetic skill for skill enhanced llm'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


|
| 1.0.1 | 2026-06-29 | 补充实际运行数据、cron统计命令、未映射目录清理pitfall、层级化关键词检测规则 |
| 1.0.0 | 2026-06-29 | 初始版本: 基于Auto-Skill/SkillWeaver/Skill-MAS/OpenClaw-Skill论文的方法论吸收 |

## IO_CONTRACT

- **input**: `skills/ + cron 任务目录` — 技能使用率与调度状态扫描对象（27 技能 / 21 cron 任务口径）
- **input**: `evolution-state.json` — 进化状态摘要（v2 数据源）
- **output**: `references/skill-usage-data(-v2).md` — 技能使用率报告（运行次数、已归档任务、技能库统计）
- **output**: `unmapped_dirs: list[str]` — 未映射目录清理判定（只清理、不误删在用技能/脚本目录）

## 原则 (Principles)

1. **「凡数必源，无源则删。」** — 运行统计（27 技能 / 21 cron / 1352 次）须有采集口径与命令溯源，无源不立数。
2. **「先核后清，慎之再慎。」** — 未映射目录清理前必核验不在用，只清理、不误删在用技能/脚本目录。
3. **「源一不二，两版同口径。」** — v1 与 v2 使用率数据口径一致，evolution-state.json 摘要为唯一数据源。
4. **「统计可复，命令可验。」** — 21 个 cron 任务的运行统计命令须可执行、可复现，结果可验。



## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[SKIL-001]** 运行统计数据缺乏采集口径或命令溯源 → 拒绝发布数据，必须确保“凡数必源”，无源则删
- **[SKIL-002]** 执行未映射目录清理操作前 → 必须先行核验目录不在用，遵循“先核后清”原则以防误删在用技能
- **[SKIL-003]** 生成 v1 与 v2 版本的使用率报告时 → 必须保持两版数据口径一致，并以 evolution-state.json 为唯一数据源
- **[SKIL-004]** 统计 cron 任务运行数据时 → 必须确保统计命令可执行、可复现且结果可验证
- **[SKIL-005]** 扫描发现无 cron 引用且无调用记录的目录 → 标记为未映射目录，核验后执行清理并更新技能库统计
- **[SKIL-006]** 检测到统计命令不可复现或清理操作误删在用目录 → 立即触发回滚机制，拒绝发布报告并修复数据源

## Golden 集合 · GOLDEN SET

- **Golden Input**: `skills/` + cron 任务目录扫描（27 技能 / 21 cron 任务口径）+ `evolution-state.json` 摘要
- **Golden Output**: `references/skill-usage-data-v2.md`（运行 1352 次、已归档任务、技能库统计，与 v1 同口径）；`unmapped_dirs: []` 清理判定（仅清理未在用目录）
- **Golden Error**: 未映射目录清理误删在用技能/脚本目录 → 先核后清违反原则，回滚；或 21 个 cron 统计命令不可复现 → 数据无源，报告拒发

## 示例 · EXAMPLES

**输入**：`skills/`（27 技能）+ cron 任务目录（21 任务）+ `evolution-state.json` 摘要
**输出**：`references/skill-usage-data-v2.md` — 运行 1352 次、已归档任务 3 个、技能库 27 条目（含使用率排序）；`unmapped_dirs: []`（无清理需求）

**输入**：扫描发现 `skills/old-experiment/` 无 cron 引用、无 skill_view 调用记录
**输出**：`unmapped_dirs: ["skills/old-experiment/"]` → 核验不在用后清理，报告更新为 26 技能

## 十、参考文件

- `references/skill-usage-data.md` — 首次完整采集的技能使用率数据(27个技能、21个cron任务、1352次运行)
- `references/skill-usage-data-v2.md` — 更新版：含已归档任务、技能库统计、evolution-state.json摘要


# Skill Enhanced Llm---
> (P032 去重: 保留另一份 4 行独有内容)
## 验证清单 (Verification)
- [ ] 技能使用率数据已采集且与 v2 更新版一致（含已归档任务、技能库统计、evolution-state.json 摘要）
- [ ] 21 个 cron 任务的运行统计命令已验证（1352 次运行口径一致）
- [ ] 未映射目录已清理，且未误删在用的技能/脚本目录
