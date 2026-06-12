# Cron错误诊断模式

本文档记录cron错误的分类模式和诊断路径。

## 错误分类

### 1. 语法错误 (SyntaxError)

特征：`SyntaxError: unterminated string literal`

根因：Python f-string中包含换行符或中文字符在特定编码下导致字符串未闭合。

诊断：
```bash
tail -30 ~/.hermes/cron/output/<job_id>/<latest>.md
# 查找 "SyntaxError" 关键字
```

修复模式：
- 从f-string中提取复杂表达式为中间变量
- 避免在f-string内嵌换行符（用`\\n`字面量而非实际换行）
- 用英文字符串替代中文符号（pass/fail替代✓/✗）
- timedelta等依赖必须在文件顶部import，不能延迟到函数内部

案例：qc_batch_scan.py 第242行
```python
# 错误：
report += f"| {name} | {r['d8_count']} | {r['d10a_coverage']:.0%} | {'✓' if r.get('pipeline_complete') else '✗'} | {r.get('gate_summary', '?')} |\n"

# 修复：
pipe = 'pass' if r.get('pipeline_complete') else 'fail'
d8 = r['d8_count']
d10a = r['d10a_coverage']
gates = r.get('gate_summary', '?')
report += f"| {name} | {d8} | {d10a:.0%} | {pipe} | {gates} |\n"
```

### 2. 超时错误 (Timeout)

特征：`Script timed out after 120s` 或 `RuntimeError: Request timed out`

根因：
- no_agent脚本：rclone sync 大目录全量扫描+频繁输出（--stats 1s）
- LLM任务：模型服务不可达（curl 000）

诊断：
```bash
# no_agent脚本超时：
tail ~/.hermes/cron/output/<job_id>/<latest>.md | grep "timed out"

# LLM超时：
curl -s -o /dev/null -w "%{http_code}" http://100.100.252.99:8000/v1/models
curl -s -o /dev/null -w "%{http_code}" http://100.82.27.51:3000/v1/models
```

修复模式：
- 脚本层面：--quiet + --stats 5s + --bwlimit 限速
- prompt层面：增加pre-flight连接探测，fallback策略

### 3. 误报 (False Positive)

特征：日志含"Error"或"FAILED"字样但实际输出是成功的。

根因：cron日志加载了skill SKILL.md内容，其中包含错误处理代码示例。

诊断：
```bash
# 精确匹配真正的失败
grep -c "FAILED\|timed out" ~/.hermes/cron/output/<job_id>/2026-06-1*.md

# 避免：grep -c "Error" — 会匹配skill内容
```

## 诊断流程

```
cronjob(list) -> filter last_status=="error"
  for each error job:
    read latest log
    if "SyntaxError" -> patch script
    if "timed out" -> check timeout source (script vs LLM)
      script timeout -> reduce output, add bandwidth limit
      LLM timeout -> add pre-flight check to prompt
    if "false positive" -> ignore
    verify fix (py_compile / bash -n)
    list again -> check last_status
```
