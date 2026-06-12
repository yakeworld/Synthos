---
name: skill-integrity-audit
description: "技能库断裂诊断与恢复 — 当核心技能缺失、技能库分裂或 cron 引用不存在技能时执行。"
author: "Synthos"
version: "1.0.0"
tags:
- integrity
- audit
- skill-management
- system-health
metadata:
  synthos:
    priority: P1
    atom_type: meta-integrity
    description: 技能库断裂诊断与恢复 — 当核心技能缺失、技能库分裂或 cron 引用不存在技能时执行。
    signature: ['skill_inventory: list[Skill], cron_config: dict -> audit_report: dict'] -> ['audit_report: dict (missing_skills: list[str], broken_references: list[str], recovery_suggestions: list[str])']
    related_skills: [quality-gate, evolution, cognitive-atom-architecture, project-experience-distillation, paper-pipeline]


# Skill Integrity Audit — 技能库断裂诊断与恢复

> 当 agent 发现核心技能缺失、技能库分裂或 cron 引用了不存在的技能时执行。
> 核心哲学：技能是系统产物。技能缺失 = 系统产物丢失 = 进化失败。

## 原理层 · 文言

| 概念 | 文言 | 义 |
|------
  io_contract: input: ['skill_inventory: list[Skill], cron_config: dict -> audit_report: dict', 'output: ['audit_report: dict (missing_skills: list[str], broken_references: list[str], recovery_suggestions: list[str])']
|------|----|
| 技能即产物 | 文以验法，技乃所产 | 论文是验证，技能是产出；产物丢失 = 系统退步 |
| 闲则整之 | 闲则整之，不待问 | 发现断裂即修，不等确认 |
| 去形留神 | 去形留神，源一不二 | 记录修复路径而非具体文件名 |

## 诊断步骤

### Step 1: 识别断裂

```bash
# 检查 cron 任务引用的技能是否存在
# 列出所有 cron 任务及其引用的 skill
hermes cron list

# 检查核心技能是否存在
for skill in paper-pipeline quality-gate evolution skill-integrity-audit; do
  if [ ! -d "~/.hermes/skills/$skill" ]; then
    echo "MISSING: $skill"
  fi
done
```

### Step 2: 定位备份

```bash
# 检查备份目录
ls -la ~/.hermes/skills_bak_synthos_*/

# 查找特定技能
find ~/.hermes/skills_bak_synthos_*/ -name "SKILL.md" -path "*/$skill_name/*"
```

### Step 3: 执行恢复

```bash
# 从备份恢复技能
BACKUP_SRC=~/.hermes/skills_bak_synthos_20260531/writing/paper-pipeline
DEST=~/.hermes/skills/paper-pipeline

if [ -d "$BACKUP_SRC" ]; then
  cp -r "$BACKUP_SRC" "$DEST"
  echo "✓ Restored $skill_name"
fi
```

### Step 4: 验证

```bash
# 验证 skill_view 能正常加载
skill_view $skill_name

# 验证 cron 任务能正确引用
hermes cron list | grep -A5 "$skill_name"
```

## 常见断裂模式

### 模式 A：技能被误删除
- **症状**：cron 任务引用了不存在的 skill → 每次运行都失败
- **根因**：技能被删除但 cron 配置未更新
- **修复**：从备份恢复 + 检查是否应该保留还是迁移

### 模式 B：技能库分裂
- **症状**：`~/.hermes/skills/` 和 `Synthos/skills/` 中技能不一致
- **根因**：技能在不同目录间同步失败
- **修复**：统一到一个源（`~/.hermes/skills/`），清理另一处

### 模式 C：cron 引用了不存在的技能
- **症状**：cron 任务配置中 `skills` 字段指向不存在的技能
- **根因**：技能被重命名或迁移，cron 配置未更新
- **修复**：更新 cron 任务配置，移除或替换为正确技能名

## 修复后的检查清单

- [ ] 技能已从备份恢复或重新创建
- [ ] skill_view 能正常加载
- [ ] cron 任务配置已验证（或更新）
- [ ] 检查是否有其他技能也处于类似状态
- [ ] 记录修复到 session 日志

## Pitfalls

1. **不要只修复一个就停** — 检查所有 cron 任务引用的技能是否都存在
2. **备份可能已过时** — 检查备份日期，如果太旧可能需要重新创建技能
3. **技能可能已迁移** — 检查技能是否被移动到其他目录而非删除
4. **cron 任务可能已废弃** — 如果技能确实不需要了，应删除 cron 任务而非恢复技能

## Related Resources

| 资源 | 说明 |
|------|------|
| `references/skill-missing-incident-2026-06-12.md` | paper-pipeline 断裂事件完整记录 |