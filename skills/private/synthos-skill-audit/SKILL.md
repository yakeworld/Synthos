---
name: synthos-skill-audit
description: Synthos Skill Audit
signature: 'synthos-skill-audit -> private: synthetic skill for synthos skill audit'
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
    description: Synthos Skill Audit
    signature: 'synthos-skill-audit -> private: synthetic skill for synthos skill
      audit'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---

## IO_CONTRACT

- **input**: 待审计技能文件 — `/learn` 生成的技能 + Synthos 标准技能（五节法对照对象）
- **input**: 双仓库架构状态 — 隐私技能迁移状态、路径陷阱点
- **output**: 映射审计结论 — 四块→五节法映射结果 + 调用层级差异分析
- **output**: 隐私扫描分级报告 — 敏感凭据检出与修复记录（路径陷阱检测/权限修复）

## 原则 (Principles)

1. **「先明其制，后论其合。」** — 审计以 Synthos 五节法为标准对照对象，四块→五节法映射方有合离之分。
2. **「层级有差，调用有别。」** — 调用层级差异须显式记录：`/learn` 生成技能与标准技能层级不同，不可混同。
3. **「凭据不入文，入则即修。」** — 隐私扫描分级后，敏感凭据不得出现于技能内容，检出即修复。
4. **「陷阱先探，权限先固。」** — 路径陷阱检测与权限修复（v1.4.0）先行，双仓库架构迁移状态须审计覆盖。

|
| 2026-06-28 | 2.1.0 | 新增 `ref/learn-vs-synthos-comparison.md` — `/learn` 生成技能 vs Synthos 标准完整对比，四块→五节法映射，调用层级差异分析 |
| 2026-06-27 | 2.0.0 | 重构：提炼思想/原理/IO Contract/流程/方法/规则。具体命令、案例移至 ref/ |
| 2026-06-25 | 1.5.0 | 新增双仓库架构、隐私技能迁移、隐私扫描分级 |
| 2026-06-21 | 1.4.0 | 新增路径陷阱检测、权限修复 |
| 2026-06-18 | 1.3.0 | 合并 project-health-audit，新增项目健康检查流程 |

# Synthos Skill Audit