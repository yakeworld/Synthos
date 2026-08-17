---
name: apple-reminders
description: apple-reminders
version: 1.0.0
category: apple
signature: 'apple-reminders -> apple: Use `remindctl` to manage Apple Reminders directly
  from the terminal. Tasks sync'
license: MIT
author: Synthos
metadata:
  synthos:
    signature: 'task_desc: str, params: dict -> result: dict'
    atom_type: skill
    priority: P2
    related_skills:
    - apple
    - apple-notes
---


## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告

## Pitfalls
- 
- 

## Verification
- 
- 
- 
- 
1. 
2. 
3. 
## IO_CONTRACT

- **input**: `task: str, list: str` — 用户请求描述、上下文信息
- **output**: `reminder_status: dict — 提醒事项`

> 对应原则：P2（机械原子暴露输入输出规范）

# Apple Reminders

Use `remindctl` to manage Apple Reminders directly from the terminal. Tasks sync across all Apple devices via iCloud.

## Prerequisites

- **macOS** with Reminders.app
- Install: `brew install steipete/tap/remindctl`
- Grant Reminders permission when prompted
- Check: `remindctl status` / Request: `remindctl authorize`

## When to Use

- User mentions "reminder" or "Reminders app"
- Creating personal to-dos with due dates that sync to iOS
- Managing Apple Reminders lists
- User wants tasks to appear on their iPhone/iPad

## When NOT to Use

- Scheduling agent alerts → use the cronjob tool instead
- Calendar events → use Apple Calendar or Google Calendar
- Project task management → use GitHub Issues, Notion, etc.
- If user says "remind me" but means an agent alert → clarify first

## Quick Reference

### View Reminders

```bash
remindctl                    # Today's reminders
remindctl today              # Today
remindctl tomorrow           # Tomorrow
remindctl week               # This week
remindctl overdue            # Past due
remindctl all                # Everything
remindctl 2026-01-04         # Specific date
```

### Manage Lists

```bash
remindctl list               # List all lists
remindctl list Work          # Show specific list
remindctl list Projects --create    # Create list
remindctl list Work --delete        # Delete list
```

### Create Reminders

```bash
remindctl add "Buy milk"
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl add --title "Meeting prep" --due "2026-02-15 09:00"
```

### Complete / Delete

```bash
remindctl complete 1 2 3          # Complete by ID
remindctl delete 4A83 --force     # Delete by ID
```

### Output Formats

```bash
remindctl today --json       # JSON for scripting
remindctl today --plain      # TSV format
remindctl today --quiet      # Counts only
```

## Date Formats

Accepted by `--due` and date filters:
- `today`, `tomorrow`, `yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601 (`2026-01-04T12:34:56Z`)

## Rules

1. When user says "remind me", clarify: Apple Reminders (syncs to phone) vs agent cronjob alert
2. Always confirm reminder content and due date before creating
3. Use `--json` for programmatic parsing

## 验证清单 · VERIFICATION

- [ ] 权限与授权已检查：macOS 环境就绪，`remindctl status` 正常，必要时 `remindctl authorize` 完成授权（APPL-005）
- [ ] 意图澄清：用户说 "remind me" 时已区分 Apple Reminders（同步设备）vs agent cronjob 警报，日历事件/项目任务已转介其他工具（APPL-001/004）
- [ ] 创建前确认：提醒内容、所属列表、截止日期三项已与用户确认后再执行 `remindctl add`（APPL-002）
- [ ] 日期格式正确：`--due` 使用受支持格式（today/tomorrow、YYYY-MM-DD、YYYY-MM-DD HH:mm、ISO 8601）
- [ ] 输出格式符合用途：程序化解析用 `--json`，人工查看用 `--plain`/`--quiet`（APPL-003）

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[APPL-014]** 用户提及 "remind me" 或 "提醒" → 必须澄清是指 Apple Reminders（同步至设备）还是 Agent Cronjob 警报
- **[APPL-015]** 创建提醒事项前 → 必须确认提醒内容、所属列表及截止日期
- **[APPL-016]** 需要程序化解析提醒数据时 → 使用 `--json` 参数获取结构化输出
- **[APPL-017]** 用户意图涉及日历事件或项目管理 → 拒绝使用 Apple Reminders，转而推荐 Calendar 或 GitHub/Notion
- **[APPL-018]** 执行 `remindctl` 命令前 → 检查 macOS 环境及 Reminders 权限授权状态
- **[APPL-019]** 处理日期参数时 → 支持 `today`/`tomorrow` 等相对时间或 `YYYY-MM-DD HH:mm` 等绝对时间格式

## 示例 · EXAMPLES

1. **创建同步到 iPhone 的提醒**：输入「明天下午3点提醒我开会」→ 与用户确认内容/列表/日期后执行 `remindctl add --title "开会" --list Work --due "2026-02-15 15:00"` → 验证：`remindctl tomorrow --json` 中出现该条目且 due 正确。
2. **用户说 "remind me"（意图模糊）**：输入「remind me to review the PR」→ 先澄清是 Apple Reminders（同步到手机）还是 agent cronjob 警报；若是日历事件则转介 Calendar → 验证：澄清后走对分支，未误建 Reminders 条目。
3. **脚本化统计逾期项**：输入「列出所有逾期提醒」→ `remindctl overdue --json` 程序化解析（不用人眼读 plain 输出）→ 验证：JSON 可被 `python3 -c "import json,sys;print(len(json.load(sys.stdin)))"` 解析且计数与 `remindctl overdue --quiet` 一致。
