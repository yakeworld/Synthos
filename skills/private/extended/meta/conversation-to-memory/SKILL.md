---
name: conversation-to-memory
description: '⚡ P0 从会话提取高价值信息→记忆。动灵三问: 生长方向?框架维度?发酵潜力?+宪法护栏(记忆不能覆写CONSTITUTION)+凝练压缩策略。防记忆膨胀同时保留高信号事实。每条记忆标注生长方向和发酵潜力。'
signature: 'conversation-to-memory -> ~: placeholder signature. Update with actual contract.'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.5.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: '⚡ P0 从会话提取高价值信息→记忆。动灵三问: 生长方向?框架维度?发酵潜力?+宪法护栏(记忆不能覆写CONSTITUTION)+凝练压缩策略。防记忆膨胀同时保留高信号事实。每条记忆标注生长方向和发酵潜力。'
    signature: 'conversation-to-memory -> ~: placeholder signature. Update with actual contract.'
    priority: P2
    synthos_version: 1.5.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
author: Hermes Agent
---


|
| **生长方向** | 这条记忆支持系统哪个生长方向？ | 增强对用户偏好判断的准确性 |
| **框架维度** | 与7+1框架哪个维度相关？ | P2(原子边界精确)：记录新工具路径 |
| **发酵潜力** | 这条记忆能发酵（转化为新能力/新技能）吗？ | 可沉淀为skill:记住用户路径偏好 |

## IO_CONTRACT

- **input**: `session_transcript: str` — 当前会话内容（原子任务完成时 ≥5 次工具调用且有明确产出）
- **input**: `current_memory: str` — 现有记忆库（memory target 2200 chars / user target 1375 chars，容量水位检查）
- **output**: `memory_entries: list[str]` — 陈述式记忆条目（每条标注生长方向/框架维度/发酵潜力，remove→replace→add 原子操作）
- **output**: `consolidation_report` — 三问过滤、宪法护栏与压缩结果（使用率 60-75%，无指令式语气，无重复同类项）

**原则**：不能回答这三问的记忆，在生长视角下价值存疑。但暂不为此设硬性删除，而是作为优先级排序依据。

## Operational Steps

1. **收集候选** — 按优先级分类（用户偏好→环境细节→工作流方法），标记高价值项
2. **三问过滤** — 7天后产生新知识？帮助理解生长轨迹？session_search能找到？
3. **凝练压缩** — 指令式→陈述式，合并同类项，去冗余，用连接符替代完整句子
4. **空间管理** — >2000 chars 时按价值排序删除，优先保留用户偏好和环境细节
5. **原子操作** — 按操作顺序模板执行：先remove→再replace→再add，确保all-or-nothing

## Pitfalls

1. **记录已完成任务**：PR#42 merged、batch done→7天后是噪音，用session_search
2. **指令式语气**："Always use XXX"→被误解为硬规则，改为"User prefers"
3. **分散同类项**：同项目路径分多条→合并
4. **跳过宪法检查**：记忆不能绕过CONSTITUTION
5. **操作顺序错误**：remove后紧跟replace同一条目，all-or-nothing导致整批失败
6. **长文本匹配失败**：条目内容中的Unicode差异（→/->）或空格导致匹配失败，改用短关键字符串
7. **超过80%容量**：必须主动清理，否则整批操作被拒
8. **记忆膨胀**：每条记忆标注"生长方向"和"发酵潜力"，不能回答这两问的暂存而非删除

## Verification

1. 所有记忆是否为陈述式而非指令式？
2. 是否通过了动灵三问（生长方向/框架维度/发酵潜力）？
3. 宪法检查是否通过（无违反CONSTITUTION不可修改条款）？
4. 操作顺序是否符合remove→replace→add模板？
5. 使用率是否控制在60-75%（memory target 2200 chars, user target 1375 chars）？
6. 是否有重复/分散同类项需要合并？---





|
| **生长方向** | 这条记忆支持系统哪个生长方向？ | 增强对用户偏好判断的准确性 |
| **框架维度** | 与7+1框架哪个维度相关？ | P2(原子边界精确)：记录新工具路径 |
| **发酵潜力** | 这条记忆能发酵（转化为新能力/新技能）吗？ | 可沉淀为skill:记住用户路径偏好 |

**原则**：不能回答这三问的记忆，在生长视角下价值存疑。但暂不为此设硬性删除，而是作为优先级排序依据。

## Operational Steps

1. **收集候选** — 按优先级分类（用户偏好→环境细节→工作流方法），标记高价值项
2. **三问过滤** — 7天后产生新知识？帮助理解生长轨迹？session_search能找到？
3. **凝练压缩** — 指令式→陈述式，合并同类项，去冗余，用连接符替代完整句子
4. **空间管理** — >2000 chars 时按价值排序删除，优先保留用户偏好和环境细节
5. **原子操作** — 按操作顺序模板执行：先remove→再replace→再add，确保all-or-nothing

## Pitfalls

1. **记录已完成任务**：PR#42 merged、batch done→7天后是噪音，用session_search
2. **指令式语气**："Always use XXX"→被误解为硬规则，改为"User prefers"
3. **分散同类项**：同项目路径分多条→合并
4. **跳过宪法检查**：记忆不能绕过CONSTITUTION
5. **操作顺序错误**：remove后紧跟replace同一条目，all-or-nothing导致整批失败
6. **长文本匹配失败**：条目内容中的Unicode差异（→/->）或空格导致匹配失败，改用短关键字符串
7. **超过80%容量**：必须主动清理，否则整批操作被拒
8. **记忆膨胀**：每条记忆标注"生长方向"和"发酵潜力"，不能回答这两问的暂存而非删除

## Verification

1. 所有记忆是否为陈述式而非指令式？
2. 是否通过了动灵三问（生长方向/框架维度/发酵潜力）？
3. 宪法检查是否通过（无违反CONSTITUTION不可修改条款）？
4. 操作顺序是否符合remove→replace→add模板？
5. 使用率是否控制在60-75%（memory target 2200 chars, user target 1375 chars）？
6. 是否有重复/分散同类项需要合并？
