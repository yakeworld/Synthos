# Cron 论文入库模式

将现有手稿（Markdown/LaTeX）自动转化为 Synthos 管线论文。

## 触发场景
- 发现目录中有未入库的论文草稿
- 从 /home 或其他目录发现新素材
- 需要批量处理已有手稿

## 工作流

### Step 1: 手稿评估
用 delegate_task 检查 N 篇手稿，分析已入库/新论文

### Step 2: Cron 调度
每篇论文一个 cron job，1天/篇间隔：

```
hermes cron create --name "batch-name" \
  --schedule "0 8 * * *" \
  --skill paper-pipeline \
  --prompt "将手稿转化为论文" \
  --repeat N
```

- `--repeat N`: 总处理篇数
- `--schedule "0 8 * * *"`: 每日08:00

### Step 3: 监控
cron 状态: hermes cron list
论文产出: Synthos/outputs/papers/{name}/

### 本会话案例
2026-06-05: bppv/BPPV/ 中 8 篇手稿 → 5 篇新论文。cron 每日 1 篇，5 天完成。

### 注意事项
- 手稿可能重复（同一主题不同版本）→ 评估时合并
- 手稿中英文混杂 → paper-pipeline 自动处理
- cron 执行失败时检查 hermes cron list 的 last_status
