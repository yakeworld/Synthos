---
name: cron-system-maintenance
description: 'Cron任务运维：诊断error状态、修复脚本缺陷、验证连接性。覆盖cron job list分析、错误分类、脚本语法验证、prompt更新、vLLM多节点负载均衡。'
version: 1.0.0
allowed-tools:
- cronjob
- terminal
- read_file
- write_file
- skill_manage
metadata:
  synthos:
    version: 1.2.0
    priority: P1
    atom_type: workflow
    author: Synthos
    signature: 'job_list -> diagnose -> fix -> verify'

---


# cron-system-maintenance

Cron任务运维：诊断error状态、修复脚本缺陷、验证连接性。覆盖cron job list分析、错误分类、脚本语法验证、prompt更新、vLLM多节点负载均衡。

## 触发条件

- cron job list中任何job `last_status == "error"`
- 用户要求检查cron健康状态
- cron连续失败（同一job连续3次error）
- 闲置时主动巡检

## 执行步骤

1. **列出所有cron任务** — `cronjob(action='list')`
2. **筛选error jobs** — 提取`last_status == "error"`的job列表
3. **定位错误根源** — 对每个error job：
   - 读取最近错误日志：`~/.hermes/cron/output/<job_id>/*.md`（取最新的）
   - 分类错误类型：
     - **语法错误** — Python SyntaxError、Shell语法错误
     - **超时错误** — `timed out`、`Request timed out`、`Script timed out after 120s`
     - **连接错误** — curl返回000、connection refused
     - **运行时错误** — 其他RuntimeError
     - **技能缺失** — cron引用的SKILL.md被删除（根因是技能缺失而非网络超时）
   - 注意误报：skill加载内容含"Error"/"FAILED"但不是真正失败
4. **关键诊断：技能缺失检测** — 在`cronjob(action='list')`输出中查看`skill`字段，然后用`ls ~/.hermes/skills/<skill_name>/SKILL.md`验证存在性。如果技能缺失，从备份或Synthos/skills/恢复。
5. **修复脚本** — 根据错误类型修复：
   - 语法错误：直接patch文件
   - 超时：减少输出(`--quiet`)、增加间隔(`--stats`)、限速(`--bwlimit`)
   - 连接错误：在prompt中增加pre-flight探测步骤
6. **验证修复** — `python3 -m py_compile` / `bash -n`
7. **更新cron prompt** — 对持续超时任务，在prompt开头增加连接性探测代码块
8. **确认修复状态** — 再次list确认last_status是否恢复

## vLLM多节点负载均衡架构

当存在多个vLLM节点时（如amax + amax-fallback），按以下原则分配cron任务：

1. **验证节点健康**：`curl -s http://<host>:8000/v1/models` → HTTP 200 + 返回模型列表
2. **验证推理能力**：`curl -s http://<host>:8000/v1/chat/completions -d '{"model":"...","messages":[...], "max_tokens":10}'`
3. **分配规则**：
   - 高频任务（every 30m）→ 主节点（通常10ms级响应），如autonomous-core-researcher、evolution-full
   - 中频任务（every 6h / daily）→ 备节点（通常13ms级响应），如papers-daily-scan、literature-monitor、bib-standardization
   - 脚本任务（no_agent）→ 独立，不消耗LLM资源
4. **负载均衡目标**：主节点日调用~50次，备节点~7次；比例约7:1合理

## Pitfalls

- **误报率高**：约75%的"错误"文件是成功输出，skill内容含"Error"关键词被匹配。需用`grep "FAILED\|timed out"`精确匹配，而非`grep "Error"`
- **cron输出目录**：`~/.hermes/cron/output/<job_id>/<date>_time.md`，job_id是UUID
- **超时阈值**：no_agent脚本默认120s超时
- **LLM超时**：cron任务超时不一定是脚本问题——检查`custom:amax`(100.100.252.99:8000)和`amax-fallback`(100.82.27.51:8000)的可达性
- **历史日志爆炸**：单个job可能积累600+日志文件（102MB+），但旧的成功日志也会被错误标记
- **Python f-string + 多行 + CJK字符**：f-string内包含换行符`\n`和中文字符（✓/✗等）会导致`SyntaxError: unterminated string literal`。**修复**：将CJK字符替换为ASCII（'pass'/'fail'），提取变量后拼接，避免f-string内嵌多行字符串。示例：
  ```python
  # 错误
  report += f"| {name} | {'✓' if ok else '✗'} |\n"
  # 正确
  status = 'pass' if ok else 'fail'
  report += f"| {name} | {status} |\n"
  ```
- **rclone大目录sync超时**：`--stats 1s`输出频繁 + 全量扫描导致120s超时。**修复**：先用`rclone check`估计大小，sync时改用`--quiet`+`--stats 5s`+`--bwlimit 10M`限速
- **技能缺失导致的cron失败是基础设施级问题**：当cron任务引用的SKILL.md从agent技能库中被删除后（如`paper-pipeline`在2026-05-31后从`~/.hermes/skills/`消失），该任务会持续报错。错误日志显示为`RuntimeError: Request timed out`或`skill not found`，但根因是技能缺失而非网络超时。**诊断方法**：在`cronjob(action='list')`输出中查看`skill`字段，然后用`ls <skill_path>/SKILL.md`验证存在性。如果技能缺失，从备份或Synthos/skills/恢复。这种失败会伪装成网络问题，导致误诊。
- **cron任务引用不存在的技能**：cron任务可能引用一个从不存在于agent技能库中的技能（`skill`字段值在`~/.hermes/skills/`下无对应目录）。这是持续失败的根因之一，需要优先检查。

## 参考

- `references/cron-error-diagnosis-pattern.md` — 错误分类与诊断模式
- `references/cron-health-check-2026-06-12.md` — 完整诊断记录：3个error修复 + vLLM双活验证 + provider负载均衡 + 技能缺失根因发现
- `references/cron-failure-root-cause-diagnosis.md` — 技能缺失诊断流程（Step 4），最常见误诊的修复方案