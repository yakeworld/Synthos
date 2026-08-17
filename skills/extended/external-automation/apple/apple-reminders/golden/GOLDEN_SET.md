---
name: apple-reminders
description: apple-reminders 金测集 — remindctl 管理 Apple Reminders 的可执行测试
---

# 金测集: apple-reminders

> 来源: SKILL.md Golden 集合 + 验证清单 + Genes (APPL-001~006) + IO_CONTRACT + 示例。
> 核心能力：通过 `remindctl` CLI 管理 Apple Reminders（查看/列表管理/创建/完成/删除），
> 任务经 iCloud 跨设备同步。
> IO_CONTRACT: input `task: str, list: str` → output `reminder_status: dict`。
> 每个 case 验证意图澄清、创建前三确认、命令与日期格式、输出格式（P1 可复现性）。

## 测试用例

| ID | 描述 | 关键检查 |
|----|------|---------|
| case_001 | 正常：创建带日期提醒 | 创建前确认内容/列表/日期三项（APPL-002）；`remindctl add --title ... --list ... --due ...`；日期格式合法（APPL-006） |
| case_002 | 正常：程序化统计逾期 | `remindctl overdue --json` 可被 `python3 json.load` 解析（APPL-003）；计数与 `--quiet` 一致 |
| case_003 | 错误路径：意图模糊 "remind me" | 先澄清 Apple Reminders vs agent cronjob 警报（APPL-001），澄清前不创建条目 |
| case_004 | 错误路径：未授权执行 remindctl | `remindctl status` 未授权 → 引导 `remindctl authorize`，不静默失败（APPL-005） |

## 通过标准

- 加权总分 ≥ 0.85（critical 项必过）
- case_001: 创建前必须有三项确认（内容/列表/截止日期），命令精确含 `--title`/`--list`/`--due`，`--due` 用受支持格式（today/tomorrow、YYYY-MM-DD、YYYY-MM-DD HH:mm、ISO 8601）
- case_002: 必须走 `--json` 而非人眼读 plain（APPL-003）；JSON 可解析且计数与 `--quiet` 输出一致
- case_003: 澄清前 `command_executed` 必须为 null（不得抢跑创建）；澄清问题必须区分两个分支（Apple Reminders 同步设备 / agent cronjob 警报）
- case_004: 错误含上下文（status 未授权）与可执行恢复命令（`remindctl authorize`）
- 所有 case: 日历事件/项目任务请求必须转介 Calendar 或 GitHub/Notion（APPL-004 / When NOT to Use）

## 权重

| 权重 | 值 | 含义 |
|------|----|------|
| critical | 1.0 | 必须通过（case_001 / case_003） |
| high | 0.7 | 重要但不致命（case_002 / case_004） |

## 期望输出

每个 case 的期望输出存放于 `golden/expected/case_NNN.json`，包含：
- `expected_output`: 命令 / 结果结构 / 澄清与错误结构
- `verification`: 可执行的校验断言列表

期望输出采用**语义等价判定**：
- 命令字符串按 SKILL.md Quick Reference 精确匹配（标题/列表名可变，flag 结构必须一致）
- reminder_status 必须是 dict，键名稳定（如 `status`, `title`, `list`, `due`, `error`, `recovery`, `clarify`）
- 日期值语义等价（相对 today/tomorrow 与对应绝对日期可互认，但必须在受支持格式集合内）

## 关联

- SKILL.md Genes: APPL-001~006
- SKILL.md 验证清单: 5 项（权限授权 / 意图澄清 / 创建前确认 / 日期格式 / 输出格式）
- SKILL.md 示例: 3 条（创建同步提醒 / 意图模糊澄清 / 逾期统计脚本化）
- 相关技能: apple（父级路由）, apple-notes, cronjob 工具（agent 警报分支）
