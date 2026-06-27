# 质量闸门 Cron 报告输出协议

**适用场景**: 作为 scheduled cron job 运行时，需要向用户交付质量迭代报告。

## 输出模式

### 模式1: [SILENT] — 全PASS
当满足以下全部条件时输出 `[SILENT]`（不做任何投递）：
1. 所有活跃 Codex 任务已完成（或无活跃任务）
2. 所有论文 gate_status = PASS
3. 最近 comprehensive quality report 无 P0/P1 问题
4. 无 state.json 内部不一致

### 模式2: 生成报告 — 有阻塞问题
当存在以下任一情况时生成报告并派发 Codex：
- 有论文 gate_status ≠ PASS
- 有论文 gates_result.hard_fails > 0（虚假通过）
- 有论文结构不完整（缺失 02-data/、04-results/ 等）
- 有活跃 Codex 任务等待结果

## 报告格式

```
# Quality Gate — Pipeline Health Report [时间戳]

## Pipeline 全景
| 指标 | 值 |
|:-----|:---|
| 论文总数 | 103 |
| gate_status=PASS | 93 |
| publication step | 74 |

## 关键发现
1. [发现1: 数字支撑]
2. [发现2: 数字支撑]

## 本轮动作
派发 Codex 任务: [论文名] 质量检查与修复 (codex-[会话名] 运行中)

## QC 清单
| 论文 | 状态 | 备注 |
|:-----|:-----|:------|
| PIMA | PASS (85/100) | 已完成 |
| off-axis-iris | HARD_FAIL (20/100) | Codex 修复中 |
```

## 报告交付位置
- 保存到 `~/.hermes/scripts/quality-iteration-report-<timestamp>.md`
- 同时作为 cron 的最终响应输出（系统自动投递给用户）

## 决策流程
```
扫描所有论文 → 按 gates_result.quality_score 从低到高排序
    → 有 codex 任务运行中？等待并检查产出
    → 最低分论文有 codex 任务在跑？跳过
    → 最低分论文无 codex 任务？派发新任务
    → 全部 PASS → [SILENT]
```
