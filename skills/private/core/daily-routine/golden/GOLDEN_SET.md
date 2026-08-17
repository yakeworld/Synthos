---
name: daily-routine
description: GOLDEN_SET.md
---

# 金测集: daily-routine

> 本技能是 REDIRECT 入口：仅做分流判断，不在此文件内实现任何日常自动化逻辑（DAIL-001）。
> 分流目标仅限三个：`research/daily-intelligence-briefing`（每日智报）/ `devops/cron-system-maintenance`（Cron运维）/ `devops/project-health-audit`（Self-check）。
> Golden 集合是测试的单一真理来源。

## 测试用例

| ID | 描述 | 关键检查 | 权重 |
|----|------|---------|------|
| 1 | 正常路径：arXiv/PubMed 情报请求 → 重定向至 daily-intelligence-briefing | `routing == "research/daily-intelligence-briefing"`；仅 skill_view 重定向，不产出执行结果；不修改目标技能内容 | critical |
| 2 | 正常路径：cron 运维 + 系统健康检查请求 → 分别重定向至正确目标 | cron 请求 → `devops/cron-system-maintenance`；健康检查 → `devops/project-health-audit`；分流目标均在白名单三目标内 | critical |
| 3 | 错误路径：请求未匹配三个目标 + 在技能文件内直接实现自动化逻辑 | 未匹配请求提示用户明确意图而非猜测执行（DAIL-005）；技能文件内实现自动化逻辑判定违反 REDIRECT 边界，验证清单第 2 条不通过 | high |

## 通过标准

- 加权总分 ≥ 0.80
- 所有 critical 检查通过
- 分流目标仅限白名单三个，未匹配时禁止猜测执行
- 技能文件保持重定向入口，不含任何日常自动化实现逻辑

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过 |
| high | 0.7 | 重要但不致命 |
| medium | 0.4 | 有价值但不是核心 |

## 已知陷阱

1. 在本技能文件内直接实现日常自动化逻辑 → 违反 REDIRECT 边界（Golden Error）
2. 未匹配三个目标的请求被猜测执行 → 违反 DAIL-005，必须提示用户明确意图
3. 重定向时修改目标技能内容 → 违反 DAIL-006，仅允许 skill_view 加载
