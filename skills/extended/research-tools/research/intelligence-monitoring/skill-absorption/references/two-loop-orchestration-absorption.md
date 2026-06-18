# Two-Loop Orchestration: AI-Research-SKILLs → ROUTE 吸收案例

> 2026-05-18 | 吸收自 Orchestra-Research/AI-research-SKILLs (8,492⭐, MIT)
> 目标原子: task-router (ROUTE) v1.1.0 → v1.2.0
> 评估分: 4.3/5

## 吸收模式：编排协议注入（Phase 1 新类别）

编排协议注入是 Phase 1 的第五种机制类型，专门用于将外部项目的编排模式（循环/状态机/条件分支）注入目标系统的路由层。

## 被改文件

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `skills/task-router/SKILL.md` | rewrite | 新增3种执行模式 + 循环协议 + 退出条件 + 状态追踪 + 输出schema |
| `skills/task-router/references/IO_CONTRACT.md` | rewrite | 新增 input(mode_hint, context) + output(loop_state) |
| `skills/task-router/references/BOUNDARY.md` | extend | 声明循环编排 vs 原子认知的5项边界 |
| `skills/task-router/references/CHANGE_LOG.md` | extend | v1.2.0 变更记录 |

## 注入的核心机制

### 1. 执行模式分类（新增）
- `simple_chain` — 线性执行，保留原有行为
- `exploratory_loop` — 仅内循环：HYP→VER→ASC 迭代
- `research_twoloop` — 双循环：内循环 + 每5轮外循环复盘

### 2. 内循环协议
```
Bootstrap (ACQ→EXT) → 重复 HYP→VER→ASC 直到收敛/最大10轮/用户中断
```

### 3. 外循环协议
```
每5轮: ASC全局模式识别 → HYP方向决策 → continue/pivot/finalize
```

### 4. 循环状态追踪
```
loop_state: {inner_iterations, outer_iterations, exit_reason, accumulated_results, outer_reviews}
```

## 实现模式（可复用）

1. **不改已有流程，仅追加新模式** — 原有 simple_chain 路径完全保留
2. **通过 keyword tags 触发模式选择** — needs_research/needs_twoloop
3. **mode_hint 覆盖机制** — 用户或 evolution 引擎可强制指定模式
4. **四重同步** — SKILL.md + IO_CONTRACT + BOUNDARY + CHANGE_LOG 同时更新

## 发现的陷阱

| 陷阱 | 规避 |
|------|------|
| 无限循环 | 强制 max_inner_iterations=10 |
| 外循环过慢 | 执行时主动报告"正在复盘第 N 轮" |
| 收敛误判 | 连续2轮收敛信号才视为真收敛 |
| 方向漂移 | 至少5次内循环后才允许 pivot |
| 上下文膨胀 | 每次外循环后压缩历史（摘要+最近3轮） |
| 一次性查询不应循环 | 关键词判定时，缺乏 needs_research 标记则不触发 |

## 前置条件

在应用此模式前，目标原子必须已有：
- 清晰的 IO_CONTRACT（输入/输出 schema）
- 明确的 BOUNDARY（职责边界）
- 已存在的线性执行路径
