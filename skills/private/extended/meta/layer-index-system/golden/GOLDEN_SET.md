# Golden 集合 · layer-index-system

> 单一真理来源。所有改进必须通过 golden 测试。

## 测试用例表

| Case ID | 名称 | 类型 | 输入要点 | 预期行为 |
|---------|------|------|----------|----------|
| case_001 | 正常检索：devops 层 + "cron" | normal | layer="devops", query="cron", context={} | 返回匹配 devops 层中 "cron" 的技能列表 |
| case_002 | 错误路径：缺失 layer 参数 | error | layer 缺失, query="python", context={} | 拒绝执行，返回含缺失字段名+恢复建议的错误 |
| case_003 | 边界：空 query | error | layer="devops", query="", context={} | 触发边界验证（LAYE-004），返回空列表+提示 |

## 通过标准

### case_001（正常检索）
1. 输出 `skill_list` 为 `list[dict]`，每项含 `name` 和 `description` 字段
2. 结果仅含 devops 层中匹配 "cron" 的技能（如 `cron-system-maintenance`、`devops`）
3. 不含其他 layer 的技能
4. 结构严格符合 IO_CONTRACT

### case_002（缺失参数）
1. 不产出 `skill_list`
2. 错误信息包含：缺失字段名（"layer"）
3. 错误信息包含上下文（哪个调用失败）
4. 错误信息包含恢复建议（提供有效 layer 名称）
5. 引用 LAYE-001 规则

### case_003（空 query）
1. 触发 LAYE-004 边界验证
2. 返回 `skill_list: []` 或明确错误
3. 错误/提示包含上下文与恢复建议
4. 不抛出未捕获异常

## 文件清单

- `cases/case_001.json` — 正常检索输入
- `cases/case_002.json` — 缺失参数输入
- `cases/case_003.json` — 空 query 边界输入
- `expected/case_001.json` — 正常检索预期输出
- `expected/case_002.json` — 缺失参数预期错误
- `expected/case_003.json` — 空 query 预期错误
