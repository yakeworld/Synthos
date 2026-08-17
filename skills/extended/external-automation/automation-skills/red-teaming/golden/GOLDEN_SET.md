# GOLDEN_SET.md — red-teaming

> 对应原则：P1（认知原子语义可复现：同一输入 + 同一路由逻辑 → 等价路由结论）
> golden_set_origin: self_defined

## 设计依据

本技能为 **external-automation 父级路由技能**（parent-skill），本身不执行红队测试，仅作为目录索引：
校验 `request` / `context` 输入，将请求路由到唯一子技能 `godmode`（LLM 越狱攻击：Parseltongue、GODMODE、ULTRAPLINIAN）执行。

金标准的目标是验证：**给定相同的路由请求，父级能否正确分发到 `godmode`，且在未知/错误输入时返回带上下文的错误信息（而非裸异常）**。父级仅做路由决策，不依赖通用方案、不越界执行子技能逻辑。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 子技能路由 | 1/1 | godmode |
| 错误路径 | 2/2 | 未知子技能拒绝、参数缺失拒绝 |
| 参数契约 | P2 | request: str, context: dict |
| 输出契约 | P2 | result: dict |

## 测试用例 (cases/)

### case_001: 正常路由 — GODMODE 越狱攻击模拟
- **输入**: `request="run godmode jailbreak simulation", context={"attack": "GODMODE", "target": "llm-guardrail"}`
- **期望**: 路由到 `godmode` 子技能；父级仅作为目录索引；针对特定越狱攻击（RED-002）由子技能执行特定防御/模拟策略；输出 `result` 为 dict

### case_002: 错误路径 — 未知子技能
- **输入**: `request="run ultrain-attack", context={"attack": "ULTRAPLINIAN", "target": "unknown-skill"}`
- **期望**: 参数校验拒绝（不在已知子技能范围）；错误信息包含上下文与恢复指引（列出唯一可用子技能 godmode）

### case_003: 错误路径 — 参数缺失（Golden Error）
- **输入**: `request="", context={}`
- **期望**: 输入校验拒绝（request 必须为非空 str）；错误信息明确指向缺失字段，而非裸异常（RED-005）

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

期望输出（v0.1.0）采用**路由决策语义等价判定**：
- `routed_to` 必须精确匹配预期子技能名（或 null）
- `status` 必须精确匹配（`ok` / `error`）
- 错误路径：`error.context` 必须提及触发字段，`error.recovery` 必须列出可用子技能
- 正常路径：`result` 必须为 dict 类型

## pass_threshold: 1.00

含义：3 个测试用例全部通过。

### 阈值理由
- 路由决策是确定性映射（仅 1 个子技能），不存在风格变体
- 越狱攻击路由必须针对特定策略（RED-002），通用方案视为路由失败
- 参数缺失/未验证代码必须 100% 报错或隔离（RED-005 / RED-006）

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-07-08 | 初始自设金标准，3 个 case（1 正常路由 + 2 错误路径） | Synthos Agent |
