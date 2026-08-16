---
name: apple-notes
description: apple-notes
version: 1.0.0
category: apple
signature: 'apple-notes -> apple: Use `memo` to manage Apple Notes directly from the
  terminal. Notes sync across a'
license: MIT
author: Synthos
metadata:
  synthos:
    signature: 'task_desc: str, params: dict -> result: dict'
    atom_type: skill
    priority: P2
    related_skills:
    - apple
    - apple-reminders
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

- **input**: `note_action: str, content: str` — 用户请求描述、上下文信息
- **output**: `note_result: dict — 备忘录`

> 对应原则：P2（机械原子暴露输入输出规范）

# Apple Notes

Use `memo` to manage Apple Notes directly from the terminal. Notes sync across all Apple devices via iCloud.

## Prerequisites

- **macOS** with Notes.app
- Install: `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- Grant Automation access to Notes.app when prompted (System Settings → Privacy → Automation)

## When to Use

- User asks to create, view, or search Apple Notes
- Saving information to Notes.app for cross-device access
- Organizing notes into folders
- Exporting notes to Markdown/HTML

## When NOT to Use

- Obsidian vault management → use the `obsidian` skill
- Bear Notes → separate app (not supported here)
- Quick agent-only notes → use the `memory` tool instead

## Quick Reference

### View Notes

```bash
memo notes                        # List all notes
memo notes -f "Folder Name"       # Filter by folder
memo notes -s "query"             # Search notes (fuzzy)
```

### Create Notes

```bash
memo notes -a                     # Interactive editor
memo notes -a "Note Title"        # Quick add with title
```

### Edit Notes

```bash
memo notes -e                     # Interactive selection to edit
```

### Delete Notes

```bash
memo notes -d                     # Interactive selection to delete
```

### Move Notes

```bash
memo notes -m                     # Move note to folder (interactive)
```

### Export Notes

```bash
memo notes -ex                    # Export to HTML/Markdown
```

## Limitations

- Cannot edit notes containing images or attachments
- Interactive prompts require terminal access (use pty=true if needed)
- macOS only — requires Apple Notes.app

## Rules

1. Prefer Apple Notes when user wants cross-device sync (iPhone/iPad/Mac)
2. Use the `memory` tool for agent-internal notes that don't need to sync
3. Use the `obsidian` skill for Markdown-native knowledge management

## 验证清单 · VERIFICATION

- [ ] 前置环境就绪：macOS 已安装 `memo`（`brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`），且 Notes.app 自动化权限已授予（System Settings → Privacy → Automation）
- [ ] 场景选择正确：非 Obsidian vault、非 agent 内部记忆（应用 `memory` 工具），确属跨设备同步需求才用 Apple Notes
- [ ] 命令用法正确：查看/搜索用 `memo notes`（`-f`/`-s`）、创建用 `memo notes -a "Title"`、导出用 `-ex`
- [ ] 限制处理得当：含图片/附件的笔记拒绝直接编辑，仅提示手动处理或改为查看（APPL-002）
- [ ] 交互模式可用：删除/移动/编辑（`-d`/`-m`/`-e`）在终端支持 pty 时正常完成用户选择（APPL-004）

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

- **[APPL-001]** 用户需要跨设备（iPhone/iPad/Mac）同步笔记 → 优先使用 Apple Notes (`memo`) 而非本地存储或 Obsidian
- **[APPL-002]** 笔记内容包含图片或附件 → 拒绝直接编辑操作，提示限制并建议手动处理或仅查看
- **[APPL-003]** 需要快速创建或查看笔记 → 使用 `memo notes -a "Title"` 或 `memo notes -s "query"` 进行非交互式操作
- **[APPL-004]** 执行删除、移动或复杂编辑操作 → 启用交互式模式（`-d`, `-m`, `-e`）并确保终端支持 pty 以处理用户选择
- **[APPL-005]** 用户请求仅用于 Agent 内部记忆且无需同步 → 使用 `memory` 工具而非 Apple Notes
- **[APPL-006]** 需要导出笔记内容用于其他工具处理 → 使用 `memo notes -ex` 导出为 Markdown 或 HTML 格式
- **[APPL-007]** 首次运行或权限缺失 → 检查 macOS 自动化权限（System Settings → Privacy → Automation）并引导用户授权
