# cron-failure-root-cause-diagnosis

## 触发条件

- cron job `last_status == "error"`
- 用户报告cron任务失败
- 闲置时主动巡检

## 诊断步骤

### Step 1: 列出所有error任务

```
cronjob(action='list') → 提取 last_status == "error" 的job
```

### Step 2: 读取错误日志

```
~/.hermes/cron/output/<job_id>/*.md  → 取最新文件
```

### Step 3: 分类错误类型

| 类型 | 特征 | 根因 | 修复 |
|------|------|------|------|
| 语法错误 | SyntaxError, unexpected indentation | Python/Shell代码有bug | 直接patch文件 |
| 超时错误 | `timed out`, `Request timed out` | LLM不可达或脚本耗时过长 | prompt加pre-flight检查或脚本限速 |
| 技能缺失 | `skill not found`, 或LLM超时 | cron引用的SKILL.md被删除 | 从备份或Synthos/skills/恢复技能 |
| 连接错误 | curl返回000, connection refused | vLLM节点不可达 | 切换到其他节点或修复网络 |
| 误报 | `grep "Error"`匹配但实际成功 | skill内容含"Error"关键词 | 用`grep "FAILED\|timed out"`精确匹配 |

### Step 4: 技能缺失检测（关键）

**最常见误诊**：cron任务因引用不存在的SKILL.md而持续失败，错误日志显示为`Request timed out`。根因是技能缺失，不是网络问题。

检测流程：
```
1. cronjob(action='list') → 查看 skill 字段
2. ls ~/.hermes/skills/<skill_name>/SKILL.md
3. 如果不存在 → 技能缺失 → 从备份或Synthos/skills/恢复
```

历史案例：`paper-pipeline`在2026-05-31后被删除，但cron任务`autonomous-core-researcher`仍引用它，导致每30分钟失败一次，持续86天。

### Step 5: 验证vLLM节点

```bash
curl -s http://100.100.252.99:8000/v1/models  # amax
curl -s http://100.82.27.51:8000/v1/models    # amax-fallback
```

两者都应返回HTTP 200 + 模型列表。

### Step 6: 修复脚本

| 错误类型 | 修复策略 |
|----------|---------|
| 语法错误 | patch文件，验证`python3 -m py_compile` / `bash -n` |
| 超时（脚本） | 加`--quiet`、`--stats 5s`、`--bwlimit 10M` |
| 超时（LLM） | prompt加pre-flight探测，fallback到其他节点 |
| 技能缺失 | 从备份恢复，或重建技能 |

## Pitfalls

1. **误报率**：约75%的"错误"文件是成功输出，skill内容含"Error"关键词被匹配
2. **技能缺失伪装成网络超时**：最常见误诊。skill缺失→LLM无法执行→超时→误以为网络问题
3. **历史日志爆炸**：单个job可能积累600+日志文件（102MB+）
4. **Python f-string + 多行 + CJK**：f-string内嵌换行符和中文字符→`SyntaxError: unterminated string literal`。修复：替换CJK为ASCII，提取变量后拼接
5. **rclone sync超时**：`--stats 1s`输出频繁 + 全量扫描→120s超时。修复：`--quiet`+`--stats 5s`+`--bwlimit`