# Skill Quality Audit Report — 2026-06-12

> 审计 `sda2/Synthos/skills/` 中 143 个 SKILL.md 的质量水平。
> 产出用于识别改进优先级。

## 关键数据

| 质量维度 | 数值 | 百分比 |
|---------|------|--------|
| BOUNDARY.md | 8/143 | 6% |
| IO_CONTRACT.md | 8/143 | 6% |
| EVIDENCE_SCHEMA.md | 8/143 | 6% |
| CHANGE_LOG.md | 8/143 | 6% |
| 完整 golden 测试 | 8/143 | 6% |
| SKILL.md ≥2KB | 91/143 | 64% |
| 含中文（类级别） | 17/37 | 46% |
| 有 references/ | 102/143 | 71% |
| 完整 frontmatter | 14/143 | 10% |

## Cron 任务发现的问题

### qc-batch-scan — KeyError
**根因**：JSON 状态文件包含已删除目录的条目，`r['d8_count']` 不存在。
**修复**：`r['d8_count']` → `r.get('d8_count')`（所有键用 `.get()`）。

### synthos-papers-to-gdrive.sh — 120s 超时
**根因**：`rclone check` 在大目录上超时。
**修复**：移除 `rclone check`，直接 `rclone sync`。

## 改进优先级

### P0: Cron 脚本错误
- ✅ `qc_batch_scan.py` 已修复
- ✅ `synthos-papers-to-gdrive.sh` 已修复

### P1: quality-gate 结构文件
`quality-gate` 是 P0 核心闸门，但缺少：
- BOUNDARY.md
- IO_CONTRACT.md
- EVIDENCE_SCHEMA.md
- CHANGE_LOG.md

### P2: 类级别技能中文缺失
37 个类级别技能中 20 个无中文内容，违反 Synthos 身份认同。

### P3: Golden 测试覆盖率
目标 ≥70%，当前仅 6%。按使用频率优先级补充。