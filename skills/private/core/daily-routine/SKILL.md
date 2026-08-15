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

- **每日智报：** `skill_view(name='research/daily-intelligence-briefing')` — arXiv/HN/PubMed 三源情报
- **Cron运维：** `skill_view(name='devops/cron-system-maintenance')` — 定时任务管理
- **Self-check：** `skill_view(name='devops/project-health-audit')` — 系统健康检查

## 验证清单 (Verification)

- [ ] 已按 REDIRECT 分流至 `research/daily-intelligence-briefing`（每日智报）与 `devops/cron-system-maintenance`（Cron运维）
- [ ] 本技能文件保持重定向入口，未在本文件内实现日常自动化逻辑
- [ ] 系统健康检查已指向 `devops/project-health-audit`（Self-check）
