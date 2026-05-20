# IO_CONTRACT.md — task-router

> 对应原则：P2
> 权威来源：docs/atom-io-schemas.md

## 概述

原子类型：router
上游依赖：无（唯一入口点）

## Input

| 字段 | 类型 | 必须 | 来源 | 说明 |
|------|------|:----:|------|------|
| `query` | string | ✅ | 用户输入 | 原始查询文本 |
| `mode_hint` | string | ❌ | 用户/evolution | 执行模式提示：`simple` / `exploratory` / `research` / `auto`（默认auto） |
| `context` | dict | ❌ | evolution引擎 | 上次循环的执行上下文（用于循环迭代） |

## Output（pipeline_trace.json）

### 标准输出（所有模式通用）

| 字段 | 类型 | 说明 |
|------|------|------|
| `run_id` | string | 运行标识（时间戳） |
| `query` | string | 原始查询 |
| `status` | string | `completed` / `short_circuited` / `error` / `loop_exited` |
| `routing.mode` | string | 执行模式：`simple_chain` / `exploratory_loop` / `research_twoloop` |
| `routing.complexity` | string | `simple` / `medium` / `complex` / `full` / `research` |
| `routing.loops_executed` | int | 执行循环数（非循环模式=0） |

### 循环模式额外输出（exploratory / research）

| 字段 | 类型 | 说明 |
|------|------|------|
| `loop_state.inner_iterations` | int | 内循环执行次数 |
| `loop_state.outer_iterations` | int | 外循环执行次数（仅research模式） |
| `loop_state.exit_reason` | string | 退出原因：`converged` / `max_iterations` / `pivot` / `user_interrupt` |
| `loop_state.accumulated_results` | array | 每次内循环的结果摘要 |
| `loop_state.outer_reviews` | array | 每次外循环的复盘摘要（仅research模式） |
