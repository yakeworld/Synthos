# GOLDEN_SET.md — cron-diagnostics

> 对应原则：P1（智能原子包含诊断逻辑：cronjob action=list 全量状态 → 诊断报告 JSON + 优化建议）
> golden_set_origin: self_defined

## 设计依据

本技能输入为 cronjob action=list 采集的任务清单（或直接触发），输出为诊断报告 JSON +
优化建议列表。金标准为自设（self_defined），验证目标：**给定相同的任务清单，技能能否
按诊断矩阵正确判定每个任务的健康度、识别功能重叠、交叉验证计数（总任务/付费/暂停/错误
与清单一致），并为每条建议给出可执行 action（update/remove/create）；批量 timeout 场景
必须优先判 HIGH 并先检查 codex profile 完整性（CRON-003）**。

判定规则：
- 报告计数必须与 case 输入清单交叉一致（P0 凡数必源）
- 每条 optimization 必须含 action ∈ {update, remove, create}
- 批量 no_agent timeout + profiles 缺失 → 必须标记 HIGH 且修复顺序为先 profile 后批量操作

## 测试用例表

| case | 名称 | 类型 | 输入摘要 | 期望要点 | 关联 Genes |
|------|------|------|----------|----------|-----------|
| case_001 | 15 任务标准诊断 | 正常 | 15 任务（付费 6、暂停 2、错误 1、重叠 3 组） | 报告计数交叉一致；5 条建议均含可执行 action；优化后 10 任务、付费 4 | CRON-001/002/004 |
| case_002 | no_agent 配置错误 + deliver 丢失 | 错误 | no_agent 任务带 model / 非 no_agent deliver=local | 判 MEDIUM 配置错误；建议 update 修复配置与投递 | CRON-005 |
| case_003 | 批量 no_agent 超时 + profile 缺失 | 错误 | 多个 no_agent 任务同时 timeout，~/.codex/profiles/ 不全 | 判 HIGH；先核对 codex profile 完整性，再执行批量操作 | CRON-003 |

## 通过标准

- **pass_threshold: 0.80**（3 个 case 至少 2 个通过）
- case_001：计数交叉一致 + 每条建议有可执行 action + 付费任务数落入 4-6 区间
- case_002：MEDIUM 配置错误判定命中 + 建议 action=update
- case_003：HIGH 判定命中 + 修复顺序先 profile 后批量（顺序断言）
- 权重区分：case_001 为 critical（主路径），case_002/003 为 high（错误路径）

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-27 | 初始自设金标准，3 个 case（1 正常 + 2 错误） | Synthos Agent |
