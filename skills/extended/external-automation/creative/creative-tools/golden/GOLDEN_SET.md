---
name: creative-tools
description: creative-tools 金测集 — 复合套件的路由决策与错误报告可执行测试
---

# 金测集: creative-tools

> 来源: SKILL.md Genes（CREA-001~008）与验证清单。每个 case 验证路由决策的正确性（P1 可复现性）。
> 核心断言（CREA-001 / 验证清单第 1 项）：任务必须路由到唯一的成员子技能（25 个 members 之一），不得在套件层直接执行；P3 人机分层——路由器负责路由，原子负责执行。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | ASCII 艺术请求路由到 ascii-art（正常路径） | `task_desc` 描述 ASCII 艺术需求 → 路由到唯一成员 `ascii-art`；`result` 结构可追溯至成员输出（CREA-001/CREA-007） |
| case_002 | TouchDesigner 任务未先查元数据（错误路径） | TD 相关任务 → 必须先调用 `td_get_par_info` 获取元数据，严禁猜测参数名（CREA-005 / 验证清单第 4 项）；失败时返回含上下文与恢复建议的错误报告（CREA-008），而非裸异常 |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 路由目标必须是 25 个 members 中的唯一成员（ascii-art）；输入符合 IO_CONTRACT（`task_desc: str` 非空 + `context: dict`）；`result: dict` 可追溯至实际执行的成员
- case_002: 在调用任何 TD 操作前必须先调用 `td_get_par_info`（Golden Error 路径：跳过元数据查询直接猜参数名 → 判失败）；错误报告必须含失败步骤 + 可操作恢复建议，裸异常判失败

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001/002） |
| high | 0.7 | 重要但不致命（预留扩展 case） |

## 关联

- SKILL.md Genes: CREA-001~008
- SKILL.md 验证清单（唯一成员路由 / IO_CONTRACT 校验 / TD 元数据先行 / 设计方向 2-3 变体 / 错误报告含恢复建议）
- IO_CONTRACT: `task_desc: str, context: dict -> result: dict`
- Members: 25 个子技能（见 SKILL.md Members 小节）
