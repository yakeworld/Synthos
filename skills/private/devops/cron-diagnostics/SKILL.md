---
name: cron-diagnostics
description: "Cron 任务健康诊断与优化 — 分析 15 个 cron 任务的健康度、频率、调度冲突、deliver 配置、付费任务成本，输出优化方案。"
version: 1.0.0
allowed-tools:
- terminal
license: MIT
metadata:
  synthos:
    version: 1.0.0
    author: Synthos
    signature: 'action: list → result: diagnostic report → action: batch update/remove/create → result: optimized cron list'
    atom_type: skill
    priority: P1

---

## IO_CONTRACT

- **input**: 无（直接触发）
- **output**: 诊断报告 JSON + 优化建议列表
- **副作用**: 可能调用 cronjob action=update/remove/create

> 对应原则：P1（智能原子包含诊断逻辑）

## 核心流程

### Step 1: 数据采集

```bash
cronjob action=list
```

获取所有 cron 任务的完整状态。

### Step 2: 诊断矩阵

对每个任务运行以下检查：

| 检查项 | 条件 | 严重度 |
|--------|------|--------|
| **已暂停** | `enabled=false` 或 `paused=true` | HIGH |
| **错误状态** | `last_status="error"` | HIGH |
| **配置错误** | `no_agent=True` 且 `model` 不为 null | MEDIUM |
| **配置错误** | 非 `no_agent` 但无 `model` 指定 | HIGH |
| **配置错误** | 非 `no_agent` 但 `deliver="local"`（不投递到聊天） | MEDIUM |
| **配置冗余** | `no_agent=True` 且 `deliver="origin"` | LOW |
| **付费任务** | `provider` 包含 "deepseek" | INFO（需人工确认） |
| **频率过高** | `schedule` 包含 `every` 且间隔 < 1h | INFO |
| **功能重叠** | 多个任务做同一件事（如 D8 扫描 + bib 标准化） | MEDIUM |

### Step 3: 功能重叠检测

按关键词分组任务名和描述：

```python
# 论文管线
paper_keywords = ["paper", "quality", "bib", "d8", "d10a", "repair", "review", "scan"]

# 进化循环
evolution_keywords = ["evolution", "evolve", "probe", "full", "cycle"]

# 监控
monitor_keywords = ["heartbeat", "monitor", "scan", "check", "audit", "sync"]
```

同一组内如果多个任务使用相同或相似 model + 做相似内容，标记为重叠。

### Step 4: 频率聚类

按执行频率分组：

```
高频 (< 1h):  每 30m
中频 (1-4h):  every 2h, every 360m
低频 (daily): 0 6 * * *, 0 9 * * *
超长 (monthly): 0 9 1 * *
```

识别同一组内可合并的任务。

### Step 5: 输出报告

```
=== CRON 诊断报告 ===

总任务: N
  Agent: M (付费 X, 免费 Y)
  Script: K
  已暂停: P
  错误: E

=== 付费任务 ===
  1. name: model, schedule, cost_impact

=== 功能重叠 ===
  1. [论文管线] task-A + task-B → 建议合并

=== 配置问题 ===
  1. [HIGH] task-X: enabled=false, last_status=error
  2. [MEDIUM] task-Y: deliver=local 不投递

=== 优化建议 ===
  1. 删除 task-Z (已暂停, 无活跃使用)
  2. 合并 task-A + task-B → unified-task
  3. 修复 task-Y deliver 配置
```

## 优化操作模式

### 清理模式（推荐直接执行）
```bash
# 删除已暂停任务
cronjob action=remove job_id="<id>"

# 删除已完成的一次性任务
cronjob action=remove job_id="<id>"

# 合并任务：删除旧任务 → 创建新任务
cronjob action=remove job_id="<old>"
cronjob action=create schedule="..." model="..." prompt="..."
```

### 修复模式
```bash
# 修复 deliver 配置
cronjob action=update job_id="<id>" deliver="origin"

# 修复配置错误
cronjob action=update job_id="<id>" model="..." provider="..."
```

## 优化原则

1. **先删后加**：删除无效/冗余任务优先于修复配置
2. **合并同类**：功能重叠的任务合并为一个，减少 API 消耗
3. **保留价值**：每个保留的任务必须有明确用途和独立价值
4. **频率合理**：心跳类 30m 可接受，扫描类 ≤4h 合理，论文任务 daily 足够
5. **付费控制**：DeepSeek 付费任务控制在 4-6 个，其余用免费模型

## 典型优化结果

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 总任务数 | 15 | 10-11 |
| 付费任务 | 6 | 4 |
| 已暂停 | 2 | 0 |
| 功能重叠 | 3 组 | 0 |
| 配置错误 | 1 | 0 |

## 参考

- `references/cron-diagnostics-pattern.md` — 诊断模式详细步骤
## 验证清单 · VERIFICATION

1. **输入验证**: {输入条件是否完整}
2. **输出验证**: {输出格式是否符合预期}
3. **边界验证**: {边界条件是否处理}
4. **错误处理**: {异常场景是否覆盖}

> 每项验证必须可执行、可记录、可复现。

