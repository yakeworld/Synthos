---
name: daily-routine
description: REDIRECT — 日常自动化见 cron 运维 + 每日智报
signature: redirect -> research/daily-intelligence-briefing, devops/cron-system-maintenance
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.1
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: REDIRECT — 日常自动化见 cron 运维 + 每日智报
    signature: redirect -> research/daily-intelligence-briefing, devops/cron-system-maintenance
    priority: P2
    synthos_version: 1.0.1
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: research
---








# REDIRECT

此技能尚未独立实现。日常自动化功能分布在：

## IO_CONTRACT

- **input**: `routine_request: str` — 日常自动化请求（触发本入口的分流判断）
- **output**: `routing: str` — REDIRECT 分流决策：`research/daily-intelligence-briefing`（每日智报）/ `devops/cron-system-maintenance`（Cron运维）/ `devops/project-health-audit`（Self-check）
- **output**: `本技能不产出日常自动化执行结果` — 仅作为重定向入口，不实现具体逻辑

## 原则 (Principles)

> **入口无实，只指不代。** 本技能是重定向之门，不在此内实现自动化逻辑——守门者不越权代劳。
> **分流有据，一事一门。** 每日智报归 daily-intelligence-briefing，定时任务归 cron-system-maintenance，各归其位，不杂糅。

- **每日智报：** `skill_view(name='research/daily-intelligence-briefing')` — arXiv/HN/PubMed 三源情报
- **Cron运维：** `skill_view(name='devops/cron-system-maintenance')` — 定时任务管理
- **Self-check：** `skill_view(name='devops/project-health-audit')` — 系统健康检查


## Golden 集合 · GOLDEN SET

- **Golden Input**: `routine_request: "生成今日 arXiv/PubMed 情报"`
- **Golden Output**: `routing: "research/daily-intelligence-briefing"` 分流；同类：cron 请求 → `devops/cron-system-maintenance`，健康检查 → `devops/project-health-audit`；本技能不产出执行结果
- **Golden Error**: 在本技能文件内直接实现日常自动化逻辑（未分流即执行）→ 违反 REDIRECT 边界，验证清单第 2 条不通过

## 示例 · EXAMPLES

**输入**：`routine_request: "生成今日 arXiv/PubMed 情报"`
**输出**：`routing: "research/daily-intelligence-briefing"` → 加载该技能执行三源情报采集

**输入**：`routine_request: "检查 cron 任务健康度"`
**输出**：`routing: "devops/cron-system-maintenance"` → 加载 cron 运维技能执行诊断

## 约束规则 · RULES

- 本技能仅做分流判断，不在此文件内实现任何日常自动化逻辑
- 分流目标仅限三个：daily-intelligence-briefing / cron-system-maintenance / project-health-audit
- 未匹配到三个目标之一的请求，提示用户明确意图而非猜测执行
- 不修改目标技能的内容，只做 `skill_view` 重定向

## 验证清单 (Verification)

- [ ] 已按 REDIRECT 分流至 `research/daily-intelligence-briefing`（每日智报）与 `devops/cron-system-maintenance`（Cron运维）
- [ ] 本技能文件保持重定向入口，未在本文件内实现日常自动化逻辑
- [ ] 系统健康检查已指向 `devops/project-health-audit`（Self-check）
