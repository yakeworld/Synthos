# evolution_protocol.md — 11步协议（v2.19 完整版）

> 此文件存储完整的11步进化执行协议。主skill包含概要，详细步骤在此。

## 第0步：LOAD_CONSTITUTION

加载CONSTITUTION.md，注入宪法意识：
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

> **[v2.18] Reference-style skill recognition** — 5个原子技能（EXT/ASC/HYP/ARG/VER）使用两-tier架构：精简SKILL.md（~19行，~40字符description）+ rich references/ + golden/。这些不是结构缺陷，而是架构选择。PROBE测试必须识别 references/ 目录存在且文件≥3 为有效引用型技能，score=1.0。

## 第五步：BENCHMARK — 功能测试+Golden验证

轮转策略：
- 奇数轮：knowledge-acquisition + knowledge-extraction + association-discovery
- 偶数轮：hypothesis-generation + argument-expression + viewpoint-verification
- 每轮：task-router

Golden验证：加载 golden/cases/*.json，验证JSON有效且含所有必填字段。

## 第六步：OPTIMIZE — 技能自动优化

```
[1] COLLECT_FAILURES → [1.5] REFLECTIVE_ANALYSIS → [2] ANALYZE_ROOTS → [3] SELECT_STRATEGY
[4] PATCH_SKILL → [5] VERIFY_PATCH → [5.5] ROLLBACK决策
[6] REFLECT → [7] ITERATE（最多2次）
```

回滚协议：VERIFY_PATCH失败→git revert自动回滚。同一技能连续3次回滚→锁定。

## 第七步：EXTERNAL — 主动吸收引擎

每轮执行（不再等7轮）：
```
[1] LOAD_DB → [2] FOLLOW_UP → [3] SCAN_NEW → [4] EVALUATE
[5] EXPAND → [6] SELF_INSPECT → [7] UPDATE_DB
```
关键词8类别轮转：research_agent, architecture, literature, knowledge, reasoning, pipeline, evaluation, self_discovered。

## 第八步：DIAGNOSE — 综合诊断

### 综合评分公式
```
综合分 = 结构平均×0.25 + 基准分×0.25 + OPTIMIZE效果×0.10 + 技能树覆盖率×0.10 + 吸收潜力×0.10 + 宪法对齐×0.20
```

### Pareto 多维优化
当存在多个可改进维度时，计算 Pareto 前沿以选择最优改进路径。

## 第 8.5 步：EDIT_BUDGET — 编辑预算约束

```
EDIT_BUDGET = max(2, 5 - (CURRENT_CYCLE // 5))
```

## 第九步：IMPROVE — 单指标聚焦

### 假说前置协议（v2.16）
每次编辑前必须输出 hypothesis_preamble（target_dimension + current_measurement + hypothesis + expected_measurement + falsification）。

### rejected_buffer 防护（v2.15）
被拒编辑入 buffer，下次 IMPROVE 自动排除重复方案。

### VERIFY 四态决策（v2.16）
| 判决 | 含义 | 动作 |
|:-----|:------|:-----|
| keep:best | 分数提升，创新基线 | KEEP + 记录为 new_best |
| keep:insight | 分数未提升，但有价值 | KEEP（不应用）+ 记录 lessons |
| discard:regression | 分数下降，明确退化 | REVERT + rejected_buffer.WRITE |
| discard:useless | 分数持平，无新信息 | REVERT + 记录 dead_end |

### 硬收敛护栏
- 连续3轮无提升 → 强制切换维度
- 同一target被rejected_buffer排除3次 → 锁定
- 同一指标连续3轮波动<5% → 升级方法设计

## 第十一步：RECORD — 更新状态和日志

| 子步骤 | 动作 |
|:-------|:-----|
| 11a. UPDATE_STATE | 更新 evolution-state.json |
| 11b. WRITE_LOG | 追加 evolution-log.md |
| **11c. CRYSTALLIZE_SKILL** | **自动结晶稳定执行轨迹** |
| 11d. EXTRACT_LESSONS | 提取教训到 lessons.jsonl |
| 11e. SAVE_REPORT | 生成 report_{cycle}.json |
| 11f. UPDATE_DB | 更新 absorption-tracked.json |

### [v2.19] CRYSTALLIZE_SKILL 增强 (autocontext absorption)

**improvement-loop auto-crystallize**: 3次成功模式→自动结晶，失败→回滚。
文言：去芜存菁，留真去伪。

**knowledge-inheritance contract**: evolution-state.json 新增 `inherited_knowledge` 字段，记录跨轮知识传递。
文言：前鉴不丢，后事之师。

**trace-continuity markers**: evolution-log.md 新增 `kept` / `discarded` 标记。
文言：迭代有约，出必有痕。

### [v2.17] 原 CRYSTALLIZE_SKILL

原理：技能最好的来源不是预先编写，而是从执行轨迹中自动结晶。

触发条件：同一任务模式成功执行 ≥3 次 → 输出 pending_review SKILL.md 草稿。

### Git-as-Memory 循环
Phase 0.5: git checkout -b evolution/cycle-{N}
Phase A: COMMIT BEFORE VERIFY
Phase B: VERIFY + DECIDE
Phase C: READ HISTORY → DIAGNOSE前看20条git log

### 主动推理协议
当检测到高不确定性时进入 Active Inference 模式，输出 active_inference_proposal。