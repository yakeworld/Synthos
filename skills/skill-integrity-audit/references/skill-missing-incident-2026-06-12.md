# Paper-Pipeline Skill Missing Incident — 2026-06-12

## 问题发现

Agent 在自我审计时发现 `paper-pipeline` 技能从 `~/.hermes/skills/` 中消失，但仍存在于备份目录 `~/.hermes/skills_bak_synthos_20260531/writing/paper-pipeline/`。

## 影响范围

- **cron 任务**：`autonomous-core-researcher` (job_id: ff134d00da00) 每 30 分钟触发，引用 `paper-pipeline` 和 `quality-gate` 技能
- **错误表现**：每次运行都因找不到 skill 而失败，状态标记为 `error`
- **持续时间**：86+ 天（从备份日期 2026-05-31 开始缺失）

## 诊断过程

1. 运行 `skill_view paper-pipeline` → 返回 "Skill not found"
2. 检查 `ls ~/.hermes/skills/paper-pipeline` → 目录不存在
3. 检查备份目录 `ls ~/.hermes/skills_bak_synthos_*/` → 找到备份
4. 检查 cron 任务配置 → 确认任务仍引用 `paper-pipeline`

## 修复步骤

```bash
# 从备份恢复
BACKUP_SRC=~/.hermes/skills_bak_synthos_20260531/writing/paper-pipeline
DEST=~/.hermes/skills/paper-pipeline

cp -r "$BACKUP_SRC" "$DEST"

# 验证
skill_view paper-pipeline  # 应该正常加载
hermes cron list           # 确认任务配置正确
```

## 验证结果

- `paper-pipeline` 技能已恢复，包含：
  - `SKILL.md` (47,982 bytes) — 完整技能定义
  - `references/` (61 文件) — 参考文档
  - `scripts/` (3 文件) — 辅助脚本
  - `templates/` (2 文件) — 模板文件

## 根本原因分析

**可能原因**：技能在 2026-05-31 后被误删除或迁移，但 cron 配置未更新。

**系统缺陷**：没有自动检测技能缺失的机制。86 天内无人发现。

## 预防措施

1. **自动化检查**：在 cron 任务启动前检查引用的技能是否存在
2. **技能库同步**：确保 `~/.hermes/skills/` 和 `Synthos/skills/` 保持一致
3. **监控告警**：当 cron 任务因技能缺失失败时立即告警

## 相关修复

- 同时发现并修复了 `qc_batch_scan.py` 语法错误
- 修复了 `synthos-papers-to-gdrive.sh` 超时问题
- 为 `autonomous-core-researcher` 添加了 pre-flight 网络探测

## 后续行动

1. 检查其他 cron 任务引用的技能是否都存在
2. 评估 `skills_bak_synthos_*/` 备份中是否还有其他已删除的核心技能
3. 统一技能库管理策略（确定单一源目录）