# 技能审计实战记录 — 2026-05-30

本文件记录了一次完整的 166-skill 审计的操作模式，便于未来复用。

## 审计范围

- 总量: 166 skills (含 `.archive` 22 + 核心 ~40 + 外部 ~90 + 吸收 ~36)
- 核心关注: Synthos 核心技能的质量要素
- 清理: `.archive` 中的技能 → 吸收/删除/移出

## 操作模式

### 1. 全量列出技能

```bash
skills_list  # 或直接扫描 filesystem
find ~/.hermes/skills/ -name 'SKILL.md' -exec dirname {} \; | sed 's|.*/skills/||' | sort
```

### 2. 分类归类

按路径前缀分类:
- `uncategorized/` → 需要审核，可能是未归类的新技能
- `.archive/` → 已废弃但未删除的技能
- `mlops/`, `research/`, `writing/` 等 → 按功能领域

### 3. Archive 评估矩阵

对每个 `.archive` 中的技能，按以下三类处置:

| 类别 | 条件 | 处置 |
|:-----|:-----|:------|
| **已吸收到主技能** | 内容已被主技能覆盖（如 paper-workflow → paper-pipeline） | `rm -rf` + 记录 absorbed_into |
| **有价值但被误归档** | 独立可用的方法论/工作流 | `mv` 到正确分类目录 |
| **完全过时** | 描述的是 v0.x 架构/已被替代的技术 | `rm -rf` |

### 4. 核心技能质量检查清单

| 检查项 | 方法 | 标准 |
|:-------|:-----|:-----|
| 文言节 | `grep -c '文言' SKILL.md` | ≥1 条（核心技能 ≥4 条） |
| 版本号 | `grep 'version:' SKILL.md` | 必须存在 |
| 验证清单 | `grep -cE '验证\|Verification\|Checklist'` | ≥5 |
| 文件大小 | `wc -c SKILL.md` | ≥5KB（太薄则内容可能不足） |

### 5. 吸收规则（从 archive → 主技能）

```yaml
# 吸收映射示例:
reflexive-abstraction:              → project-experience-distillation
paper-workflow:                     → paper-pipeline
sci-paper-loop-optimization:        → dual-quality-check-v2 + academic-paper-completion
hermes-scientist:                   → autonomous-core-researcher (deprecated)
notebooklm-literature-optimization:  → notebooklm-cli
semantic-scholar:                   → research-paper-search
agent-skills-compliance:            → quality-gate
project-health-assessment:          → quality-gate
project-security-audit:             → quality-gate
multi-model-research-routing:       → task-router
task-router-config:                 → task-router
ml-pipeline-debugging:              → systematic-debugging
```

## 一次性清理模式的收益

- 删除 13 个冗余 skill → 减少 skill_view 时的搜索空间
- 移出 9 个被归档的有用 skill → 恢复可用性
- 添加 8 条 文言 → 提升核心技能哲学一致性
- `.archive` 归零 → 无遗留死文件夹

## 未来建议

- 每个新技能创建时自动检查是否应归类而非留在 uncategorized
- 每季度运行一次 archive 清理（累计不会超过 5 个新条目）
- 核心技能（quality-gate, paper-pipeline, evolution 等）每次 major 版本更新时检查文言一致性
