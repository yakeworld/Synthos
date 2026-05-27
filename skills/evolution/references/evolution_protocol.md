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

## 第五步：BENCHMARK — 功能测试+Golden验证（v2.12 新增自动数据集）

轮转策略：
- 奇数轮：knowledge-acquisition + knowledge-extraction + association-discovery
- 偶数轮：hypothesis-generation + argument-expression + viewpoint-verification
- 每轮：task-router

### [v2.12] 自动评估数据集构建

当原子缺乏 golden 测试用例时，自动从 SKILL.md 内容生成合成测试集。

#### 触发条件
- 原子未设 golden 用例或 golden 覆盖率 < 50%
- 新创建的原子首次基准测试
- 旧原子连续 3 轮 BENCHMARK 通过后，自动补充新生成的测试用例

#### 自动构建流程

```yaml
auto_dataset_builder:
  1. EXTRACT_SKILL_KNOWLEDGE:
     - 从 SKILL.md 中提取：
       a. 输入契约（input fields, types, constraints）
       b. 输出契约（output fields, types, examples）
       c. 边界条件（from BOUNDARY.md）
       d. 已知陷阱（from SKILL.md陷阱节）
       e. 验证清单（from SKILL.md验证清单节）
  
  2. GENERATE_TEST_CASES:
     - 对每个可测试维度生成 2-3 个用例：
       a. 正常路径（happy path）：标准输入→预期输出
       b. 边界路径（edge case）：边界输入→预期错误/降级行为
       c. 失败路径（failure path）：无效输入→预期错误
     - 用例必须：
       - 从真实数据生成（不虚构DOI/URL/分数）
       - 附 expected 输出字段和验证条件
       - 标注入参来源（哪些 API 会被调用）
  
  3. VALIDATE_DATASET:
     - 验证每个用例的 JSON 格式正确
     - 验证输入/输出与 SKILL.md 的 I/O 契约一致
     - 输出到 golden/cases/ 目录
     - 更新 GOLDEN_SET.md（补充测试用例说明）

  4. FALLBACK:
     - 如果自动生成失败（不足 3 个用例），标记为 \"auto_dataset_failed\" 并记录 lesson
     - 不阻塞 BENCHMARK 继续执行
```

