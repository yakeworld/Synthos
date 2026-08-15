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

## 十、参考文件

- `references/skill-usage-data.md` — 首次完整采集的技能使用率数据(27个技能、21个cron任务、1352次运行)
- `references/skill-usage-data-v2.md` — 更新版：含已归档任务、技能库统计、evolution-state.json摘要

# Skill Enhanced Llm---





|
| 1.0.1 | 2026-06-29 | 补充实际运行数据、cron统计命令、未映射目录清理pitfall、层级化关键词检测规则 |
| 1.0.0 | 2026-06-29 | 初始版本: 基于Auto-Skill/SkillWeaver/Skill-MAS/OpenClaw-Skill论文的方法论吸收 |

## 十、参考文件

- `references/skill-usage-data.md` — 首次完整采集的技能使用率数据(27个技能、21个cron任务、1352次运行)
- `references/skill-usage-data-v2.md` — 更新版：含已归档任务、技能库统计、evolution-state.json摘要

# Skill Enhanced Llm

## 验证清单 (Verification)

- [ ] 技能使用率数据已采集且与 v2 更新版一致（含已归档任务、技能库统计、evolution-state.json 摘要）
- [ ] 21 个 cron 任务的运行统计命令已验证（1352 次运行口径一致）
- [ ] 未映射目录已清理，且未误删在用的技能/脚本目录
