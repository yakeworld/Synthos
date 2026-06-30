---


name: cron-system-maintenance
related_skills: []
description: 'Cron任务运维：诊断error状态、修复脚本缺陷、验证连接性。覆盖cron job list分析、错误分类、脚本语法验证、prompt更新、vLLM多节点负载均衡。'
version: 1.0.0
license: MIT
author: Synthos
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
    atom_type: pipeline
    author: Synthos
    signature: 'job_list -> diagnose -> fix -> verify'



---



## IO_CONTRACT

- **input**: `cron_job: str, action: str` — 用户请求描述、上下文信息
- **output**: `result: dict — cron任务执行结果`

> 对应原则：P2（机械原子暴露输入输出规范）



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
- **Orphaned output directory cleanup**: cron任务被删除/重命名后在cron.output/目录留下残留输出目录（UUID目录名），不自动清理。定期执行：1) 列出cron.output/所有目录；2) 对照jobs.json中的id字段；3) 未匹配的目录移到.archive/子目录；4) paper-harvester使用status.json格式而非.md，不归档。参考实际案例：1ce13791(paper-quality-orchestrator, 173次运行/912KB)、0f0240a5(synthos-discussions-check, 5次)、42b92230(paper-repair, 1次)、4b666072(autonomous-core-researcher, 1次/BLOCKED)、6f9658a8(synthos-discussion-watch, 5次)、7c3528ae(cross-project-evolution, 1次)。

- **Cron → Codex 脚本迁移**：cron agent 任务（model 指向本地 vLLM）可迁移为 `no_agent=true` + `script` 模式，脚本内调用 `codex exec`。优势：获得 Codex 的自主规划能力。迁移步骤：1) 提取原 prompt 为 shell 脚本中的 `codex exec` 参数；2) 设置 `script` 字段；3) 选择合适 profile（hermes 用于代码任务，amax 用于进化相关）；4) 验证无 PTY 环境可运行。
- **Cron job 状态持久化缺失**：`synthos-daily-promo` 类的 cron 任务（每日轮转发帖）没有持久化状态机制来跟踪上次发布的序号。当任务失败时（如 timeout），下一次运行必须从 cron output 文件和 session DB 重建状态。修复方法：在 cron job 的 output 目录中写一个 `state.json` 或 `next_number.txt`，每次成功完成后递增；或者在 prompt 中增加状态自检步骤。详见 `references/cron-state-persistence-pattern.md`。

- **quality-gate cron 执行模式**：每4小时运行一次，核心流程为：
  1. 扫描 outputs/papers/ 下所有含 state.json 的论文目录（约100-150个）
  2. 用 python 脚本批量读取 quality_score 和 gate_status（而非逐个打开JSON）
  3. 筛选 FAIL/HARD_FAIL 论文和 gate_status != PASS 的论文
  4. 检查 tmux 会话中是否有仍在运行的 Codex 任务
  5. 读取最近一次 07-quality/ 下的 comprehensive report
  6. 如果全部 PASS → 输出 [SILENT]；如果有阻塞问题 → 生成报告并派 Codex
  7. 状态写入 /tmp/quality-gate-report-<date>.md 作为交付物
  **关键发现**：state.json 的 quality_score 可能有内部不一致（top-level vs gates_result），需要对比；archive 目录中的 FAIL 论文不需要处理；低分论文（<75）如果 gate=PASS 则不算阻塞。

- **Cron provider drift**: 当服务器节点被移除或替换后，cronjobs 引用旧 provider 名称时会静默失败（`Unknown provider 'custom:amax-1'`）。`cronjob(action='update')` 实际上不会修改 provider 字段 — provider 在 job 创建时固化。修复方法：必须 `action='remove'` 旧 job，然后用正确的 `model.provider` 重新 `action='create'`。任何服务器节点变更后，必须通过 `cronjob(action='list')` 验证所有 cronjob 的 provider 名称。

## 参考

- `references/cron-error-diagnosis-pattern.md` — 错误分类与诊断模式
- `references/cron-health-check-2026-06-12.md` — 完整诊断记录
- `references/quality-gate-cron-pattern.md` — Quality gate cron job 执行模式
- `references/cron-failure-root-cause-diagnosis.md` — 技能缺失诊断流程
- `references/codex-process-diagnosis-2026-06-21.md` — 诊断运行中 Codex 进程
- `references/cron-state-persistence-pattern.md` — Cron job 状态持久化
- `references/cron-timeout-fix-pattern.md` — Cron provider 超时修复模式（批量10个job一次性修复）
- `references/cron-provider-drift.md` — 服务器节点变更后 cronjob provider 名称漂移的诊断与修复

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## Golden 集合 · GOLDEN SET

- **Golden Input**: 标准输入样本（覆盖正常路径）
- **Golden Output**: 预期输出（精确匹配或格式校验）
- **Golden Error**: 预期错误信息（覆盖失败路径）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。



# Cron System Maintenance