Golden验证：加载 golden/cases/*.json，验证JSON有效且含所有必填字段。如存在自动数据集，额外验证其与 I/O 契约的一致性。

## 第六步：OPTIMIZE — 技能自动优化（v2.12 新增反射式分析）

触发条件、优化流程、策略选择、回滚协议：

```[1] COLLECT_FAILURES → [1.5] REFLECTIVE_ANALYSIS → [2] ANALYZE_ROOTS → [3] SELECT_STRATEGY
[4] PATCH_SKILL → [5] VERIFY_PATCH → [5.5] ROLLBACK决策
[6] REFLECT → [7] ITERATE（最多2次）
```

### [v2.12] 第 1.5 步：REFLECTIVE_ANALYSIS（吸收自 GEPA 反射式演化）

在收集失败案例后、分析根因之前，先执行反射式分析。

**原理**：不只看"任务失败"这个结果，而是读取完整的执行轨迹，理解**为什么**失败。失败原因往往隐藏在轨迹的细节中——选择错误的工具、忽略关键信息、生成不完整输出等。

#### 反射式分析流程

```yaml
reflective_analysis:
  1. LOAD_TRACES:
     - 读取本轮 evolution 执行的完整轨迹（terminal 输出、tool 调用序列、中间结果）
     - 从 evolution-log.md 提取最近的教训
     - 从 lessons.jsonl 提取近 3 轮的失败模式
  
  2. IDENTIFY_FAILURE_MECHANISMS:
     - 对每个失败（BENCHMARK failure / VERIFY failure / user correction）：
       a. 记录失败症状（symptom）
       b. 逆向追踪执行路径（traceback）
       c. 定位根因位置（root_location）：skill 描述模糊 / 步骤缺失 / 工具使用不当 / 边界未覆盖
       d. 分类失败类型（failure_type）：逻辑错误 / 遗漏步骤 / 幻觉 / 边界溢出 / 工具选择错误
  
  3. GENERATE_TARGETED_FIXES:
     - 对每个根因位置，生成针对性修复建议
     - 修复策略优先级（从高到低）：
       1. 步骤补充（缺失的流程步骤）
       2. 边界强化（未覆盖的边缘情况）
       3. 描述精确化（模糊的指令）
       4. 工具替换（不合适的工具选择）
     - 每个修复建议附带：预期效果 + 副作用评估

  4. OUTPUT:
     reflective_analysis_report:
       - failures_analyzed: N
       - root_causes: list[RootCause]
       - targeted_fixes: list[TargetedFix]
       - recommended_strategy: "deterministic|reflective|evolutionary"
```

#### 与下游步骤的衔接

```
REFLECTIVE_ANALYSIS 输出（推荐策略）→ ANALYZE_ROOTS 深化分析 → SELECT_STRATEGY
                                                                ↓
                                                   确定性补丁（当根因明确）
                                                   反思调整（当根因模糊但有方向）
                                                   进化变异（当根因未知/随机探索）
```

可用策略：确定性补丁、反思调整、进化变异。策略选择优先历史成功率最高的，但 REFLECTIVE_ANALYSIS 的推荐策略拥有 1.5 倍权重。\n\n回滚协议：VERIFY_PATCH失败→git revert自动回滚。同一技能连续3次回滚→锁定。

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

### 综合评分公式（v2.12 新增 Pareto 多维优化）
```
综合分 = 结构平均×0.25 + 基准分×0.25 + OPTIMIZE效果×0.10 + 技能树覆盖率×0.10 + 吸收潜力×0.10 + 宪法对齐×0.20
```

### [v2.12] Pareto 多维优化

在综合评分基础上，引入 Pareto 前沿分析，替代纯粹的单指标聚焦。当存在多个可改进维度时，计算 Pareto 前沿以选择最优改进路径。

#### 原理

不是所有改进方向都有同样的价值。当一个改进方向在**至少一个维度上提升、且不在任何维度上损害**时，它就是 Pareto-optimal。改进应优先选择 Pareto-optimal 方向。

#### Pareto 分析流程

```yaml
pareto_analysis:
  1. IDENTIFY_IMPROVABLE_DIMENSIONS:
     - 列出所有分数 < 1.0 的维度
     - 对每个维度：估计改进所需的 effort (low/medium/high) 和 预期收益 (0-1)

  2. CONSTRUCT_PARETO_FRONT:
     - 坐标系：X=effort (反比), Y=expected_gain
     - 标记所有候选改进的 (effort_score, gain) 坐标
     - 计算 Pareto-optimal 前沿（非支配解集）
     - 落在前沿之外的点标记为 dominated

  3. SELECT_OPTIMAL:
     - 从 Pareto 前沿中选择：
       a. 最高 gain/effort 比率的改进
       b. 如果多个不分伯仲 → 选与上次 IMPROVE 维度不同者（避免局部最优）
       c. 如果 Pareto 前沿为空 → 回退到单指标聚焦（原逻辑）

  4. OUTPUT:
     pareto_report:
       - candidates_evaluated: N
       - pareto_optimal: list[Dimension]
       - dominated_excluded: list[Dimension]
       - selected: Dimension
       - rationale: str
```

#### 与 IMPROVE 的衔接

```
Pareto 分析输出 → 如果选择了 Pareto-optimal 维度：
                      IMPROVE 聚焦该维度
                   如果无 Pareto-optimal 维度：
                      回退到单指标聚焦（原逻辑：最低分维度）
```

等级：EXCELLENT ≥0.85 | GOOD 0.70-0.84 | FAIR 0.50-0.69 | POOR <0.50

### 主动推理门
当检测到高不确定性时，生成"最小化不确定性"的实验建议。不阻塞当前循环。

## 第 8.5 步（新增 v2.15）：EDIT_BUDGET — 编辑预算约束

> 吸收自 SkillOpt (Yang et al. 2026) — 限制每轮编辑量防止过度修改。

### 原理

SkillOpt 的核心发现：**过度修改是进化失败的主因**。初始周期允许大范围探索，但随系统成熟，修改量应衰减。每轮设置编辑预算（edit budget），超出即截断，保留精力到下轮。

### 编辑预算公式

```
CURRENT_CYCLE = evolution-state.json 的 evolution_count
BASE_BUDGET  = 5                      # 初始 max edits/cycle
DECAY_FACTOR = 1                      # 每轮减少 1
MIN_BUDGET   = 2                      # 地板值
EDIT_BUDGET  = max(MIN_BUDGET, BASE_BUDGET - (CURRENT_CYCLE // 5))
```

| Cycle 区间 | 预算 | 含义 |
|:-----------|:----:|:-----|
| cycle 1-5 | 5 edits | 新系统允许大范围探索 |
| cycle 6-10 | 4 edits | 开始收敛 |
| cycle 11-15 | 3 edits | 精细化调整 |
| cycle 16+ | 2 edits | 成熟期，只做最必要修改 |

### 执行协议

```yaml
edit_budget:
  1. CALCULATE:
     - 读取 evolution_count 计算当前预算
     - 输出: budget_available = N

  2. APPLY_IN_IMPROVE:
     - IMPROVE 每次编辑前检查 budget_available
     - 每次编辑（patch/write_file/skill_manage）消耗 1 单位
     - budget_available <= 0 → 停止本轮编辑
     - 记录: "EDIT_BUDGET exhausted after N edits"

  3. TRACK:
     - 在 evolution-state.json 新增字段:
       edit_budget:
         allocated: N
         consumed: M
         remaining: N-M
     - 日志追加: "[v2.15] EDIT_BUDGET: {consumed}/{allocated}"

  4. RATIONALE:
     - 过剩预算自动滚入下轮（BUT 不累计，防止堆叠）
     - 如连续 3 轮预算耗尽仍无改进 → 触发 Nudge 熔断
```

### 与 DIAGNOSE → IMPROVE 的衔接

```diff
 DIAGNOSE → [8.5 EDIT_BUDGET → 计算预算] → IMPROVE（每次编辑消耗预算）
                                                ↓
                                         预算耗尽？→ 停止编辑，继续 VERIFY
                                         有余额？→ 继续编辑
```

## 第九步：IMPROVE — 单指标聚焦（v2.15 新增 rejected_buffer 防护，v2.16 新增假说前置）

### [v2.16] 假说前置协议（Hypothesis Preamble）

> 吸收自 ResearcherSkill — 每次编辑前先写假说，使方向可证伪、失败可学习。

每次 IMPROVE 编辑（patch/write_file/skill_manage）前，必须输出：

```yaml
hypothesis_preamble:
  target_dimension: <聚焦维度>
  current_measurement: <当前值 or "无">
  hypothesis: "如果修改 [X], 预期 [Y 提升 Z%], 因为 [机制推理]"
  expected_measurement: <预期验证值>
  falsification: "如果 [Z 不提升或下降], 则假说被证伪, 应回归"
```

假说被证伪 ≠ 编辑被退回。被证伪的假说同样有价值——记录到 lessons 作为"已试过的方向"。

每轮只修分数最低的一个维度。不并行不全面调整。
修复顺序：机制缺口→技能执行→评估参数→外部扫描。

### [v2.15] rejected_buffer 防护

> 吸收自 SkillOpt (Yang et al. 2026) — 被拒编辑入 buffer，防止重复错误。

#### 原理

SkillOpt 的核心发现：**被拒绝的程序是最有价值的学习信号**。当 VERIFY 判定某次编辑失败（分数下降或未提升），将该编辑的（目标、内容、失败原因）存入 rejected_buffer。下次 IMPROVE 选择编辑时，自动排除与 buffer 中匹配的方案。

#### rejected_buffer 数据结构

存储位置：`outputs/evolution/rejected_buffer.json`

```json
{
  "buffer": [
    {
      "cycle": 42,
      "target": "knowledge-acquisition",
      "change_summary": "Added S2 API retry logic with 3s timeout",
      "hypothesis": "S2 API 429 failures will drop by 50%",
      "failure_reason": "score_dropped_from_0.85_to_0.72",
      "verification_detail": "BENCHMARK failed on ACQ-01 (timeout)",
      "timestamp": "2026-05-26T12:00:00Z"
    }
  ],
  "max_size": 50,
  "auto_cleanup": "evict oldest when > max_size"
}
```

#### 执行协议

```yaml
rejected_buffer:
  WRITE（在 VERIFY 失败后）:
    - 当 VERIFY 判定 FAIL（分数下降或未提升）:
      - 记录 (cycle, target, change_summary, hypothesis, failure_reason, timestamp)
      - 追加到 rejected_buffer.json
      - 标记 reason 类型: score_drop / no_improvement / benchmark_fail / structural_degradation

  READ（在 IMPROVE 选择编辑前）:
    - 加载 rejected_buffer.json
    - 检查 IMPROVE target 是否与 buffer 中最近 3 条匹配：
      - 匹配规则：target 相同 + change_summary 语义相似（由 agent 判断）
      - 命中时：自动排除该方案，选择次优方向
      - 连续 3 次排除同一 target → 记录教训 "target X exhausted all viable approaches"

  CLEANUP:
    - 每轮在 RECORD 阶段触发：
      - 删除 cycle < (current - 20) 的旧条目（只留近 20 轮）
      - 保留失败次数 > 3 的 target 聚合统计（不删）
```

#### 与 VERIFY 的衔接

```diff
 VERIFY 判定:
   PASS → KEEP, 清除该 target 的 buffer 匹配
   FAIL → REVERT (git) + rejected_buffer.WRITE(cycle, target, change, reason)
         ↓
  下次 IMPROVE: rejected_buffer.READ → 自动排除重复方案
```

### [v2.16] VERIFY 四态决策 + 硬收敛护栏

> 吸收自 ResearcherSkill — 失败也有信息价值，连续不提升则强制转向。

#### VERIFY 四态决策

| 判决 | 含义 | 动作 |
|:-----|:------|:-----|
| **keep:best** | 分数提升，创新基线 | KEEP + 记录为 new_best |
| **keep:insight** | 分数未提升，但发现了有价值的方向/反模式 | KEEP（不应用）+ 记录到 lessons 作为 insight |
| **discard:regression** | 分数下降，明确退化 | REVERT (git) + rejected_buffer.WRITE |
| **discard:useless** | 分数持平，无新信息 | REVERT + 记录为 dead_end |

#### 硬收敛护栏（v2.16）

当以下任一条件触发时，**强制**跳转聚焦维度（不等待 Nudge 软提示）：

```yaml
hard_convergence_gates:
  consecutive_no_improvement:
    threshold: 3           # 连续3轮同一维度无提升
    action: FORCE_PIVOT    # 强制切换到次低分维度
    rationale: "三度不济，易弦更张"
  
  same_target_exhausted:
    threshold: 3           # 同一target被rejected_buffer排除3次
    action: LOCK_TARGET    # 锁定该target到"已穷尽"状态，本轮不再尝试
    rationale: "路尽则返，不改空耗"
  
  plateau_detected:
    condition: "同一指标连续3轮波动 < 5%"
    action: ESCALATE       # 升级问题：从局部优化转为方法重新设计
    rationale: "无尺则立规，以文度文"
```

触发 HARD_GATE 后，在 evolution-state.json 记录 gate_event，并追加 lessons。

## 第十一步：RECORD — 更新状态和日志（v2.17 吸收 GenericAgent：事后技能结晶）

| 子步骤 | 动作 |
|:-------|:-----|
| 11a. UPDATE_STATE | 更新 evolution-state.json |
| 11b. WRITE_LOG | 追加 evolution-log.md（含7种事件类型+provenance标记） |
| **11c. CRYSTALLIZE_SKILL** | **新增** — 自动结晶稳定执行轨迹为 skill |
| 11d. EXTRACT_LESSONS | 提取教训到 lessons.jsonl |
| 11e. SAVE_REPORT | 生成报告 outputs/evolution/report_{cycle}.json |
| 11f. UPDATE_DB | 更新 absorption-tracked.json |

### [v2.17] 11c. CRYSTALLIZE_SKILL — 事后技能结晶

> 吸收自 GenericAgent (lsdefine, ⭐12,156, MIT) — 事成即录，录即成技

#### 原理

GenericAgent 的核心发现：**技能最好的来源不是预先编写，而是从执行轨迹中自动结晶**。每次成功完成一项任务，执行路径中包含了完整的知识——用了什么工具、经历了什么步骤、解决了什么坑。将这些信息固化为 skill，下次遇到同类任务直接调用。

Synthos 已有 `project-experience-distillation`（SubagentStop 触发），但它是事件驱动且需要手动确认。本步骤将其扩展为**持续内联结晶**。

#### 触发条件

```yaml
crystallize_skill:
  trigger: "同一任务模式成功执行 ≥3 次（由 agent 判断任务类型相似性）"
  filter: |
    排除以下情况：
      - 纯临时一次性任务（如"读这个文件"）
      - 已有明确 skill 覆盖的模式
      - 执行轨迹不足 3 步的简单操作
  action: |
    1. 从执行轨迹提取：任务目标、关键步骤、使用工具、遇到的坑和解决方法
    2. 判断是否有复用价值（同一用户/项目是否会再次遇到）
    3. 生成 SKILL.md 草稿（含原理层·文言 + 方法层·白话 + 触发条件 + 验证清单）
    4. 标记为 pending_review（不自动创建，避免噪声）
    5. 在 evolution-log 记录 "crystallized skill candidate: [name]"

  自动注入点（无需标记 pending_review）：
    - discovery pattern（发现某个 API 的稳定用法）
    - debugging script（解决某个特定错误类型的步骤）
    - workflow optimization（耗时操作的优化方案）
```

**文言**：事成即录，录即成技。一次做，二次熟，三次固之。

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
