---
name: skill-integrity-audit
description: "技能库断裂诊断与恢复 — 当核心技能缺失、技能库分裂或 cron 引用了不存在的技能时执行。"
author: "Synthos"
version: "2.1.0"
tags:
- integrity
- audit
- skill-management
- system-health
metadata:
  synthos:
    priority: P0
    atom_type: "self-healing"
    category: "infrastructure"
---

# Skill Integrity Audit — 技能库断裂诊断与恢复

> 当 agent 发现核心技能缺失、技能库分裂或 cron 引用了不存在的技能时执行。
> 核心哲学：技能是系统产物。技能缺失 = 系统产物丢失 = 进化失败。

## 原理层 · 文言

| 概念 | 文言 | 义 |
|------|------|----|
| 技能即产物 | 文以验法，技乃所产 | 论文是验证，技能是产出；产物丢失 = 系统退步 |
| 闲则整之 | 闲则整之，不待问 | 发现断裂即修，不等确认 |
| 去形留神 | 去形留神，源一不二 | 记录修复路径而非具体文件名 |

## 镜像同步协议（2026-06-12 建立）

> **权威源规则。** `/media/yakeworld/sda2/Synthos/skills/` 是权威源。
> `~/.hermes/skills/` 是镜像，必须与权威源同步。

**同步规则：**
- 重叠技能（两者都有）：以权威源为准，覆盖镜像
- 本地独有非 Hermes 内置技能：推送至上游权威源（local → sda2）
- 本地独有 Hermes 内置技能（dogfood, email, gaming, hermes, red-teaming）：保留不删除

**安全同步模式（2026-06-12 实战修正）：**
```bash
# 对重叠技能：先删除再复制，避免嵌套重复
rm -rf "$HOME/.hermes/skills/$skill"
cp -r "$sda2_dir/$skill" "$HOME/.hermes/skills/$skill"
```

**嵌套目录重复陷阱（2026-06-12 发现）：**
`cp -r src/ skill/ dest/` 当 `dest/skill/` 已存在同名目录时，会创建 `skill/skill/` 嵌套重复。

## 诊断步骤

1. 识别断裂 — `hermes cron list` + `skill_view` 检查
2. 定位备份 — `find ~/.hermes/skills_bak_synthos_*/`
3. 执行恢复 — `cp -r` 从备份
4. 验证 — `skill_view` + `hermes cron list`

## Pitfalls

1. **不要只修复一个就停** — 检查所有 cron 任务引用的技能
2. **备份可能已过时** — 检查备份日期
3. **技能可能已迁移** — 检查是否移动到其他目录
4. **嵌套目录重复** — `cp -r` 到同名目录会创建 `skill/skill/`，先 `rm -rf` 再 `cp -r`
5. **镜像同步顺序** — 重叠技能以权威源为准
6. **状态文件陈旧** — cron JSON 状态含已删除目录条目导致 KeyError。用 `.get()` 或清除 `~/.hermes/qc_last_scan_v*.json`
7. **rclone 超时** — `rclone check` 超过 120s。直接 `rclone sync`
8. **质量门结构缺失** — quality-gate 缺少 BOUNDARY/IO_CONTRACT/EVIDENCE_SCHEMA/CHANGE_LOG
9. **url insteadOf 冲突** — `~/.gitconfig` 中 HTTPS->SSH 转换导致 403。`git config --global --unset url.https://github.com/.insteadOf`
10. **credential.helper 冲突** — `store` 覆盖 `gh auth git-credential`。`git config --global --unset credential.helper`
11. **PAT scope 不足** — 只读 PAT 导致 git push 403。需要 Classic/Fine-grained PAT 勾选 `repo` scope

## 技能质量审计 (2026-06-12→v4)

> 系统化审计 + 自动修复技能结构。按 Synthos 哲学分层处理：
> - **类级别技能**（核心原子/质量相关/基础设施）→ 需要完整结构：BOUNDARY.md + IO_CONTRACT.md + EVIDENCE_SCHEMA.md + CHANGE_LOG.md + golden/ + references/ + 原理层（文言）
> - **工具级别技能**（嵌套在类下）→ 只需精简使用说明，不强制结构文件

### 质量审计 Cron 脚本

脚本位置：`scripts/skill_quality_audit_v4.py`
- 扫描所有 143+ 技能，按优先级 P0→P1 修复
- P0：核心技能（evolution, quality-gate, paper-pipeline 等 25+ 个）
- P1：其余所有类级别技能
- 自动创建缺失的 BOUNDARY.md / IO_CONTRACT.md / EVIDENCE_SCHEMA.md / CHANGE_LOG.md
- 自动创建 golden/ 目录和 golden/GOLDEN_SET.md
- 自动创建 references/ 目录
- 为所有类级别 SKILL.md 注入原理层（文言文）
- 跳过 8 个非目录条目

### 质量基线 (2026-06-13)

- 总技能：157（含嵌套工具级）
- 优秀 (≥77.8%)：7 个（5%）— evolution, task-router, knowledge-acquisition 等
- 低质 (<44.4%)：135 个（94%）— 大部分缺少结构文件
- **平均质量：14.6%，中位数：12.5%**

### 核心原则

> 文以验法，技乃所产。类级别技能需完整结构（原理层+契约层+证据层+变更层）；工具级别技能只需精简使用说明。

## Related Resources

| 资源 | 说明 |
|------|------|
| `scripts/skill_quality_audit_v4.py` | 技能质量自动审计与修复 Cron 脚本 |
| `references/skill-quality-audit-v2-2026-06-12.md` | 技能质量审计报告 v2 |
| `references/skill-quality-baseline.md` | 2026-06-13 更新后质量基线数据 |
| `references/skill-missing-incident-2026-06-12.md` | paper-pipeline 断裂事件记录 |
| `references/git-credential-debug.md` | GitHub 认证调试完整路径 |
| `references/skill-philosophy-class-vs-tool.md` | 类级别 vs 工具级别技能质量要求差异 |