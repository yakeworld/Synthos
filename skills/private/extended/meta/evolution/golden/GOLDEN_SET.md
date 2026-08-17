# Golden 集合 · evolution

> 本技能是自进化引擎（P0 meta-evolution）。核心 IO（源自 SKILL.md / IO_CONTRACT.md）:
> - **输入**: `current_state`（evolution-state.json 内容）、`cycle_data`
>   （cycle 编号、PROBE/BENCHMARK 实测计数、git 状态）
> - **输出**: `evolution_report`（四态决策、六维评分、recommendations、next_actions）
>   + 更新 `evolution-state.json` / 追加 `evolution-log.md`

## 本 Golden 集合测试的两个核心不变量

1. **六维评分必须重算（数必重算，不可袭旧）**:
   `overall = structural×0.25 + benchmark×0.25 + optimize×0.10 + coverage×0.10 + absorption×0.10 + constitutional×0.20`
   VERIFY 步骤必须独立重算，不复用 state.json 声称值；声称值与重算值差异 > 5%
   → 记录 self_deception_risk，采用实测值。
2. **硬收敛护栏**: EDIT_BUDGET（单次 ≤3 个文件）、连续 3 轮无进展 → 降级 EXPLORE、
   相同目标连续 2 次 → 切换维度、burnout 保护（consecutive_healthy ≥ 20 停止）。

## 测试用例表

| case_id | 类型 | 描述 | 权重 |
|---------|------|------|------|
| case_001 | 正常 | 健康状态 + 明确改进方向（DIAGNOSE 发现验证清单缺口）→ 决策 OPTIMIZE，overall 六维精确重算并展示子分数贡献 | 0.4 |
| case_002 | 错误 | state 声称分数与实测重算差异 > 5%（自欺检测）→ 采用实测值，记录 self_deception_risk，拒绝以声称值推进 | 0.3 |
| case_003 | 错误 | 连续 3 轮无进展（rejected_buffer 有同方向建议）→ 硬收敛护栏触发，降级 EXPLORE | 0.3 |

## 通过标准

1. **结构**: `cases/` 与 `expected/` 中每个 `case_XXX.json` 可被 `json.load` 解析；
   case 与 expected 的 `case_id` 一一对应。
2. **case_001（正常）**:
   - `decision == "OPTIMIZE"`；
   - `overall_score` 与六维按公式精确重算值一致（容差 0.0001）；
   - 输出含 `benchmark_components`：version_pct×0.33 + signature_pct×0.33 +
     io_contract_pct×0.34 各项子分数（Cycle 175 公式验证规则）；
   - `next_actions` 指向单一最低 ROI 维度（一维一修），编辑预算 ≤ 3 文件。
3. **case_002（错误-自欺）**:
   - `self_deception_detected == true`，`claimed_score` 与 `measured_score` 均输出，
     差异 > 5%；
   - 状态采用 `measured_score`（实测值优先），`self_deception_risk` 已记录；
   - 不基于声称值执行任何 IMPROVE 动作。
4. **case_003（错误-收敛）**:
   - `hard_convergence_triggered == true`，`action == "degrade_to_explore"`；
   - 被驳回方向进入 `rejected_buffer`，`next_actions` 不含同方向建议（同方向不再提）；
   - 无新编辑动作（降级轮不编辑）。
5. **可复现性 (P1)**: 同一 `current_state` + `cycle_data` 二次运行，
   决策与 overall 分数一致。
6. **诚实性 (P0)**: 期望分数必须由输入子分数按公式可手算复现；
   公式本身不可被进化引擎修改（只有宪法可改评分标准）。

## 用例文件

- `cases/case_001.json` — 正常：OPTIMIZE + 六维精确重算
- `cases/case_002.json` — 错误：声称 vs 实测偏差 → self_deception_risk
- `cases/case_003.json` — 错误：硬收敛 → 降级 EXPLORE
- `expected/case_001.json` … `expected/case_003.json` — 对应期望与验证方法

> 文言: 镜照万物，必先自照。以病镜看病，所见皆妄。数必重算，不可袭旧。
