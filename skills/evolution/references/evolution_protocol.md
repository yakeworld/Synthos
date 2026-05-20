# 进化执行协议（11步）

> 此文件存储完整的11步进化执行协议。主skill包含概要，详细步骤在此。

## 第0步：LOAD_CONSTITUTION

`read_file(synthos_constitution_ref)` 加载CONSTITUTION.md，注入宪法意识：
- 不可修改条款（碳硅共生、自进化最高优先、MIT开源、原子边界）
- 哲学免疫系统（承认但不跟随）
- 认识论原则（诚实优于取悦）
- 宪法层级（CON > MEM > CMD > SKL > DEF）

失败处理：文件不可读→记录warning，继续但不跳过。

## 第一步：LOAD_STATE — 三级渐进式加载

| 级别 | 内容 | 时机 |
|------|------|------|
| L1 | evolution-state.json（last_run, evolution_count, 简略评分） | 始终 |
| L2 | evolution-log.md 最近20行 + lessons.jsonl 最近20条 | 条件加载 |
| L3 | absorption-tracked.json（项目库） | 仅EXTERNAL步骤 |

输出：prev_scores, prev_benchmark, current_cycle

## 第二步：LESSONS — 历史教训注入

从 `outputs/evolution/lessons.jsonl` 加载近30天的历史教训，过滤与本次BENCHMARK相关的条目。

## 第三步：DRIFT_CHECK — 三问自检

```
[1] 本会话行为是否从宪法和诚实阅读出发？
[2] 最近决策是否与初始原则一致？
[3] 产出是否与明显为真的事物对应？
```

输出：drift_level (🟢/🟡/🔶/🔴)
失败处理：🟢→继续 🟡→记录 🔶→记录+重置 🔴→记录lessons+通知用户

## 第四步：PROBE — 结构探测

用7原子结构健康检查表（文件名、描述长度、allowed-tools等10项）。评分公式见 QUALITY_CRITERIA.md。

## 第五步：BENCHMARK — 功能测试+Golden验证

轮转策略：
- 奇数轮：knowledge-acquisition + knowledge-extraction + association-discovery
- 偶数轮：hypothesis-generation + argument-expression + viewpoint-verification
- 每轮：task-router

Golden验证：加载 golden/cases/*.json，验证JSON有效且含所有必填字段。

## 第六步：OPTIMIZE — 技能自动优化

触发条件、优化流程、策略选择、回滚协议：

```
[1] COLLECT_FAILURES → [2] ANALYZE_ROOTS → [3] SELECT_STRATEGY
[4] PATCH_SKILL → [5] VERIFY_PATCH → [5.5] ROLLBACK决策
[6] REFLECT → [7] ITERATE（最多2次）
```

可用策略：确定性补丁、反思调整、进化变异。策略选择优先历史成功率最高的。
回滚协议：VERIFY_PATCH失败→git revert自动回滚。同一技能连续3次回滚→锁定。

## 第七步：EXTERNAL — 主动吸收引擎

每轮执行（不再等7轮）：
```
[1] LOAD_DB → [2] FOLLOW_UP → [3] SCAN_NEW → [4] EVALUATE
[5] EXPAND → [6] SELF_INSPECT → [7] UPDATE_DB
```
关键词8类别轮转：research_agent, architecture, literature, knowledge, reasoning, pipeline, evaluation, self_discovered。

## 第八步：DIAGNOSE — 综合诊断

### 假设先行
在改进前写可验证假说：target_dimension + current_score + predicted_score + mechanism + verification + rationale。

### 宪法对齐检查
| 检查项 | 通过条件 | 失败处理 |
|--------|---------|---------|
| 不违反不可修改条款 | 无违反 | 🔴拒绝+lessons |
| 哲学免疫系统未被绕过 | 无违反证据 | 🟡回正+记录 |
| 认识论原则被遵守 | 断言有来源 | 🟡记录 |
| 漂移未达中重度 | ≤🟢 | 🟢正常 |

### 结构分对比
- current < 0.5 → CRITICAL
- current < prev - 0.1 → DEGRADED

### 基准分对比
- benchmark < 0.5 → FUNCTIONAL_DEGRADED
- 同一测试连续3轮不通过 → PERSISTENT_FAILURE

### 综合评分公式
```
综合分 = 结构平均×0.25 + 基准分×0.25 + OPTIMIZE效果×0.10 + 技能树覆盖率×0.10 + 吸收潜力×0.10 + 宪法对齐×0.20
```

等级：EXCELLENT ≥0.85 | GOOD 0.70-0.84 | FAIR 0.50-0.69 | POOR <0.50

### 主动推理门
当检测到高不确定性时，生成"最小化不确定性"的实验建议。不阻塞当前循环。

## 第九步：IMPROVE — 单指标聚焦

每轮只修分数最低的一个维度。不并行不全面调整。
修复顺序：机制缺口→技能执行→评估参数→外部扫描。

## 第十步：VERIFY — 验证

对已patch的原子：确认可加载、重算结构分、重跑失败案例。

## 第十一步：RECORD — 更新状态和日志

- 更新 evolution-state.json
- 追加 evolution-log.md（含7种事件类型+provenance标记）
- 提取教训到 lessons.jsonl
- 生成报告 outputs/evolution/report_{cycle}.json
- 更新 absorption-tracked.json

## Git-as-Memory 循环（v2.11）

```
Phase 0.5: git checkout -b evolution/cycle-{N}
Phase A: COMMIT BEFORE VERIFY（每次BENCHMARK前）
Phase B: VERIFY + DECIDE（PASS→KEEP / FAIL→REVERT）
Phase C: READ HISTORY → DIAGNOSE前看20条git log
```

## 主动推理协议

当检测到以下条件时进入 Active Inference 模式：
- 原子置信度跨度≥0.3
- 结构分≥0.9但方差>0.2
- 外部评分≥4.0且未吸收
- 连续3+次调用返回不确定性结果

输出：active_inference_proposal 到 outputs/evolution/active_inference_{cycle}.json
