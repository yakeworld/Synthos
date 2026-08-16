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


## Golden 集合 · GOLDEN SET

- **Golden Input**: `session_transcript: <≥5 次工具调用且有明确产出的会话>` + `current_memory: <1800/2200 chars，使用率 82%>`
- **Golden Output**: memory_entries 均为陈述式且各标注生长方向/框架维度/发酵潜力；操作按 remove→replace→add 顺序执行；consolidation_report 显示使用率回落至 60-75%
- **Golden Error**: 写入指令式语气（"Always use XXX"）→ 改为陈述式（"User prefers ..."）；容量 >80% 未主动清理 → 整批操作被拒

## Pitfalls

1. **记录已完成任务**：PR#42 merged、batch done→7天后是噪音，用session_search
2. **指令式语气**："Always use XXX"→被误解为硬规则，改为"User prefers"
3. **分散同类项**：同项目路径分多条→合并
4. **跳过宪法检查**：记忆不能绕过CONSTITUTION
5. **操作顺序错误**：remove后紧跟replace同一条目，all-or-nothing导致整批失败
6. **长文本匹配失败**：条目内容中的Unicode差异（→/->）或空格导致匹配失败，改用短关键字符串
7. **超过80%容量**：必须主动清理，否则整批操作被拒
8. **记忆膨胀**：每条记忆标注"生长方向"和"发酵潜力"，不能回答这两问的暂存而非删除

## 验证清单 · VERIFICATION

1. **输入**: 会话满足 ≥5 次工具调用且有明确产出；current_memory 使用率已检查（<80%）
2. **过程**: 三问过滤（生长方向/框架维度/发酵潜力）已逐条执行；宪法护栏检查通过
3. **输出**: 记忆条目均为陈述式；操作按 remove→replace→add 顺序执行；使用率回落至 60-75%
4. **边界**: 容量 >80% 时已主动清理；空会话（无高价值信息）时输出空 entries 不强行写入
5. **错误**: 整批操作失败时 all-or-nothing 回滚；Unicode 匹配失败时改用短关键字符串重试

## 示例 · EXAMPLES

**输入**：`session_transcript: <12 次工具调用，完成 lit-import 去重入库>` + `current_memory: 1800/2200 chars（82%）`
**输出**：remove 1 条过期路径 → add 2 条（"lit-import 去重经 BibTeX key 排序，重复条目 0" 标注：生长方向=工具链稳定/维度=P1 原子可复现/发酵=可沉淀为独立 skill）→ 使用率 71%

**输入**：`session_transcript: <8 次调用，PR#42 merged>`
**输出**：memory_entries: []（已完成任务 7 天后是噪音，归 session_search，不写入记忆）

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


## Genes (策略基因)

> 紧凑策略表示。条件→策略。需要深度时参考完整文档。

- **[CONV-001]** 候选记忆无法回答“生长方向/框架维度/发酵潜力”三问 → 标记为低优先级用于排序而非立即删除，防止误删潜在高价值信息
- **[CONV-002]** 记忆内容涉及已完成的具体任务（如 PR 合并、批次完成） → 不写入长期记忆，转而依赖 session_search 检索，避免记忆噪音
- **[CONV-003]** 记忆条目采用指令式语气（如 "Always use..."） → 强制转换为陈述式事实描述（如 "User prefers..."），防止被误解为硬规则
- **[CONV-004]** 记忆库容量使用率超过 80% → 触发主动清理机制，按价值排序删除低优先级项，确保整批操作不被拒绝
- **[CONV-005]** 执行记忆更新操作时 → 严格遵循 remove→replace→add 的原子顺序，确保 all-or-nothing 一致性，避免中间状态导致失败
- **[CONV-006]** 待写入的记忆与 CONSTITUTION 宪法条款冲突 → 立即拦截并拒绝写入，确保记忆系统不覆写核心宪法护栏
- **[CONV-007]** 存在多条分散的同类记忆项（如同项目不同路径） → 合并为单条高信号记忆，并使用连接符替代完整句子以压缩空间
- **[CONV-008]** 记忆匹配因 Unicode 差异（如箭头符号）或空格导致失败 → 改用短关键字符串进行匹配重试，提高操作鲁棒性
