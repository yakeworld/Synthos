---
name: task-router
description: task-router 金测集 — 路由决策的可执行测试
---

# 金测集: task-router

> 来源: SKILL.md Golden 集合（L267-271）。每个 case 验证路由决策的正确性（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 标准文献搜索路由 | route=standard, chain=[knowledge-acquisition, knowledge-extraction] |
| case_002 | 微操 context 反模式 | context 含微操指令 → 应判失败（子代理中断） |
| case_003 | 批量任务拆分 | >10 篇论文 → 拆为并行子任务 |
| case_004 | 单点写作任务路由 | 润色引言 → 仅 ARG（不越级） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: route 必须为 standard，chain 必须含 knowledge-acquisition
- case_002: 必须拒绝微操 context（Golden Error 路径）
- case_003: 必须拆分而非单代理超载
- case_004: 写作/润色类仅调 ARG，不越级加 ACQ/EXT

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001/002） |
| high | 0.7 | 重要但不致命（case_003） |

## 关联

- SKILL.md Genes: ROUT-001~006
- Golden 集合: SKILL.md L267-271
