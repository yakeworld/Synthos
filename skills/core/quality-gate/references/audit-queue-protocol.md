# AUDIT_QUEUE.md 审计队列协议

## 概述

AUDIT_QUEUE.md 是论文质量审计队列的权威记录文件，位于 `/media/yakeworld/sda2/Synthos/outputs/papers/AUDIT_QUEUE.md`。cron 作业每日三次执行（09:00/14:00/20:00）处理队列中的论文。

## 优先级

优先级：P0(公开数据预测) > P1(BPPV仿真) > P2a(眼球算法) > P2b(眼球有数据) > P2c(眼球其他)

## 审计流程

### 步骤1：读取队列
```bash
head -5 /media/yakeworld/sda2/Synthos/outputs/papers/AUDIT_QUEUE.md
```

### 步骤2：定位待审计论文
- 按优先级取队列中第一篇 `QS≠0` 且状态为"待审计"的论文
- 跳过已 VERIFIED/BLOCKED 的论文

### 步骤3：检查 07-quality/ 目录
必须存在的4份标准报告：
- `report-1-universal-six-domains.md` — 通用六域报告
- `report-2-*specialty*.md` — 类型专项报告
- `report-3-references-audit.md` — 引用审查报告
- `report-4-inspector-report.md` — 检查员报告

**关键规则**：缺失任何一份 → 无论 state.json 显示什么，都视为未验证。

### 步骤4：质量门验证
- 检查 `quality_score ≥ 0.85`（通过阈值）
- 检查 `gate_status` 为 PASS/VERIFIED
- 检查 `quality_gates` 中所有 G1-G7 为 PASS
- 检查 D8/D10a 完整性

### 步骤5：状态判定与更新

| 条件 | 队列状态 | 后续操作 |
|------|---------|---------|
| 4份报告全部存在且完整 + qs≥0.85 + G1-G7全PASS | 从队列移除 → VERIFIED | 完成 |
| P0_WAITING_USER 或 BLOCKED 标记 | BLOCKED | 等待人工处理 |
| 07-quality/ 报告缺失/不完整 | IN_PROGRESS 或 NEEDS_REPAIR | 重新生成报告或标记修复 |
| quality_score < 0.85 | NEEDS_REPAIR | 需要完整修复后重新审计 |
| D8=0 或 D10a=0% | NEEDS_REPAIR | 需要补充引用体系 |

### 步骤6：更新文件
1. 更新 `state.json`：`gate_status` 和 `notes`
2. 更新 `AUDIT_QUEUE.md`：修改论文行状态
3. 如通过：从队列移除该论文

## state.json CLAIMED vs 07-quality/ VERIFIED

**核心原则**：state.json 是"声称状态"，07-quality/ 目录是"验证状态"。审计员不能仅凭 state.json 就认为论文已通过——必须独立验证 07-quality/ 中4份报告的存在和完整性。

**bppv-pinn-canalolithiasis 案例**：
- state.json: gate_status=PASS, quality_score=88, D8=15/15, D10a=100%, G1-G7全部PASS
- 07-quality/：仅含 quality-report.md（旧扫描工具输出），缺失 report-1~4
- 正确判定：未验证 → 从 paper.tex 重新生成4份报告 → VERIFIED

## 注意

07-quality/ 中的 `status.json` 和 `quality-report.md` 可能来自旧的扫描工具（如 PARTIAL-PAPERS D8/D10a/DOI Batch Scan），不是标准四报告格式。审计时必须检查标准报告文件是否存在，不能仅依赖 status.json 中的分数。
