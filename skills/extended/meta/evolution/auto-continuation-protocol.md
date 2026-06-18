# Auto-Continuation Protocol

> 来源: evolution SKILL.md v2.20
> 用户指令: "自动持续迭代，判断用户回答，超过阈值自动执行"

## 自动持续条件

当以下**全部**条件满足时，自动进入下一进化周期：

| 条件 | 阈值 | 说明 |
|:-----|:----:|:-----|
| `overall_score` | ≥ 0.85 | 综合评分达到 EXCELLENT 等级 |
| `status` | "healthy" | 系统状态健康 |
| `rejected_buffer_hits` | = 0 | 无被驳回的编辑 |
| `consecutive_healthy` | < 20 | 连续健康轮数未达到上限 |
| `drift_level` | "green" 或 "yellow" | 无中度或重度漂移 |

## 触发流程

```
检查条件 → 全部满足?
  ├── 是 → 进入下一周期 (DIAGNOSE → OPTIMIZE → ...)
  └── 否 → 停止，记录原因到 evolution-log.md，人工审查
```

## 自动迭代记录

每次自动迭代必须:
1. 在 `evolution-state.json` 中更新 cycle 编号和状态
2. 在 `evolution-log.md` 中追加 cycle 记录
3. 在 `lessons.jsonl` 中追加 lesson，type="Maintenance"

## 停止条件

当以下任一条件触发时，**不**自动继续:
- score < 0.85
- status != "healthy"
- rejected_buffer_hits > 0
- consecutive_healthy ≥ 20
- drift_level = "orange" 或 "red"
- BENCHMARK FAIL (任何原子分数 < 0.95)

## 手动干预

用户可随时通过消息中断自动迭代。
用户在下次消息中明确要求"继续"时，系统恢复自动迭代。