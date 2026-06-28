# Cron 诊断模式详解

## 诊断命令模板

### 完整诊断脚本

```bash
#!/bin/bash
# cron-diagnostics.sh — Cron 任务健康诊断
# 用法: bash cron-diagnostics.sh

# 1. 获取所有 cron 任务（需通过 hermes agent 执行）
# cronjob action=list

# 2. 检查关键指标
echo "=== CRON HEALTH CHECK ==="

# 检查 paused 任务
echo "Paused tasks:"
# grep "paused" output

# 检查 error 状态
echo "Error status:"
# grep "last_status.*error" output

# 检查 deliver 配置
echo "Local deliver (agent):"
# grep "deliver.*local" output (non-no_agent jobs)

# 检查 paid tasks
echo "Paid tasks (deepseek):"
# grep "deepseek" output
```

### 诊断输出 JSON 模板

```json
{
  "total": 15,
  "by_type": {"agent": 11, "script": 4},
  "by_provider": {"deepseek": 6, "qwen": 7, "script_only": 2},
  "by_status": {"ok": 13, "error": 1, "paused": 2, "completed": 1},
  "issues": [
    {"job_id": "f33ce777b4ba", "name": "synthos-papers-to-gdrive", "severity": "HIGH", "issue": "paused + error", "action": "remove"},
    {"job_id": "e75667c2351f", "name": "literature-monitor", "severity": "INFO", "issue": "paid (deepseek-v4-flash)", "action": "verify"}
  ],
  "redundant_groups": {
    "paper_pipeline": ["papers-daily-scan", "bib-standardization", "daily-papers-report", "paper-repair", "paper-quality-review", "paper-layer-b-review"],
    "evolution": ["synthos-evolution-probe", "synthos-evolution-full"]
  },
  "optimization_actions": [
    {"type": "remove", "job_ids": ["f33ce777b4ba", "45481e6fe564", "e2ced0c400ad"]},
    {"type": "merge", "from": ["63bd3bc7ee08", "a8c95de4bb2e"], "to": "unified-paper-scan"},
    {"type": "fix", "job_id": "9bf24f47487c", "field": "deliver", "from": "local", "to": "origin"}
  ]
}
```

## 常见优化场景

### 场景 1：清理僵尸任务
**信号**: enabled=false, paused, 或 last_run_at 超过 30 天

### 场景 2：合并重复扫描
**信号**: 2+ 个任务使用相同 model 扫描同一目录

### 场景 3：控制付费任务
**信号**: deepseek 付费任务 > 4 个

### 场景 4：修复配置错误
**信号**: no_agent=True 但 model 不为 null, 或 agent 用 deliver=local

## 频率合理性标准

| 任务类型 | 合理频率 | 示例 |
|----------|----------|------|
| 心跳/监控 | 15-30m | gpu-heartbeat |
| 快速扫描 | 1-4h | qc-batch-scan |
| 论文扫描 | daily | unified-paper-scan |
| 论文修复 | 2h | paper-repair |
| 论文质量 | daily (多个时段) | G7, B质控 |
| 进化循环 | daily 03:00 | evolution-full |
| 文献监控 | daily 08:00 | literature-monitor |
| 月任务 | 1/月 | github-discussion |