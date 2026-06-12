---
name: paper-cron-scan
description: BOUNDARY — Skill paper-cron-scan 边界定义
---

# 边界定义: paper-cron-scan

## 范围
'论文管线 Cron 扫描 — 轻量级白空间扫描、旋转方向轮转、日志追加。每次 Cron 运行执行：读取 tracker → 扫描 PubMed/OpenAlex 5个旋转方向 → 验证候选白空间 → 追加 agent-log.md → 更新 last_run。'

## 输入
- 任务/需求描述
- 目标/预期输出

## 输出
- 对应工具操作的完整结果

## 边界
- 不属于本技能范围的工作应路由到其他技能或拒绝
