# Cron 配置记录 — 2026-05-30

本文件记录 Synthos 记忆系统相关的 cron 作业配置。

## 活跃 Cron

### qc-batch-scan (每6小时)

```yaml
job_id: 7e137e0e36d6
name: qc-batch-scan
schedule: every 360m (每6小时)
script: qc_batch_scan.py
mode: no_agent
deliver: origin (发送到主对话)
```

**行为**: 扫描45+论文的D8/D9/D10a，与上次状态比对，只在有变化时输出。

### memory-consolidation (每天凌晨3:00)

```yaml
job_id: 9926ae23cdbc  
name: memory-consolidation
schedule: 0 3 * * * (每天3:00)
script: memory_consolidate.py
mode: no_agent
deliver: origin (发送到主对话)
```

**行为**: FSRS 间隔重复计算 + memory 空间管理 + fact_store 健康检查。只在首次运行或指标变化时输出。

## 停用的 Cron

### 旧 memory-consolidation (已替换)

```yaml
job_id: 41f32dd5f5ac (已删除)
name: memory-consolidation
schedule: 0 4 * * 0 (每周日凌晨4:00)
mode: agent (加载 memory-enhancement skill)
```

**原因**: 替换为每日3:00的 no_agent 脚本版，更轻量、更频繁。

## 脚本位置

- `~/.hermes/scripts/qc_batch_scan.py`
- `~/.hermes/scripts/memory_consolidate.py`
- 状态文件: `~/.hermes/qc_last_scan.json`
- 状态文件: `~/.hermes/memory_consolidation_state.json`

## 添加新 Cron 的原则

1. 优先 `no_agent=True`（纯脚本，零 Token 开销）
2. 脚本写 stdout → 有变化才输出 → cron 自动转发
3. 状态持久化到 `~/.hermes/*.json` 
4. 名字用中横线（`memory-consolidation` 而非 `memoryConsolidation`）
