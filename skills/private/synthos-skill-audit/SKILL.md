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

# Synthos Skill Audit---

> (P032 去重: 保留另一份 9 行独有内容)
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[SYNT-001]** 审计 `/learn` 生成技能时 → 必须以 Synthos 五节法为标准对照对象，执行四块结构到五节法的逐节映射
- **[SYNT-002]** 对比不同来源技能时 → 须显式记录调用层级差异（如 P2 vs P0-P1），严禁将 `/learn` 生成技能与标准技能混同
- **[SYNT-003]** 执行隐私扫描检出敏感凭据时 → 必须立即执行修复（如环境变量化），确保凭据不残留于技能内容中
- **[SYNT-004]** 开始审计流程前 → 优先执行路径陷阱检测与权限修复，确保双仓库架构迁移状态被完整覆盖
- **[SYNT-005]** 验证审计结果时 → 若隐私扫描检出 0 处凭据，需复核扫描覆盖范围，防止因未执行完整扫描而误报“通过”
## 验证清单 (Verification)
- [ ] `/learn` 生成技能已对照 Synthos 标准完成映射（四块→五节法）并记录调用层级差异
- [ ] 已执行路径陷阱检测与权限修复（v1.4.0）
- [ ] 隐私扫描分级已执行，敏感凭据未出现在技能内容中
- [ ] 审计已覆盖双仓库架构（含隐私技能迁移状态）
## Golden 集合 · GOLDEN SET
- **Golden Input**: `/learn` 生成的技能文件（四块结构）+ Synthos 标准技能（五节法），含双仓库架构路径（`skills/private/` vs `skills/`）与隐私技能迁移状态清单。
- **Golden Output**: 映射审计结论 — 四块→五节法逐节对照表、调用层级差异记录、路径陷阱检测结果（如 broken symlink 已修复）、隐私扫描分级报告（检出 N 处敏感凭据并全部修复），双仓库架构迁移状态完整覆盖。
- **Golden Error**: 审计仅比对五节法结构，未执行隐私扫描 → 检出 0 处凭据即报"通过" → 诊断：违反"凭据不入文，入则即修"原则，扫描覆盖不全；修复：补跑隐私扫描分级（grep API Key/Token/密码模式），对检出凭据执行环境变量化修复后重新验证。
## 示例 · EXAMPLES
- **示例一（/learn 技能审计）**：输入：`/learn` 生成的 `xhs-content` 技能（四块结构：思想/原理/流程/方法）+ Synthos 标准技能（五节法）→ 输出：四块→五节法逐节对照表（思想→原则、原理→核心原则、流程→验证清单、方法→Golden 集合）、调用层级差异记录（`/learn` 为 P2，标准技能为 P0-P1）、隐私扫描报告（检出 0 处凭据）、路径陷阱检测（1 处 broken symlink 已修复）。来源：`ref/learn-vs-synthos-comparison.md`。
- **示例二（双仓库架构审计）**：输入：`skills/private/` 下 3 个待迁移隐私技能 + 迁移状态清单 → 输出：迁移覆盖率 2/3（1 个技能因含 API Key 硬编码被拦截），拦截项附 grep 检出位置（行号）+ 修复建议（环境变量化），修复后复扫通过。来源：`git diff` 输出 + `grep` 日志。