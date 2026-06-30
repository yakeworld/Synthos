# 技能使用率监控 — 实际运行数据

> 2026-06-29 首次完整采集

## Cron运行统计

| 指标 | 数值 |
|------|------|
| 总任务数 | 21个 (15个在jobs.json + 6个已删除) |
| 总运行次数 | 1,352次 |
| 时间跨度 | 2026-05-12 ~ 2026-06-29 |
| 高频任务(>100次) | 2个 (gpu-heartbeat: 1028, paper-quality-orchestrator: 173) |

### Top 10 高频任务

| 任务名称 | 运行次数 | 最近运行 |
|---------|---------|---------|
| gpu-heartbeat | 1,028 | 2026-06-29 11:48 |
| paper-quality-orchestrator | 173 | 2026-06-08 04:38 |
| literature-monitor | 29 | 2026-06-29 08:04 |
| daily-papers-report | 28 | 2026-06-29 07:01 |
| paper-quality-iteration | 21 | 2026-06-29 09:04 |
| unified-paper-scan | 10 | 2026-06-29 06:02 |
| synthos-daily-promo | 9 | 2026-06-29 12:01 |
| daily-intelligence | 7 | 2026-06-29 07:31 |
| research-proposal-generator | 7 | 2026-06-29 09:15 |
| paper-harvester | 7 | 2026-06-29 08:34 |

## 技能库统计

| 指标 | 数值 |
|------|------|
| 总技能数 | 27个 |
| 空壳(<200B) | 0个 |
| L1原子技能 | 0个 |
| L2复合技能 | 3个 |
| L3高级技能 | 5个 |
| 未定级 | 19个 |

### Top 10 最大技能

1. chinese-literature-access — 17,157B
2. paper-knowledge-base — 14,203B
3. ollama-catalog-monitor — 13,185B
4. llm-model-selection — 11,243B
5. cnipa-patent-management — 10,487B
6. opencode-config — 10,393B
7. author-paper-integrity-audit — 9,497B
8. codex-tmux-control — 9,004B
9. paper-knowledge-extraction — 8,882B
10. skill-consolidation — 7,540B

## 未映射任务(6个)

- `1ce1379174ea` → paper-quality-orchestrator (173次)
- `6f9658a85fd5` → synthos-discussion-watch (5次)
- `0f0240a5b432` → synthos-discussions-check (5次)
- `42b92230282f` → paper-repair (1次)
- `4b66607290e6` → autonomous-core-researcher (1次, BLOCKED)
- `7c3528aee3d4` → cross-project-evolution (1次)

## 层级化建议

### L3 (高级技能)
- author-paper-integrity-audit
- codex-tmux-control
- node-failover-protocol
- research-audit-unified-scan
- retraction-investigation

### L2 (复合技能)
- data-driven-narrative-rebuild
- project-health-tracking
- skillopt-absorption

### L2/L3? (19个待分类)
- chinese-literature-access, cnipa-patent-management, feishu-file-send, feishu-image-send, llm-model-selection, memory-feedback-automation, memory-infrastructure, ollama-catalog-monitor, opencode-config, paper-knowledge-base, paper-knowledge-extraction, pubscholar, pupil-shape-research, self-deception-risk, skill-consolidation, skill-quality-check, tmux-codex-debugging, paper-harvest, hermes-agent
