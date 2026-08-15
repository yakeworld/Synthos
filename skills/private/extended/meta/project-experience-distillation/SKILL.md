---
name: project-experience-distillation
description: 'Synthos skill: project-experience-distillation'
signature: 'project-experience-distillation -> meta: synthetic skill for project experience distillation'
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
    description: 'Synthos skill: project-experience-distillation'
    signature: 'project-experience-distillation -> meta: synthetic skill for project experience distillation'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
---


|
| 1 | **抽象不够** — 只在项目级别描述而不提升到通用级别 | 去掉项目名/路径/日期，保留可跨复用的模式 |
| 2 | **只记录不反思** — 记录了步骤没问"为什么有效" | 思想提升是灵魂，不是可选的 |
| 3 | **和 project-absorption 混淆** — 本技能是内部反思，project-absorption 是外部吸收 | 内部反思 = 从自身实践学；外部吸收 = 从外部项目学 |
| 4 | **轻易创建新 skill** | 普遍规律优先扩展现有技能，只有个性化规则才新开 |
| 5 | **建完 skill 不跑质量门** | 新建 skill 至少通过 L1 格式门 |
| 6 | **文档退化** — 累积 patch 操作导致同一节重复出现 | 大重构时重写整个文件，不累积 patch |
| 7 | **抽象级别不够深** — 只去掉实体名没上升到约束类型级别 | 真正的抽象是识别出**约束类型**，不是去掉名字保留模板 |

## IO_CONTRACT

- **input**: `project_practice: md` — 具体项目实践记录（含步骤、项目名、路径、日期）
- **input**: `reflection_q: "为什么有效"` — 反思问题（思想提升，非可选；目标是识别约束类型）
- **output**: `reusable_patterns` — 去掉项目名/路径/日期后上升到约束类型级别的跨项目可复用模式
- **output**: `skill_update: SKILL.md diff` — 优先扩展现有技能；确需新建时至少通过 L1 格式质量门

## 参考文件

- `ref/project-absorption-pattern.md` — 内部反思 vs 外部吸收对比方法论。两者是双向进化引擎：内部反思从自身实践学（P0），外部吸收从外部项目学（P1）。
- `references/batch-loop-pattern.md` — 批量循环执行模式。

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）---





|
| 1 | **抽象不够** — 只在项目级别描述而不提升到通用级别 | 去掉项目名/路径/日期，保留可跨复用的模式 |
| 2 | **只记录不反思** — 记录了步骤没问"为什么有效" | 思想提升是灵魂，不是可选的 |
| 3 | **和 project-absorption 混淆** — 本技能是内部反思，project-absorption 是外部吸收 | 内部反思 = 从自身实践学；外部吸收 = 从外部项目学 |
| 4 | **轻易创建新 skill** | 普遍规律优先扩展现有技能，只有个性化规则才新开 |
| 5 | **建完 skill 不跑质量门** | 新建 skill 至少通过 L1 格式门 |
| 6 | **文档退化** — 累积 patch 操作导致同一节重复出现 | 大重构时重写整个文件，不累积 patch |
| 7 | **抽象级别不够深** — 只去掉实体名没上升到约束类型级别 | 真正的抽象是识别出**约束类型**，不是去掉名字保留模板 |

## 参考文件

- `ref/project-absorption-pattern.md` — 内部反思 vs 外部吸收对比方法论。两者是双向进化引擎：内部反思从自身实践学（P0），外部吸收从外部项目学（P1）。
- `references/batch-loop-pattern.md` — 批量循环执行模式。

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

## 验证清单 (Verification)

- [ ] 提炼已去掉项目名/路径/日期，上升到可跨项目复用的模式
- [ ] 已问"为什么有效"并提炼出约束类型（而非仅去掉实体名保留模板）
- [ ] 区分内部反思（本技能）与外部吸收（project-absorption），未混淆
- [ ] 普遍规律优先扩展现有技能，未轻易新建 skill
- [ ] 新建 skill 已至少通过 L1 格式质量门
- [ ] 无累积 patch 导致的同节重复，大重构时整文件重写
