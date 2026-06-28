---
name: incident-response
description: "事故响应 — 故障检测、应急响应、根因分析、事后复盘。为Synthos系统建立完善的事故处理流程。"
version: 1.0.0
allowed-tools:
- terminal
- execute_code
- browser
- cronjob
- skill_manage
- read_file
- write_file
- send_message
metadata:
  synthos:
    version: 1.0.0
    priority: P0
    atom_type: skill
    author: Synthos
    description: "事故响应 — 故障检测、应急响应、根因分析、事后复盘"
    signature: 'incident -> detect + respond + contain + recover + review'
    related_skills: ["system-reliability-engineering", "quality-gate", "cron-system-maintenance"]
triggers:
  - Cron连续失败≥3次或Cron全部error
  - 系统可用性低于SLO(99.9%)
  - 用户报告系统功能异常
  - 监控告警触发(P1/P0级别)
  - 进化循环score<0.7或status!=healthy
  - 知识图谱连通性<95%

---

# incident-response

> 事故响应方法论，为Synthos系统建立完善的故障检测、应急响应、根因分析和事后复盘流程。

## 触发条件

- cron连续失败≥3次或cron全部error
- 系统可用性低于SLO(99.9%)
- 用户报告系统功能异常
- 监控告警触发(P1/P0级别)
- 进化循环score<0.7或status!=healthy
- 知识图谱连通性<95%

## 执行步骤

1. **事故分级** — 根据影响范围和严重性:
   - **P0**(严重): 系统完全不可用，影响所有用户。进化循环完全失败、所有Cron停止、知识图谱损坏。响应: 15分钟。
   - **P1**(高): 核心功能受损。论文生成失败、部分Cron失败、关键技能失效。响应: 1小时。
   - **P2**(中): 非核心功能受损。单个论文检查失败、少数Cron失败。响应: 4小时。
   - **P3**(低): 体验问题。轻微性能下降、文档不一致。响应: 24小时。

2. **故障检测** — 确认事故范围:
   - `cronjob(action='list')` — 检查所有job状态
   - `ls ~/.hermes/cron/output/<job_id>/` — 检查错误日志
   - 系统资源: `df -h`, `free -m`, `top -bn1 | head -20`
   - 知识图谱: 检查graph.json连通性

3. **应急响应** — 按P0→P1→P2→P3分级处理:
   - **P0**: 立即响应 → 遏制扩散 → 恢复核心功能 → 通知用户
   - **P1**: 1小时内响应 → 确认影响范围 → 临时缓解 → 安排恢复
   - **P2**: 4小时内响应 → 评估影响 → 排期修复
   - **P3**: 24小时内响应 → 纳入下一次迭代

4. **根因分析** — 使用5 Whys方法:
   ```
   问题: Cron任务失败
   Why 1: 为什么失败? → 连接超时
   Why 2: 为什么超时? → vLLM节点无响应
   Why 3: 为什么无响应? → CPU满载
   Why 4: 为什么满载? → 多个高负载任务同时执行
   Why 5: 为什么同时执行? → Cron调度没有优先级和负载均衡
   根因: Cron调度策略缺陷
   ```

5. **事故复盘** — 无责备文化，关注系统:
   - 时间线重建: 检测→响应→遏制→恢复→验证
   - 影响评估: 影响范围、持续时间、用户影响
   - 改进措施: 短期(3天)、中期(1周)、长期(1月)
   - 责任人: 每个改进措施指定明确责任人

6. **持续改进** — 建立事故知识库:
   - 每次事故记录在evolution-state.json的incidents列表
   - 事故模式识别: 同一根因重复出现→系统性问题
   - 改进验证: 跟踪改进措施实施效果

## Pitfalls

- **无责备文化陷阱**: 复盘时不要追究"谁犯的错"，而要问"什么流程让错误发生了"。追责文化会导致隐瞒和重复犯错。
- **时间线不精确**: 事故时间线必须精确到分钟。从日志中实际提取，不要凭记忆估算。不精确的时间线会导致根因分析错误。
- **MTTR定义混淆**: MTTR是"从检测到恢复为SLO内"的时间，不是"从检测到开始处理"。开始处理≠恢复。统一这个定义才能准确衡量。
- **改进措施不闭环**: 复盘后制定的改进措施必须跟踪到完成。每个措施指定责任人、截止日期、验证方式。未完成→下次复盘首先检查。
- **事故报告过度技术化**: 事故报告要给不同角色看。技术团队看根因分析，管理层看影响和改进，用户看恢复状态。一份报告多种语言。
- **重复事故忽视**: 同一类型事故出现2次就是模式，不是偶然。出现3次就是系统缺陷，必须从根本上解决。不要每次只修表面。

## 参考

- Google SRE Incident Response: https://sre.google/sre-book/incident-response/
- AWS Incident Response: https://aws.amazon.com/blogs/mt/incident-response-best-practices/
- ITIL Incident Management: https://www.itilhouse.com/itil_book_2011/e2e_content/incident_management.htm

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

1. **输入验证**: 输入参数/文件/路径是否完整且有效
2. **过程验证**: 中间步骤/转换/计算是否正确
3. **输出验证**: 输出格式/内容是否符合预期
4. **边界验证**: 空输入、极大值、异常场景是否处理
5. **错误处理**: 失败时是否有明确的错误信息和恢复指引


## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。
