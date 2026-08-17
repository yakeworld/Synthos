# GOLDEN_SET.md — quality

> 对应原则：P1（原子可复现性）/ P2（机械原子暴露输入输出规范）
> golden_set_origin: self_defined
>
> golden 三件套 = 本文件 + `cases/` + `expected/`。所有改进必须通过 golden 测试。

## 设计依据

本技能是父级目录索引（IO_CONTRACT：input `skill_path: str`，output `quality_report: dict`），实际执行路由到子技能 `falsification-validation` / `golden-test-methodology`。金标准目标：验证输入校验（QUAL-001：空/无效 skill_path 必须拒绝执行，不报错崩溃）、有效路径路由到子技能并产出符合 IO_CONTRACT 的 `quality_report: dict`（QUAL-003）、错误路径输出含上下文与恢复建议的明确错误信息（QUAL-005）。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 输入校验 | 有效路径 + 无效路径 | QUAL-001 / QUAL-006 |
| 路由 | 子技能分发 | falsification-validation / golden-test-methodology |
| 输出契约 | quality_report: dict | QUAL-003 / QUAL-007 |
| 错误处理 | 2 种 | 空输入拒绝 + 无效路径错误信息 |

## 测试用例 (cases/)

### case_001: 正常路径 — 有效 skill_path 路由到子技能
- **输入**: `skill_path = "skills/private/extended/research-tools/synthos-akne-bridge/kg-bridge"`（存在的技能目录）
- **期望**: 路由到 `golden-test-methodology` 子技能执行质量检查；输出 `quality_report: dict` 含 `skill`、`checks`（每项 passed/failed + evidence）、`overall_passed` 字段，结构与 IO_CONTRACT 一致

### case_002: 错误路径 — 空 skill_path 输入
- **输入**: `skill_path = ""`
- **期望**: 按 QUAL-001 拒绝执行（不崩溃、不抛裸异常），`status = "rejected"`；错误信息含上下文（输入为空）与恢复建议（提供有效技能路径），不暴露内部状态（QUAL-008）

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_XXX.json`：
- case_001: `status="success"` + `routed_to` 子技能 + `quality_report` 完整结构
- case_002: `status="rejected"` + `error`（上下文 + 恢复建议）

### 通过标准（判定规则）
1. case_001: `quality_report` 含 `skill` / `checks` / `overall_passed` 三字段；`checks` 每项含 `name` + `passed` + `evidence`
2. case_001: `routed_to` ∈ {`falsification-validation`, `golden-test-methodology`}（父级不自行执行，QUAL 路由约束）
3. case_002: `status="rejected"` 且 `error` 含 `context` + `recovery` 字段
4. 两个 case 均无裸异常抛出、无内部状态泄露

## pass_threshold: 1.00

机械原子（atom_type=mechanical），输入校验与路由为确定性行为 → 全部 case 必须通过。

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-06-13 | 初始自设金标准，2 个 case（正常 + 错误） | Synthos Agent |
