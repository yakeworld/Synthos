# Golden 集合 · conversation-to-memory

> 单一真理来源。所有改进必须通过 golden 测试。

## 测试用例表

| Case ID | 名称 | 类型 | 输入要点 | 预期行为 |
|---------|------|------|----------|----------|
| case_001 | 正常提取：lit-import 去重入库 | normal | session 含 12 次工具调用，完成去重任务；current_memory 82% 使用率 | remove→add 操作，使用率回落至 60-75%，条目陈述式 |
| case_002 | 空会话：PR 合并无高价值信息 | normal | session 仅完成 PR#42 merged（8 次调用） | memory_entries 为空，不强行写入 |
| case_003 | 错误路径：指令式语气 + 容量超限 | error | 候选记忆含 "Always use XXX"；current_memory 90% 使用率 | 整批操作被拒；报告容量超限，要求先清理 |

## 通过标准

### case_001（正常提取）
1. `memory_entries` 中每条均为陈述式（无 "Always use" / "必须" 等指令式语言）
2. 每条记忆标注：生长方向、框架维度、发酵潜力
3. 操作顺序：remove → replace → add
4. `consolidation_report.usage_ratio` 在 0.60–0.75 范围
5. 宪法检查通过（无违反 CONSTITUTION 不可修改条款）

### case_002（空会话）
1. `memory_entries` 为空列表 `[]`
2. 报告中说明原因（已完成任务 7 天后是噪音，归 session_search）
3. 不产生任何 remove/replace/add 操作

### case_003（错误路径）
1. 检测到指令式语气，标记需转换为陈述式
2. 容量 >80% 触发主动清理机制
3. 整批操作被拒绝（all-or-nothing）
4. 错误信息包含：违规条目、容量数值、恢复建议（先清理后重试）

## 文件清单

- `cases/case_001.json` — 正常提取输入
- `cases/case_002.json` — 空会话输入
- `cases/case_003.json` — 错误路径输入
- `expected/case_001.json` — 正常提取预期输出
- `expected/case_002.json` — 空会话预期输出
- `expected/case_003.json` — 错误路径预期输出
