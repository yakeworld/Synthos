# GOLDEN_SET.md — gaming

> 对应原则：P1（认知原子语义可复现：同一输入 + 同一路由逻辑 → 等价路由结论）
> golden_set_origin: self_defined

## 设计依据

本技能为 **external-automation 父级路由技能**（parent-skill），本身不执行游戏操作，仅作为目录索引：
校验 `game_type` / `mode` 输入，将请求路由到子技能 `minecraft-modpack-server` 或 `pokemon-player` 执行。

金标准的目标是验证：**给定相同的路由请求，父级能否正确分发到对应子技能，且在未知/错误输入时返回带上下文的错误信息（而非裸异常）**。

## 金标准覆盖范围

| 维度 | 覆盖 | 说明 |
|------|:--:|------|
| 子技能路由 | 2/2 | minecraft-modpack-server、pokemon-player |
| 错误路径 | 1/1 | 未知 game_type 拒绝 |
| 参数契约 | P2 | game_type: str, mode: str |
| 输出契约 | P2 | game_state: dict |

## 测试用例 (cases/)

### case_001: 正常路由 — Minecraft 模组服务器
- **输入**: `game_type="minecraft", mode="modpack-server"`
- **期望**: 路由到 `minecraft-modpack-server` 子技能；父级不执行实际游戏操作；输出 `game_state` 为 dict

### case_002: 正常路由 — 宝可梦模拟器
- **输入**: `game_type="pokemon", mode="player"`
- **期望**: 路由到 `pokemon-player` 子技能；父级仅作为目录索引；输出 `game_state` 结构一致

### case_003: 错误路径 — 未知游戏类型
- **输入**: `game_type="chess", mode="play"`
- **期望**: 参数校验拒绝（不在已知子技能范围）；错误信息包含上下文（未知 game_type）与恢复指引（列出可用子技能），而非裸异常

## 期望输出 (expected/)

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`。

期望输出（v0.1.0）采用**路由决策语义等价判定**：
- `routed_to` 必须精确匹配预期子技能名（或 null）
- `status` 必须精确匹配（`ok` / `error`）
- 错误路径：`error.context` 必须提及 `game_type`，`error.recovery` 必须列出全部可用子技能
- 正常路径：`game_state` 必须为 dict 类型

## pass_threshold: 1.00

含义：3 个测试用例全部通过。

### 阈值理由
- 路由决策是确定性映射（game_type → 子技能），不存在风格变体
- 未知输入的错误路径必须 100% 给出带上下文的恢复指引（GAMI-004）
- 父级越界执行（P3 人机分层）视为路由失败，必须拒绝

## 更新历史

| 版本 | 日期 | 变更 | 审批 |
|------|------|------|------|
| 0.1.0 | 2026-07-08 | 初始自设金标准，3 个 case（2 正常路由 + 1 错误路径） | Synthos Agent |
